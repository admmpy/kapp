"""
Lesson routes for lesson content and exercises

Endpoints:
- GET /api/lessons/:id - Get lesson with exercises
- POST /api/lessons/:id/start - Mark lesson started
- POST /api/lessons/:id/complete - Mark lesson completed
- POST /api/exercises/:id/submit - Submit exercise answer
"""
import json
import re
from datetime import datetime
from typing import Optional
from flask import Blueprint, request, jsonify, current_app
from database import db
from models_v2 import Lesson, Exercise, UserProgress, GrammarMastery, ExerciseSRS
from llm_service import OpenAIClient
from security import sanitize_user_input
from utils import not_found_response, error_response, validation_error_response
from routes.helpers import get_user_progress, get_or_create_user_progress, get_current_user_id
import logging

logger = logging.getLogger(__name__)

lessons_bp = Blueprint("lessons", __name__)
_attempt_llm_client = None
ENGLISH_PHRASE_MAP = {
    "감사합니다": "Thank you.",
    "감사합니다. 잘 들었어요.": "Thank you. I heard well.",
    "내일 날씨가 좋을까요?": "Will the weather be good tomorrow?",
    "네, 감사합니다.": "Yes, thank you.",
    "네, 알겠습니다. 잠깐만 기다려 주세요.": "Yes, understood. Please wait a moment.",
    "물 있어요?": "Do you have water?",
    "물 한 잔 주세요.": "Please give me a glass of water.",
    "미안합니다": "I'm sorry.",
    "미안해요. 뭐라고요?": "Sorry. What did you say?",
    "사과 네 개 주세요.": "Please give me four apples.",
    "사과 다섯 개 주세요.": "Please give me five apples.",
    "사과 두 개 주세요.": "Please give me two apples.",
    "사과 세 개 주세요.": "Please give me three apples.",
    "식당이 어디에 있어요?": "Where is the restaurant?",
    "실례합니다. 지나갈게요.": "Excuse me. Let me pass.",
    "아니요, 괜찮습니다.": "No, it's okay.",
    "아니요, 모르겠어요.": "No, I don't know.",
    "안녕하세요": "Hello.",
    "안녕하세요. 만나서 반갑습니다.": "Hello. Nice to meet you.",
    "안녕하세요. 죄송합니다.": "Hello. I'm sorry.",
    "안녕히 가세요": "Goodbye (to someone leaving).",
    "안녕히 가세요. 감사합니다.": "Goodbye. Thank you.",
    "안녕히 계세요. 고마워요.": "Goodbye (when leaving). Thanks.",
    "어제 날씨가 나빴어요.": "The weather was bad yesterday.",
    "여기서 기다리세요. 가지 마세요.": "Wait here. Don't go.",
    "오늘 날씨가 좋아요.": "The weather is good today.",
    "오늘 뭐 해요?": "What are you doing today?",
    "오늘은 사월 이십일입니다.": "Today is April 21st.",
    "오늘은 삼월 십오일입니다.": "Today is March 15th.",
    "오늘은 오월 십일입니다.": "Today is May 11th.",
    "오늘은 일월 오일입니다.": "Today is January 5th.",
    "이것은 만 원입니다.": "This is ten thousand won.",
    "이것은 삼천 원입니다.": "This is three thousand won.",
    "이것은 오천 원입니다.": "This is five thousand won.",
    "이것은 천 원입니다.": "This is one thousand won.",
    "잠깐만 기다려 주세요. 금방 돌아올게요.": "Please wait a moment. I'll be right back.",
    "저기요, 도와주세요.": "Excuse me, please help.",
    "저는 김민수입니다. 학생이 아니에요.": "I am Kim Min-su. I am not a student.",
    "저는 미국에서 왔습니다.": "I came from the United States.",
    "저는 서른 살입니다.": "I am thirty years old.",
    "저는 스무 살입니다.": "I am twenty years old.",
    "저는 스물다섯 살입니다.": "I am twenty-five years old.",
    "저는 열아홉 살입니다.": "I am nineteen years old.",
    "저는 일본에서 왔습니다.": "I came from Japan.",
    "저는 중국에서 왔어요.": "I came from China.",
    "저는 한국에서 왔어요.": "I came from Korea.",
    "제 이름은 김민수입니다. 대학생이에요.": "My name is Kim Min-su. I am a college student.",
    "제 이름은 김민수입니다. 선생님이에요.": "My name is Kim Min-su. I am a teacher.",
    "제 이름은 박지현입니다. 회사원이에요.": "My name is Park Ji-hyeon. I am an office worker.",
    "죄송합니다. 다시 말해 주세요.": "I'm sorry. Please say it again.",
    "죄송합니다. 잘 못 들었어요.": "I'm sorry. I didn't hear well.",
    "주스 두 잔 주세요.": "Please give me two glasses of juice.",
    "지하철역이 어디에 있어요?": "Where is the subway station?",
    "출구가 어디에 있어요?": "Where is the exit?",
    "커피 주세요.": "Coffee, please.",
    "한국어를 가르쳐요.": "I teach Korean.",
    "한국어를 공부해요.": "I study Korean.",
    "한국어를 배우고 싶어요.": "I want to learn Korean.",
    "한국어를 잘 해요.": "I speak Korean well.",
    "화장실이 어디에 있어요?": "Where is the bathroom?",
}


