import pytest
from app.engine.observer_manager import ActiveObserverManager
from app.engine.scheduler import DocketScheduler

@pytest.mark.asyncio
async def test_queue_priority_and_slot_limit():
    mgr = ActiveObserverManager()
    scheduler = DocketScheduler(mgr)

    # 1. Queue is initially empty
    status = scheduler.get_status()
    assert status["queued_docket"] is None
    assert status["is_queue_full"] is False

    # 2. First submission succeeds
    ok, msg, status = await scheduler.submit_to_queue("42", "192.168.1.50")
    assert ok is True
    assert status["is_queue_full"] is True
    assert status["queued_docket"]["payload"] == "42"

    # 3. Second submission fails because queue is 1-deep
    ok2, msg2, status2 = await scheduler.submit_to_queue("99", "192.168.1.51")
    assert ok2 is False
    assert "Queue is currently full" in msg2

    # 4. Selection prioritizes queued docket
    payload, source = await scheduler.select_next_payload()
    assert payload == "42"
    assert "Public Petition" in source

    # 5. After selection, queue is cleared and ready for new inputs
    status3 = scheduler.get_status()
    assert status3["queued_docket"] is None
    assert status3["is_queue_full"] is False

@pytest.mark.asyncio
async def test_sequential_progression_and_expansion():
    mgr = ActiveObserverManager()
    scheduler = DocketScheduler(mgr)
    scheduler.range_start = 1
    scheduler.range_end = 3
    scheduler.expansion_step = 3
    scheduler.current_seq = 1

    # Traverse range 1..3
    p1, _ = await scheduler.select_next_payload()
    assert p1 == "1"
    p2, _ = await scheduler.select_next_payload()
    assert p2 == "2"
    p3, _ = await scheduler.select_next_payload()
    assert p3 == "3"
    assert scheduler.range_end == 6  # Expanded by 3!

    # Next payload is 4
    p4, _ = await scheduler.select_next_payload()
    assert p4 == "4"


@pytest.mark.asyncio
async def test_mistrial_retrial_before_increasing_top_number():
    mgr = ActiveObserverManager()
    scheduler = DocketScheduler(mgr)
    scheduler.range_start = 1
    scheduler.range_end = 10
    scheduler.expansion_step = 10

    # Resume with highest completed = 9 and missing/mistrialed = [4, 7]
    scheduler.resume_from_calendar_seq(9, missing_seqs=[4, 7])
    assert scheduler.range_end == 10
    assert scheduler.pending_mistrials == [4, 7]

    # First, court finishes #10 (the end of the current range 1..10), but does NOT expand range_end yet!
    p_10, _ = await scheduler.select_next_payload()
    assert p_10 == "10"
    assert scheduler.range_end == 10

    # Now at the ceiling of 10: instead of increasing range_end to 20, it retries mistrials [4, 7]!
    p_retry1, src1 = await scheduler.select_next_payload()
    assert p_retry1 == "4"
    assert "Mistrial Retrial" in src1
    assert scheduler.range_end == 10

    # Suppose 4 mistrials again during its retrial! It is placed at the front so it retries next once quorum recovers
    await scheduler.register_mistrial(p_retry1, src1)
    assert scheduler.range_end == 10
    assert scheduler.pending_mistrials[0] == 4

    # Next retries 4 again, then 7, and only increases range_end to 20 after all mistrials succeed!
    p_retry1b, _ = await scheduler.select_next_payload()
    assert p_retry1b == "4"
    assert scheduler.range_end == 10

    p_retry2, _ = await scheduler.select_next_payload()
    assert p_retry2 == "7"
    assert scheduler.range_end == 10

    # Now pending_mistrials is empty -> next payload expands range_end to 20 and selects 11!
    p_11, _ = await scheduler.select_next_payload()
    assert p_11 == "11"
    assert scheduler.range_end == 20
