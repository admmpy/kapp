"""Tests for training enhancement features

Tests:
- Stage 1: N/A (frontend-only, IndexedDB)
- Stage 2: Exercise ordering logic (frontend-only, but we test data shape)
- Stage 3: Grammar pattern mastery tracking (backend routes + models)
"""
import json
import pytest
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from database import db
from models_v2 import GrammarPattern, GrammarMastery, Exercise, ExerciseSRS


# ===========================================
# Stage 2 - Data shape tests (exercise types and audio_url presence)
# ===========================================


class TestExerciseDataShape:
    """Verify exercises have the right fields for speaking-first ordering"""

    def test_lesson_returns_exercise_types(self, client, sample_course):
        """Lesson endpoint should return exercise_type for each exercise"""
        resp = client.get(f"/api/lessons/{sample_course['lesson_id']}")
        assert resp.status_code == 200
        data = resp.get_json()
        exercises = data["lesson"]["exercises"]
        types = [ex["exercise_type"] for ex in exercises]
        assert "vocabulary" in types
        assert "grammar" in types
        assert "listening" in types
        assert "reading" in types

    def test_audio_url_present_on_audio_exercises(self, client, sample_course):
        """Exercises with audio should have audio_url in response"""
        resp = client.get(f"/api/lessons/{sample_course['lesson_id']}")
        data = resp.get_json()
        exercises = data["lesson"]["exercises"]

        audio_exercises = [ex for ex in exercises if "audio_url" in ex]
        assert len(audio_exercises) == 2  # vocabulary + listening
        for ex in audio_exercises:
            assert ex["exercise_type"] in ("vocabulary", "listening")

    def test_non_audio_exercises_no_audio_url(self, client, sample_course):
        """Grammar and reading exercises should not have audio_url"""
        resp = client.get(f"/api/lessons/{sample_course['lesson_id']}")
        data = resp.get_json()
        exercises = data["lesson"]["exercises"]

        for ex in exercises:
            if ex["exercise_type"] in ("grammar", "reading"):
                assert "audio_url" not in ex

    def test_display_order_preserved(self, client, sample_course):
        """Exercises should be returned in display_order"""
        resp = client.get(f"/api/lessons/{sample_course['lesson_id']}")
        data = resp.get_json()
        exercises = data["lesson"]["exercises"]
        orders = [ex["display_order"] for ex in exercises]
        assert orders == sorted(orders)


# ===========================================
# Stage 3 - Grammar mastery tracking
# ===========================================


class TestGrammarMasteryDisabled:
    """When GRAMMAR_MASTERY_ENABLED=false, mastery features should not appear"""

    def test_lesson_has_no_grammar_patterns_when_disabled(self, client, sample_course):
        """Lesson response should not include grammar_patterns when flag is off"""
        resp = client.get(f"/api/lessons/{sample_course['lesson_id']}")
        data = resp.get_json()
        assert "grammar_patterns" not in data["lesson"]

    def test_submit_has_no_pattern_mastery_when_disabled(self, client, sample_course):
        """Submit response should not include pattern_mastery when flag is off"""
        exercise_id = sample_course["exercise_ids"][1]  # grammar exercise
        resp = client.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "안녕히 가세요"},
        )
        data = resp.get_json()
        assert "pattern_mastery" not in data


