"""
Shared SM-2 spaced repetition algorithm

Operates on any object with SM-2 fields:
    .repetitions, .review_interval, .ease_factor, .next_review_date
"""
from datetime import datetime, timedelta


def apply_sm2(item, quality: int) -> None:
    """
    Apply SM-2 algorithm to update review scheduling.

    Args:
        item: Any object with .repetitions, .review_interval,
              .ease_factor, .next_review_date attributes
        quality: User's quality rating (0-5)
                 0-2: incorrect, 3-5: correct

    SM-2 Algorithm:
    - If quality < 3: reset repetitions to 0, interval to 1 day
    - If quality >= 3: calculate new interval based on ease factor
    - Ease factor adjusts based on quality (min 1.3)
    """
    if quality < 3:
        item.repetitions = 0
        item.review_interval = 1
        item.next_review_date = datetime.utcnow() + timedelta(days=1)
    else:
        if item.repetitions == 0:
            item.review_interval = 1
        elif item.repetitions == 1:
            item.review_interval = 6
        else:
            item.review_interval = int(item.review_interval * item.ease_factor)

        item.repetitions += 1
        item.next_review_date = datetime.utcnow() + timedelta(days=item.review_interval)

    # Update ease factor (min 1.3)
    item.ease_factor = max(
        1.3,
        item.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
    )
