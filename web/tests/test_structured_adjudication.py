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

        if "Bailiff Bar" in sys_msg:
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
    assert transcript["final_token"] == "Fizz"
    assert "Buzz Syndicate" in transcript["judge_baz_order"]

    # Verify ledger recorded docket
    total = await ledger.get_total_cases()
    assert total == 1

    last = await ledger.get_last_ruling()
    assert last["payload"] == "3"
    assert last["emitted_token"] == "Fizz"

    await engine.close()
