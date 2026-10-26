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
