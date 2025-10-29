"""SM-2 spaced repetition algorithm

This module implements the SuperMemo 2 (SM-2) algorithm for calculating
optimal review intervals based on user performance.

Algorithm overview:
- Takes quality rating (0-5) as input
- Calculates next review interval in days
- Updates ease factor based on performance
- Returns new scheduling parameters

References:
- https://www.supermemo.com/en/archives1990-2015/english/ol/sm2

Quality Rating Scale:
- 5: Perfect response
- 4: Correct response after hesitation
- 3: Correct response with serious difficulty
- 2: Incorrect response; correct one remembered
- 1: Incorrect response; correct one seemed familiar
- 0: Complete blackout
"""
from datetime import date, timedelta
from typing import Tuple


def calculate_sm2(
    quality: int,
    repetitions: int,
    ease_factor: float,
    interval: int
) -> Tuple[int, int, float, date]:
    """Calculate next review parameters using SM-2 algorithm
    
    Args:
        quality: User's quality rating (0-5)
        repetitions: Number of consecutive successful reviews
        ease_factor: Current ease factor (minimum 1.3)
        interval: Current interval in days
    
    Returns:
        Tuple of (new_repetitions, new_interval, new_ease_factor, next_review_date)
    
    Algorithm:
        1. If quality < 3 (failed): reset repetitions and interval
        2. If quality >= 3 (passed):
           - Increment repetitions
           - Calculate new interval based on repetitions
           - Update ease factor
        3. Ease factor adjusted by: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        4. Minimum ease factor is 1.3
    """
    # Validate input
    if not 0 <= quality <= 5:
        raise ValueError(f"Quality must be between 0 and 5, got {quality}")
    
    if ease_factor < 1.3:
        ease_factor = 1.3
    
    # Quality < 3 means failed review - start over
    if quality < 3:
        new_repetitions = 0
        new_interval = 1  # Review again tomorrow
        new_ease_factor = ease_factor  # Don't change ease factor on failure
    else:
        # Successful review (quality >= 3)
        new_repetitions = repetitions + 1
        
        # Calculate new interval based on repetitions
        if new_repetitions == 1:
            # First successful review: 1 day
            new_interval = 1
        elif new_repetitions == 2:
            # Second successful review: 6 days
            new_interval = 6
        else:
            # Subsequent reviews: multiply previous interval by ease factor
            new_interval = round(interval * ease_factor)
        
        # Update ease factor based on quality
        # Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        ease_adjustment = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        new_ease_factor = ease_factor + ease_adjustment
        
        # Ensure ease factor doesn't go below 1.3
        new_ease_factor = max(1.3, new_ease_factor)
    
    # Calculate next review date
    next_review_date = date.today() + timedelta(days=new_interval)
    
    return new_repetitions, new_interval, new_ease_factor, next_review_date


def update_card_after_review(card, quality_rating: int):
    """Update card's SM-2 parameters after a review
    
    Args:
        card: Card model instance
        quality_rating: User's quality rating (0-5)
    
    This function modifies the card object in place with new scheduling parameters.
    """
    new_reps, new_interval, new_ef, next_date = calculate_sm2(
        quality=quality_rating,
        repetitions=card.repetitions,
        ease_factor=card.ease_factor,
        interval=card.interval
    )
    
    # Update card with new parameters
    card.repetitions = new_reps
    card.interval = new_interval
    card.ease_factor = new_ef
    card.next_review_date = next_date
    
    return card


def get_review_intervals_preview(ease_factor: float = 2.5) -> dict:
    """Get preview of review intervals for different quality ratings
    
    Useful for showing users how the algorithm works.
    
    Args:
        ease_factor: Starting ease factor (default 2.5)
    
    Returns:
        Dictionary with review intervals for each quality rating
    """
    preview = {}
    
    for quality in range(6):
        intervals = []
        reps = 0
        ef = ease_factor
        interval = 0
        
        # Simulate 10 reviews at this quality level
        for _ in range(10):
            reps, interval, ef, _ = calculate_sm2(quality, reps, ef, interval)
            intervals.append(interval)
        
        preview[f"quality_{quality}"] = {
            "intervals": intervals,
            "final_ease_factor": round(ef, 2)
        }
    
    return preview