def validate_sentence_arrange(user_answer, correct_answer: str) -> bool:
    """Compare arrays of tile IDs for sentence_arrange exercises"""
    try:
        user_ids = json.loads(user_answer) if isinstance(user_answer, str) else user_answer
        correct_ids = json.loads(correct_answer) if isinstance(correct_answer, str) else correct_answer
        return user_ids == correct_ids
    except (json.JSONDecodeError, TypeError):
        return False


def validate_writing_answer(user_answer: str, correct_answer: str) -> bool:
    """
    Validate writing exercises with flexible matching
    Accepts minor variations in spacing, punctuation, and Korean romanization
    """
    if not user_answer or not correct_answer:
        return False

    # Normalize both answers
    user_normalized = user_answer.strip().lower()
    correct_normalized = correct_answer.strip().lower()

    # Exact match
    if user_normalized == correct_normalized:
        return True

    # Remove common punctuation and extra spaces for flexible matching
    import re
    user_clean = re.sub(r'[.,!?;:\s]+', ' ', user_normalized).strip()
    correct_clean = re.sub(r'[.,!?;:\s]+', ' ', correct_normalized).strip()

    return user_clean == correct_clean


def normalize_english_text(value: str) -> str:
    """Normalize English text for deterministic fallback comparisons."""
    normalized = re.sub(r"[.,!?;:\s]+", " ", value.strip().lower())
    return normalized.strip()


def looks_like_english(value: str) -> bool:
    """Heuristic check: mostly Latin text and contains at least one English letter."""
    if not value:
        return False
    if re.search(r"[가-힣]", value):
        return False
    return bool(re.search(r"[a-zA-Z]", value))


def extract_english_target(exercise: Exercise) -> Optional[str]:
    """
    Best-effort English target used by exact fallback.
    Priority:
    1) exercise.english_text
    2) correct_answer if it looks English
    """
    if exercise.english_text and exercise.english_text.strip():
        return exercise.english_text.strip()

    if exercise.correct_answer and looks_like_english(exercise.correct_answer):
        return exercise.correct_answer.strip()

    mapped = ENGLISH_PHRASE_MAP.get((exercise.correct_answer or "").strip())
    if mapped:
        return mapped

    return None


def build_micro_hint(target: Optional[str]) -> str:
    """Generate a constrained clue without revealing the full answer."""
    if not target:
        return "Focus on the core meaning in plain English, then retry."

    words = [w for w in re.split(r"\s+", target.strip()) if w]
    if not words:
        return "Focus on the core meaning in plain English, then retry."

    hinted = []
    for word in words[:2]:
        letters = re.sub(r"[^a-zA-Z0-9]", "", word)
        if letters:
            hinted.append(f"{letters[0].lower()}... ({len(letters)} letters)")

    if hinted:
        return f"Micro-hint: start with {', '.join(hinted)}."

    return "Micro-hint: think of a short everyday English phrase."


