"""Tests for SM-2 spaced repetition algorithm

Target: 90%+ coverage of srs.py
"""
import pytest
from datetime import date, timedelta
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from srs import calculate_sm2, update_card_after_review, get_review_intervals_preview


class TestCalculateSM2:
    """Test cases for calculate_sm2 function"""

    # Quality validation tests
    def test_quality_below_zero_raises_error(self):
        """Quality rating below 0 should raise ValueError"""
        with pytest.raises(ValueError, match="Quality must be between 0 and 5"):
            calculate_sm2(quality=-1, repetitions=0, ease_factor=2.5, interval=0)

    def test_quality_above_five_raises_error(self):
        """Quality rating above 5 should raise ValueError"""
        with pytest.raises(ValueError, match="Quality must be between 0 and 5"):
            calculate_sm2(quality=6, repetitions=0, ease_factor=2.5, interval=0)

    def test_quality_zero_is_valid(self):
        """Quality rating of 0 (complete blackout) should be valid"""
        reps, interval, ef, next_date = calculate_sm2(
            quality=0, repetitions=3, ease_factor=2.5, interval=10
        )
        assert reps == 0
        assert interval == 1

    def test_quality_five_is_valid(self):
        """Quality rating of 5 (perfect response) should be valid"""
        reps, interval, ef, next_date = calculate_sm2(
            quality=5, repetitions=0, ease_factor=2.5, interval=0
        )
        assert reps == 1
        assert interval == 1

    # Failed review tests (quality < 3)
    def test_failed_review_resets_repetitions(self):
        """Failed review (quality < 3) should reset repetitions to 0"""
        for quality in [0, 1, 2]:
            reps, interval, ef, next_date = calculate_sm2(
                quality=quality, repetitions=5, ease_factor=2.5, interval=30
            )
            assert reps == 0, f"Quality {quality} should reset repetitions"

    def test_failed_review_sets_interval_to_one(self):
        """Failed review should set interval to 1 day"""
        for quality in [0, 1, 2]:
            reps, interval, ef, next_date = calculate_sm2(
                quality=quality, repetitions=5, ease_factor=2.5, interval=30
            )
            assert interval == 1, f"Quality {quality} should set interval to 1"

    def test_failed_review_preserves_ease_factor(self):
        """Failed review should not change ease factor"""
        original_ef = 2.3
        reps, interval, ef, next_date = calculate_sm2(
            quality=2, repetitions=5, ease_factor=original_ef, interval=30
        )
        assert ef == original_ef

    # First successful review tests
    def test_first_successful_review_interval(self):
        """First successful review should have interval of 1 day"""
        reps, interval, ef, next_date = calculate_sm2(
            quality=4, repetitions=0, ease_factor=2.5, interval=0
        )
        assert reps == 1
        assert interval == 1

    # Second successful review tests
    def test_second_successful_review_interval(self):
        """Second successful review should have interval of 6 days"""
        reps, interval, ef, next_date = calculate_sm2(
            quality=4, repetitions=1, ease_factor=2.5, interval=1
        )
        assert reps == 2
        assert interval == 6

    # Subsequent review tests
    def test_third_review_multiplies_by_ease_factor(self):
        """Third+ reviews should multiply interval by ease factor"""
        ease_factor = 2.5
        previous_interval = 6
        reps, interval, ef, next_date = calculate_sm2(
            quality=4,
            repetitions=2,
            ease_factor=ease_factor,
            interval=previous_interval,
        )
        assert reps == 3
        assert interval == round(previous_interval * ease_factor)  # 6 * 2.5 = 15

    def test_fourth_review_continues_multiplication(self):
        """Fourth review continues multiplying by ease factor"""
        ease_factor = 2.5
        previous_interval = 15
        reps, interval, ef, next_date = calculate_sm2(
            quality=4,
            repetitions=3,
            ease_factor=ease_factor,
            interval=previous_interval,
        )
        assert reps == 4
        # Ease factor changes slightly after each review, but interval grows

    # Ease factor adjustment tests
    def test_perfect_quality_increases_ease_factor(self):
        """Perfect quality (5) should increase ease factor"""
        original_ef = 2.5
        reps, interval, ef, next_date = calculate_sm2(
            quality=5, repetitions=2, ease_factor=original_ef, interval=6
        )
        assert ef > original_ef

    def test_low_quality_decreases_ease_factor(self):
        """Low quality (3) should decrease ease factor"""
        original_ef = 2.5
        reps, interval, ef, next_date = calculate_sm2(
            quality=3, repetitions=2, ease_factor=original_ef, interval=6
        )
        assert ef < original_ef

    def test_quality_four_keeps_ease_factor_unchanged(self):
        """Quality 4 should keep ease factor unchanged (formula yields 0 adjustment)"""
        # For quality=4: EF' = EF + (0.1 - 1*(0.08 + 1*0.02)) = EF + 0
        original_ef = 2.5
        reps, interval, ef, next_date = calculate_sm2(
            quality=4, repetitions=2, ease_factor=original_ef, interval=6
        )
        assert ef == original_ef

    # Minimum ease factor tests
    def test_ease_factor_minimum_enforced(self):
        """Ease factor should never go below 1.3"""
        # Start with low ease factor
        reps, interval, ef, next_date = calculate_sm2(
            quality=3, repetitions=2, ease_factor=1.3, interval=6
        )
        assert ef >= 1.3

    def test_ease_factor_corrected_if_below_minimum(self):
        """Input ease factor below 1.3 should be corrected to 1.3"""
        reps, interval, ef, next_date = calculate_sm2(
            quality=5, repetitions=0, ease_factor=1.0, interval=0
        )
        # The ease factor should be at least 1.3 after correction
        assert ef >= 1.3

    # Next review date tests
    def test_next_review_date_calculated_correctly(self):
        """Next review date should be today + interval days"""
        reps, interval, ef, next_date = calculate_sm2(
            quality=4, repetitions=1, ease_factor=2.5, interval=1
        )
        expected_date = date.today() + timedelta(days=interval)
        assert next_date == expected_date

    def test_failed_review_schedules_tomorrow(self):
        """Failed review should schedule for tomorrow"""
        reps, interval, ef, next_date = calculate_sm2(
            quality=1, repetitions=5, ease_factor=2.5, interval=30
        )
        expected_date = date.today() + timedelta(days=1)
        assert next_date == expected_date

    # Edge case tests
    def test_very_high_repetitions(self):
        """Algorithm should handle high repetition counts"""
        reps, interval, ef, next_date = calculate_sm2(
            quality=4, repetitions=100, ease_factor=2.5, interval=365
        )
        assert reps == 101
        assert interval > 365

    def test_exact_ease_factor_formula(self):
        """Test the exact ease factor adjustment formula"""
        # Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        # For quality=5: EF' = EF + (0.1 - 0 * (0.08 + 0)) = EF + 0.1
        original_ef = 2.5
        reps, interval, ef, next_date = calculate_sm2(
            quality=5, repetitions=2, ease_factor=original_ef, interval=6
        )
        expected_ef = original_ef + 0.1
        assert abs(ef - expected_ef) < 0.001

    def test_quality_three_ease_adjustment(self):
        """Test ease factor adjustment for quality=3"""
        # For quality=3: EF' = EF + (0.1 - 2 * (0.08 + 2 * 0.02)) = EF + (0.1 - 2 * 0.12) = EF - 0.14
        original_ef = 2.5
        reps, interval, ef, next_date = calculate_sm2(
            quality=3, repetitions=2, ease_factor=original_ef, interval=6
        )
        expected_ef = original_ef + (0.1 - 2 * (0.08 + 2 * 0.02))
        assert abs(ef - expected_ef) < 0.001


