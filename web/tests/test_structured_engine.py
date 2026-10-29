"""
Tests for structured output schemas, streaming JSON field extraction, and resilient parsing.
"""

import json
import pytest
from app.engine.streaming_parser import StreamingFieldExtractor, ResilientParser
from app.engine.structured_schemas import (
    BailiffAnnouncement,
    StrategyConferralTurn,
    FloorPetition,
    RatificationPlea,
    JudgeBazRuling
)

def test_streaming_field_extractor_clean():
    extractor = StreamingFieldExtractor(target_field="speech")
    chunks = [
        '{\n  "speech": "All ',
        'rise for ',
        'Judge Baz.',
        ' Docket 42 is open.",\n  "action": "call_to_order"\n}'
    ]
    streamed = []
    for chunk in chunks:
        out = extractor.feed(chunk)
        if out:
            streamed.append(out)

    assert "".join(streamed) == "All rise for Judge Baz. Docket 42 is open."
    assert extractor.get_extracted_speech() == "All rise for Judge Baz. Docket 42 is open."
    
    parsed = ResilientParser.parse(extractor.get_raw_text(), BailiffAnnouncement)
    assert parsed.speech == "All rise for Judge Baz. Docket 42 is open."
    assert parsed.action == "call_to_order"
    assert parsed.presiding_judge == "Judge Baz"

def test_streaming_field_extractor_escapes():
    extractor = StreamingFieldExtractor(target_field="speech")
    chunks = [
        '{"speech": "Hello \\"World\\"\\nLine 2", "action": "call_to_order"}'
    ]
    streamed = [extractor.feed(c) for c in chunks if extractor.feed(c)]
    extracted = extractor.get_extracted_speech()
    assert extracted == 'Hello "World"\nLine 2'

def test_resilient_parser_markdown_wrapper():
    raw = '''```json
    {
        "speech": "Strategic memo for payload 15",
        "action": "proceed_to_court",
        "ready_for_court": true,
        "strategy_choice": "assert_exclusive_domain",
        "confidence": 0.95
    }
    ```'''
    turn = ResilientParser.parse(raw, StrategyConferralTurn)
    assert turn.speech == "Strategic memo for payload 15"
    assert turn.action == "proceed_to_court"
    assert turn.ready_for_court is True
    assert turn.confidence == 0.95

def test_resilient_parser_fallback_unstructured():
    raw = "The Fizz consortium demands exclusive jurisdiction under Rule 42-B."
    turn = ResilientParser.parse(raw, StrategyConferralTurn, default_speech=raw)
    assert turn.speech == raw
    assert turn.action == "confer_further"
    assert turn.ready_for_court is False

def test_resilient_parser_judge_ruling():
    raw = '''{
        "speech": "Byzantine Appellate Board dissolves stays and emits Fizz.",
        "action": "dissolve_stays_and_emit",
        "verdict": "Fizz",
        "prejudice": true
    }'''
    ruling = ResilientParser.parse(raw, JudgeBazRuling)
    assert ruling.speech == "Byzantine Appellate Board dissolves stays and emits Fizz."
    assert ruling.action == "dissolve_stays_and_emit"
    assert ruling.verdict == "Fizz"
    assert ruling.prejudice is True

def test_schema_property_ordering_speech_first_enums_last():
    """Verify that speech (reasoning) is first, action is second-to-last, and status is last in all structured schemas."""
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

    models = [
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
    ]

    for model_cls in models:
        schema = model_cls.model_json_schema()
        keys = list(schema["properties"].keys())
        required_keys = schema.get("required", [])
        assert keys[0] == "speech", f"{model_cls.__name__} must have 'speech' as first property for reasoning prior to decisions."
        assert keys[-2] == "action", f"{model_cls.__name__} must have 'action' immediately before 'status'."
        assert keys[-1] == "status", f"{model_cls.__name__} must have 'status' (public social media status) as the last property."
        assert required_keys == keys, (
            f"{model_cls.__name__} must include ALL properties in 'required' ({keys}) so Ollama's GBNF grammar forces the LLM to emit 'action' and 'status'!"
        )