def parse_llm_attempt_status(raw: str) -> Optional[str]:
    """Parse model output and return correct/wrong status when possible."""
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        parsed = json.loads(text)
        status = str(parsed.get("status", "")).lower().strip()
        if status in {"correct", "wrong"}:
            return status
    except Exception:
        pass

    lowered = text.lower()
    if '"status":"correct"' in lowered or '"status": "correct"' in lowered:
        return "correct"
    if '"status":"wrong"' in lowered or '"status": "wrong"' in lowered:
        return "wrong"
    return None


def get_attempt_llm_client() -> Optional[OpenAIClient]:
    """Get or create LLM client for attempt semantic checks."""
    global _attempt_llm_client

    if not current_app.config.get("LLM_ENABLED", False):
        return None

    api_key = current_app.config.get("OPENAI_API_KEY")
    if not api_key:
        return None

    if _attempt_llm_client is None:
        _attempt_llm_client = OpenAIClient(
            api_key=api_key,
            model=current_app.config.get("OPENAI_MODEL", "gpt-4o-mini"),
            timeout=6,
            cache_dir=current_app.config.get("LLM_CACHE_DIR", "data/llm_cache"),
        )

    return _attempt_llm_client


def judge_attempt_with_llm(attempt: str, target: str) -> Optional[str]:
    """Semantic English correctness check using LLM, returns correct/wrong or None on failure."""
    client = get_attempt_llm_client()
    if client is None:
        return None

    system_prompt = (
        "You are a strict grader. Compare learner English attempt to target meaning. "
        "Return JSON only: {\"status\":\"correct\"} or {\"status\":\"wrong\"}. "
        "Mark correct only when meaning is clearly equivalent."
    )
    user_prompt = (
        f"Target meaning: {target}\n"
        f"Learner attempt: {attempt}\n"
        "Return JSON only."
    )

    try:
        response = client.chat(
            prompt=user_prompt,
            system=system_prompt,
            temperature=0.0,
            max_tokens=40,
            use_cache=False,
        )
        return parse_llm_attempt_status(response)
    except Exception as err:
        logger.warning(f"Attempt LLM check failed, using fallback: {err}")
        return None


def translate_text_with_llm(text: str) -> Optional[str]:
    """Translate Korean phrase to concise natural English with LLM, if available."""
    client = get_attempt_llm_client()
    if client is None:
        return None

    system_prompt = (
        "You are a Korean-to-English translator. "
        "Return only the English translation as plain text, no notes."
    )
    user_prompt = f"Translate this Korean phrase to English: {text}"

    try:
        translated = client.chat(
            prompt=user_prompt,
            system=system_prompt,
            temperature=0.0,
            max_tokens=60,
            use_cache=True,
        ).strip()
        return translated or None
    except Exception as err:
        logger.warning(f"Option translation failed, fallback to source text: {err}")
        return None


def build_option_tiles(exercise: Exercise) -> tuple[list[dict], str]:
    """
    Build display tiles for option-based exercises.
    Returns (tiles, option_mode) where option_mode is english|korean.
    """
    if not exercise.options:
        return [], "korean"

    try:
        raw_options = json.loads(exercise.options)
    except json.JSONDecodeError:
        return [], "korean"

    if not isinstance(raw_options, list):
        return [], "korean"

    tiles = []
    english_count = 0
    for raw in raw_options:
        key = str(raw)
        label = key
        translated = False

        if looks_like_english(key):
            english_count += 1
        else:
            mapped = ENGLISH_PHRASE_MAP.get(key.strip())
            if mapped:
                label = mapped
                translated = True
                english_count += 1
            else:
                llm_translation = translate_text_with_llm(key)
                if llm_translation:
                    label = llm_translation
                    translated = True
                    english_count += 1

        tiles.append({"key": key, "label": label, "translated": translated})

    option_mode = "english" if english_count == len(tiles) and tiles else "korean"
    return tiles, option_mode


