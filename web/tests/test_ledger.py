import pytest
import os
import tempfile
from app.database.models import DocketLedger

@pytest.mark.asyncio
async def test_ledger_total_cases_and_last_ruling():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        ledger = DocketLedger(db_path)
        await ledger.initialize()

        # Initially empty
        assert await ledger.get_total_cases() == 0
        assert await ledger.get_last_ruling() is None

        # Record first docket
        await ledger.record_docket(
            case_id="BZ-2026-0001",
            payload="1",
            digital_root="1",
            terminal_glyph="1",
            fizz_valid=False,
            buzz_valid=False,
            verdict="Unaltered packet '1' emitted.",
            emitted_token="1",
            transcript={"test": "data"}
        )

        assert await ledger.get_total_cases() == 1
        last = await ledger.get_last_ruling()
        assert last is not None
        assert last["case_id"] == "BZ-2026-0001"
        assert last["payload"] == "1"
        assert last["emitted_token"] == "1"

        # Record second docket
        await ledger.record_docket(
            case_id="BZ-2026-0002",
            payload="3",
            digital_root="3",
            terminal_glyph="3",
            fizz_valid=True,
            buzz_valid=False,
            verdict="Exclusive Fizz jurisdiction.",
            emitted_token="Fizz",
            transcript={"test": "data 2"}
        )

        assert await ledger.get_total_cases() == 2
        last2 = await ledger.get_last_ruling()
        assert last2 is not None
        assert last2["case_id"] == "BZ-2026-0002"
        assert last2["payload"] == "3"
        assert last2["emitted_token"] == "Fizz"

        # Verify get_all_dockets in order of inquisition (asc and desc)
        all_asc = await ledger.get_all_dockets(order="asc")
        assert [d["payload"] for d in all_asc] == ["1", "3"]
        all_desc = await ledger.get_all_dockets(order="desc")
        assert [d["payload"] for d in all_desc] == ["3", "1"]

        # Record a queued high number ("420") followed by sequential ("2")
        # to verify order of inquisition (NOT numeric value of payload)
        await ledger.record_docket(
            case_id="BZ-2026-0420",
            payload="420",
            digital_root="6",
            terminal_glyph="0",
            fizz_valid=True,
            buzz_valid=True,
            verdict="Merged FizzBuzz.",
            emitted_token="FizzBuzz",
            transcript={"test": "data 420"}
        )
        await ledger.record_docket(
            case_id="BZ-2026-0004",
            payload="2",
            digital_root="2",
            terminal_glyph="2",
            fizz_valid=False,
            buzz_valid=False,
            verdict="Raw 2.",
            emitted_token="2",
            transcript={"test": "data 2"}
        )

        inq_desc = await ledger.get_all_dockets(order="desc")
        assert [d["payload"] for d in inq_desc] == ["2", "420", "3", "1"]
        inq_asc = await ledger.get_all_dockets(order="asc")
        assert [d["payload"] for d in inq_asc] == ["1", "3", "420", "2"]

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
