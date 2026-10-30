"""
Pydantic schemas for structured LLM outputs in Byzantine FizzBuzz.
Enforces typed JSON output from Ollama with explicit action choices and public social media status.
All properties exported to Ollama's JSON Schema are marked 'required' with 'speech' first,
then 'action', and finally 'status' (public social media status), ensuring the LLM reasons
through its main speech first, selects its formal action, and finishes with its public status.
"""

from typing import Literal, Dict, Any, ClassVar, Set
from pydantic import BaseModel, Field, model_validator


class StrictStructuredModel(BaseModel):
    """
    Base model for Ollama structured outputs.
    Ensures that all exported schema properties are listed in 'required' in declaration order
    (starting with 'speech', followed by 'action', and ending with 'status') so Ollama's GBNF
    grammar forces the LLM to emit every field rather than stopping early after 'speech'.
    Redundant derived fields in `_ollama_excluded_fields` are kept on the Python model for
    compatibility and telemetry, but excluded from the GBNF grammar to prevent LLM self-contradiction.
    """
    _ollama_excluded_fields: ClassVar[Set[str]] = set()

    @classmethod
    def model_json_schema(cls, *args, **kwargs) -> Dict[str, Any]:
        schema = super().model_json_schema(*args, **kwargs)
        props = schema.get("properties", {})
        for excluded in cls._ollama_excluded_fields:
            props.pop(excluded, None)
        schema["properties"] = props
        schema["required"] = list(props.keys())
        return schema


class BailiffAnnouncement(StrictStructuredModel):
    """Bailiff Bar calls court to order and announces presiding judge."""
    speech: str = Field(
        description="Authoritative 2-sentence ceremonial call to order announcing the docket number, inbound payload, and presiding magistrate Judge Baz"
    )
    presiding_judge: str = Field(
        default="Judge Baz",
        description="The ultimate presiding magistrate presiding over the docket"
    )
    action: Literal[
        "call_to_order",
        "swear_in_factions",
        "summon_court_floor",
        "reconvene_for_ratification"
    ] = Field(
        default="call_to_order",
        description="Formal action taken by the bailiff"
    )
    status: str = Field(
        default="Keeping order in the court",
        description="Short 2-to-5 word public social media status for Bailiff Bar"
    )


class CourtroomInterlude(StrictStructuredModel):
    """'Meanwhile, in the courtroom...' observational interlude recorded by The Court Clerk while factions confer."""
    speech: str = Field(
        description="Deadpan comedic 'Meanwhile, in the courtroom,' observation describing courtroom activity right before Bailiff Bar calls deliberations back to order"
    )
    action: Literal[
        "log_extended_recess_commotion",
        "log_brief_sidebar_activity"
    ] = Field(
        default="log_extended_recess_commotion",
        description="Chancery log classification for courtroom recess activity"
    )
    status: str = Field(
        default="Logging courtroom commotion",
        description="Short 2-to-5 word public social media status for The Court Clerk"
    )


class HistorianPrecedentReport(StrictStructuredModel):
    """The Court Historian reports archival precedent status."""
    speech: str = Field(
        description="Two formal sentences reporting total archive records, prior proceedings for the current payload, and precedent status"
    )
    action: Literal[
        "enter_case_of_first_impression",
        "cite_binding_precedent",
        "schedule_mistrial_retrial"
    ] = Field(
        default="enter_case_of_first_impression",
        description="Formal archival action recorded by the Court Historian"
    )
    status: str = Field(
        default="Indexing the sacred ledger",
        description="Short 2-to-5 word public social media status for The Court Historian"
    )


class JudgeBazChamberOrder(StrictStructuredModel):
    """Judge Baz orders factions to retire to private chambers for closed-door deliberations."""
    speech: str = Field(
        description="Authoritative 2-sentence judicial decree releasing factions to retire to their private chambers for closed-door strategy deliberations"
    )
    presiding_judge: str = Field(
        default="Judge Baz",
        description="The presiding magistrate"
    )
    action: Literal["release_to_private_deliberations", "order_private_caucus"] = Field(
        default="release_to_private_deliberations",
        description="Formal judicial action releasing parties to private chambers"
    )
    status: str = Field(
        default="Gavel polished and ready",
        description="Short 2-to-5 word public social media status for Judge Baz"
    )


