"""
Integration tests for AsyncByzantineConsensusEngine with structured outputs,
Bailiff Bar, Judge Baz, and dynamic counterpart strategy conferring.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.engine.async_engine import AsyncByzantineConsensusEngine
from app.engine.observer_manager import ActiveObserverManager
from app.database.models import DocketLedger


@pytest.mark.asyncio
async def test_structured_adjudication_flow(tmp_path):
    from app.config import config
    config.phase_delay_seconds = 0.0
    config.token_stream_delay = 0.0
    config.stage_delay_seconds = 0.0

    db_path = str(tmp_path / "test_dockets.db")
    ledger = DocketLedger(db_path)
    await ledger.initialize()

    from starlette.websockets import WebSocketState
    observer_mgr = ActiveObserverManager()
    mock_ws = MagicMock()
    mock_ws.client_state = WebSocketState.CONNECTED
    mock_ws.send_text = AsyncMock()
    observer_mgr.observers[mock_ws] = True

    engine = AsyncByzantineConsensusEngine(ledger, observer_mgr)

    # Mock Ollama stream responses for each phase
    def mock_stream_response(url, json_data):
        messages = json_data.get("messages", [])
        sys_msg = messages[0]["content"] if messages else ""

        if "You are The Court Clerk" in sys_msg and "log_extended_recess_commotion" in sys_msg:
            payload_dict = {
                "speech": (
                    "Meanwhile, in the courtroom, Judge Baz is methodically polishing his solid mahogany gavel with artisanal beeswax. "
                    "At the chancery desk, The Court Clerk is stamping RECEIVED IN TRIPLICATE onto blank manila folders. "
                    "In the back row of the gallery, three K-Street interns are playing rock-paper-scissors over a fifty-pound briefcase."
                ),
                "action": "log_extended_recess_commotion",
                "status": "Logging courtroom commotion"
            }
        elif "You are The Court Clerk" in sys_msg and "log_brief_sidebar_activity" in sys_msg:
            payload_dict = {
                "speech": (
                    "Meanwhile, in the courtroom, Brother Eusebius is frantically dusting a 14th-century vellum scroll with a peacock feather."
                ),
                "action": "log_brief_sidebar_activity",
                "status": "Stamping appellate sidebar notes"
            }
        elif "Bailiff Bar" in sys_msg:
            payload_dict = {
                "speech": "All rise! The Zero-Trust Court is now in session for Payload 3. Judge Baz is presiding.",
                "presiding_judge": "Judge Baz",
                "action": "call_to_order"
            }
        elif "You are the Fizz Quantitative Strategist" in sys_msg:
            payload_dict = {
                "speech": "Digital root 3 satisfies Rule 42-B; I propose asserting 100% exclusive Fizz domain. Do you concur, Lobbyist-3?",
                "strategy_choice": "assert_exclusive_domain",
                "action": "confer_further"
            }
        elif "You are Lobbyist-3 (Fizz Floor Counsel)" in sys_msg:
            payload_dict = {
                "speech": "I concur with the Quantitative Strategist; our Rule 42-B claim is ironclad and our strategy is locked. We proceed immediately to open court.",
                "strategy_choice": "assert_exclusive_domain",
                "action": "proceed_to_court"
            }
        elif "You are the Buzz Boundary Inspector" in sys_msg:
            payload_dict = {
                "speech": "Terminal glyph 3 fails strict Article V inspection; we must mount a procedural standing challenge. Do you concur, Lobbyist-5?",
                "strategy_choice": "challenge_jurisdiction",
                "action": "confer_further"
            }
        elif "You are Lobbyist-5 (Buzz Floor Counsel)" in sys_msg:
            payload_dict = {
                "speech": "Agreed, Inspector; we will challenge Fizz's jurisdiction on the floor. Our strategy is locked and we proceed to court.",
                "strategy_choice": "challenge_jurisdiction",
                "action": "proceed_to_court"
            }
        elif "Zero-Trust Forensic Auditor" in sys_msg:
            payload_dict = {
                "speech": "Forensic inspection confirms digital root '3' -> Lobbyist-3 (Fizz): PASS, and terminal glyph '3' -> Lobbyist-5 (Buzz): REJECT.",
                "fizz_status": "PASS",
                "buzz_status": "REJECT",
                "action": "certify_fizz"
            }
        elif "Algorithmic Antitrust Regulator" in sys_msg:
            payload_dict = {
                "speech": "No concurrent valid dual claims exist on payload '3'. Single-domain market clearance is granted to Fizz Consortium.",
                "market_ruling": "single_domain_clearance",
                "action": "grant_market_clearance"
            }
        elif "Fizz Appellate Litigation Team" in sys_msg:
            payload_dict = {
                "speech": "Our Fizz Consortium won 100% KPI allocation. Lobbyist-3 should ratify and accept the verdict immediately.",
                "recommended_plea": "accept",
                "action": "advise_ratification"
            }
        elif "Buzz Appellate Litigation Team" in sys_msg:
            payload_dict = {
                "speech": "The Forensic Auditor rejected our boundary claim on payload '3'. Lobbyist-5 should file an Article V exception and demand appellate remand.",
                "recommended_plea": "decline_and_demand_remand",
                "action": "advise_remand_challenge"
            }
        elif "Floor Ratification Plea" in sys_msg and "Lobbyist-3" in sys_msg:
            payload_dict = {
                "speech": "The Fizz Consortium formally accepts and ratifies the Forensic Auditor's certification of payload '3' under Rule 42-B.",
                "action": "accept"
            }
        elif "Floor Ratification Plea" in sys_msg and "Lobbyist-5" in sys_msg:
            payload_dict = {
                "speech": "The Buzz Syndicate formally declines ratification of the award and demands immediate appellate remand before Judge Baz.",
                "action": "decline_and_demand_remand"
            }
        elif "Lobbyist-3" in sys_msg or "Lobbyist-5" in sys_msg:
            payload_dict = {
                "speech": "We petition sovereign jurisdiction based on digital root 3 under Rule 42-B.",
                "cited_rule": "Rule 42-B",
                "jurisdiction_claimed": "Fizz",
                "action": "petition_claim"
            }
        elif "Judge Baz" in sys_msg and ("retire" in sys_msg or "chambers" in sys_msg):
            payload_dict = {
                "speech": "Counsel are ordered to retire to their private chambers. Judge Baz presides.",
                "presiding_judge": "Judge Baz",
                "action": "release_to_private_deliberations"
            }
        elif "Judge Baz" in sys_msg:
            payload_dict = {
                "speech": "The remand exceptions filed by the Buzz Syndicate are overruled upon de novo verification under the Modulo-Free Accord. All stays are dissolved and token 'Fizz' is ordered emitted.",
                "verdict": "Fizz",
                "action": "dissolve_stays_and_emit"
            }
        else:
            payload_dict = None

        if payload_dict:
            raw_content = json.dumps(payload_dict)
        else:
            raw_content = "Testimony recorded under the Zero-Trust Accord."

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        async def aiter_lines():
            yield json.dumps({"message": {"content": raw_content}, "done": True})

        mock_response.aiter_lines = aiter_lines
        return mock_response

    class MockStreamContext:
        def __init__(self, resp):
            self.resp = resp
        async def __aenter__(self):
            return self.resp
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    def mock_stream(method, url, json=None):
        resp = mock_stream_response(url, json)
        return MockStreamContext(resp)

    engine.client.stream = mock_stream

    # Execute adjudication for payload 3
    transcript = await engine.adjudicate("3", "Unit Test")

    assert transcript["payload"] == "3"
    assert "Judge Baz" in transcript["bailiff_proclamation"]
    assert "Judge Baz" in transcript["judge_chamber_order"]
    # Verify 2-round counterpart exchange in both chambers (Strategist/Inspector -> Lobbyist)
    assert len(transcript["conferring_rounds"]["fizz"]) == 2
    assert transcript["conferring_rounds"]["fizz"][0]["action"] == "confer_further"
    assert transcript["conferring_rounds"]["fizz"][1]["action"] == "proceed_to_court"
    assert len(transcript["conferring_rounds"]["buzz"]) == 2
    assert transcript["conferring_rounds"]["buzz"][0]["action"] == "confer_further"
    assert transcript["conferring_rounds"]["buzz"][1]["action"] == "proceed_to_court"
    # Verify "Meanwhile, in the courtroom..." interludes & Bailiff Bar calls back to order
    assert "Meanwhile, in the courtroom," in transcript["courtroom_interlude_chambers"]
    assert "called back to order" in transcript["bailiff_floor_summons"]
    assert "Meanwhile, in the courtroom," in transcript["courtroom_interlude_appellate"]
    assert "called back to order" in transcript["bailiff_ratification_summons"]
    assert len(transcript["courtroom_interlude_chambers"]) > len(transcript["courtroom_interlude_appellate"])
    assert transcript["final_token"] == "Fizz"
    assert "Buzz Syndicate" in transcript["judge_baz_order"]

    # Verify event ordering: each "Meanwhile, in the Courtroom" SPEECH_COMPLETE is immediately followed by Bailiff Bar PHASE_TRANSITION
    sent_events = [json.loads(call.args[0]) for call in mock_ws.send_text.call_args_list]
    speech_and_transition = [
        ev for ev in sent_events if ev.get("event") in ("PHASE_TRANSITION", "SPEECH_COMPLETE")
    ]
    interlude_complete_indices = [
        idx for idx, ev in enumerate(speech_and_transition)
        if ev.get("event") == "SPEECH_COMPLETE" and "Meanwhile, in the Courtroom" in ev.get("speaker", "")
    ]
    assert len(interlude_complete_indices) == 2
    for idx in interlude_complete_indices:
        next_ev = speech_and_transition[idx + 1]
        assert next_ev["event"] == "PHASE_TRANSITION"
        assert next_ev["speaker"] == "Bailiff Bar"

    # Verify ledger recorded docket
    total = await ledger.get_total_cases()
    assert total == 1

    last = await ledger.get_last_ruling()
    assert last["payload"] == "3"
    assert last["emitted_token"] == "Fizz"

    await engine.close()


@pytest.mark.asyncio
async def test_mistrial_declaration_on_ollama_failure(tmp_path):
    """
    Verifies that when Ollama communication fails:
    1. Remaining normal tribunal stages are immediately aborted.
    2. Bailiff Bar and Judge Baz officially declare a Mistrial and set a future retrial date
       prior to the next statutory max range increase (#range_end).
    3. 'Mistrial' is recorded as the emitted_token event (instead of Fizz/Buzz/number).
    4. Internal server URLs/IPs are never leaked into the transcript or WebSocket broadcasts.
    """
    import httpx
    from app.config import config
    config.phase_delay_seconds = 0.0
    config.token_stream_delay = 0.0
    config.stage_delay_seconds = 0.0

    db_file = str(tmp_path.joinpath("test_mistrial.db"))
    ledger = DocketLedger(db_file)
    await ledger.initialize()

    from starlette.websockets import WebSocketState
    observer_mgr = ActiveObserverManager()
    mock_ws = MagicMock()
    mock_ws.client_state = WebSocketState.CONNECTED
    mock_ws.send_text = AsyncMock()
    observer_mgr.observers[mock_ws] = True

    engine = AsyncByzantineConsensusEngine(ledger, observer_mgr)

    class FailingStreamContext:
        async def __aenter__(self):
            raise httpx.ConnectError("All connection attempts failed")
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    def failing_stream(method, url, json=None):
        return FailingStreamContext()

    engine.client.stream = failing_stream

    transcript = await engine.adjudicate("15", "Statutory Calendar", range_end=600)

    assert transcript["mistrial"] is True
    assert transcript["final_token"] == "Mistrial"
    assert transcript["retrial_before_max_increase"] == 600
    assert "Bailiff Bar" in transcript["bailiff_mistrial_proclamation"] or "Judge Baz" in transcript["bailiff_mistrial_proclamation"]
    assert "MISTRIAL" in transcript["judge_mistrial_order"]
    assert "#600" in transcript["judge_mistrial_order"]
    assert transcript["retrial_scheduled_for"] in transcript["judge_mistrial_order"]

    # Ensure no internal IP or raw exception string leaked into transcript
    raw_dump = json.dumps(transcript)
    assert "192.168." not in raw_dump
    assert "All connection attempts failed" not in raw_dump

    # Verify database recorded 'Mistrial' as the emitted_token
    last = await ledger.get_last_ruling()
    assert last is not None
    assert last["payload"] == "15"
    assert last["emitted_token"] == "Mistrial"
    assert "OFFICIAL ORDER OF MISTRIAL" in last["verdict"]

    # Verify get_calendar_state treats the Mistrial as pending retrial
    max_cal, missing = await ledger.get_calendar_state(start_seq=15)
    assert max_cal == 15
    assert 15 in missing

    # Verify Foo Universal News (FUN) recap script on Mistrial
    assert "fun_recap" in transcript
    assert "This just in..." in transcript["fun_recap"]
    assert "...In other news..." in transcript["fun_recap"]
    assert transcript["fun_recap"].endswith("You're watching FUN.")

    await engine.close()


@pytest.mark.asyncio
async def test_foo_universal_news_recap_script_and_stream(tmp_path):
    """
    Verifies that Foo Universal News (FUN) generates and streams a recap script with:
    - Newscaster cues ([CUE: ...] / [ANCHOR CUE: ...])
    - Opening 'This just in...'
    - Story 1 covering Judge Baz's ruling and the Victory Speech
    - Transition '...In other news...' + Story 2 (random Onion-style parody headline)
    - Sign-off 'You're watching FUN.'
    """
    from app.config import config
    config.phase_delay_seconds = 0.0
    config.token_stream_delay = 0.0

    db_file = str(tmp_path.joinpath("test_fun.db"))
    ledger = DocketLedger(db_file)
    await ledger.initialize()

    from starlette.websockets import WebSocketState
    observer_mgr = ActiveObserverManager()
    mock_ws = MagicMock()
    mock_ws.client_state = WebSocketState.CONNECTED
    mock_ws.send_text = AsyncMock()
    observer_mgr.observers[mock_ws] = True

    engine = AsyncByzantineConsensusEngine(ledger, observer_mgr)

    sample_transcript = {
        "case_id": "BZ-2026-0015",
        "payload": "15",
        "final_token": "FizzBuzz",
        "judge_baz_order": "De novo verification confirms digital root 6 and glyph 5 mandate joint token 'FizzBuzz'. All appeals are barred with prejudice.",
        "victory_address": "Today the merged FizzBuzz Conglomerate achieves total synergistic market dominance!"
    }

    streamed_script = await engine.stream_fun_recap(sample_transcript)

    assert "CUE:" in streamed_script
    assert "This just in..." in streamed_script
    assert "Judge Baz" in streamed_script
    assert "FizzBuzz" in streamed_script
    assert "synergistic market dominance" in streamed_script
    assert "...In other news..." in streamed_script
    assert sample_transcript["fun_parody_headline"] in streamed_script
    assert streamed_script.endswith("You're watching FUN.")

    await engine.close()