@lessons_bp.route("/lessons/<int:lesson_id>", methods=["GET"])
def get_lesson(lesson_id: int):
    """
    Get lesson with grammar explanation and exercises

    Response:
        {
            "lesson": {
                "id": 1,
                "title": "Hello & Goodbye",
                "description": "...",
                "grammar_explanation": "...",
                "grammar_tip": "...",
                "estimated_minutes": 5,
                "unit_id": 1,
                "exercises": [
                    {
                        "id": 1,
                        "exercise_type": "vocabulary",
                        "question": "...",
                        "instruction": "...",
                        "korean_text": "...",
                        "romanization": "...",
                        "english_text": "...",
                        "options": ["a", "b", "c", "d"],
                        "audio_url": "..."
                    },
                    ...
                ],
                "progress": {
                    "is_started": true,
                    "is_completed": false,
                    "completed_exercises": 3,
                    "total_exercises": 8
                }
            }
        }
    """
    try:
        lesson = db.session.get(Lesson, lesson_id)
        if not lesson:
            return not_found_response("Lesson")

        progress = get_user_progress(lesson_id)

        exercises = []
        for ex in lesson.exercises:
            exercise_data = {
                "id": ex.id,
                "exercise_type": ex.exercise_type.value,
                "question": ex.question,
                "instruction": ex.instruction,
                "display_order": ex.display_order,
            }

            # Add type-specific fields
            if ex.korean_text:
                exercise_data["korean_text"] = ex.korean_text
            if ex.romanization:
                exercise_data["romanization"] = ex.romanization
            if ex.english_text:
                exercise_data["english_text"] = ex.english_text
            if ex.content_text:
                exercise_data["content_text"] = ex.content_text
            if ex.audio_url:
                exercise_data["audio_url"] = ex.audio_url
            if ex.options:
                try:
                    exercise_data["options"] = json.loads(ex.options)
                except json.JSONDecodeError:
                    exercise_data["options"] = []

            # Don't include correct_answer in the response (for security)
            exercises.append(exercise_data)

        progress_data = None
        if progress:
            progress_data = {
                "is_started": progress.is_started,
                "is_completed": progress.is_completed,
                "completed_exercises": progress.completed_exercises,
                "total_exercises": progress.total_exercises,
                "score": progress.score,
            }

        lesson_data = {
            "id": lesson.id,
            "title": lesson.title,
            "description": lesson.description,
            "grammar_explanation": lesson.grammar_explanation,
            "grammar_tip": lesson.grammar_tip,
            "estimated_minutes": lesson.estimated_minutes,
            "unit_id": lesson.unit_id,
            "exercise_count": lesson.exercise_count,
            "exercises": exercises,
            "progress": progress_data,
        }

        # Include grammar patterns with mastery data when feature is enabled
        if current_app.config.get("GRAMMAR_MASTERY_ENABLED"):
            user_id = get_current_user_id()
            pattern_ids = [gp.id for gp in lesson.grammar_patterns]

            # Single query for all mastery records (avoids N+1)
            mastery_map = {}
            if pattern_ids:
                mastery_records = (
                    db.session.query(GrammarMastery)
                    .filter(
                        GrammarMastery.user_id == user_id,
                        GrammarMastery.pattern_id.in_(pattern_ids),
                    )
                    .all()
                )
                mastery_map = {m.pattern_id: m for m in mastery_records}

            grammar_patterns = []
            for gp in lesson.grammar_patterns:
                pattern_data = {
                    "id": gp.id,
                    "title": gp.title,
                    "pattern": gp.pattern,
                    "meaning": gp.meaning,
                    "example_korean": gp.example_korean,
                    "example_english": gp.example_english,
                }
                mastery = mastery_map.get(gp.id)
                if mastery:
                    pattern_data["mastery"] = {
                        "mastery_score": mastery.mastery_score,
                        "attempts": mastery.attempts,
                        "correct": mastery.correct,
                    }
                grammar_patterns.append(pattern_data)
            lesson_data["grammar_patterns"] = grammar_patterns

        return jsonify({"lesson": lesson_data}), 200

    except Exception as e:
        logger.error(f"Error getting lesson {lesson_id}: {e}")
        return error_response("Failed to get lesson", 500)


