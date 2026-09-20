from datetime import datetime, timedelta

def calculate_next_review_due(
    mastery_score: float,
    review_count: int,
    last_reviewed_at: datetime | None,
) -> datetime | None:
    """
    Calculates the next review date using a deterministic baseline SRS heuristic.
    
    Inputs:
        mastery_score: float between 0.0 and 1.0
        review_count: int, the total number of valid evidence events
        last_reviewed_at: datetime of the last valid evidence
        
    Rules:
        - Minimum interval: 1 day
        - Maximum interval: 30 days
        - Base interval: 1 day
        - Multiplier: 1.0 + (mastery_score * 2.0) (scales from 1.0 to 3.0)
        - Formula: interval_days = base_interval * (multiplier ^ (review_count - 1))
        - Clamped to [1, 30] days.
    """
    if last_reviewed_at is None or review_count <= 0:
        return None
        
    # Clamp mastery score just in case
    mastery_score = max(0.0, min(1.0, mastery_score))
    
    base_interval = 1.0
    multiplier = 1.0 + (mastery_score * 2.0)
    
    # Calculate exponential interval
    interval_days = base_interval * (multiplier ** (review_count - 1))
    
    # Clamp between 1 and 30 days
    interval_days = max(1.0, min(30.0, interval_days))
    
    # We use round to get whole days to keep things simple and predictable
    return last_reviewed_at + timedelta(days=round(interval_days))
