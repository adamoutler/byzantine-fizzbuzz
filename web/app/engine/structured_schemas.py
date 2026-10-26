"""
Pydantic schemas for structured LLM outputs in Byzantine FizzBuzz.
Enforces typed JSON output from Ollama with explicit action choices and metadata.
All properties exported to Ollama's JSON Schema are marked 'required' with 'speech' first
and 'action' last, ensuring the LLM reasons through its speech before emitting its decision enum.
"""

from typing import Literal, Dict, Any, ClassVar, Set
from pydantic import BaseModel, Field, model_validator


class StrictStructuredModel(BaseModel):
    """
    Base model for Ollama structured outputs.
    Ensures that all exported schema properties are listed in 'required' in declaration order
    (starting with 'speech' and ending with 'action') so Ollama's GBNF grammar forces the LLM
    to emit every field rather than stopping early after 'speech'.
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
    action: Literal["call_to_order", "swear_in_factions"] = Field(
        default="call_to_order",
        description="Formal action taken by the bailiff"
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


class ForensicAuditReport(StrictStructuredModel):
    """Zero-Trust Forensic Auditor verification report."""
    speech: str = Field(
        description="Two concise bullet points or sentences stating PASS or REJECT for Lobbyist-3 (Fizz) and Lobbyist-5 (Buzz) based strictly on recursive digital root and terminal glyph inspection"
    )
    fizz_status: Literal["PASS", "REJECT"] = Field(
        default="REJECT",
        description="Forensic audit determination for Fizz Consortium base-3 claim"
    )
    buzz_status: Literal["PASS", "REJECT"] = Field(
        default="REJECT",
        description="Forensic audit determination for Buzz Syndicate base-5 claim"
    )
    action: Literal[
        "certify_fizz",
        "certify_buzz",
        "refer_collision_to_antitrust",
        "reject_all_claims"
    ] = Field(
        default="reject_all_claims",
        description="Formal forensic certification action"
    )


class AntitrustDetermination(StrictStructuredModel):
    """Algorithmic Antitrust Regulator market concentration determination."""
    speech: str = Field(
        description="Formal regulatory ruling either arbitrating a 3-round FizzBuzz merger with a 50/50 KPI split or granting market clearance without injunction"
    )
    market_ruling: Literal[
        "single_domain_clearance",
        "mandatory_fizzbuzz_merger",
        "independent_passthrough"
    ] = Field(
        default="independent_passthrough",
        description="Antitrust market structure classification"
    )
    action: Literal[
        "grant_market_clearance",
        "issue_merger_consent_decree",
        "clear_independent_payload"
    ] = Field(
        default="clear_independent_payload",
        description="Formal regulatory action issued by the Antitrust Regulator"
    )


class AppellateBriefing(StrictStructuredModel):
    """Appellate Litigation Team briefing to faction Lobbyist."""
    speech: str = Field(
        description="Two concise sentences (no markdown headers) advising your faction's Lobbyist on whether to ratify the verdict or demand appellate remand"
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

    @model_validator(mode="after")
    def _sync_demands_remand(self) -> "RatificationPlea":
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