class TestUpdateCardAfterReview:
    """Test cases for update_card_after_review function"""

    def test_updates_card_repetitions(self, app, sample_card):
        """Should update card repetitions after review"""
        from models import Card

        with app.app_context():
            card = Card.query.get(sample_card)
            original_reps = card.repetitions
            update_card_after_review(card, quality_rating=4)
            assert card.repetitions == original_reps + 1

    def test_updates_card_interval(self, app, sample_card):
        """Should update card interval after review"""
        from models import Card

        with app.app_context():
            card = Card.query.get(sample_card)
            update_card_after_review(card, quality_rating=4)
            assert card.interval == 1  # First successful review

    def test_updates_card_ease_factor(self, app, sample_card):
        """Should update card ease factor after review"""
        from models import Card

        with app.app_context():
            card = Card.query.get(sample_card)
            original_ef = card.ease_factor
            update_card_after_review(card, quality_rating=5)
            assert card.ease_factor != original_ef

    def test_updates_next_review_date(self, app, sample_card):
        """Should update card next_review_date after review"""
        from models import Card

        with app.app_context():
            card = Card.query.get(sample_card)
            update_card_after_review(card, quality_rating=4)
            assert card.next_review_date is not None
            assert card.next_review_date == date.today() + timedelta(days=1)

    def test_failed_review_resets_card(self, app, sample_card):
        """Failed review should reset card progress"""
        from models import Card

        with app.app_context():
            card = Card.query.get(sample_card)
            # First do some successful reviews
            update_card_after_review(card, quality_rating=4)
            update_card_after_review(card, quality_rating=4)
            assert card.repetitions == 2

            # Now fail
            update_card_after_review(card, quality_rating=1)
            assert card.repetitions == 0
            assert card.interval == 1


class TestGetReviewIntervalsPreview:
    """Test cases for get_review_intervals_preview function"""

    def test_returns_all_quality_levels(self):
        """Should return preview for all quality levels 0-5"""
        preview = get_review_intervals_preview()
        for i in range(6):
            assert f"quality_{i}" in preview

    def test_returns_ten_intervals_per_quality(self):
        """Should return 10 simulated intervals per quality"""
        preview = get_review_intervals_preview()
        for i in range(6):
            assert len(preview[f"quality_{i}"]["intervals"]) == 10

    def test_returns_final_ease_factor(self):
        """Should return final ease factor for each quality"""
        preview = get_review_intervals_preview()
        for i in range(6):
            assert "final_ease_factor" in preview[f"quality_{i}"]

    def test_failed_quality_stays_at_one(self):
        """Failed quality (0-2) should keep interval at 1"""
        preview = get_review_intervals_preview()
        for quality in [0, 1, 2]:
            intervals = preview[f"quality_{quality}"]["intervals"]
            assert all(i == 1 for i in intervals)

    def test_high_quality_increases_intervals(self):
        """High quality (5) should produce increasing intervals"""
        preview = get_review_intervals_preview()
        intervals = preview["quality_5"]["intervals"]
        # First two are fixed (1, 6), then should generally increase
        assert intervals[0] == 1
        assert intervals[1] == 6
        # Later intervals should be larger
        assert intervals[-1] > intervals[2]

    def test_custom_ease_factor(self):
        """Should accept custom starting ease factor"""
        preview = get_review_intervals_preview(ease_factor=3.0)
        # With higher ease factor, intervals should grow faster
        intervals_high = preview["quality_5"]["intervals"]

        preview_default = get_review_intervals_preview(ease_factor=2.5)
        intervals_default = preview_default["quality_5"]["intervals"]

        # Compare later intervals (not first two which are fixed)
        assert intervals_high[5] >= intervals_default[5]
