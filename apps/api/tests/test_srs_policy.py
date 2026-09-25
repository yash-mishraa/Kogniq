from datetime import UTC, datetime, timedelta

from domain.student.srs_policy import calculate_next_review_due


def test_srs_initial_state() -> None:
    # No reviews yet
    assert calculate_next_review_due(0.0, 0, None) is None

def test_srs_first_review() -> None:
    # After first review, the exponent is (1-1) = 0. So multiplier^0 = 1.
    # Base interval is 1 day.
    now = datetime.now(UTC)
    due = calculate_next_review_due(1.0, 1, now)
    assert due is not None
    assert due == now + timedelta(days=1)
    
    due = calculate_next_review_due(0.0, 1, now)
    assert due is not None
    assert due == now + timedelta(days=1)

def test_srs_mastery_0() -> None:
    # mastery=0.0 -> multiplier=1.0. Regardless of review count, interval is 1 day.
    now = datetime.now(UTC)
    for rc in range(1, 10):
        due = calculate_next_review_due(0.0, rc, now)
        assert due is not None
        assert due == now + timedelta(days=1)

def test_srs_mastery_0_5() -> None:
    # mastery=0.5 -> multiplier=2.0.
    # rc=1 -> 1 day
    # rc=2 -> 2 days
    # rc=3 -> 4 days
    # rc=4 -> 8 days
    # rc=5 -> 16 days
    # rc=6 -> 32 -> clamped to 30 days
    now = datetime.now(UTC)
    assert calculate_next_review_due(0.5, 1, now) == now + timedelta(days=1)
    assert calculate_next_review_due(0.5, 2, now) == now + timedelta(days=2)
    assert calculate_next_review_due(0.5, 3, now) == now + timedelta(days=4)
    assert calculate_next_review_due(0.5, 4, now) == now + timedelta(days=8)
    assert calculate_next_review_due(0.5, 5, now) == now + timedelta(days=16)
    assert calculate_next_review_due(0.5, 6, now) == now + timedelta(days=30)

def test_srs_mastery_1_0() -> None:
    # mastery=1.0 -> multiplier=3.0.
    # rc=1 -> 1 day
    # rc=2 -> 3 days
    # rc=3 -> 9 days
    # rc=4 -> 27 days
    # rc=5 -> 81 -> clamped to 30 days
    now = datetime.now(UTC)
    assert calculate_next_review_due(1.0, 1, now) == now + timedelta(days=1)
    assert calculate_next_review_due(1.0, 2, now) == now + timedelta(days=3)
    assert calculate_next_review_due(1.0, 3, now) == now + timedelta(days=9)
    assert calculate_next_review_due(1.0, 4, now) == now + timedelta(days=27)
    assert calculate_next_review_due(1.0, 5, now) == now + timedelta(days=30)

def test_srs_invalid_mastery() -> None:
    # Should clamp
    now = datetime.now(UTC)
    assert calculate_next_review_due(1.5, 4, now) == now + timedelta(days=27) # treats as 1.0
    assert calculate_next_review_due(-0.5, 4, now) == now + timedelta(days=1) # treats as 0.0

def test_srs_timezone_awareness() -> None:
    # Should return the same timezone type as input
    now_naive = datetime.now()
    now_aware = datetime.now(UTC)
    
    due_naive = calculate_next_review_due(1.0, 2, now_naive)
    assert due_naive is not None
    assert due_naive.tzinfo is None
    
    due_aware = calculate_next_review_due(1.0, 2, now_aware)
    assert due_aware is not None
    assert due_aware.tzinfo == UTC
