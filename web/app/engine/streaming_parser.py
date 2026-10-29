"""
Streaming JSON field extractor and resilient parser for Ollama structured outputs.
Demuxes the 'speech' string field token-by-token for typewriter streaming while
accumulating and repairing structured JSON for typed Pydantic validation.
"""

import json
import logging
import re
from typing import Dict, Any, Type, Optional, List
from pydantic import BaseModel, ValidationError

logger = logging.getLogger("byzantine.parser")


def check_court_readiness(speech: str) -> bool:
    """
    Robust semantic analysis determining if a caucus speech indicates readiness to proceed to court
    or an affirmative decision to cease internal deliberations.
    Avoids false positives when a speaker asks a question ('before we proceed to court, do you concur?').
    """
    if not speech:
        return False
    text = speech.lower().strip()

    # If the speaker explicitly asks to confer further or poses a question before proceeding, do not force exit
    confer_indicators = [
        r"\bbefore\s+we\s+(proceed|enter|move)\b",
        r"\bconfer\s+further\b",
        r"\bcontinue\s+(our\s+)?deliberat",
        r"\brequire\s+your\s+(input|assessment|concurrence)\b",
        r"\bdo\s+you\s+concur\b.*\?$"
    ]
    for c_pat in confer_indicators:
        if re.search(c_pat, text):
            return False

    court_patterns = [
        r"\bproceed\s+(immediately|directly|forthwith|now)\s+to\s+(open\s+)?court\b",
        r"\bwe\s+proceed\s+to\s+(open\s+)?court\b",
        r"\baction\s+is\s+to\s+(immediately\s+)?proceed\b.*?\bcourt\b",
        r"\benter\s+(open\s+)?court\s+(immediately|now|forthwith)\b",
        r"\bmove\s+to\s+(open\s+)?court\b",
        r"\bready\b.*?\b(for\s+court|for\s+trial|for\s+floor|to\s+litigate)\b",
        r"\bcease\b.*?\bdeliberat",
        r"\bconclude\b.*?\bdeliberat",
        r"\bstop\b.*?\b(deliberat|confer)",
        r"\bbypass\b.*?\bdeliberat",
        r"\bdemand\b.*?\b(immediate\s+)?(court|floor)\b",
        r"\bprepared\b.*?\bfor\s+(court|floor|trial)\b",
        r"\bmobilized\b.*?\bfor\s+(trial|court|floor)\b",
        r"\bbrief\s+for\s+court\b",
        r"\bfloor\s+proceedings\b",
        r"\bstrategy\s+is\s+(locked|finalized|confirmed)\b"
    ]
    for pat in court_patterns:
        if re.search(pat, text):
            return True
    return False


class StreamingFieldExtractor:
    """
    Finite-state machine that parses incoming JSON chunks and extracts the string value
    of a designated field (default 'speech') character-by-character as it arrives.
    Decodes escape sequences (\", \\n, \\\\, etc.) and yields clean plain-text tokens.
    """
    FIND_KEY = 0
    FIND_COLON = 1
    FIND_QUOTE = 2
    IN_STRING = 3
    DONE = 4

    def __init__(self, target_field: str = "speech"):
        self.target_field = target_field
        self.state = self.FIND_KEY
        self.raw_buffer: List[str] = []
        self._key_buffer = ""
        self._in_key = False
        self._escaped = False
        self._extracted: List[str] = []

    def feed(self, chunk: str) -> str:
        """Processes a streamed chunk and returns any decoded characters inside the target field."""
        self.raw_buffer.append(chunk)
        emitted: List[str] = []

        for char in chunk:
            if self.state == self.FIND_KEY:
                if char == '"':
                    if self._in_key:
                        self._in_key = False
                        if self._key_buffer == self.target_field:
                            self.state = self.FIND_COLON
                        self._key_buffer = ""
                    else:
                        self._in_key = True
                        self._key_buffer = ""
                elif self._in_key:
                    self._key_buffer += char

            elif self.state == self.FIND_COLON:
                if char == ':':
                    self.state = self.FIND_QUOTE

            elif self.state == self.FIND_QUOTE:
                if char == '"':
                    self.state = self.IN_STRING
                    self._escaped = False

            elif self.state == self.IN_STRING:
                if self._escaped:
                    if char == 'n':
                        emitted.append('\n')
                    elif char == 't':
                        emitted.append('\t')
                    elif char == '"':
                        emitted.append('"')
                    elif char == '\\':
                        emitted.append('\\')
                    else:
                        emitted.append(char)
                    self._escaped = False
                elif char == '\\':
                    self._escaped = True
                elif char == '"':
                    self.state = self.DONE
                else:
                    emitted.append(char)

            elif self.state == self.DONE:
                pass

        delta = "".join(emitted)
        if delta:
            self._extracted.append(delta)
        return delta

    def get_extracted_speech(self) -> str:
        return "".join(self._extracted).strip()

    def get_raw_text(self) -> str:
        return "".join(self.raw_buffer).strip()


