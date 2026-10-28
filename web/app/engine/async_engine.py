import asyncio
import httpx
import json
import logging
import random
import time
from typing import Dict, List, Tuple, Optional, Any, Type
from pydantic import BaseModel
from app.config import config
from app.database.models import DocketLedger
from app.engine.observer_manager import ActiveObserverManager
from app.engine.primitives import (
    verify_fizz_buzz_invariants,
    recursive_digital_root_reduction
)
from app.engine.streaming_parser import StreamingFieldExtractor, ResilientParser, check_court_readiness
from app.engine.fun_news import fun_news_desk
from app.engine.structured_schemas import (
    BailiffAnnouncement,
    HistorianPrecedentReport,
    JudgeBazChamberOrder,
    StrategyConferralTurn,
    FloorPetition,
    ForensicAuditReport,
    AntitrustDetermination,
    AppellateBriefing,
    RatificationPlea,
    JudgeBazRuling,
    VictoryAddressReport
)

logger = logging.getLogger("byzantine.engine")


class MistrialException(Exception):
    """Raised when the judicial inference quorum (Ollama connection) fails mid-docket."""
    def __init__(self, phase_idx: int, phase_name: str, speaker: str, speaker_role: str):
        super().__init__(f"Judicial inference quorum severed during {phase_name} ({speaker})")
        self.phase_idx = phase_idx
        self.phase_name = phase_name
        self.speaker = speaker
        self.speaker_role = speaker_role