def test_caucus_readiness_harmonization():
    """Verify that speeches expressing intent to cease deliberation and proceed to court harmonize action."""
    from app.engine.streaming_parser import check_court_readiness

    user_snippets = [
        "The payload '10' mandates immediate execution of the boundary mapping protocols to finalize the encroachment vectors, thereby solidifying our claim under Article V; therefore, we will cease further internal deliberation and immediately prepare the comprehensive legal brief for court, focusing solely on establishing binding precedent to preempt any further Fizz maneuvers.",
        "Payload '10' confirms the necessity of immediate execution of the boundary mapping protocols to finalize encroachment vectors, thereby solidifying our claim under Article V; therefore, we will cease further internal deliberation and immediately finalize the comprehensive legal brief, focusing solely on establishing binding precedent to preempt any further Fizz maneuvers and proceed directly to court.",
        "Payload '10' mandates the immediate cessation of further internal deliberation; we will finalize the comprehensive legal brief by focusing exclusively on establishing binding precedent derived from the finalized boundary mapping to preempt any further Fizz maneuvers. Therefore, the Caucus action is to immediately proceed directly to court with the finalized documentation, as the established encroachment vectors now provide sufficient, undeniable grounds for our claim under Article V.",
        "Payload '10' dictates that we immediately cease further deliberation, solidifying our strategy to present the finalized boundary mapping as undeniable evidence of encroachment vectors under Article V, thereby establishing the necessary binding precedent against any further Fizz maneuvers. We will finalize all documentation immediately, and the Caucus action is to proceed directly to court with this established claim, as the grounds for our assertion are now sufficient and undeniable."
    ]

    for snippet in user_snippets:
        assert check_court_readiness(snippet) is True

        # Test ResilientParser harmonization
        raw_json = f'{{"speech": {json.dumps(snippet)}, "action": "confer_further", "ready_for_court": false}}'
        parsed = ResilientParser.parse(raw_json, StrategyConferralTurn)
        assert parsed.action == "proceed_to_court", f"Failed to harmonize action to proceed_to_court for: {snippet}"
        assert parsed.ready_for_court is True

def test_ratification_plea_harmonization():
    """Verify that speeches expressing intent to decline/remand harmonize action to decline_and_demand_remand."""
    # 1. Unstructured text fallback
    raw_text = "DECLINE AND DEMAND REMAND"
    parsed1 = ResilientParser.parse(raw_text, RatificationPlea, default_speech=raw_text)
    assert parsed1.action == "decline_and_demand_remand"
    assert parsed1.demands_remand is True

    # 2. Conflicted raw JSON (action says accept but speech says DECLINE AND DEMAND REMAND)
    raw_json = '{"speech": "DECLINE AND DEMAND REMAND. We contest the split award.", "action": "accept", "demands_remand": false}'
    parsed2 = ResilientParser.parse(raw_json, RatificationPlea)
    assert parsed2.action == "decline_and_demand_remand"
    assert parsed2.demands_remand is True

    # 3. Clean acceptance
    raw_accept = '{"speech": "ACCEPT the award and praise the board.", "action": "decline_and_demand_remand", "demands_remand": true}'
    parsed3 = ResilientParser.parse(raw_accept, RatificationPlea)
    assert parsed3.action == "accept"
    assert parsed3.demands_remand is False

    # 4. Concession mentioning "without requesting appellate remand" (Docket BZ-2026-0680 regression)
    raw_concede = json.dumps({
        "speech": (
            "While the Fizz Consortium reserves all future statutory rights pertaining to this matter, "
            "we hereby accept and concede the forensic finding regarding payload '680' without requesting appellate remand. "
            "This concession is made solely to avoid further expenditure on a calculation already determined by the underlying mathematical audit."
        ),
        "action": "accept",
        "status": "Finding accepted; moving forward."
    })
    parsed4 = ResilientParser.parse(raw_concede, RatificationPlea)
    assert parsed4.action == "accept"
    assert parsed4.demands_remand is False