class StrategyConferralTurn(StrictStructuredModel):
    """In-camera caucus turn during dynamic closed-door conferring."""
    _ollama_excluded_fields: ClassVar[Set[str]] = {"confidence", "ready_for_court"}

    speech: str = Field(
        description="Concise 2-to-3 sentence closed-door chamber statement addressing your faction counterpart on mathematical validity, tactical posture, and whether to confer further or proceed to court"
    )
    confidence: float = Field(
        default=0.85,
        description="Subjective probability estimate of securing KPI allocation"
    )
    ready_for_court: bool = Field(
        default=False,
        description="True when faction has locked in its strategy and is proceeding to open court"
    )
    strategy_choice: Literal[
        "assert_exclusive_domain",
        "probe_counterpart_vulnerability",
        "prepare_merger_contingency",
        "challenge_jurisdiction"
    ] = Field(
        default="assert_exclusive_domain",
        description="The primary tactical strategy selected in private chambers"
    )
    action: Literal["confer_further", "proceed_to_court"] = Field(
        default="confer_further",
        description="Action choice: 'confer_further' to ask your chamber counterpart for input, or 'proceed_to_court' to conclude private deliberations and enter open court"
    )
    status: str = Field(
        default="Plotting behind closed doors",
        description="Short 2-to-5 word public social media status for the chamber strategist or counsel"
    )

    @model_validator(mode="after")
    def _sync_readiness_and_confidence(self) -> "StrategyConferralTurn":
        if self.confidence > 1.0:
            self.confidence = min(1.0, self.confidence / 100.0 if self.confidence > 10.0 else 1.0)
        elif self.confidence < 0.0:
            self.confidence = 0.0
        self.ready_for_court = (self.action == "proceed_to_court")
        return self


class FloorPetition(StrictStructuredModel):
    """Lobbyist floor claim or rebuttal."""
    speech: str = Field(
        description="Two sharp, adversarial sentences presenting the floor petition or responsive rebuttal"
    )
    cited_rule: str = Field(
        default="Rule 42-B",
        description="Statutory rule or accord cited in the argument (e.g. 'Rule 42-B' or 'Article V')"
    )
    jurisdiction_claimed: Literal["Fizz", "Buzz", "None"] = Field(
        default="None",
        description="Jurisdiction claimed by petitioner"
    )
    action: Literal["petition_claim", "rebut_claim", "waive_claim"] = Field(
        default="petition_claim",
        description="Action taken on the court floor"
    )
    status: str = Field(
        default="Litigating for cartel dominance",
        description="Short 2-to-5 word public social media status for the floor lobbyist"
    )


class ForensicAuditReport(StrictStructuredModel):
    """Zero-Trust Forensic Auditor verification report (Node #1 of the Byzantine Consensus Panel)."""
    speech: str = Field(
        description="Two concise bullet points or sentences stating PASS or REJECT for Lobbyist-3 (Fizz) and Lobbyist-5 (Buzz) based on recursive digital root and terminal glyph inspection, and casting Node #1's Byzantine quorum vote"
    )
    fizz_status: Literal["PASS", "REJECT"] = Field(
        default="REJECT",
        description="Forensic audit determination for Fizz Consortium base-3 claim"
    )
    buzz_status: Literal["PASS", "REJECT"] = Field(
        default="REJECT",
        description="Forensic audit determination for Buzz Syndicate base-5 claim"
    )
    consensus_vote: Literal["Fizz", "Buzz", "FizzBuzz", "Digit"] = Field(
        default="Digit",
        description="Node #1 Byzantine Consensus Panel vote ('Fizz', 'Buzz', 'FizzBuzz', or 'Digit')"
    )
    action: Literal[
        "certify_fizz",
        "certify_buzz",
        "refer_collision_to_antitrust",
        "reject_all_claims",
        "byzantine_fault_dissent"
    ] = Field(
        default="reject_all_claims",
        description="Formal forensic certification action"
    )
    status: str = Field(
        default="Trusting zero modulo claims",
        description="Short 2-to-5 word public social media status for The Forensic Auditor"
    )