class TestGrammarPatternInLesson:
    """Test grammar patterns appear in lesson response when enabled"""

    def test_lesson_includes_grammar_patterns(
        self, client_with_mastery, sample_course_with_patterns
    ):
        """Lesson should include grammar_patterns array when mastery is enabled"""
        lesson_id = sample_course_with_patterns["lesson_id"]
        resp = client_with_mastery.get(f"/api/lessons/{lesson_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "grammar_patterns" in data["lesson"]
        patterns = data["lesson"]["grammar_patterns"]
        assert len(patterns) == 2

    def test_grammar_pattern_fields(
        self, client_with_mastery, sample_course_with_patterns
    ):
        """Each grammar pattern should have required fields"""
        lesson_id = sample_course_with_patterns["lesson_id"]
        resp = client_with_mastery.get(f"/api/lessons/{lesson_id}")
        data = resp.get_json()
        pattern = data["lesson"]["grammar_patterns"][0]
        assert "id" in pattern
        assert "title" in pattern
        assert "pattern" in pattern
        assert "meaning" in pattern
        assert "example_korean" in pattern
        assert "example_english" in pattern

    def test_grammar_pattern_no_mastery_initially(
        self, client_with_mastery, sample_course_with_patterns
    ):
        """Patterns should not have mastery data before any practice"""
        lesson_id = sample_course_with_patterns["lesson_id"]
        resp = client_with_mastery.get(f"/api/lessons/{lesson_id}")
        data = resp.get_json()
        for pattern in data["lesson"]["grammar_patterns"]:
            assert "mastery" not in pattern


class TestGrammarMasterySubmit:
    """Test mastery tracking on exercise submission"""

    def test_correct_answer_creates_mastery(
        self, client_with_mastery, sample_course_with_patterns
    ):
        """Submitting correct answer to pattern-linked exercise creates mastery record"""
        exercise_id = sample_course_with_patterns["exercise_ids"][0]
        resp = client_with_mastery.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "안녕하세요"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["correct"] is True
        assert "pattern_mastery" in data
        assert data["pattern_mastery"]["pattern_title"] == "Formal Greeting"
        assert data["pattern_mastery"]["mastery_score"] == 100.0
        assert data["pattern_mastery"]["attempts"] == 1

    def test_incorrect_answer_creates_mastery(
        self, client_with_mastery, sample_course_with_patterns
    ):
        """Submitting wrong answer still creates mastery record with 0% score"""
        exercise_id = sample_course_with_patterns["exercise_ids"][0]
        resp = client_with_mastery.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "안녕"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["correct"] is False
        assert "pattern_mastery" in data
        assert data["pattern_mastery"]["mastery_score"] == 0.0
        assert data["pattern_mastery"]["attempts"] == 1

    def test_mastery_score_updates_across_attempts(
        self, client_with_mastery, sample_course_with_patterns
    ):
        """Mastery score should update as more attempts are made"""
        exercise_id = sample_course_with_patterns["exercise_ids"][0]

        # First attempt: correct
        resp1 = client_with_mastery.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "안녕하세요"},
        )
        data1 = resp1.get_json()
        assert data1["pattern_mastery"]["mastery_score"] == 100.0  # 1/1

        # Second attempt: wrong
        resp2 = client_with_mastery.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "안녕"},
        )
        data2 = resp2.get_json()
        assert data2["pattern_mastery"]["mastery_score"] == 50.0  # 1/2
        assert data2["pattern_mastery"]["attempts"] == 2

        # Third attempt: correct
        resp3 = client_with_mastery.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "안녕하세요"},
        )
        data3 = resp3.get_json()
        # 2/3 = 66.67%
        assert abs(data3["pattern_mastery"]["mastery_score"] - 66.67) < 1
        assert data3["pattern_mastery"]["attempts"] == 3

    def test_no_pattern_mastery_for_unlinked_exercise(
        self, client_with_mastery, sample_course_with_patterns
    ):
        """Exercise without grammar_pattern_id should not return pattern_mastery"""
        exercise_id = sample_course_with_patterns["exercise_ids"][2]  # vocab, no pattern
        resp = client_with_mastery.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "Thank you"},
        )
        data = resp.get_json()
        assert "pattern_mastery" not in data

    def test_mastery_visible_in_lesson_after_practice(
        self, client_with_mastery, sample_course_with_patterns
    ):
        """After submitting, lesson endpoint should show mastery data on the pattern"""
        exercise_id = sample_course_with_patterns["exercise_ids"][0]
        lesson_id = sample_course_with_patterns["lesson_id"]

        # Submit a correct answer
        client_with_mastery.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "안녕하세요"},
        )

        # Check lesson
        resp = client_with_mastery.get(f"/api/lessons/{lesson_id}")
        data = resp.get_json()
        patterns = data["lesson"]["grammar_patterns"]

        # First pattern should have mastery, second should not
        assert "mastery" in patterns[0]
        assert patterns[0]["mastery"]["mastery_score"] == 100.0
        assert patterns[0]["mastery"]["attempts"] == 1
        assert "mastery" not in patterns[1]

    def test_different_patterns_tracked_independently(
        self, client_with_mastery, sample_course_with_patterns
    ):
        """Each pattern should track mastery independently"""
        ex1_id = sample_course_with_patterns["exercise_ids"][0]  # pattern1
        ex2_id = sample_course_with_patterns["exercise_ids"][1]  # pattern2

        # Correct for pattern1
        resp1 = client_with_mastery.post(
            f"/api/exercises/{ex1_id}/submit",
            json={"answer": "안녕하세요"},
        )
        # Wrong for pattern2
        resp2 = client_with_mastery.post(
            f"/api/exercises/{ex2_id}/submit",
            json={"answer": "감사합니다"},
        )

        data1 = resp1.get_json()
        data2 = resp2.get_json()

        assert data1["pattern_mastery"]["mastery_score"] == 100.0
        assert data2["pattern_mastery"]["mastery_score"] == 0.0