class ResilientParser:
    """
    Multi-stage fallback parser that validates raw text against a Pydantic model.
    Guarantees no unhandled exceptions even if Ollama outputs truncated or malformed JSON.
    """
    @classmethod
    def _harmonize_model(cls, model_inst: BaseModel) -> BaseModel:
        """Harmonizes structured model action and metadata with semantic intent in speech."""
        speech_text = getattr(model_inst, "speech", "")
        if not speech_text:
            return model_inst

        speech_upper = speech_text.upper()
        speech_lower = speech_text.lower()

        # 1. Ratification Pleas (Phase 6): Harmonize accept vs decline_and_demand_remand
        if hasattr(model_inst, "action") and hasattr(model_inst, "demands_remand"):
            negated_remand = any(
                neg in speech_lower
                for neg in (
                    "without requesting appellate remand",
                    "without demanding remand",
                    "without demanding appellate remand",
                    "without requesting remand",
                    "do not demand remand",
                )
            )
            has_decline = any(
                term in speech_upper
                for term in (
                    "DECLINE",
                    "CONTEST",
                    "REJECT THE",
                    "FILE EXCEPTION",
                    "FILE A FORMAL EXCEPTION",
                    "FILE A FORMAL BOUNDARY EXCEPTION",
                )
            ) or (
                any(
                    term in speech_upper
                    for term in (
                        "DEMAND REMAND",
                        "DEMAND APPELLATE REMAND",
                        "DEMAND IMMEDIATE APPELLATE REMAND",
                    )
                )
                and not negated_remand
            )
            has_accept = (
                negated_remand
                or any(
                    term in speech_upper
                    for term in ("ACCEPT", "PRAISE", "RATIFY", "APPROVE", "CONCEDE", "ACQUIESCE")
                )
            )

            if has_accept and not has_decline:
                try:
                    return model_inst.model_copy(update={"action": "accept", "demands_remand": False})
                except Exception:
                    try:
                        setattr(model_inst, "action", "accept")
                        setattr(model_inst, "demands_remand", False)
                    except Exception:
                        pass
            elif has_decline:
                try:
                    return model_inst.model_copy(update={"action": "decline_and_demand_remand", "demands_remand": True})
                except Exception:
                    try:
                        setattr(model_inst, "action", "decline_and_demand_remand")
                        setattr(model_inst, "demands_remand", True)
                    except Exception:
                        pass

        # 2. Strategy Caucus (Phase 1): Harmonize court readiness
        if hasattr(model_inst, "action") and hasattr(model_inst, "ready_for_court"):
            if check_court_readiness(speech_text):
                try:
                    return model_inst.model_copy(update={"action": "proceed_to_court", "ready_for_court": True})
                except Exception:
                    try:
                        setattr(model_inst, "action", "proceed_to_court")
                        setattr(model_inst, "ready_for_court", True)
                    except Exception:
                        pass

        # 3. Floor Petitions (Phase 2): Harmonize petition vs rebuttal vs waiver
        if hasattr(model_inst, "action") and hasattr(model_inst, "jurisdiction_claimed"):
            updates: Dict[str, Any] = {}
            if any(term in speech_lower for term in ["refute", "rebut", "theft", "fraud", "contest", "counter", "overreach", "maneuver"]):
                updates["action"] = "rebut_claim"
            elif any(term in speech_lower for term in ["petition", "claim", "assert", "demand 100%", "open floor"]):
                updates["action"] = "petition_claim"

            if getattr(model_inst, "jurisdiction_claimed", "None") == "None":
                if any(term in speech_lower for term in ["fizz", "base-3", "digital root", "rule 42-b"]):
                    updates["jurisdiction_claimed"] = "Fizz"
                elif any(term in speech_lower for term in ["buzz", "base-5", "terminal glyph", "article v"]):
                    updates["jurisdiction_claimed"] = "Buzz"

            if updates:
                try:
                    return model_inst.model_copy(update=updates)
                except Exception:
                    for k, v in updates.items():
                        try:
                            setattr(model_inst, k, v)
                        except Exception:
                            pass

        # 4. Judge Baz Final Ruling (Phase 7): Harmonize decree action
        if hasattr(model_inst, "action") and hasattr(model_inst, "prejudice") and hasattr(model_inst, "verdict"):
            if any(term in speech_lower for term in ["exception", "stay", "dissolve", "remand"]):
                try:
                    return model_inst.model_copy(update={"action": "dissolve_stays_and_emit", "prejudice": True})
                except Exception:
                    pass
            elif "uncontested" in speech_lower:
                try:
                    return model_inst.model_copy(update={"action": "ratify_uncontested", "prejudice": True})
                except Exception:
                    pass

        return model_inst

    @classmethod
    def parse(
        cls,
        raw_text: str,
        model_cls: Type[BaseModel],
        default_speech: str = "",
        fallback_overrides: Optional[Dict[str, Any]] = None
    ) -> BaseModel:
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

        # Attempt 1: Direct JSON parse
        try:
            data = json.loads(cleaned)
            if isinstance(data, dict):
                if fallback_overrides:
                    for k, v in fallback_overrides.items():
                        if k not in data or data[k] is None or data[k] == "":
                            data[k] = v
                return cls._harmonize_model(model_cls.model_validate(data))
        except Exception:
            pass

        # Attempt 2: Regex extraction of embedded JSON object
        try:
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                if isinstance(data, dict):
                    if fallback_overrides:
                        for k, v in fallback_overrides.items():
                            if k not in data or data[k] is None or data[k] == "":
                                data[k] = v
                    return cls._harmonize_model(model_cls.model_validate(data))
        except Exception:
            pass

        # Attempt 3: Regex heuristic extraction of key fields
        speech_match = re.search(r'"speech":\s*"((?:[^"\\]|\\.)*)"', cleaned)
        action_match = re.search(r'"action":\s*"([^"]+)"', cleaned)
        status_match = re.search(r'"status":\s*"((?:[^"\\]|\\.)*)"', cleaned)
        ready_match = re.search(r'"ready_for_court":\s*(true|false)', cleaned, re.IGNORECASE)

        extracted_speech = ""
        if speech_match:
            try:
                extracted_speech = json.loads(f'"{speech_match.group(1)}"')
            except Exception:
                extracted_speech = speech_match.group(1)

        if not extracted_speech:
            extracted_speech = default_speech or cleaned

        synth_dict: Dict[str, Any] = {
            "speech": extracted_speech,
        }
        if action_match:
            synth_dict["action"] = action_match.group(1)
        if status_match:
            try:
                synth_dict["status"] = json.loads(f'"{status_match.group(1)}"')
            except Exception:
                synth_dict["status"] = status_match.group(1)
        if ready_match:
            synth_dict["ready_for_court"] = ready_match.group(1).lower() == "true"

        if fallback_overrides:
            for k, v in fallback_overrides.items():
                if k not in synth_dict or not synth_dict[k]:
                    synth_dict[k] = v

        try:
            return cls._harmonize_model(model_cls.model_validate(synth_dict))
        except ValidationError:
            safe_kwargs: Dict[str, Any] = {"speech": extracted_speech}
            if fallback_overrides:
                safe_kwargs.update(fallback_overrides)
            try:
                return cls._harmonize_model(model_cls.model_validate(safe_kwargs))
            except Exception as e:
                logger.warning(f"ResilientParser failed strict validation for {model_cls.__name__}: {e}. Returning default instance.")
                return cls._harmonize_model(model_cls.model_construct(speech=extracted_speech, **(fallback_overrides or {})))
