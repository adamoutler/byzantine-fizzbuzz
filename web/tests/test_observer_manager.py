import asyncio
import pytest
from unittest.mock import MagicMock
from app.engine.observer_manager import ActiveObserverManager

@pytest.mark.asyncio
async def test_active_observer_tracking():
    mgr = ActiveObserverManager()
    assert mgr.active_count == 0
    assert mgr.total_count == 0

    ws1 = MagicMock()
    ws2 = MagicMock()

    # Register ws1
    mgr.register(ws1)
    assert mgr.total_count == 1
    assert mgr.active_count == 1

    # Register ws2
    mgr.register(ws2)
    assert mgr.total_count == 2
    assert mgr.active_count == 2

    # ws1 tab is hidden
    mgr.set_visibility(ws1, False)
    assert mgr.total_count == 2
    assert mgr.active_count == 1

    # ws2 tab is hidden -> active count reaches 0
    mgr.set_visibility(ws2, False)
    assert mgr.active_count == 0

    # Unregister ws1
    mgr.unregister(ws1)
    assert mgr.total_count == 1
    assert mgr.active_count == 0

@pytest.mark.asyncio
async def test_standby_gate_wakeup():
    mgr = ActiveObserverManager()
    ws = MagicMock()

    # Create task waiting on active observer
    wait_task = asyncio.create_task(mgr.wait_for_active_observer())
    await asyncio.sleep(0.05)
    assert not wait_task.done()

    # Register observer -> wakes wait_task immediately
    mgr.register(ws)
    await asyncio.sleep(0.05)
    assert wait_task.done()
    assert await wait_task is True