class TestGrammarMasteryModels:
    """Test the grammar mastery database models directly"""

    def test_grammar_pattern_creation(self, app_with_mastery):
        """GrammarPattern model should be creatable"""
        with app_with_mastery.app_context():
            course = db.session.query(
                __import__("models_v2", fromlist=["Course"]).Course
            ).first()
            # This test just verifies the model exists and tables were created
            count = db.session.query(GrammarPattern).count()
            assert count >= 0  # Just verify query works

    def test_grammar_mastery_unique_constraint(
        self, app_with_mastery, sample_course_with_patterns
    ):
        """GrammarMastery should enforce unique (user_id, pattern_id)"""
        with app_with_mastery.app_context():
            pattern_id = sample_course_with_patterns["pattern_ids"][0]

            mastery1 = GrammarMastery(
                user_id=1, pattern_id=pattern_id, attempts=1, correct=1, mastery_score=100.0
            )
            db.session.add(mastery1)
            db.session.commit()

            # Trying to add another with same user_id + pattern_id should fail
            mastery2 = GrammarMastery(
                user_id=1, pattern_id=pattern_id, attempts=2, correct=1, mastery_score=50.0
            )
            db.session.add(mastery2)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

    def test_cascade_delete_patterns_with_lesson(
        self, app_with_mastery, sample_course_with_patterns
    ):
        """Deleting a lesson should cascade delete its grammar patterns"""
        with app_with_mastery.app_context():
            from models_v2 import Lesson

            lesson_id = sample_course_with_patterns["lesson_id"]
            lesson = db.session.get(Lesson, lesson_id)

            pattern_count_before = db.session.query(GrammarPattern).count()
            assert pattern_count_before == 2

            db.session.delete(lesson)
            db.session.commit()

            pattern_count_after = db.session.query(GrammarPattern).count()
            assert pattern_count_after == 0


class TestExerciseSubmitBaseline:
    """Test basic exercise submission still works correctly"""

    def test_correct_answer(self, client, sample_course):
        """Correct answer should return correct=true"""
        exercise_id = sample_course["exercise_ids"][0]
        resp = client.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "Hello"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["correct"] is True
        assert data["correct_answer"] == "Hello"

    def test_incorrect_answer(self, client, sample_course):
        """Incorrect answer should return correct=false with correct_answer"""
        exercise_id = sample_course["exercise_ids"][0]
        resp = client.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "Goodbye"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["correct"] is False
        assert data["correct_answer"] == "Hello"

    def test_missing_answer_field(self, client, sample_course):
        """Missing answer should return validation error"""
        exercise_id = sample_course["exercise_ids"][0]
        resp = client.post(
            f"/api/exercises/{exercise_id}/submit",
            json={},
        )
        assert resp.status_code == 400

    def test_nonexistent_exercise(self, client):
        """Submitting to nonexistent exercise should return 404"""
        resp = client.post(
            "/api/exercises/99999/submit",
            json={"answer": "test"},
        )
        assert resp.status_code == 404

    def test_explanation_returned(self, client, sample_course):
        """Explanation should be included in response"""
        exercise_id = sample_course["exercise_ids"][0]
        resp = client.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "Hello"},
        )
        data = resp.get_json()
        assert data["explanation"] == "안녕하세요 means hello"

    def test_case_insensitive_matching(self, client, sample_course):
        """Answer matching should be case-insensitive"""
        exercise_id = sample_course["exercise_ids"][0]
        resp = client.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "hello"},
        )
        data = resp.get_json()
        assert data["correct"] is True


