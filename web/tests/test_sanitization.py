import pytest
from app.config import config
from app.engine.observer_manager import ActiveObserverManager
from app.engine.scheduler import DocketScheduler

@pytest.fixture
def scheduler():
    mgr = ActiveObserverManager()
    return DocketScheduler(mgr)

def test_sanitize_valid_inputs(scheduler):
    ok, val, err = scheduler.sanitize_input("15")
    assert ok is True
    assert val == "15"
    assert err == ""

    ok, val, err = scheduler.sanitize_input("  100  ")
    assert ok is True
    assert val == "100"

def test_sanitize_leading_zeros(scheduler):
    ok, val, err = scheduler.sanitize_input("007")
    assert ok is True
    assert val == "7"

    # "000" normalizes to "0", but fails because min_allowed_docket is 1
    ok, val, err = scheduler.sanitize_input("000")
    assert ok is False
    assert "Payload must be at least" in err

def test_sanitize_bounds_enforcement(scheduler):
    # Below min_allowed (default 1)
    ok, val, err = scheduler.sanitize_input("0")
    assert ok is False
    assert f"Payload must be at least {config.min_allowed_docket}" in err

    # Above max_allowed (default 10000)
    ok, val, err = scheduler.sanitize_input("999999")
    assert ok is False
    assert f"Payload cannot exceed {config.max_allowed_docket}" in err

def test_sanitize_rejection_of_non_digits(scheduler):
    # Letters
    ok, _, err = scheduler.sanitize_input("15a")
    assert ok is False
    assert "strictly decimal digits" in err

    # Hex
    ok, _, err = scheduler.sanitize_input("0x1F")
    assert ok is False

    # Binary
    ok, _, err = scheduler.sanitize_input("0b101")
    assert ok is False

    # Float / decimals
    ok, _, err = scheduler.sanitize_input("3.14")
    assert ok is False

    # Negative numbers
    ok, _, err = scheduler.sanitize_input("-15")
    assert ok is False

    # Symbols
    ok, _, err = scheduler.sanitize_input("1,000")
    assert ok is False

    # Excessively long string (DoS cap > 100 chars)
    ok, _, err = scheduler.sanitize_input("9" * 101)
    assert ok is False
    assert "100-digit statutory cap" in err