@lessons_bp.route("/lessons/<int:lesson_id>/start", methods=["POST"])
def start_lesson(lesson_id: int):
    """
    Mark lesson as started

    Response:
        {
            "success": true,
            "progress": {
                "is_started": true,
                "started_at": "2024-01-15T10:30:00Z"
            }
        }
    """
    try:
        lesson = db.session.get(Lesson, lesson_id)
        if not lesson:
            return not_found_response("Lesson")

        progress = get_or_create_user_progress(lesson_id, lesson.exercise_count)

        if not progress.is_started:
            progress.is_started = True
            progress.started_at = datetime.utcnow()
            progress.total_exercises = lesson.exercise_count

        progress.last_activity_at = datetime.utcnow()
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "progress": {
                        "is_started": progress.is_started,
                        "started_at": progress.started_at.isoformat()
                        if progress.started_at
                        else None,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error starting lesson {lesson_id}: {e}")
        db.session.rollback()
        return error_response("Failed to start lesson", 500)


@lessons_bp.route("/lessons/<int:lesson_id>/complete", methods=["POST"])
def complete_lesson(lesson_id: int):
    """
    Mark lesson as completed

    Request body:
        {
            "score": 85.5,
            "time_spent_seconds": 300
        }

    Response:
        {
            "success": true,
            "progress": {
                "is_completed": true,
                "completed_at": "2024-01-15T10:35:00Z",
                "score": 85.5
            }
        }
    """
    try:
        lesson = db.session.get(Lesson, lesson_id)
        if not lesson:
            return not_found_response("Lesson")

        data = request.get_json() or {}
        score = data.get("score")
        time_spent = data.get("time_spent_seconds", 0)

        progress = get_or_create_user_progress(lesson_id, lesson.exercise_count)

        if not progress.is_started:
            progress.is_started = True
            progress.started_at = datetime.utcnow()

        progress.is_completed = True
        progress.completed_at = datetime.utcnow()
        progress.completed_exercises = lesson.exercise_count
        progress.last_activity_at = datetime.utcnow()

        if score is not None:
            progress.score = float(score)
        if time_spent:
            progress.time_spent_seconds = int(time_spent)

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "progress": {
                        "is_completed": progress.is_completed,
                        "completed_at": progress.completed_at.isoformat()
                        if progress.completed_at
                        else None,
                        "score": progress.score,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error completing lesson {lesson_id}: {e}")
        db.session.rollback()
        return error_response("Failed to complete lesson", 500)


@lessons_bp.route("/exercises/<int:exercise_id>/submit", methods=["POST"])
def submit_exercise(exercise_id: int):
    """
    Submit an answer for an exercise

    Request body:
        {
            "answer": "hello",
            "quality": 4,
            "peeked": false
        }

    Response:
        {
            "correct": true,
            "correct_answer": "hello",
            "explanation": "..."
        }
    """
    try:
        exercise = db.session.get(Exercise, exercise_id)
        if not exercise:
            return not_found_response("Exercise")

        data = request.get_json()
        if not data or "answer" not in data:
            return validation_error_response("answer is required")

        user_answer = data["answer"]
        quality = data.get("quality")
        peeked = data.get("peeked", False)

        if quality is not None:
            if not isinstance(quality, int):
                return validation_error_response("quality must be an integer")
            if quality < 0 or quality > 5:
                return validation_error_response("quality must be between 0 and 5")

        if not isinstance(peeked, bool):
            return validation_error_response("peeked must be a boolean")
        correct_answer = exercise.correct_answer

        # Handle different exercise types with appropriate validation
        if exercise.exercise_type.value == "sentence_arrange":
            is_correct = validate_sentence_arrange(user_answer, correct_answer)
        elif exercise.exercise_type.value == "writing":
            is_correct = validate_writing_answer(str(user_answer), correct_answer)
        else:
            # Standard text comparison for other exercise types
            user_answer_normalized = str(user_answer).strip().lower()
            correct_answer_normalized = correct_answer.strip().lower()
            is_correct = user_answer_normalized == correct_answer_normalized

        progress = get_user_progress(exercise.lesson_id)

        if progress:
            if is_correct and progress.completed_exercises < progress.total_exercises:
                progress.completed_exercises += 1
            progress.last_activity_at = datetime.utcnow()

        response_data = {
            "correct": is_correct,
            "correct_answer": exercise.correct_answer,
            "explanation": exercise.explanation,
        }

        # Update grammar mastery when feature is enabled and exercise is linked to a pattern
        if (
            current_app.config.get("GRAMMAR_MASTERY_ENABLED")
            and exercise.grammar_pattern_id
        ):
            user_id = get_current_user_id()
            mastery = (
                db.session.query(GrammarMastery)
                .filter(
                    GrammarMastery.user_id == user_id,
                    GrammarMastery.pattern_id == exercise.grammar_pattern_id,
                )
                .first()
            )
            if not mastery:
                mastery = GrammarMastery(
                    user_id=user_id,
                    pattern_id=exercise.grammar_pattern_id,
                    attempts=0,
                    correct=0,
                    mastery_score=0.0,
                )
                db.session.add(mastery)

            mastery.attempts += 1
            if is_correct:
                mastery.correct += 1
            mastery.mastery_score = (mastery.correct / mastery.attempts) * 100
            mastery.last_practiced_at = datetime.utcnow()

            pattern = exercise.grammar_pattern
            response_data["pattern_mastery"] = {
                "pattern_title": pattern.title if pattern else "Unknown",
                "mastery_score": mastery.mastery_score,
                "attempts": mastery.attempts,
            }

        # Auto-seed SRS record when sentence SRS is enabled
        if current_app.config.get("SENTENCE_SRS_ENABLED"):
            from srs_utils import apply_sm2

            user_id = get_current_user_id()
            srs = (
                db.session.query(ExerciseSRS)
                .filter(
                    ExerciseSRS.user_id == user_id,
                    ExerciseSRS.exercise_id == exercise_id,
                )
                .first()
            )
            if not srs:
                srs = ExerciseSRS(
                    user_id=user_id,
                    exercise_id=exercise_id,
                    times_practiced=0,
                    times_correct=0,
                    review_interval=1,
                    ease_factor=2.5,
                    repetitions=0,
                )
                db.session.add(srs)

            srs.times_practiced += 1
            if is_correct:
                srs.times_correct += 1

            effective_quality = 4 if is_correct else 1
            if quality is not None:
                effective_quality = min(quality, 3) if peeked else quality

            apply_sm2(srs, effective_quality)
            response_data["applied_quality"] = effective_quality

        db.session.commit()

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error submitting exercise {exercise_id}: {e}")
        db.session.rollback()
        return error_response("Failed to submit exercise", 500)


@lessons_bp.route("/exercises/<int:exercise_id>/attempt-check", methods=["POST"])
def check_exercise_attempt(exercise_id: int):
    """
    Evaluate attempt-first input with semantic LLM + deterministic fallback.

    Request body:
        {
            "attempt": "hello",
            "attempt_number": 1,
            "used_hint": false
        }
    """
    try:
        exercise = db.session.get(Exercise, exercise_id)
        if not exercise:
            return not_found_response("Exercise")

        if not exercise.options:
            return validation_error_response("attempt-check only supports option exercises")

        data = request.get_json(silent=True) or {}
        attempt = data.get("attempt")
        attempt_number = data.get("attempt_number")
        used_hint = data.get("used_hint")

        if not isinstance(attempt, str):
            return validation_error_response("attempt must be a string")
        if not isinstance(attempt_number, int) or attempt_number not in (1, 2):
            return validation_error_response("attempt_number must be 1 or 2")
        if not isinstance(used_hint, bool):
            return validation_error_response("used_hint must be a boolean")

        sanitized_attempt, _ = sanitize_user_input(attempt, max_length=200, check_injection=True)
        if not sanitized_attempt.strip():
            return validation_error_response("attempt is required")

        target = extract_english_target(exercise)
        if not target and exercise.correct_answer and not looks_like_english(exercise.correct_answer):
            target = translate_text_with_llm(exercise.correct_answer)
        status = "unscored"
        method = "unscored"

        if target:
            exact_match = normalize_english_text(sanitized_attempt) == normalize_english_text(target)
            llm_status = judge_attempt_with_llm(sanitized_attempt, target)
            if llm_status in {"correct", "wrong"} and not exact_match:
                status = llm_status
                method = "llm_semantic"
            else:
                status = "correct" if exact_match else "wrong"
                method = "exact_fallback"

        can_retry = attempt_number == 1 and status == "wrong"
        force_options = (attempt_number == 2 and status != "correct") or status == "unscored"
        micro_hint = None
        if attempt_number == 1 and status != "correct":
            micro_hint = (
                build_micro_hint(target)
                if status != "unscored"
                else "Micro-hint: think about the core meaning in simple English."
            )

        feedback_map = {
            "correct": "Correct attempt. Now confirm with options.",
            "wrong": "Not yet. Use the clue and try once more.",
            "unscored": "Could not score automatically. Continue with scaffold.",
        }
        option_tiles = None
        option_mode = None
        if force_options and status != "correct":
            built_tiles, built_mode = build_option_tiles(exercise)
            option_tiles = built_tiles
            option_mode = built_mode

        return (
            jsonify(
                {
                    "status": status,
                    "method": method,
                    "resolved_target_english": target,
                    "micro_hint": micro_hint,
                    "feedback": feedback_map[status],
                    "option_tiles": option_tiles,
                    "option_mode": option_mode,
                    "challenge_state": {
                        "attempts_used": attempt_number,
                        "can_retry": can_retry,
                        "force_options": force_options,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error checking attempt for exercise {exercise_id}: {e}")
        return error_response("Failed to check attempt", 500)


@lessons_bp.route("/lessons/<int:lesson_id>/next", methods=["GET"])
def get_next_lesson(lesson_id: int):
    """
    Get the next lesson in sequence

    Response:
        {
            "next_lesson": {
                "id": 2,
                "title": "...",
                "unit_id": 1,
                ...
            },
            "is_last_in_unit": false,
            "is_last_in_course": false
        }
    """
    try:
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return not_found_response("Lesson not found")

        # Get lessons in same unit
        same_unit_lessons = Lesson.query.filter_by(unit_id=lesson.unit_id).order_by(Lesson.display_order).all()
        current_index = next((i for i, l in enumerate(same_unit_lessons) if l.id == lesson_id), -1)

        # Check if there's a next lesson in the same unit
        if current_index >= 0 and current_index < len(same_unit_lessons) - 1:
            next_lesson = same_unit_lessons[current_index + 1]
            return jsonify(
                {
                    "next_lesson": {
                        "id": next_lesson.id,
                        "title": next_lesson.title,
                        "description": next_lesson.description,
                        "unit_id": next_lesson.unit_id,
                        "estimated_minutes": next_lesson.estimated_minutes,
                        "exercise_count": len(next_lesson.exercises) if next_lesson.exercises else 0,
                    },
                    "is_last_in_unit": False,
                    "is_last_in_course": False,
                }
            ), 200

        # No more lessons in unit - check if there's next unit
        from models_v2 import Unit
        current_unit = Unit.query.get(lesson.unit_id)
        if not current_unit:
            return jsonify({"next_lesson": None, "is_last_in_unit": True, "is_last_in_course": True}), 200

        next_unit = Unit.query.filter_by(course_id=current_unit.course_id).filter(
            Unit.display_order > current_unit.display_order
        ).order_by(Unit.display_order).first()

        if next_unit:
            # Get first lesson in next unit
            first_lesson_in_next_unit = Lesson.query.filter_by(unit_id=next_unit.id).order_by(
                Lesson.display_order
            ).first()
            if first_lesson_in_next_unit:
                return jsonify(
                    {
                        "next_lesson": {
                            "id": first_lesson_in_next_unit.id,
                            "title": first_lesson_in_next_unit.title,
                            "description": first_lesson_in_next_unit.description,
                            "unit_id": first_lesson_in_next_unit.unit_id,
                            "estimated_minutes": first_lesson_in_next_unit.estimated_minutes,
                            "exercise_count": len(first_lesson_in_next_unit.exercises)
                            if first_lesson_in_next_unit.exercises
                            else 0,
                        },
                        "is_last_in_unit": True,
                        "is_last_in_course": False,
                    }
                ), 200

        # No more lessons in course
        return jsonify({"next_lesson": None, "is_last_in_unit": True, "is_last_in_course": True}), 200

    except Exception as e:
        logger.error(f"Error getting next lesson for {lesson_id}: {e}")
        return error_response("Failed to get next lesson", 500)