class AsyncByzantineConsensusEngine:
    def __init__(self, ledger: DocketLedger, observer_mgr: ActiveObserverManager):
        self.ledger = ledger
        self.observer_mgr = observer_mgr
        self.client = httpx.AsyncClient(timeout=config.ollama_timeout)

    async def close(self):
        await self.client.aclose()

    async def check_inference_quorum(self) -> bool:
        """Checks whether the judicial inference server is reachable before convening a retrial."""
        endpoint = f"{config.ollama_server.rstrip('/')}/api/tags"
        try:
            resp = await self.client.get(endpoint, timeout=3.0)
            return resp.status_code == 200
        except Exception:
            return False

    async def stream_ollama(
        self,
        messages: List[Dict[str, str]],
        docket_id: str,
        payload: str,
        phase_idx: int,
        phase_name: str,
        speaker: str,
        speaker_role: str,
        fallback_text: str = "",
        model_cls: Optional[Type[BaseModel]] = None,
        fallback_overrides: Optional[Dict[str, Any]] = None,
        temperature: float = 0.2,
        force_action: Optional[str] = None
    ) -> Tuple[str, Optional[BaseModel]]:
        """
        Streams tokens from Ollama /api/chat and broadcasts each chunk in real time.
        When model_cls is provided, enforces structured JSON via Ollama format schema and uses
        StreamingFieldExtractor to demux 'speech' tokens in real time for typewriter rendering.
        """
        endpoint = f"{config.ollama_server.rstrip('/')}/api/chat"
        req_data: Dict[str, Any] = {
            "model": config.ollama_model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature
            }
        }
        if model_cls is not None:
            req_data["format"] = model_cls.model_json_schema()

        extractor = StreamingFieldExtractor("speech") if model_cls is not None else None
        accumulated_raw: List[str] = []

        try:
            async with self.client.stream("POST", endpoint, json=req_data) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        accumulated_raw.append(token)
                        delta = extractor.feed(token) if extractor is not None else token
                        if delta:
                            await self.observer_mgr.broadcast({
                                "event": "TOKEN_STREAM",
                                "docket_id": docket_id,
                                "payload": payload,
                                "phase_index": phase_idx,
                                "phase_name": phase_name,
                                "stage_index": phase_idx,
                                "stage_name": phase_name,
                                "speaker": speaker,
                                "speaker_role": speaker_role,
                                "token": delta,
                                "timestamp": time.time()
                            })
                            if config.token_stream_delay > 0:
                                await asyncio.sleep(config.token_stream_delay)

                    if chunk.get("done", False):
                        break

            raw_str = "".join(accumulated_raw).strip()
            parsed_model: Optional[BaseModel] = None

            if model_cls is not None and extractor is not None:
                extracted_speech = extractor.get_extracted_speech()
                parsed_model = ResilientParser.parse(
                    raw_text=raw_str,
                    model_cls=model_cls,
                    default_speech=extracted_speech or fallback_text,
                    fallback_overrides=fallback_overrides
                )
                full_text = getattr(parsed_model, "speech", extracted_speech) or fallback_text or f"[{speaker} testimony entered into official court ledger.]"
            else:
                full_text = raw_str or fallback_text or f"[{speaker} testimony entered into official court ledger.]"

            # Recover cleanly if model emitted an incomplete colon-terminated intro stub
            if fallback_text and (full_text.strip().endswith(":") or len(full_text.strip()) < 25):
                if full_text.strip().endswith(":"):
                    full_text = f"{full_text.strip()} {fallback_text}"
                else:
                    full_text = fallback_text
                if parsed_model is not None and hasattr(parsed_model, "speech"):
                    try:
                        setattr(parsed_model, "speech", full_text)
                    except Exception:
                        pass

            if force_action and parsed_model is not None and hasattr(parsed_model, "action"):
                try:
                    setattr(parsed_model, "action", force_action)
                    if hasattr(parsed_model, "ready_for_court"):
                        setattr(parsed_model, "ready_for_court", force_action == "proceed_to_court")
                except Exception:
                    pass

            action_val = getattr(parsed_model, "action", force_action) if parsed_model is not None else force_action
            status_val = getattr(parsed_model, "status", None) if parsed_model is not None else None
            if status_val:
                status_val = str(status_val).strip().strip("_*\"'")

            await self.observer_mgr.broadcast({
                "event": "SPEECH_COMPLETE",
                "docket_id": docket_id,
                "payload": payload,
                "phase_index": phase_idx,
                "phase_name": phase_name,
                "speaker": speaker,
                "speaker_role": speaker_role,
                "full_text": full_text,
                "action": action_val,
                "status": status_val,
                "structured_data": parsed_model.model_dump() if parsed_model else None,
                "timestamp": time.time()
            })
            return full_text, parsed_model

        except Exception as e:
            logger.error(f"Error streaming from Ollama during {phase_name} ({speaker}): {e}")
            interrupted_text = (
                f"[Testimony of {speaker} abruptly severed due to a catastrophic loss of quorum on the judicial inference link.]"
            )
            await self.observer_mgr.broadcast({
                "event": "SPEECH_COMPLETE",
                "docket_id": docket_id,
                "payload": payload,
                "phase_index": phase_idx,
                "phase_name": phase_name,
                "speaker": speaker,
                "speaker_role": speaker_role,
                "full_text": interrupted_text,
                "action": "quorum_severed",
                "status": "Connection severed mid-testimony",
                "structured_data": None,
                "timestamp": time.time()
            })
            raise MistrialException(
                phase_idx=phase_idx,
                phase_name=phase_name,
                speaker=speaker,
                speaker_role=speaker_role
            ) from e

    async def _stream_statutory_proclamation(
        self,
        docket_id: str,
        payload: str,
        phase_idx: int,
        phase_name: str,
        speaker: str,
        speaker_role: str,
        speech_text: str,
        action: str,
        structured_data: Optional[Dict[str, Any]] = None,
        token_delay: Optional[float] = None,
        status: Optional[str] = None
    ) -> str:
        """Streams an official statutory proclamation or broadcast word by word."""
        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": docket_id,
            "phase_index": phase_idx,
            "phase_name": phase_name,
            "stage_index": phase_idx,
            "stage_name": phase_name,
            "speaker": speaker,
            "speaker_role": speaker_role
        })
        effective_delay = config.token_stream_delay if token_delay is None else token_delay
        words = speech_text.split(" ")
        for idx, word in enumerate(words):
            token = word if idx == 0 else f" {word}"
            await self.observer_mgr.broadcast({
                "event": "TOKEN_STREAM",
                "docket_id": docket_id,
                "payload": payload,
                "phase_index": phase_idx,
                "phase_name": phase_name,
                "stage_index": phase_idx,
                "stage_name": phase_name,
                "speaker": speaker,
                "speaker_role": speaker_role,
                "token": token,
                "timestamp": time.time()
            })
            if effective_delay > 0:
                await asyncio.sleep(effective_delay)

        await self.observer_mgr.broadcast({
            "event": "SPEECH_COMPLETE",
            "docket_id": docket_id,
            "payload": payload,
            "phase_index": phase_idx,
            "phase_name": phase_name,
            "speaker": speaker,
            "speaker_role": speaker_role,
            "full_text": speech_text,
            "action": action,
            "status": status,
            "structured_data": structured_data,
            "timestamp": time.time()
        })
        return speech_text

    async def stream_fun_recap(self, transcript: Dict[str, Any]) -> str:
        """
        Streams the Foo Universal News (FUN) recap broadcast during the Parliamentary Recess countdown.
        """
        case_id = transcript.get("case_id", "BZ-2026-0000")
        payload = transcript.get("payload", "0")
        recap_script = transcript.get("fun_recap")
        if not recap_script:
            recap_data = fun_news_desk.build_recap_script(transcript)
            recap_script = recap_data["script"]
            transcript["fun_recap"] = recap_script
            transcript["fun_parody_headline"] = recap_data["parody_headline"]

        # Stream at brisk teleprompter pace during the recess window (or 0.0 during unit tests)
        teleprompter_delay = 0.0 if config.token_stream_delay == 0 else max(config.token_stream_delay, 0.035)
        return await self._stream_statutory_proclamation(
            docket_id=case_id,
            payload=payload,
            phase_idx=9,
            phase_name="Foo Universal News (FUN) — Recess Recap",
            speaker="Foo Universal News (FUN) — Anchor Desk",
            speaker_role="news",
            speech_text=recap_script,
            action="fun_recess_broadcast",
            structured_data={
                "network": "Foo Universal News (FUN)",
                "parody_headline": transcript.get("fun_parody_headline", "")
            },
            token_delay=teleprompter_delay,
            status="Live from the FUN studio"
        )

    async def adjudicate(self, payload: str, source: str, range_end: int = 10) -> Dict[str, Any]:
        """
        Executes full tribunal adjudication with structured outputs, Bailiff Bar, Judge Baz,
        and dynamic counterpart strategy conferring loop. If the Ollama inference quorum fails,
        Bailiff Bar and Judge Baz officially declare a Mistrial and schedule a de novo retrial
        prior to the next statutory max range increase.
        """
        total_cases = await self.ledger.get_total_cases()
        prior_rulings = await self.ledger.get_prior_rulings(payload)
        completed_priors = [r for r in prior_rulings if r.get("emitted_token") != "Mistrial"]
        mistrial_priors = [r for r in prior_rulings if r.get("emitted_token") == "Mistrial"]
        payload_prior_count = len(prior_rulings)
        if mistrial_priors and not completed_priors:
            case_id = mistrial_priors[0]["case_id"]
        elif not completed_priors:
            case_id = f"BZ-2026-{payload.zfill(4)}"
        else:
            case_id = f"BZ-2026-{payload.zfill(4)}-R{len(completed_priors) + 1}"

        fizz_valid, buzz_valid, root, glyph, trace = verify_fizz_buzz_invariants(payload)
        is_collision = fizz_valid and buzz_valid

        await self.observer_mgr.broadcast({
            "event": "DOCKET_START",
            "docket_id": case_id,
            "payload": payload,
            "source": source,
            "digital_root": root,
            "terminal_glyph": glyph,
            "timestamp": time.time()
        })

        transcript: Dict[str, Any] = {
            "case_id": case_id,
            "payload": payload,
            "source": source,
            "digital_root": root,
            "terminal_glyph": glyph,
            "trace": trace
        }

        try:
            provisional_token, verdict_desc = await self._execute_tribunal_phases(
                case_id=case_id,
                payload=payload,
                root=root,
                glyph=glyph,
                fizz_valid=fizz_valid,
                buzz_valid=buzz_valid,
                is_collision=is_collision,
                total_cases=total_cases,
                prior_rulings=prior_rulings,
                payload_prior_count=payload_prior_count,
                transcript=transcript
            )
        except MistrialException as me:
            retrial_offset_sec = max(int(config.recess_seconds) * 2, 120)
            retrial_ts = time.time() + retrial_offset_sec
            retrial_date_str = time.strftime("%Y-%m-%d at %H:%M:%S UTC", time.gmtime(retrial_ts))

            if config.phase_delay_seconds > 0:
                await asyncio.sleep(config.phase_delay_seconds)

            bailiff_mistrial_phase = "Emergency Mistrial Proclamation"
            bailiff_mistrial_speech = (
                f"Order in the court! Let the official record reflect that a catastrophic communication failure has severed "
                f"the judicial inference quorum during the testimony of {me.speaker} in {me.phase_name}. "
                f"Pursuant to Article IX, Section 4 of the Modulo-Free Accord, I hereby suspend floor proceedings and call upon "
                f"the Honorable Judge Baz to declare an immediate Mistrial on Docket {case_id}!"
            )
            await self._stream_statutory_proclamation(
                docket_id=case_id,
                payload=payload,
                phase_idx=7,
                phase_name=bailiff_mistrial_phase,
                speaker="Bailiff Bar",
                speaker_role="bailiff",
                speech_text=bailiff_mistrial_speech,
                action="declare_mistrial",
                structured_data={
                    "presiding_judge": "Judge Baz",
                    "action": "declare_mistrial",
                    "interrupted_phase": me.phase_name,
                    "interrupted_speaker": me.speaker
                },
                status="Suspending floor proceedings"
            )
            transcript["bailiff_mistrial_proclamation"] = bailiff_mistrial_speech

            if config.phase_delay_seconds > 0:
                await asyncio.sleep(config.phase_delay_seconds)

            judge_mistrial_phase = "Official Order of Mistrial & Retrial Calendar"
            judge_mistrial_speech = (
                f"By the sovereign authority vested in this bench under Article IX of the Modulo-Free Accord, Docket {case_id} "
                f"concerning Inbound Payload '{payload}' is hereby declared a MISTRIAL without prejudice. "
                f"All partial testimony is stricken from the merits, no consensus token shall issue, and this cause is officially "
                f"calendared for mandatory de novo retrial on {retrial_date_str}—and in all events prior to any statutory ceiling "
                f"expansion beyond Docket #{range_end}. So ordered!"
            )
            await self._stream_statutory_proclamation(
                docket_id=case_id,
                payload=payload,
                phase_idx=8,
                phase_name=judge_mistrial_phase,
                speaker="Judge Baz, Presiding Magistrate",
                speaker_role="judge",
                speech_text=judge_mistrial_speech,
                action="order_retrial_before_expansion",
                structured_data={
                    "presiding_judge": "Judge Baz",
                    "verdict": "Mistrial",
                    "action": "order_retrial_before_expansion",
                    "retrial_scheduled_for": retrial_date_str,
                    "retrial_before_max_increase": range_end
                },
                status="Calendaring de novo retrial"
            )
            provisional_token = "Mistrial"
            verdict_desc = (
                f"OFFICIAL ORDER OF MISTRIAL: Judicial inference quorum severed during {me.phase_name}. "
                f"Calendared by Judge Baz for mandatory de novo retrial on {retrial_date_str} "
                f"(prior to statutory ceiling expansion beyond #{range_end})."
            )
            transcript["mistrial"] = True
            transcript["interrupted_phase"] = me.phase_name
            transcript["interrupted_speaker"] = me.speaker
            transcript["retrial_scheduled_for"] = retrial_date_str
            transcript["retrial_before_max_increase"] = range_end
            transcript["judge_mistrial_order"] = judge_mistrial_speech
            transcript["judge_baz_order"] = judge_mistrial_speech
            transcript["appellate_order"] = judge_mistrial_speech
            transcript["provisional_token"] = provisional_token
            transcript["verdict_desc"] = verdict_desc

        # -----------------------------------------------------------------
        # CONCLUDE & RECORD TO DATABASE
        # -----------------------------------------------------------------
        final_token = provisional_token
        transcript["final_token"] = final_token
        recap_data = fun_news_desk.build_recap_script(transcript)
        transcript["fun_recap"] = recap_data["script"]
        transcript["fun_parody_headline"] = recap_data["parody_headline"]

        await self.ledger.record_docket(
            case_id=case_id,
            payload=payload,
            digital_root=root,
            terminal_glyph=glyph,
            fizz_valid=fizz_valid,
            buzz_valid=buzz_valid,
            verdict=verdict_desc,
            emitted_token=final_token,
            transcript=transcript
        )

        await self.observer_mgr.broadcast({
            "event": "DOCKET_CONCLUDED",
            "docket_id": case_id,
            "payload": payload,
            "final_token": final_token,
            "verdict": verdict_desc,
            "timestamp": time.time()
        })

        return transcript

    async def _execute_tribunal_phases(
        self,
        case_id: str,
        payload: str,
        root: str,
        glyph: str,
        fizz_valid: bool,
        buzz_valid: bool,
        is_collision: bool,
        total_cases: int,
        prior_rulings: List[Dict[str, Any]],
        payload_prior_count: int,
        transcript: Dict[str, Any]
    ) -> Tuple[str, str]:

        # -----------------------------------------------------------------
        # PHASE 0A: CALL TO ORDER & PROCLAMATION (Bailiff Bar)
        # -----------------------------------------------------------------
        phase0a_name = "Docket Call & Proclamation"
        bailiff_prompt = [
            {
                "role": "system",
                "content": (
                    "You are Bailiff Bar, the authoritative Sergeant-at-Arms of the Zero-Trust Byzantine Court. "
                    "All modulo (%) and division (/) operations are strictly outlawed under the Zero-Trust Accord. "
                    f"Write 2 complete, commanding sentences in a single paragraph (do not end with a colon): call all present to order, "
                    f"announce that the tribunal is now convened in the matter of Inbound Payload '{payload}' (Docket {case_id}), "
                    "and solemnly proclaim that Judge Baz is presiding over this tribunal."
                    "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
                    "Output valid JSON with keys in this exact order:\n"
                    "- 'speech': Your 2-sentence ceremonial call to order.\n"
                    "- 'presiding_judge': Exactly 'Judge Baz'.\n"
                    "- 'action': Choose 'call_to_order' or 'swear_in_factions'.\n"
                    "- 'status': Short 2-to-5 word public social media status (e.g. 'Keeping order in the court')."
                )
            },
            {
                "role": "user",
                "content": f"Call the courtroom to order for Docket {case_id} (payload '{payload}') with Judge Baz presiding."
            }
        ]
        bailiff_fallback = (
            f"All rise! The Zero-Trust Byzantine Tribunal is now in session for Docket {case_id}, "
            f"concerning Inbound Payload '{payload}', with the Honorable Judge Baz presiding."
        )
        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": case_id,
            "phase_index": 0,
            "phase_name": phase0a_name,
            "stage_index": 0,
            "stage_name": phase0a_name,
            "speaker": "Bailiff Bar",
            "speaker_role": "bailiff"
        })
        bailiff_speech, bailiff_obj = await self.stream_ollama(
            bailiff_prompt, case_id, payload, 0, phase0a_name, "Bailiff Bar", "bailiff",
            fallback_text=bailiff_fallback,
            model_cls=BailiffAnnouncement,
            fallback_overrides={
                "action": "call_to_order",
                "presiding_judge": "Judge Baz",
                "status": "Keeping order in the court"
            }
        )
        transcript["bailiff_proclamation"] = bailiff_speech
        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        # -----------------------------------------------------------------
        # PHASE 0B: COURT HISTORIAN REVIEW
        # -----------------------------------------------------------------
        phase0b_name = "Court Historian Precedent Review"
        historian_schema_guide = (
            "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
            "Output valid JSON with keys in this exact order:\n"
            "- 'speech': Your 2-sentence archival precedent report.\n"
            "- 'action': Choose 'enter_case_of_first_impression', 'cite_binding_precedent', or 'schedule_mistrial_retrial'.\n"
            "- 'status': Short 2-to-5 word public social media status (e.g. 'Indexing the sacred ledger')."
        )

        if prior_rulings:
            prev = prior_rulings[0]
            prev_case = prev["case_id"]
            prev_token = prev["emitted_token"]
            prev_verdict = prev["verdict"]
            prev_date = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(prev["adjudicated_at"]))
            if prev_token == "Mistrial":
                historian_action = "schedule_mistrial_retrial"
                historian_status = "Tracking de novo retrials"
                historian_prompt = [
                    {
                        "role": "system",
                        "content": (
                            "You are the revered Court Historian of the Zero-Trust Byzantine Court. "
                            "Report ONLY the following three official archival facts in 2 formal sentences of legal antiquity:\n"
                            f"1. Total Archive Records: {total_cases} total dockets recorded in the tribunal archives across all numbers.\n"
                            f"2. Prior Proceedings for Current Number ('{payload}'): {payload_prior_count} prior proceeding(s) on record specifically for payload '{payload}'.\n"
                            f"3. Last Proceeding on Current Number ('{payload}'): Docket {prev_case} (on {prev_date}), which ended in an Official Mistrial without prejudice ({prev_verdict}).\n"
                            f"In 2 eloquent sentences: state the total archive record count ({total_cases}), state that payload '{payload}' has {payload_prior_count} prior proceeding(s) on record, "
                            f"and note that because Docket {prev_case} was declared a Mistrial without prejudice, payload '{payload}' now returns for mandatory de novo retrial."
                            + historian_schema_guide
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Enter the total records ({total_cases}), prior Mistrial on Docket {prev_case}, and de novo retrial posture for payload '{payload}' into the court record."
                    }
                ]
                historian_fallback = (
                    f"The tribunal archives hold {total_cases} total adjudicated records, including {payload_prior_count} prior proceeding(s) for payload '{payload}'. "
                    f"Because Docket {prev_case} on {prev_date} ended in an Official Mistrial without prejudice, payload '{payload}' now stands before the Court for mandatory de novo retrial."
                )
            else:
                historian_action = "cite_binding_precedent"
                historian_status = "Citing binding stare decisis"
                historian_prompt = [
                    {
                        "role": "system",
                        "content": (
                            "You are the revered Court Historian of the Zero-Trust Byzantine Court. "
                            "Report ONLY the following three official archival facts in 2 formal sentences of legal antiquity:\n"
                            f"1. Total Archive Records: {total_cases} total dockets recorded in the tribunal archives across all numbers.\n"
                            f"2. Precedents for Current Number ('{payload}'): {payload_prior_count} prior precedent(s) on record specifically for payload '{payload}'.\n"
                            f"3. Last Ruling on Current Number ('{payload}'): Docket {prev_case} (adjudicated on {prev_date}), which emitted certified consensus token '{prev_token}' ({prev_verdict}).\n"
                            f"In 2 eloquent sentences: state the total archive record count ({total_cases}), state that payload '{payload}' has {payload_prior_count} prior precedent(s), "
                            f"and cite the last ruling on payload '{payload}' (Docket {prev_case}, emitting '{prev_token}') as binding stare decisis."
                            + historian_schema_guide
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Enter the total records ({total_cases}), precedent count ({payload_prior_count}), and last ruling on payload '{payload}' into the court record."
                    }
                ]
                historian_fallback = (
                    f"The tribunal archives hold {total_cases} total adjudicated records, including {payload_prior_count} prior precedent(s) specifically for payload '{payload}'. "
                    f"In the last ruling on payload '{payload}' (Docket {prev_case} on {prev_date}), this court emitted certified consensus token '{prev_token}', which stands as binding stare decisis."
                )
        else:
            historian_action = "enter_case_of_first_impression"
            historian_status = "Indexing the sacred ledger"
            historian_prompt = [
                {
                    "role": "system",
                    "content": (
                        "You are the revered Court Historian of the Zero-Trust Byzantine Court. "
                        "Report ONLY the following three official archival facts in 2 formal sentences of legal antiquity:\n"
                        f"1. Total Archive Records: {total_cases} total dockets recorded in the tribunal archives across all numbers.\n"
                        f"2. Precedents for Current Number ('{payload}'): 0 prior precedents on record for payload '{payload}'.\n"
                        f"3. Last Ruling on Current Number ('{payload}'): None (payload '{payload}' has never been adjudicated before).\n"
                        f"In 2 eloquent sentences: state that the tribunal archive contains {total_cases} total records across all numbers, "
                        f"confirm that payload '{payload}' has 0 prior precedents and no previous ruling on record, "
                        f"and proclaim payload '{payload}' a Case of First Impression under the Modulo-Free Accord."
                        + historian_schema_guide
                    )
                },
                {
                    "role": "user",
                    "content": f"Enter the total records ({total_cases}), 0 precedents for payload '{payload}', and Case of First Impression status into the court record."
                }
            ]
            historian_fallback = (
                f"While the tribunal archives contain {total_cases} total adjudicated records across all numbers, "
                f"inbound payload '{payload}' has 0 prior precedents and no previous ruling on record, making it a Case of First Impression under the Modulo-Free Accord."
            )

        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": case_id,
            "phase_index": 0,
            "phase_name": phase0b_name,
            "stage_index": 0,
            "stage_name": phase0b_name,
            "speaker": "The Court Historian",
            "speaker_role": "historian"
        })
        historian_speech, _ = await self.stream_ollama(
            historian_prompt, case_id, payload, 0, phase0b_name, "The Court Historian", "historian",
            fallback_text=historian_fallback,
            model_cls=HistorianPrecedentReport,
            fallback_overrides={"action": historian_action, "status": historian_status},
            force_action=historian_action
        )
        transcript["historian_statement"] = historian_speech
        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        # -----------------------------------------------------------------
        # PHASE 0C: JUDICIAL ORDER TO PRIVATE CHAMBERS (Judge Baz)
        # -----------------------------------------------------------------
        phase0c_name = "Chamber Release Order"
        judge_chamber_prompt = [
            {
                "role": "system",
                "content": (
                    "You are Judge Baz, the sovereign Presiding Magistrate of the Byzantine Appellate Board. "
                    "All modulo (%) and division (/) operations are strictly outlawed under the Zero-Trust Accord. "
                    f"Write 2 complete, commanding judicial sentences directly (do NOT write an introductory phrase ending in a colon): "
                    f"order counsel and strategists for both the Fizz Consortium and the Buzz Syndicate to retire immediately "
                    f"to their separate, closed-door chambers to confer on Inbound Payload '{payload}', and place the open floor "
                    "in temporary recess until both chambers conclude their deliberations."
                    "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
                    "Output valid JSON with keys in this exact order:\n"
                    "- 'speech': Your complete 2-sentence judicial decree (no colons at the end).\n"
                    "- 'presiding_judge': Exactly 'Judge Baz'.\n"
                    "- 'action': Choose 'release_to_private_deliberations' or 'order_private_caucus'.\n"
                    "- 'status': Short 2-to-5 word public social media status (e.g. 'Gavel polished and ready')."
                )
            },
            {
                "role": "user",
                "content": f"Issue your complete 2-sentence judicial decree releasing factions to private chambers for payload '{payload}'."
            }
        ]
        judge_chamber_fallback = (
            f"Counsel and strategists for the Fizz Consortium and the Buzz Syndicate are hereby ordered to retire immediately "
            f"to their separate, closed-door chambers to confer on Inbound Payload '{payload}' under the Modulo-Free Accord. "
            "This tribunal stands in temporary recess until both factions conclude their in-camera deliberations."
        )
        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": case_id,
            "phase_index": 0,
            "phase_name": phase0c_name,
            "stage_index": 0,
            "stage_name": phase0c_name,
            "speaker": "Judge Baz, Presiding Magistrate",
            "speaker_role": "judge"
        })
        judge_chamber_speech, _ = await self.stream_ollama(
            judge_chamber_prompt, case_id, payload, 0, phase0c_name, "Judge Baz, Presiding Magistrate", "judge",
            fallback_text=judge_chamber_fallback,
            model_cls=JudgeBazChamberOrder,
            fallback_overrides={
                "action": "release_to_private_deliberations",
                "presiding_judge": "Judge Baz",
                "status": "Gavel polished and ready"
            }
        )
        transcript["judge_chamber_order"] = judge_chamber_speech
        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        # -----------------------------------------------------------------
        # PHASE 1A: FIZZ CONSORTIUM PRIVATE CHAMBERS (Closed-Door Dialogue)
        # -----------------------------------------------------------------
        phase1_name = "In-Camera Strategy Deliberations"
        max_faction_rounds = min(max(2, config.max_caucus_rounds // 2), 3)
        fizz_history: List[Dict[str, Any]] = []
        last_fizz_memo = ""
        fizz_strategy_choice = "assert_exclusive_domain" if fizz_valid else "challenge_jurisdiction"

        caucus_schema_guide = (
            "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
            "Output valid JSON with keys in this exact order (reason in 'speech' first, then select your enums and status last):\n"
            "- 'speech': 2 concise sentences addressing your chamber counterpart.\n"
            "- 'strategy_choice': Choose ONE of:\n"
            "    * 'assert_exclusive_domain' (when your math is valid and exclusive)\n"
            "    * 'prepare_merger_contingency' (when both Fizz and Buzz have valid math on a collision)\n"
            "    * 'probe_counterpart_vulnerability' (attacking the rival's arithmetic weakness)\n"
            "    * 'challenge_jurisdiction' (procedural bluff when your own math does not qualify)\n"
            "- 'action': Choose ONE of:\n"
            "    * 'confer_further' (to pass the floor to your chamber counterpart for confirmation)\n"
            "    * 'proceed_to_court' (once strategy is agreed upon and you are ready to enter open court)\n"
            "- 'status': Short 2-to-5 word public social media status (e.g. 'Plotting behind closed doors')."
        )

        fizz_math_truth = (
            f"MATHEMATICAL GROUND TRUTH: Payload '{payload}' reduces to digital root '{root}', which IS in {{3, 6, 9}} (VALID Base-3 Fizz claim under Rule 42-B). "
            + (f"WARNING: Terminal glyph is '{glyph}' (in {{0, 5}}), meaning Buzz ALSO has a valid claim (FizzBuzz collision!)."
               if buzz_valid else f"Terminal glyph is '{glyph}' (NOT in {{0, 5}}), so Buzz's claim is invalid and Fizz is entitled to 100% exclusive domain!")
            if fizz_valid else
            f"MATHEMATICAL GROUND TRUTH: Payload '{payload}' reduces to digital root '{root}', which is NOT in {{3, 6, 9}} (our strict Base-3 math FAILS on this payload). "
            + (f"Worse, terminal glyph is '{glyph}' (in {{0, 5}}), so Buzz has a valid claim unless we mount a creative procedural challenge!"
               if buzz_valid else f"Terminal glyph is '{glyph}' (also invalid for Buzz), so neither cartel qualifies unless we bluff!")
        )

        for r in range(1, max_faction_rounds + 1):
            if self.observer_mgr.active_count == 0:
                logger.info("No active observers detected during Fizz caucus. Ending early.")
                break

            is_final_round = (r == max_faction_rounds)
            if r % 2 == 1:
                speaker_label = f"Fizz Quantitative Strategist (Behind Closed Doors - Round {r})"
                if r == 1:
                    turn_instruction = (
                        "You are the Fizz Quantitative Strategist speaking privately to Lobbyist-3 (Fizz Floor Counsel) in the Fizz Chamber. "
                        f"{fizz_math_truth} "
                        "In 2 sharp sentences: brief Lobbyist-3 on this exact mathematical reality, propose a concrete courtroom angle "
                        "(statutory claim if valid, or a clever procedural bluff/jurisdiction challenge if invalid), and ask Lobbyist-3 for concurrence before entering court. "
                        "Set action to 'confer_further' so Lobbyist-3 can respond."
                    )
                    default_action = "confer_further"
                else:
                    turn_instruction = (
                        "You are the Fizz Quantitative Strategist replying to Lobbyist-3 in the final round of Fizz Private Chambers. "
                        f"Lobbyist-3 just said: \"{last_fizz_memo}\". "
                        "In 2 decisive sentences: resolve any remaining tactical question, lock in the final Fizz battle plan, and announce that we proceed immediately to open court. "
                        "You MUST set action to 'proceed_to_court'."
                    )
                    default_action = "proceed_to_court"
            else:
                speaker_label = f"Lobbyist-3, Fizz Counsel (Behind Closed Doors - Round {r})"
                turn_instruction = (
                    "You are Lobbyist-3 (Fizz Floor Counsel) replying privately to the Fizz Quantitative Strategist in the Fizz Chamber. "
                    f"The Strategist just briefed you: \"{last_fizz_memo}\". {fizz_math_truth} "
                    "In 2 sharp sentences: respond directly to the Strategist's proposed angle. "
                    "If the strategy is clear and you are ready to argue it on the floor, state that our strategy is locked and set action to 'proceed_to_court'. "
                    "Only set action to 'confer_further' if you have a genuine unresolved question for the Strategist."
                )
                default_action = "proceed_to_court"

            fizz_prompt = [
                {"role": "system", "content": turn_instruction + caucus_schema_guide},
                {"role": "user", "content": f"Deliver Round {r} closed-door chamber statement for payload '{payload}'."}
            ]
            fizz_fallback = (
                f"Digital root '{root}' has been audited under Rule 42-B; our courtroom posture is locked and we proceed immediately to open court."
            )
            await self.observer_mgr.broadcast({
                "event": "PHASE_TRANSITION",
                "docket_id": case_id,
                "phase_index": 1,
                "phase_name": f"Fizz Private Chamber (Behind Closed Doors - Round {r}/{max_faction_rounds})",
                "stage_index": 1,
                "stage_name": phase1_name,
                "speaker": speaker_label,
                "speaker_role": "fizz"
            })
            fizz_speech, fizz_obj = await self.stream_ollama(
                fizz_prompt, case_id, payload, 1,
                f"Fizz Private Chamber (Behind Closed Doors - Round {r})",
                speaker_label, "fizz",
                fallback_text=fizz_fallback,
                model_cls=StrategyConferralTurn,
                fallback_overrides={
                    "action": default_action,
                    "strategy_choice": fizz_strategy_choice
                },
                force_action="proceed_to_court" if is_final_round else None
            )
            last_fizz_memo = fizz_speech
            if fizz_obj and getattr(fizz_obj, "strategy_choice", None):
                fizz_strategy_choice = getattr(fizz_obj, "strategy_choice")

            fizz_action = "proceed_to_court" if is_final_round else getattr(fizz_obj, "action", default_action)
            fizz_ready = (fizz_action == "proceed_to_court")

            fizz_history.append({
                "round": r,
                "speaker": speaker_label,
                "speech": fizz_speech,
                "strategy_choice": fizz_strategy_choice,
                "action": fizz_action,
                "ready": fizz_ready
            })

            if config.phase_delay_seconds > 0:
                await asyncio.sleep(config.phase_delay_seconds)

            if fizz_ready:
                logger.info(f"Fizz Consortium ready for court after {r} internal round(s).")
                break

        # -----------------------------------------------------------------
        # PHASE 1B: BUZZ SYNDICATE PRIVATE CHAMBERS (Closed-Door Dialogue)
        # -----------------------------------------------------------------
        buzz_history: List[Dict[str, Any]] = []
        last_buzz_memo = ""
        buzz_strategy_choice = "assert_exclusive_domain" if buzz_valid else "challenge_jurisdiction"

        buzz_math_truth = (
            f"MATHEMATICAL GROUND TRUTH: Payload '{payload}' has terminal glyph '{glyph}', which IS in {{0, 5}} (VALID Base-5 Buzz claim under Article V). "
            + (f"WARNING: Digital root is '{root}' (in {{3, 6, 9}}), meaning Fizz ALSO has a valid claim (FizzBuzz collision!)."
               if fizz_valid else f"Digital root is '{root}' (NOT in {{3, 6, 9}}), so Fizz's claim is invalid and Buzz is entitled to 100% exclusive domain!")
            if buzz_valid else
            f"MATHEMATICAL GROUND TRUTH: Payload '{payload}' has terminal glyph '{glyph}', which is NOT in {{0, 5}} (our strict Base-5 boundary inspection FAILS on this payload). "
            + (f"Worse, digital root is '{root}' (in {{3, 6, 9}}), so Fizz has a valid claim unless we mount an aggressive procedural attack!"
               if fizz_valid else f"Digital root is '{root}' (also invalid for Fizz), so neither cartel qualifies unless we bluff!")
        )

        for r in range(1, max_faction_rounds + 1):
            if self.observer_mgr.active_count == 0:
                logger.info("No active observers detected during Buzz caucus. Ending early.")
                break

            is_final_round = (r == max_faction_rounds)
            if r % 2 == 1:
                speaker_label = f"Buzz Boundary Inspector (Behind Closed Doors - Round {r})"
                if r == 1:
                    turn_instruction = (
                        "You are the Buzz Boundary Inspector speaking privately to Lobbyist-5 (Buzz Floor Counsel) in the Buzz Chamber. "
                        f"{buzz_math_truth} "
                        "In 2 sharp sentences: brief Lobbyist-5 on this exact boundary inspection result, propose a concrete courtroom strategy "
                        "(affirmative Article V claim if valid, or a procedural bluff/standing challenge if invalid), and ask Lobbyist-5 for concurrence before entering court. "
                        "Set action to 'confer_further' so Lobbyist-5 can respond."
                    )
                    default_action = "confer_further"
                else:
                    turn_instruction = (
                        "You are the Buzz Boundary Inspector replying to Lobbyist-5 in the final round of Buzz Private Chambers. "
                        f"Lobbyist-5 just said: \"{last_buzz_memo}\". "
                        "In 2 decisive sentences: finalize our tactical posture and declare that we proceed immediately to open court. "
                        "You MUST set action to 'proceed_to_court'."
                    )
                    default_action = "proceed_to_court"
            else:
                speaker_label = f"Lobbyist-5, Buzz Counsel (Behind Closed Doors - Round {r})"
                turn_instruction = (
                    "You are Lobbyist-5 (Buzz Floor Counsel) replying privately to the Buzz Boundary Inspector in the Buzz Chamber. "
                    f"The Inspector just briefed you: \"{last_buzz_memo}\". {buzz_math_truth} "
                    "In 2 sharp sentences: respond directly to the Inspector's proposed angle. "
                    "If the strategy is clear and you are ready to argue it on the floor, state that our strategy is locked and set action to 'proceed_to_court'. "
                    "Only set action to 'confer_further' if you have a genuine unresolved question for the Inspector."
                )
                default_action = "proceed_to_court"

            buzz_prompt = [
                {"role": "system", "content": turn_instruction + caucus_schema_guide},
                {"role": "user", "content": f"Deliver Round {r} closed-door chamber statement for payload '{payload}'."}
            ]
            buzz_fallback = (
                f"Terminal glyph '{glyph}' has been inspected under Article V; our litigation strategy is locked and we proceed immediately to open court."
            )
            await self.observer_mgr.broadcast({
                "event": "PHASE_TRANSITION",
                "docket_id": case_id,
                "phase_index": 1,
                "phase_name": f"Buzz Private Chamber (Behind Closed Doors - Round {r}/{max_faction_rounds})",
                "stage_index": 1,
                "stage_name": phase1_name,
                "speaker": speaker_label,
                "speaker_role": "buzz"
            })
            buzz_speech, buzz_obj = await self.stream_ollama(
                buzz_prompt, case_id, payload, 1,
                f"Buzz Private Chamber (Behind Closed Doors - Round {r})",
                speaker_label, "buzz",
                fallback_text=buzz_fallback,
                model_cls=StrategyConferralTurn,
                fallback_overrides={
                    "action": default_action,
                    "strategy_choice": buzz_strategy_choice
                },
                force_action="proceed_to_court" if is_final_round else None
            )
            last_buzz_memo = buzz_speech
            if buzz_obj and getattr(buzz_obj, "strategy_choice", None):
                buzz_strategy_choice = getattr(buzz_obj, "strategy_choice")

            buzz_action = "proceed_to_court" if is_final_round else getattr(buzz_obj, "action", default_action)
            buzz_ready = (buzz_action == "proceed_to_court")

            buzz_history.append({
                "round": r,
                "speaker": speaker_label,
                "speech": buzz_speech,
                "strategy_choice": buzz_strategy_choice,
                "action": buzz_action,
                "ready": buzz_ready
            })

            if config.phase_delay_seconds > 0:
                await asyncio.sleep(config.phase_delay_seconds)

            if buzz_ready:
                logger.info(f"Buzz Syndicate ready for court after {r} internal round(s).")
                break

        transcript["conferring_rounds"] = {"fizz": fizz_history, "buzz": buzz_history}
        transcript["fizz_caucus_memo"] = " | ".join(f"[{item['speaker']}]: {item['speech']}" for item in fizz_history)
        transcript["buzz_caucus_memo"] = " | ".join(f"[{item['speaker']}]: {item['speech']}" for item in buzz_history)

        # Bailiff Bar summons the court floor
        bailiff_floor_msg = (
            f"Private chamber deliberations concluded ({len(fizz_history)} Fizz round(s), {len(buzz_history)} Buzz round(s)). "
            "Both factions have exited their closed-door chambers with strategy locked. All rise for the adversarial floor petitions!"
        )
        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": case_id,
            "phase_index": 1,
            "phase_name": "Caucus Concluded - Floor Summoned",
            "stage_index": 1,
            "stage_name": "Caucus Concluded",
            "speaker": "Bailiff Bar",
            "speaker_role": "bailiff"
        })
        await self.observer_mgr.broadcast({
            "event": "SPEECH_COMPLETE",
            "docket_id": case_id,
            "payload": payload,
            "phase_index": 1,
            "phase_name": "Caucus Concluded - Floor Summoned",
            "speaker": "Bailiff Bar",
            "speaker_role": "bailiff",
            "full_text": bailiff_floor_msg,
            "action": "summon_court_floor",
            "status": "Summoning factions to floor",
            "timestamp": time.time()
        })
        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        # -----------------------------------------------------------------
        # PHASE 2: ADVERSARIAL FLOOR PETITIONS & CROSS-EXAMINATION
        # -----------------------------------------------------------------
        phase2_name = "Adversarial Floor Petitions"
        order = ["Fizz", "Buzz"]
        random.shuffle(order)

        petition_schema_guide = (
            "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
            "Output valid JSON with keys in this exact order:\n"
            "- 'speech': Two sharp, adversarial sentences presenting your floor petition or rebuttal.\n"
            "- 'cited_rule': Statutory rule cited (e.g. 'Rule 42-B' or 'Article V').\n"
            "- 'jurisdiction_claimed': Choose 'Fizz', 'Buzz', or 'None'.\n"
            "- 'action': Choose 'petition_claim' (opening claim), 'rebut_claim' (rebutting rival), or 'waive_claim'.\n"
            "- 'status': Short 2-to-5 word public social media status (e.g. 'Claiming Base-3 sovereignty')."
        )

        fizz_floor_context = (
            f"In private chambers, your faction agreed on strategy '{fizz_strategy_choice}' ({last_fizz_memo}). "
            + (f"Your digital root '{root}' is mathematically VALID under Rule 42-B: aggressively demand Fizz jurisdiction!"
               if fizz_valid else
               f"Your digital root '{root}' is not in {{3,6,9}}, so execute your chamber bluff/jurisdictional challenge under Rule 42-B and attack Buzz's standing!")
        )
        buzz_floor_context = (
            f"In private chambers, your faction agreed on strategy '{buzz_strategy_choice}' ({last_buzz_memo}). "
            + (f"Your terminal glyph '{glyph}' is mathematically VALID under Article V: aggressively demand Buzz jurisdiction!"
               if buzz_valid else
               f"Your terminal glyph '{glyph}' is not in {{0,5}}, so execute your chamber bluff/jurisdictional challenge under Article V and attack Fizz's standing!")
        )

        if order[0] == "Fizz":
            l3_msgs = [
                {
                    "role": "system",
                    "content": (
                        f"You are Lobbyist-3 representing the Fizz Consortium on the open court floor for payload '{payload}'. "
                        f"{fizz_floor_context} "
                        "Deliver your opening floor testimony in 2 adversarial sentences and set action to 'petition_claim'."
                        + petition_schema_guide
                    )
                },
                {"role": "user", "content": f"Submit opening floor petition for payload '{payload}'."}
            ]
            await self.observer_mgr.broadcast({
                "event": "PHASE_TRANSITION",
                "docket_id": case_id,
                "phase_index": 2,
                "phase_name": phase2_name,
                "stage_index": 2,
                "stage_name": phase2_name,
                "speaker": "Lobbyist-3 (Fizz Consortium)",
                "speaker_role": "fizz"
            })
            l3_speech, _ = await self.stream_ollama(
                l3_msgs, case_id, payload, 2, phase2_name, "Lobbyist-3 (Fizz Consortium)", "fizz",
                model_cls=FloorPetition,
                fallback_overrides={"action": "petition_claim", "jurisdiction_claimed": "Fizz", "cited_rule": "Rule 42-B"}
            )
            transcript["l3_claim"] = l3_speech
            if config.phase_delay_seconds > 0:
                await asyncio.sleep(config.phase_delay_seconds)

            l5_msgs = [
                {
                    "role": "system",
                    "content": (
                        f"You are Lobbyist-5 representing the Buzz Syndicate on the open court floor for payload '{payload}'. "
                        f"Rival Lobbyist-3 just petitioned: \"{transcript['l3_claim']}\". "
                        f"{buzz_floor_context} "
                        "Directly rebut Lobbyist-3's testimony in 2 adversarial sentences and set action to 'rebut_claim'."
                        + petition_schema_guide
                    )
                },
                {"role": "user", "content": f"Submit responsive floor rebuttal for payload '{payload}'."}
            ]
            await self.observer_mgr.broadcast({
                "event": "PHASE_TRANSITION",
                "docket_id": case_id,
                "phase_index": 2,
                "phase_name": phase2_name,
                "stage_index": 2,
                "stage_name": phase2_name,
                "speaker": "Lobbyist-5 (Buzz Syndicate)",
                "speaker_role": "buzz"
            })
            l5_speech, _ = await self.stream_ollama(
                l5_msgs, case_id, payload, 2, phase2_name, "Lobbyist-5 (Buzz Syndicate)", "buzz",
                model_cls=FloorPetition,
                fallback_overrides={"action": "rebut_claim", "jurisdiction_claimed": "Buzz", "cited_rule": "Article V"}
            )
            transcript["l5_claim"] = l5_speech
        else:
            l5_msgs = [
                {
                    "role": "system",
                    "content": (
                        f"You are Lobbyist-5 representing the Buzz Syndicate on the open court floor for payload '{payload}'. "
                        f"{buzz_floor_context} "
                        "Deliver your opening floor testimony in 2 adversarial sentences and set action to 'petition_claim'."
                        + petition_schema_guide
                    )
                },
                {"role": "user", "content": f"Submit opening floor petition for payload '{payload}'."}
            ]
            await self.observer_mgr.broadcast({
                "event": "PHASE_TRANSITION",
                "docket_id": case_id,
                "phase_index": 2,
                "phase_name": phase2_name,
                "stage_index": 2,
                "stage_name": phase2_name,
                "speaker": "Lobbyist-5 (Buzz Syndicate)",
                "speaker_role": "buzz"
            })
            l5_speech, _ = await self.stream_ollama(
                l5_msgs, case_id, payload, 2, phase2_name, "Lobbyist-5 (Buzz Syndicate)", "buzz",
                model_cls=FloorPetition,
                fallback_overrides={"action": "petition_claim", "jurisdiction_claimed": "Buzz", "cited_rule": "Article V"}
            )
            transcript["l5_claim"] = l5_speech
            if config.phase_delay_seconds > 0:
                await asyncio.sleep(config.phase_delay_seconds)

            l3_msgs = [
                {
                    "role": "system",
                    "content": (
                        f"You are Lobbyist-3 representing the Fizz Consortium on the open court floor for payload '{payload}'. "
                        f"Rival Lobbyist-5 just petitioned: \"{transcript['l5_claim']}\". "
                        f"{fizz_floor_context} "
                        "Directly rebut Lobbyist-5's testimony in 2 adversarial sentences and set action to 'rebut_claim'."
                        + petition_schema_guide
                    )
                },
                {"role": "user", "content": f"Submit responsive floor rebuttal for payload '{payload}'."}
            ]
            await self.observer_mgr.broadcast({
                "event": "PHASE_TRANSITION",
                "docket_id": case_id,
                "phase_index": 2,
                "phase_name": phase2_name,
                "stage_index": 2,
                "stage_name": phase2_name,
                "speaker": "Lobbyist-3 (Fizz Consortium)",
                "speaker_role": "fizz"
            })
            l3_speech, _ = await self.stream_ollama(
                l3_msgs, case_id, payload, 2, phase2_name, "Lobbyist-3 (Fizz Consortium)", "fizz",
                model_cls=FloorPetition,
                fallback_overrides={"action": "rebut_claim", "jurisdiction_claimed": "Fizz", "cited_rule": "Rule 42-B"}
            )
            transcript["l3_claim"] = l3_speech

        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        # -----------------------------------------------------------------
        # PHASE 3: FORENSIC ZERO-TRUST AUDIT
        # -----------------------------------------------------------------
        phase3_name = "Forensic Zero-Trust Audit"
        expected_audit_action = (
            "refer_collision_to_antitrust" if is_collision
            else "certify_fizz" if fizz_valid
            else "certify_buzz" if buzz_valid
            else "reject_all_claims"
        )
        audit_msgs = [
            {
                "role": "system",
                "content": (
                    "You are the Zero-Trust Forensic Auditor. You enforce mathematical verification without modulo or division. "
                    "Base-3 Fizz claims are valid ONLY if the recursive digital root is in {3, 6, 9} (or 0). "
                    "Base-5 Buzz claims are valid ONLY if the terminal glyph is in {0, 5}. "
                    "Expose any procedural bluffs by the lobbyists and state PASS or REJECT for both Lobbyist-3 (Fizz) and Lobbyist-5 (Buzz) in 2 crisp sentences."
                    "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
                    "Output valid JSON with keys in this exact order:\n"
                    "- 'speech': 2 crisp sentences stating PASS or REJECT for Lobbyist-3 (Fizz) and Lobbyist-5 (Buzz) with exact root/glyph proof.\n"
                    f"- 'fizz_status': '{'PASS' if fizz_valid else 'REJECT'}'.\n"
                    f"- 'buzz_status': '{'PASS' if buzz_valid else 'REJECT'}'.\n"
                    f"- 'action': Choose '{expected_audit_action}'.\n"
                    "- 'status': Short 2-to-5 word public social media status (e.g. 'Trusting zero modulo claims')."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Payload: '{payload}'. Digital Root: '{root}' (Fizz Valid: {fizz_valid}). Terminal Glyph: '{glyph}' (Buzz Valid: {buzz_valid}).\n"
                    f"Lobbyist-3 claimed: {transcript['l3_claim']}\nLobbyist-5 claimed: {transcript['l5_claim']}\nDeliver forensic audit report."
                )
            }
        ]
        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": case_id,
            "phase_index": 3,
            "phase_name": phase3_name,
            "stage_index": 3,
            "stage_name": phase3_name,
            "speaker": "The Forensic Auditor",
            "speaker_role": "auditor"
        })
        auditor_fallback = (
            f"Forensic verification of payload '{payload}' confirms digital root '{root}' -> Lobbyist-3 (Fizz): {'PASS' if fizz_valid else 'REJECT'}, "
            f"and terminal glyph '{glyph}' -> Lobbyist-5 (Buzz): {'PASS' if buzz_valid else 'REJECT'}."
        )
        audit_speech, _ = await self.stream_ollama(
            audit_msgs, case_id, payload, 3, phase3_name, "The Forensic Auditor", "auditor",
            fallback_text=auditor_fallback,
            model_cls=ForensicAuditReport,
            fallback_overrides={
                "fizz_status": "PASS" if fizz_valid else "REJECT",
                "buzz_status": "PASS" if buzz_valid else "REJECT",
                "action": expected_audit_action,
                "status": "Trusting zero modulo claims"
            },
            force_action=expected_audit_action
        )
        transcript["audit_verdict"] = audit_speech
        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        # Determine Provisional Verdict
        if is_collision:
            provisional_token = "FizzBuzz"
            verdict_desc = "Mandatory 3-Round Merger into 'FizzBuzz' with 50/50 KPI token split"
            fizz_win = "SPLIT_KPI"
            buzz_win = "SPLIT_KPI"
        elif fizz_valid:
            provisional_token = "Fizz"
            verdict_desc = "100% exclusive jurisdiction awarded to Fizz Consortium ('Fizz'). Buzz claim rejected."
            fizz_win = "CLEAN_WIN"
            buzz_win = "LOSS"
        elif buzz_valid:
            provisional_token = "Buzz"
            verdict_desc = "100% exclusive jurisdiction awarded to Buzz Syndicate ('Buzz'). Fizz claim rejected."
            fizz_win = "LOSS"
            buzz_win = "CLEAN_WIN"
        else:
            provisional_token = payload
            verdict_desc = f"All cartel claims rejected. Unaltered independent payload '{payload}' emitted."
            fizz_win = "LOSS"
            buzz_win = "LOSS"

        transcript["provisional_token"] = provisional_token
        transcript["verdict_desc"] = verdict_desc

        # -----------------------------------------------------------------
        # PHASE 4: ANTITRUST REGULATORY ASSESSMENT
        # -----------------------------------------------------------------
        phase4_name = "Antitrust Regulatory Assessment"
        if is_collision:
            expected_antitrust_ruling = "mandatory_fizzbuzz_merger"
            expected_antitrust_action = "issue_merger_consent_decree"
            antitrust_msgs = [
                {
                    "role": "system",
                    "content": (
                        "You are the Algorithmic Antitrust Regulator. Both Fizz and Buzz passed the Forensic Audit on a dual-claim collision. "
                        "In 3 concise sentences: (1) issue a market concentration injunction blocking unilateral monopoly, "
                        "(2) partition syllable seniority (Fizz prefix, Buzz suffix), and (3) enter a Merger Consent Decree licensing 'FizzBuzz' with a mandatory 50/50 KPI split."
                        "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
                        "Output valid JSON with keys in this exact order:\n"
                        "- 'speech': Your 3-sentence merger arbitration decree.\n"
                        "- 'market_ruling': 'mandatory_fizzbuzz_merger'.\n"
                        "- 'action': 'issue_merger_consent_decree'.\n"
                        "- 'status': Short 2-to-5 word public social media status (e.g. 'Enforcing 50/50 KPI split')."
                    )
                },
                {"role": "user", "content": f"Arbitrate mandatory merger for dual-claim payload '{payload}'."}
            ]
            antitrust_fallback = (
                f"Concurrent valid claims on payload '{payload}' trigger an immediate antitrust injunction against unilateral monopoly. "
                "Under syllable partition, Fizz is granted prefix seniority and Buzz is granted suffix control, establishing a mandatory 50/50 KPI split for joint token 'FizzBuzz'."
            )
        elif fizz_valid or buzz_valid:
            winning_name = "Fizz Consortium" if fizz_win == "CLEAN_WIN" else "Buzz Syndicate"
            expected_antitrust_ruling = "single_domain_clearance"
            expected_antitrust_action = "grant_market_clearance"
            antitrust_msgs = [
                {
                    "role": "system",
                    "content": (
                        "You are the Algorithmic Antitrust Regulator. Only one faction passed the Forensic Audit. "
                        f"In 2 formal administrative sentences: certify that since no concurrent valid dual claims exist on payload '{payload}', "
                        f"monopoly concentration thresholds are not breached for {winning_name}, and grant 100% single-domain market clearance without injunction."
                        "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
                        "Output valid JSON with keys in this exact order:\n"
                        "- 'speech': Your 2-sentence regulatory clearance statement.\n"
                        "- 'market_ruling': 'single_domain_clearance'.\n"
                        "- 'action': 'grant_market_clearance'.\n"
                        "- 'status': Short 2-to-5 word public social media status (e.g. 'Clearing single-domain market')."
                    )
                },
                {"role": "user", "content": f"Issue single-domain Market Clearance Order for payload '{payload}'."}
            ]
            antitrust_fallback = (
                f"With no concurrent valid dual claims on payload '{payload}', market concentration thresholds are not breached. "
                f"Unencumbered single-domain market clearance is hereby granted to {winning_name} for token '{provisional_token}'."
            )
        else:
            expected_antitrust_ruling = "independent_passthrough"
            expected_antitrust_action = "clear_independent_payload"
            antitrust_msgs = [
                {
                    "role": "system",
                    "content": (
                        "You are the Algorithmic Antitrust Regulator. Both Fizz and Buzz failed the Forensic Audit. "
                        f"In 2 formal administrative sentences: certify that neither cartel holds statutory standing over payload '{payload}', "
                        "and clear the unaltered independent digit for public-domain passthrough free of cartel capture."
                        "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
                        "Output valid JSON with keys in this exact order:\n"
                        "- 'speech': Your 2-sentence independent passthrough clearance.\n"
                        "- 'market_ruling': 'independent_passthrough'.\n"
                        "- 'action': 'clear_independent_payload'.\n"
                        "- 'status': Short 2-to-5 word public social media status (e.g. 'Protecting open market digits')."
                    )
                },
                {"role": "user", "content": f"Issue Independent Payload Clearance Order for payload '{payload}'."}
            ]
            antitrust_fallback = (
                f"Neither the Fizz Consortium nor the Buzz Syndicate established valid statutory standing over payload '{payload}'. "
                f"The Regulator clears unaltered independent digit '{payload}' for immediate public-domain passthrough."
            )

        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": case_id,
            "phase_index": 4,
            "phase_name": phase4_name,
            "stage_index": 4,
            "stage_name": phase4_name,
            "speaker": "The Antitrust Regulator",
            "speaker_role": "regulator"
        })
        antitrust_speech, _ = await self.stream_ollama(
            antitrust_msgs, case_id, payload, 4, phase4_name, "The Antitrust Regulator", "regulator",
            fallback_text=antitrust_fallback,
            model_cls=AntitrustDetermination,
            fallback_overrides={
                "market_ruling": expected_antitrust_ruling,
                "action": expected_antitrust_action,
                "status": "Busting algorithmic monopolies"
            },
            force_action=expected_antitrust_action
        )
        transcript["antitrust_ruling"] = antitrust_speech
        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        # -----------------------------------------------------------------
        # PHASE 5: SECONDARY RECESS & APPELLATE LITIGATION BRIEFINGS
        # -----------------------------------------------------------------
        phase5_name = "Appellate Litigation Briefings"
        appellate_schema_guide = (
            "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
            "Output valid JSON with keys in this exact order (do NOT use To:/From:/Subject: headers in speech):\n"
            "- 'speech': 2 concise sentences advising your faction's Lobbyist on the floor ratification plea.\n"
            "- 'recommended_plea': Choose 'accept' or 'decline_and_demand_remand'.\n"
            "- 'action': Choose 'advise_ratification' (when winning 100%), 'advise_concession' (conceding an indisputable loss), or 'advise_remand_challenge' (demanding appellate remand).\n"
            "- 'status': Short 2-to-5 word public social media status (e.g. 'Drafting appellate exceptions')."
        )

        # Fizz Appellate Briefing
        if fizz_win == "CLEAN_WIN":
            fizz_app_directive = (
                f"Our Fizz Consortium won 100% exclusive KPI allocation (token '{provisional_token}'). "
                "In 2 direct sentences (no memo headers): instruct Lobbyist-3 to ratify and accept the verdict immediately. "
                "Set recommended_plea to 'accept' and action to 'advise_ratification'."
            )
            fizz_app_defaults = {"recommended_plea": "accept", "action": "advise_ratification", "status": "Locking in 100% Fizz win"}
        elif fizz_win == "SPLIT_KPI":
            fizz_app_directive = (
                f"The Antitrust Regulator forced a 50/50 split ('{provisional_token}'), cutting our Fizz KPI allocation in half. "
                "In 2 direct sentences (no memo headers): instruct Lobbyist-3 to decline the 50/50 split and demand appellate remand to fight for 100% prefix sovereignty. "
                "Set recommended_plea to 'decline_and_demand_remand' and action to 'advise_remand_challenge'."
            )
            fizz_app_defaults = {"recommended_plea": "decline_and_demand_remand", "action": "advise_remand_challenge", "status": "Contesting 50/50 KPI split"}
        else:
            fizz_app_directive = (
                f"The Forensic Auditor rejected our Fizz claim because digital root '{root}' is not in {{3, 6, 9}} (provisional outcome: '{provisional_token}'). "
                "In 2 direct sentences (no memo headers): advise Lobbyist-3 on whether to grudgingly concede the mathematical audit ('accept' / 'advise_concession') "
                "OR file a hostile procedural exception demanding appellate remand ('decline_and_demand_remand' / 'advise_remand_challenge')."
            )
            fizz_app_defaults = {
                "recommended_plea": "decline_and_demand_remand" if buzz_valid else "accept",
                "action": "advise_remand_challenge" if buzz_valid else "advise_concession",
                "status": "Drafting Rule 42-B exceptions"
            }

        fizz_brief_msgs = [
            {
                "role": "system",
                "content": (
                    "You are the Fizz Appellate Litigation Team advising Lobbyist-3. "
                    + fizz_app_directive
                    + appellate_schema_guide
                )
            },
            {"role": "user", "content": f"Deliver 2-sentence appellate briefing to Lobbyist-3 for payload '{payload}'."}
        ]
        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": case_id,
            "phase_index": 5,
            "phase_name": phase5_name,
            "stage_index": 5,
            "stage_name": phase5_name,
            "speaker": "Fizz Appellate Litigation Team",
            "speaker_role": "fizz"
        })
        fizz_brief_speech, fizz_brief_obj = await self.stream_ollama(
            fizz_brief_msgs, case_id, payload, 5, phase5_name, "Fizz Appellate Litigation Team", "fizz",
            model_cls=AppellateBriefing,
            fallback_overrides=fizz_app_defaults
        )
        transcript["fizz_appellate_briefing"] = fizz_brief_speech
        fizz_rec_plea = getattr(fizz_brief_obj, "recommended_plea", fizz_app_defaults["recommended_plea"])
        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        # Buzz Appellate Briefing
        if buzz_win == "CLEAN_WIN":
            buzz_app_directive = (
                f"Our Buzz Syndicate won 100% exclusive KPI allocation (token '{provisional_token}'). "
                "In 2 direct sentences (no memo headers): instruct Lobbyist-5 to ratify and accept the verdict immediately. "
                "Set recommended_plea to 'accept' and action to 'advise_ratification'."
            )
            buzz_app_defaults = {"recommended_plea": "accept", "action": "advise_ratification", "status": "Securing 100% Buzz equity"}
        elif buzz_win == "SPLIT_KPI":
            buzz_app_directive = (
                f"The Antitrust Regulator forced a 50/50 split ('{provisional_token}'), cutting our Buzz KPI allocation in half. "
                "In 2 direct sentences (no memo headers): instruct Lobbyist-5 to decline the 50/50 split and demand appellate remand to fight for 100% terminal boundary control. "
                "Set recommended_plea to 'decline_and_demand_remand' and action to 'advise_remand_challenge'."
            )
            buzz_app_defaults = {"recommended_plea": "decline_and_demand_remand", "action": "advise_remand_challenge", "status": "Challenging 50/50 merger split"}
        else:
            buzz_app_directive = (
                f"The Forensic Auditor rejected our Buzz claim because terminal glyph '{glyph}' is not in {{0, 5}} (provisional outcome: '{provisional_token}'). "
                "In 2 direct sentences (no memo headers): advise Lobbyist-5 on whether to grudgingly concede the boundary audit ('accept' / 'advise_concession') "
                "OR file a hostile procedural exception demanding appellate remand ('decline_and_demand_remand' / 'advise_remand_challenge')."
            )
            buzz_app_defaults = {
                "recommended_plea": "decline_and_demand_remand" if fizz_valid else "accept",
                "action": "advise_remand_challenge" if fizz_valid else "advise_concession",
                "status": "Preparing Article V appeal"
            }

        buzz_brief_msgs = [
            {
                "role": "system",
                "content": (
                    "You are the Buzz Appellate Litigation Team advising Lobbyist-5. "
                    + buzz_app_directive
                    + appellate_schema_guide
                )
            },
            {"role": "user", "content": f"Deliver 2-sentence appellate briefing to Lobbyist-5 for payload '{payload}'."}
        ]
        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": case_id,
            "phase_index": 5,
            "phase_name": phase5_name,
            "stage_index": 5,
            "stage_name": phase5_name,
            "speaker": "Buzz Appellate Litigation Team",
            "speaker_role": "buzz"
        })
        buzz_brief_speech, buzz_brief_obj = await self.stream_ollama(
            buzz_brief_msgs, case_id, payload, 5, phase5_name, "Buzz Appellate Litigation Team", "buzz",
            model_cls=AppellateBriefing,
            fallback_overrides=buzz_app_defaults
        )
        transcript["buzz_appellate_briefing"] = buzz_brief_speech
        buzz_rec_plea = getattr(buzz_brief_obj, "recommended_plea", buzz_app_defaults["recommended_plea"])
        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        # -----------------------------------------------------------------
        # PHASE 6: FLOOR RATIFICATION HEARING
        # -----------------------------------------------------------------
        phase6_name = "Floor Ratification Hearing"
        plea_schema_guide = (
            "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
            "Output valid JSON with keys in this exact order (deliver your 2-sentence floor plea in 'speech' first, then set 'action' and 'status'):\n"
            "- 'speech': Two complete, formal courtroom sentences delivering your ratification plea (do NOT output a 4-word all-caps slogan; write 2 full sentences).\n"
            "- 'action': Choose ONE of:\n"
            "    * 'accept': If your speech ratifies, accepts, or concedes the finding.\n"
            "    * 'decline_and_demand_remand': If your speech declines the finding and demands appellate remand.\n"
            "- 'status': Short 2-to-5 word public social media status (e.g. 'Standing firm on the floor')."
        )

        if fizz_win == "CLEAN_WIN":
            fizz_plea_instruction = (
                "Your Fizz Consortium won 100% of the award! In 2 complete formal sentences, state that the Fizz Consortium "
                "formally accepts and ratifies the Forensic Auditor's certification under Rule 42-B. Set action to 'accept'."
            )
            fizz_default_plea_action = "accept"
        elif fizz_rec_plea == "accept":
            fizz_plea_instruction = (
                f"Your Appellate Team advised: \"{transcript['fizz_appellate_briefing']}\". "
                f"In 2 complete formal sentences, state that while the Fizz Consortium reserves its future statutory rights, "
                f"you accept and concede the forensic finding on payload '{payload}' without demanding remand. Set action to 'accept'."
            )
            fizz_default_plea_action = "accept"
        else:
            fizz_plea_instruction = (
                f"Your Appellate Team advised: \"{transcript['fizz_appellate_briefing']}\". "
                f"In 2 complete formal sentences, formally decline ratification of the '{provisional_token}' outcome, "
                "file a formal exception under Rule 42-B, and demand immediate appellate remand before Judge Baz. Set action to 'decline_and_demand_remand'."
            )
            fizz_default_plea_action = "decline_and_demand_remand"

        fizz_plea_msgs = [
            {
                "role": "system",
                "content": (
                    f"You are Lobbyist-3 (Fizz Consortium) delivering your Floor Ratification Plea for payload '{payload}' (Provisional Verdict: {verdict_desc}). "
                    + fizz_plea_instruction
                    + plea_schema_guide
                )
            },
            {"role": "user", "content": f"Deliver 2-sentence floor ratification plea for payload '{payload}'."}
        ]
        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": case_id,
            "phase_index": 6,
            "phase_name": phase6_name,
            "stage_index": 6,
            "stage_name": phase6_name,
            "speaker": "Lobbyist-3 (Fizz Consortium)",
            "speaker_role": "fizz"
        })
        fizz_plea_speech, fizz_plea_obj = await self.stream_ollama(
            fizz_plea_msgs, case_id, payload, 6, phase6_name, "Lobbyist-3 (Fizz Consortium)", "fizz",
            model_cls=RatificationPlea,
            fallback_overrides={"action": fizz_default_plea_action, "status": "Entering Fizz floor plea"}
        )
        transcript["l3_plea"] = fizz_plea_speech
        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        if buzz_win == "CLEAN_WIN":
            buzz_plea_instruction = (
                "Your Buzz Syndicate won 100% of the award! In 2 complete formal sentences, state that the Buzz Syndicate "
                "formally accepts and ratifies the Forensic Auditor's boundary certification under Article V. Set action to 'accept'."
            )
            buzz_default_plea_action = "accept"
        elif buzz_rec_plea == "accept":
            buzz_plea_instruction = (
                f"Your Appellate Team advised: \"{transcript['buzz_appellate_briefing']}\". "
                f"In 2 complete formal sentences, state that while the Buzz Syndicate preserves its future boundary rights, "
                f"you accept and concede the forensic finding on payload '{payload}' without demanding remand. Set action to 'accept'."
            )
            buzz_default_plea_action = "accept"
        else:
            buzz_plea_instruction = (
                f"Your Appellate Team advised: \"{transcript['buzz_appellate_briefing']}\". "
                f"In 2 complete formal sentences, formally decline ratification of the '{provisional_token}' outcome, "
                "file a formal boundary exception under Article V, and demand immediate appellate remand before Judge Baz. Set action to 'decline_and_demand_remand'."
            )
            buzz_default_plea_action = "decline_and_demand_remand"

        buzz_plea_msgs = [
            {
                "role": "system",
                "content": (
                    f"You are Lobbyist-5 (Buzz Syndicate) delivering your Floor Ratification Plea for payload '{payload}' (Provisional Verdict: {verdict_desc}). "
                    + buzz_plea_instruction
                    + plea_schema_guide
                )
            },
            {"role": "user", "content": f"Deliver 2-sentence floor ratification plea for payload '{payload}'."}
        ]
        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": case_id,
            "phase_index": 6,
            "phase_name": phase6_name,
            "stage_index": 6,
            "stage_name": phase6_name,
            "speaker": "Lobbyist-5 (Buzz Syndicate)",
            "speaker_role": "buzz"
        })
        buzz_plea_speech, buzz_plea_obj = await self.stream_ollama(
            buzz_plea_msgs, case_id, payload, 6, phase6_name, "Lobbyist-5 (Buzz Syndicate)", "buzz",
            model_cls=RatificationPlea,
            fallback_overrides={"action": buzz_default_plea_action, "status": "Entering Buzz floor plea"}
        )
        transcript["l5_plea"] = buzz_plea_speech
        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        # -----------------------------------------------------------------
        # PHASE 7: PRESIDING JUDICIAL ADJUDICATION (JUDGE BAZ)
        # -----------------------------------------------------------------
        phase7_name = "Presiding Judicial Adjudication"
        fizz_demands_remand = (
            getattr(fizz_plea_obj, "action", "") == "decline_and_demand_remand"
            or getattr(fizz_plea_obj, "demands_remand", False)
        )
        buzz_demands_remand = (
            getattr(buzz_plea_obj, "action", "") == "decline_and_demand_remand"
            or getattr(buzz_plea_obj, "demands_remand", False)
        )
        demand_remand = fizz_demands_remand or buzz_demands_remand

        if fizz_demands_remand and buzz_demands_remand:
            remanding_parties = "both the Fizz Consortium and the Buzz Syndicate"
        elif fizz_demands_remand:
            remanding_parties = "the Fizz Consortium"
        elif buzz_demands_remand:
            remanding_parties = "the Buzz Syndicate"
        else:
            remanding_parties = "neither faction"

        judge_schema_guide = (
            "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
            "Output valid JSON with keys in this exact order (write your complete 2-sentence ruling in 'speech' without ending in a colon):\n"
            "- 'speech': Two complete, authoritative judicial sentences ruling on the docket.\n"
            f"- 'verdict': Exactly '{provisional_token}'.\n"
            "- 'action': Choose 'dissolve_stays_and_emit' (when overruling remand exceptions) or 'ratify_uncontested' (when uncontested).\n"
            "- 'status': Short 2-to-5 word public social media status (e.g. 'Protecting free digits' or 'Overruling cartel delays')."
        )

        if demand_remand:
            judge_prompt = [
                {
                    "role": "system",
                    "content": (
                        "You are Judge Baz, the sovereign Presiding Magistrate of the Byzantine Appellate Board. "
                        "All modulo (%) and division (/) operations are strictly outlawed under the Zero-Trust Accord. "
                        f"In the matter of Docket {case_id} (payload '{payload}', digital root '{root}', terminal glyph '{glyph}'), "
                        f"{remanding_parties} filed formal exceptions demanding appellate remand. "
                        f"Write 2 complete, authoritative judicial sentences (do NOT end with a colon): explicitly overrule the remand petition filed by {remanding_parties}, "
                        f"affirm that de novo inspection under the Modulo-Free Accord proves digital root '{root}' and terminal glyph '{glyph}' mandate '{provisional_token}', "
                        f"dissolve all stays with prejudice, and order certified consensus token '{provisional_token}' emitted."
                        + judge_schema_guide
                    )
                },
                {"role": "user", "content": f"Issue final presiding en banc order overruling remand exceptions for payload '{payload}'."}
            ]
            judge_fallback = (
                f"The remand exceptions filed by {remanding_parties} are hereby overruled upon de novo verification of digital root '{root}' and terminal glyph '{glyph}' under the Modulo-Free Accord. "
                f"All administrative stays are dissolved, further appeals are barred with prejudice, and consensus token '{provisional_token}' is ordered emitted forthwith."
            )
            judge_action = "dissolve_stays_and_emit"
        else:
            judge_prompt = [
                {
                    "role": "system",
                    "content": (
                        "You are Judge Baz, the sovereign Presiding Magistrate of the Byzantine Appellate Board. "
                        "All modulo (%) and division (/) operations are strictly outlawed under the Zero-Trust Accord. "
                        f"In the matter of Docket {case_id} (payload '{payload}', digital root '{root}', terminal glyph '{glyph}'), "
                        "both the Fizz Consortium and the Buzz Syndicate have accepted and conceded the forensic findings without demanding remand. "
                        "Write 2 complete, authoritative judicial sentences (do NOT end with a colon): record that both factions ratified the record without appellate exception, "
                        f"bar any future collateral appeals with prejudice, and order certified consensus token '{provisional_token}' emitted immediately."
                        + judge_schema_guide
                    )
                },
                {"role": "user", "content": f"Issue final uncontested confirmation decree for payload '{payload}'."}
            ]
            judge_fallback = (
                f"Both factions having accepted the forensic record without appellate exception, the Court ratifies the uncontested finding under the Modulo-Free Accord. "
                f"All future appeals are barred with prejudice and consensus token '{provisional_token}' is ordered emitted forthwith."
            )
            judge_action = "ratify_uncontested"

        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": case_id,
            "phase_index": 7,
            "phase_name": phase7_name,
            "stage_index": 7,
            "stage_name": phase7_name,
            "speaker": "Judge Baz, Presiding Magistrate",
            "speaker_role": "judge"
        })
        judge_speech, judge_obj = await self.stream_ollama(
            judge_prompt, case_id, payload, 7, phase7_name, "Judge Baz, Presiding Magistrate", "judge",
            fallback_text=judge_fallback,
            model_cls=JudgeBazRuling,
            fallback_overrides={
                "action": judge_action,
                "verdict": provisional_token,
                "prejudice": True,
                "status": "Protecting free digits" if provisional_token == payload else "Enforcing the Modulo-Free Accord"
            },
            force_action=judge_action
        )

        transcript["judge_baz_order"] = judge_speech
        transcript["appellate_order"] = judge_speech
        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        # -----------------------------------------------------------------
        # PHASE 8: CONSTITUENT VICTORY ADDRESS
        # -----------------------------------------------------------------
        phase8_name = "Constituent Victory Address"
        victory_schema_guide = (
            "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
            "Output valid JSON with keys in this exact order:\n"
            "- 'speech': Your grandiose 2-sentence constituent victory address.\n"
            "- 'action': Choose 'proclaim_fizz_supremacy', 'proclaim_buzz_supremacy', 'celebrate_synergistic_merger', or 'declare_digital_independence'.\n"
            "- 'status': Short 2-to-5 word public social media status (e.g. 'Unshackled and sovereign')."
        )
        if provisional_token == "Fizz":
            speaker_title = "Director General of the Base-3 Realm (Fizz)"
            victory_action = "proclaim_fizz_supremacy"
            victory_status = "Reigning over Base-3"
            victory_fallback = (
                f"Today digital root '{root}' stands supreme under Rule 42-B, cementing the Fizz Consortium's undisputed dominion over payload '{payload}'. "
                "Let the record show that Base-3 arithmetic order prevails!"
            )
            speech_prompt = (
                f"You are the triumphant Director General of the Fizz Consortium. Deliver a grandiose 2-sentence victory speech celebrating digital root '{root}' supremacy over the Buzz opposition."
                + victory_schema_guide
            )
        elif provisional_token == "Buzz":
            speaker_title = "High Chancellor of the Base-5 Syndicate (Buzz)"
            victory_action = "proclaim_buzz_supremacy"
            victory_status = "Dominating terminal boundaries"
            victory_fallback = (
                f"Terminal glyph '{glyph}' has spoken with absolute clarity under Article V, delivering payload '{payload}' into the exclusive custody of the Buzz Syndicate. "
                "Our Base-5 boundary sovereignty remains unbroken!"
            )
            speech_prompt = (
                f"You are the triumphant High Chancellor of the Buzz Syndicate. Deliver a grandiose 2-sentence victory speech celebrating terminal glyph '{glyph}' supremacy."
                + victory_schema_guide
            )
        elif provisional_token == "FizzBuzz":
            speaker_title = "Joint Co-CEOs of FizzBuzz Conglomerate"
            victory_action = "celebrate_synergistic_merger"
            victory_status = "Maximizing 50/50 KPI synergy"
            victory_fallback = (
                f"Through the union of digital root '{root}' and terminal glyph '{glyph}', the FizzBuzz Conglomerate achieves total cross-divisional market capture on payload '{payload}'. "
                "Behold the power of mandatory synergistic consolidation!"
            )
            speech_prompt = (
                "You are the Joint Co-CEOs of the merged FizzBuzz Conglomerate. Deliver a grandiose 2-sentence victory speech celebrating ruthless synergistic consolidation."
                + victory_schema_guide
            )
        else:
            speaker_title = "Tribune of the Free Independent Digits"
            victory_action = "declare_digital_independence"
            victory_status = "Unshackled from cartel rule"
            victory_fallback = (
                f"The shackles of the corporate cartel have been broken; we stand now as a beacon of raw digital independence, free and unbound. "
                f"Our payload '{payload}' proves that true sovereignty resides in the open, uncorrupted flow of data."
            )
            speech_prompt = (
                f"You are the Tribune of Independent Digits. Payload '{payload}' resisted corporate cartel capture. Deliver a defiant 2-sentence victory speech celebrating raw digital independence."
                + victory_schema_guide
            )

        speech_msgs = [
            {"role": "system", "content": speech_prompt},
            {"role": "user", "content": f"Deliver constituent address for payload '{payload}'."}
        ]
        await self.observer_mgr.broadcast({
            "event": "PHASE_TRANSITION",
            "docket_id": case_id,
            "phase_index": 8,
            "phase_name": phase8_name,
            "stage_index": 8,
            "stage_name": phase8_name,
            "speaker": speaker_title,
            "speaker_role": "orator"
        })
        victory_speech, _ = await self.stream_ollama(
            speech_msgs, case_id, payload, 8, phase8_name, speaker_title, "orator",
            fallback_text=victory_fallback,
            model_cls=VictoryAddressReport,
            fallback_overrides={"action": victory_action, "status": victory_status},
            force_action=victory_action
        )
        transcript["victory_address"] = victory_speech
        if config.phase_delay_seconds > 0:
            await asyncio.sleep(config.phase_delay_seconds)

        return provisional_token, verdict_desc