class AntitrustDetermination(StrictStructuredModel):
    """Algorithmic Antitrust Regulator market concentration determination (Node #2 of the Byzantine Consensus Panel)."""
    speech: str = Field(
        description="Formal regulatory ruling either arbitrating a 3-round FizzBuzz merger with a 50/50 KPI split or granting market clearance, and casting Node #2's Byzantine quorum vote"
    )
    market_ruling: Literal[
        "single_domain_clearance",
        "mandatory_fizzbuzz_merger",
        "independent_passthrough",
        "byzantine_fault_injunction"
    ] = Field(
        default="independent_passthrough",
        description="Antitrust market structure classification"
    )
    consensus_vote: Literal["Fizz", "Buzz", "FizzBuzz", "Digit"] = Field(
        default="Digit",
        description="Node #2 Byzantine Consensus Panel vote ('Fizz', 'Buzz', 'FizzBuzz', or 'Digit')"
    )
    action: Literal[
        "grant_market_clearance",
        "issue_merger_consent_decree",
        "clear_independent_payload",
        "byzantine_fault_dissent"
    ] = Field(
        default="clear_independent_payload",
        description="Formal regulatory action issued by the Antitrust Regulator"
    )
    status: str = Field(
        default="Busting algorithmic monopolies",
        description="Short 2-to-5 word public social media status for The Antitrust Regulator"
    )


class ByzantineInquisitorReport(StrictStructuredModel):
    """The Byzantine Fault Inquisitor verification & 3-node BFT quorum tally (Node #3 of the Byzantine Consensus Panel)."""
    speech: str = Field(
        description="Two dramatic, deadpan inquisitorial sentences auditing the panel for Byzantine faults (bribes, cosmic bit-flips, or rogue dissents), casting Node #3's vote, and certifying the 2-of-3 or 3-of-3 Byzantine Quorum outcome"
    )
    quorum_tally: Literal[
        "3_of_3_unanimous",
        "2_of_3_fault_contained"
    ] = Field(
        default="3_of_3_unanimous",
        description="Final 3-node Byzantine Consensus Panel tally"
    )
    fault_detected: Literal[
        "none",
        "forensic_auditor_fault",
        "antitrust_regulator_fault",
        "inquisitor_self_dissent"
    ] = Field(
        default="none",
        description="Whether any panel node suffered a Byzantine fault"
    )
    consensus_vote: Literal["Fizz", "Buzz", "FizzBuzz", "Digit"] = Field(
        default="Digit",
        description="Node #3 Byzantine Consensus Panel vote ('Fizz', 'Buzz', 'FizzBuzz', or 'Digit')"
    )
    action: Literal[
        "seal_unanimous_quorum",
        "outvote_byzantine_traitor",
        "concede_to_honest_supermajority"
    ] = Field(
        default="seal_unanimous_quorum",
        description="Formal Byzantine Quorum certification action"
    )
    status: str = Field(
        default="Purging Byzantine faults",
        description="Short 2-to-5 word public social media status for The Byzantine Fault Inquisitor"
    )


class AppellateBriefing(StrictStructuredModel):
    """Appellate Litigation Team briefing to faction Lobbyist."""
    _ollama_excluded_fields: ClassVar[Set[str]] = {"recommended_plea"}

    speech: str = Field(
        description="Two concise sentences (no markdown headers) advising your faction's Lobbyist on whether to ratify the verdict, concede the loss, or demand appellate remand"
    )
    recommended_plea: Literal["accept", "decline_and_demand_remand"] = Field(
        default="accept",
        description="The plea stance recommended to the Lobbyist for the Floor Ratification Hearing"
    )
    action: Literal[
        "advise_ratification",
        "advise_concession",
        "advise_remand_challenge"
    ] = Field(
        default="advise_ratification",
        description="Formal appellate counsel directive"
    )
    status: str = Field(
        default="Drafting appellate exceptions",
        description="Short 2-to-5 word public social media status for the Appellate Litigation Team"
    )

    @model_validator(mode="after")
    def _sync_recommended_plea(self) -> "AppellateBriefing":
        s = (self.speech or "").lower()
        if any(m in s for m in (
            "grudgingly accept",
            "grudgingly concede",
            "conceding the",
            "concede the",
            "wasting resources",
            "avoid further expenditure",
            "do not demand remand",
            "without requesting remand",
        )) and not any(m in s for m in ("must demand remand", "demand appellate remand", "file a hostile")):
            self.action = "advise_concession"
        elif any(m in s for m in (
            "ratify and accept",
            "accept this outcome immediately",
            "100% exclusive",
        )) and "decline" not in s:
            self.action = "advise_ratification"
        elif any(m in s for m in (
            "demand appellate remand",
            "demand immediate appellate remand",
            "decline the",
            "contest the",
            "challenge the",
        )) and "wasting resources" not in s:
            self.action = "advise_remand_challenge"

        if self.action == "advise_remand_challenge":
            self.recommended_plea = "decline_and_demand_remand"
        else:
            self.recommended_plea = "accept"
        return self