class TestExerciseSubmitSrsQuality:
    """Test optional submit quality signal for sentence SRS."""

    def test_submit_accepts_quality_and_applies_to_srs(self, client, sample_course, app):
        exercise_id = sample_course["exercise_ids"][0]

        resp = client.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "Hello", "quality": 5},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["applied_quality"] == 5

        with app.app_context():
            srs = (
                db.session.query(ExerciseSRS)
                .filter(ExerciseSRS.exercise_id == exercise_id, ExerciseSRS.user_id == 1)
                .first()
            )
            assert srs is not None
            assert srs.times_practiced == 1
            assert srs.times_correct == 1
            assert srs.repetitions == 1
            assert abs(srs.ease_factor - 2.6) < 0.0001

    def test_submit_rejects_invalid_quality(self, client, sample_course):
        exercise_id = sample_course["exercise_ids"][0]

        bad_resp = client.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "Hello", "quality": 8},
        )
        assert bad_resp.status_code == 400

        type_resp = client.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "Hello", "quality": "high"},
        )
        assert type_resp.status_code == 400

    def test_submit_falls_back_to_legacy_quality_when_omitted(self, client, sample_course, app):
        exercise_id = sample_course["exercise_ids"][0]

        resp = client.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "Hello"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["applied_quality"] == 4

        with app.app_context():
            srs = (
                db.session.query(ExerciseSRS)
                .filter(ExerciseSRS.exercise_id == exercise_id, ExerciseSRS.user_id == 1)
                .first()
            )
            assert srs is not None
            assert srs.times_correct == 1
            assert srs.repetitions == 1

    def test_submit_applies_peeked_penalty(self, client, sample_course):
        exercise_id = sample_course["exercise_ids"][0]

        resp = client.post(
            f"/api/exercises/{exercise_id}/submit",
            json={"answer": "Hello", "quality": 5, "peeked": True},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["applied_quality"] == 3


class TestExerciseAttemptCheck:
    """Test attempt-first English checking endpoint."""

    def test_attempt_check_exact_fallback_correct(self, client, sample_course):
        exercise_id = sample_course["exercise_ids"][0]  # vocab, answer: Hello
        resp = client.post(
            f"/api/exercises/{exercise_id}/attempt-check",
            json={"attempt": "hello", "attempt_number": 1, "used_hint": False},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "correct"
        assert data["method"] == "exact_fallback"
        assert data["challenge_state"]["can_retry"] is False
        assert data["challenge_state"]["force_options"] is False

    def test_attempt_check_wrong_first_attempt_has_retry_and_hint(self, client, sample_course):
        exercise_id = sample_course["exercise_ids"][0]
        resp = client.post(
            f"/api/exercises/{exercise_id}/attempt-check",
            json={"attempt": "goodbye", "attempt_number": 1, "used_hint": False},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "wrong"
        assert data["challenge_state"]["can_retry"] is True
        assert data["challenge_state"]["force_options"] is False
        assert data["micro_hint"] is not None

    def test_attempt_check_wrong_second_attempt_forces_options(self, client, sample_course):
        exercise_id = sample_course["exercise_ids"][0]
        resp = client.post(
            f"/api/exercises/{exercise_id}/attempt-check",
            json={"attempt": "goodbye", "attempt_number": 2, "used_hint": True},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "wrong"
        assert data["challenge_state"]["can_retry"] is False
        assert data["challenge_state"]["force_options"] is True

    def test_attempt_check_returns_unscored_without_english_target(self, client, sample_course):
        exercise_id = sample_course["exercise_ids"][2]  # listening correct answer is Korean
        resp = client.post(
            f"/api/exercises/{exercise_id}/attempt-check",
            json={"attempt": "hello", "attempt_number": 1, "used_hint": False},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "unscored"
        assert data["method"] == "unscored"
        assert data["challenge_state"]["can_retry"] is True

    def test_attempt_check_validates_payload(self, client, sample_course):
        exercise_id = sample_course["exercise_ids"][0]
        bad_resp = client.post(
            f"/api/exercises/{exercise_id}/attempt-check",
            json={"attempt": "", "attempt_number": 1, "used_hint": False},
        )
        assert bad_resp.status_code == 400

        bad_attempt_number = client.post(
            f"/api/exercises/{exercise_id}/attempt-check",
            json={"attempt": "hello", "attempt_number": 3, "used_hint": False},
        )
        assert bad_attempt_number.status_code == 400


class TestLessonEndpoint:
    """Test the lesson endpoint returns correct data"""

    def test_get_lesson(self, client, sample_course):
        """Should return lesson with exercises"""
        resp = client.get(f"/api/lessons/{sample_course['lesson_id']}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["lesson"]["title"] == "Test Lesson"
        assert len(data["lesson"]["exercises"]) == 4

    def test_lesson_not_found(self, client):
        """Nonexistent lesson should return 404"""
        resp = client.get("/api/lessons/99999")
        assert resp.status_code == 404

    def test_exercises_dont_include_correct_answer(self, client, sample_course):
        """Exercises in lesson response should NOT include correct_answer (security)"""
        resp = client.get(f"/api/lessons/{sample_course['lesson_id']}")
        data = resp.get_json()
        for ex in data["lesson"]["exercises"]:
            assert "correct_answer" not in ex

    def test_options_parsed_from_json(self, client, sample_course):
        """Options should be parsed from JSON string to array"""
        resp = client.get(f"/api/lessons/{sample_course['lesson_id']}")
        data = resp.get_json()
        vocab_ex = [e for e in data["lesson"]["exercises"] if e["exercise_type"] == "vocabulary"][0]
        assert isinstance(vocab_ex["options"], list)
        assert len(vocab_ex["options"]) == 4