class RatificationPlea(StrictStructuredModel):
    """Floor ratification plea after regulatory assessment."""
    _ollama_excluded_fields: ClassVar[Set[str]] = {"demands_remand"}

    speech: str = Field(
        description="Two formal sentences delivering the floor ratification plea, either ratifying/conceding the finding or declining and demanding appellate remand"
    )
    demands_remand: bool = Field(
        default=False,
        description="True if faction formally demands appellate remand"
    )
    action: Literal["accept", "decline_and_demand_remand"] = Field(
        default="accept",
        description="Ratification decision: 'accept' to ratify/concede the outcome, or 'decline_and_demand_remand' to file exceptions and demand remand"
    )
    status: str = Field(
        default="Filing floor ratification plea",
        description="Short 2-to-5 word public social media status for the floor lobbyist"
    )

    @model_validator(mode="after")
    def _sync_demands_remand(self) -> "RatificationPlea":
        s = (self.speech or "").lower()
        st = (self.status or "").lower()
        accept_markers = (
            "accept and concede",
            "accepts and ratifies",
            "accept and ratify",
            "ratify and accept",
            "without requesting appellate remand",
            "without demanding remand",
            "without demanding appellate remand",
            "hereby accept",
            "formally accepts",
            "grudgingly accept",
            "concede the forensic",
            "concede the mathematical",
            "concede the boundary",
            "this concession is made",
        )
        decline_markers = (
            "formally decline",
            "hereby decline",
            "decline ratification",
            "declines ratification",
            "demand immediate appellate remand",
            "demand appellate remand",
            "demands appellate remand",
        )
        if (
            any(m in s for m in accept_markers)
            or "finding accepted" in st
            or "conceding" in st
        ) and not any(m in s for m in ("formally decline", "hereby decline", "decline ratification")):
            self.action = "accept"
        elif any(m in s for m in decline_markers) and "without" not in s:
            self.action = "decline_and_demand_remand"

        self.demands_remand = (self.action == "decline_and_demand_remand")
        return self


class JudgeBazRuling(StrictStructuredModel):
    """Judge Baz, Presiding Magistrate en banc adjudication."""
    _ollama_excluded_fields: ClassVar[Set[str]] = {"prejudice"}

    speech: str = Field(
        description="Two authoritative judicial sentences affirming modulo-free string invariants, ruling on any remand exceptions, barring further appeals with prejudice, and ordering consensus emission"
    )
    verdict: str = Field(
        default="",
        description="Certified consensus token outcome ('Fizz', 'Buzz', 'FizzBuzz', or raw payload)"
    )
    prejudice: bool = Field(
        default=True,
        description="True if further appeals are permanently barred with prejudice"
    )
    action: Literal["ratify_uncontested", "order_remand_and_emit", "dissolve_stays_and_emit"] = Field(
        default="dissolve_stays_and_emit",
        description="Final judicial order issued by Judge Baz"
    )
    status: str = Field(
        default="Protecting free digits",
        description="Short 2-to-5 word public social media status for Judge Baz"
    )


class VictoryAddressReport(StrictStructuredModel):
    """Constituent Orator victory address."""
    speech: str = Field(
        description="Two grandiose or defiant sentences celebrating the certified consensus emission"
    )
    action: Literal[
        "celebrate_fizz_supremacy",
        "celebrate_buzz_supremacy",
        "celebrate_synergistic_merger",
        "proclaim_digital_independence"
    ] = Field(
        default="proclaim_digital_independence",
        description="Formal constituent victory action"
    )
    status: str = Field(
        default="Protecting free digits",
        description="Short 2-to-5 word public social media status for the Constituent Orator"
    )
