"""
LLM routes for AI-powered learning features

Endpoints:
- POST /api/llm/explain - Explain vocabulary card
- POST /api/llm/explain-exercise - Explain exercise answer
- POST /api/llm/generate-examples - Generate example sentences
- POST /api/llm/conversation - Interactive conversation
- GET /api/llm/health - Check LLM service status
"""

from flask import Blueprint, request, jsonify, current_app
from database import db
from models_v2 import VocabularyItem, Exercise
from llm_service import OpenAIClient, PROMPT_TEMPLATES, get_level_name
from extensions import limiter
from utils import error_response, not_found_response, validation_error_response
from security import sanitize_user_input, validate_conversation_history
from datetime import datetime, timedelta
import logging
import re
import threading
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

llm_bp = Blueprint("llm", __name__)


def validate_level(level, default: int = 0) -> int:
    """Validate and clamp level to valid range (0-5)"""
    if not isinstance(level, int):
        try:
            level = int(level)
        except (TypeError, ValueError):
            return default
    return max(0, min(5, level))


def ensure_llm_enabled():
    """Return an error response if LLM is disabled."""
    if not current_app.config.get("LLM_ENABLED", False):
        return error_response("LLM is disabled", 503)
    return None


# Initialise LLM client (lazy loading)
_llm_client = None
_listening_answer_store = {}
_listening_answer_store_lock = threading.Lock()
LISTENING_ANSWER_TTL_MINUTES = 20
LISTENING_ANSWER_MAX_STORE_SIZE = 2000


def get_llm_client() -> OpenAIClient:
    """Get or create LLM client instance"""
    global _llm_client
    if _llm_client is None:
        model = str(current_app.config.get("OPENAI_MODEL", "deepseek/deepseek-v3.2"))
        if "4o-mini" in model.lower():
            logger.warning("OPENAI_MODEL requested 4o-mini; forcing deepseek/deepseek-v3.2")
            model = "deepseek/deepseek-v3.2"
        api_key = current_app.config.get("OPENAI_API_KEY")
        base_url = current_app.config.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        cache_dir = current_app.config.get("LLM_CACHE_DIR", "data/llm_cache")
        _llm_client = OpenAIClient(
            api_key=api_key,
            model=model,
            cache_dir=cache_dir,
            base_url=base_url,
        )
    return _llm_client


def _prune_listening_answer_store(now: datetime) -> None:
    expired = [
        key for key, payload in _listening_answer_store.items()
        if payload.get("expires_at") <= now
    ]
    for key in expired:
        _listening_answer_store.pop(key, None)


def _store_listening_answer(correct_answer: str, options: list[str]) -> str:
    now = datetime.utcnow()
    answer_key = str(uuid.uuid4())
    with _listening_answer_store_lock:
        _prune_listening_answer_store(now)
        if len(_listening_answer_store) >= LISTENING_ANSWER_MAX_STORE_SIZE:
            oldest = min(
                _listening_answer_store.items(),
                key=lambda item: item[1].get("created_at", now),
            )[0]
            _listening_answer_store.pop(oldest, None)
        _listening_answer_store[answer_key] = {
            "correct_answer": correct_answer,
            "options": set(options),
            "created_at": now,
            "expires_at": now + timedelta(minutes=LISTENING_ANSWER_TTL_MINUTES),
        }
    return answer_key


def _consume_listening_answer(answer_key: str):
    now = datetime.utcnow()
    with _listening_answer_store_lock:
        _prune_listening_answer_store(now)
        payload = _listening_answer_store.pop(answer_key, None)
    if payload is None:
        return None
    if payload.get("expires_at") <= now:
        return None
    return payload


def _build_listening_fallback_exercise(topic: str, level: int) -> dict:
    """Provide a deterministic exercise when live LLM generation fails."""
    topic_lower = (topic or "").lower()

    if "coffee" in topic_lower or "cafe" in topic_lower:
        return {
            "korean_text": "저는 카페에서 아이스 아메리카노 한 잔 주세요 라고 말했어요.",
            "romanization": "jeoneun kapeeseo aiseu amerikhano han jan juseyo rago marhaesseoyo.",
            "english_translation": "I said, 'One iced Americano, please,' at the cafe.",
            "question": "What is the speaker doing?",
            "options": [
                "Ordering a coffee",
                "Asking for a bus schedule",
                "Buying a train ticket",
                "Meeting a teacher",
            ],
            "correct_answer": "Ordering a coffee",
            "explanation": "The phrase includes ordering an iced Americano at a cafe.",
        }

    if "direction" in topic_lower or "way" in topic_lower or "street" in topic_lower:
        return {
            "korean_text": "지하철역이 어디에 있는지 물어봤어요.",
            "romanization": "jihacheoryeogi eodie inneunji mureobwasseoyo.",
            "english_translation": "I asked where the subway station is.",
            "question": "What is the speaker doing?",
            "options": [
                "Asking for directions",
                "Ordering lunch",
                "Introducing a friend",
                "Paying a bill",
            ],
            "correct_answer": "Asking for directions",
            "explanation": "The sentence says the speaker asked where the subway station is.",
        }

    return {
        "korean_text": "오늘은 한국어 공부를 한 시간 했어요.",
        "romanization": "oneureun hangugeo gongbureul han sigan haesseoyo.",
        "english_translation": "Today I studied Korean for one hour.",
        "question": "What did the speaker do today?",
        "options": [
            "Studied Korean",
            "Watched a movie",
            "Went shopping",
            "Cooked dinner",
        ],
        "correct_answer": "Studied Korean",
        "explanation": "The sentence explicitly says they studied Korean for one hour.",
    }


def _get_cached_audio_fallback_url(cache_dir: str) -> str | None:
    """Return any cached audio URL if fresh generation fails."""
    try:
        audio_dir = Path(current_app.root_path) / cache_dir
        candidates = sorted(audio_dir.glob("*.mp3"))
        if not candidates:
            return None
        return f"/api/audio/{candidates[0].name}"
    except Exception:
        return None


@llm_bp.route("/llm/health", methods=["GET"])
def health_check():
    """Check if LLM service is available"""
    try:
        disabled_response = ensure_llm_enabled()
        if disabled_response:
            return disabled_response
        client = get_llm_client()
        health = client.health_check()
        return jsonify(health), 200 if health["available"] else 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error", "available": False, "error": "LLM unavailable"}), 503


@llm_bp.route("/llm/explain", methods=["POST"])
@limiter.limit("10/hour")
def explain_card():
    """
    Explain a vocabulary card using LLM

    Request body:
        {
            "card_id": 123,
            "user_context": {
                "level": 1,
                "previous_ratings": [2, 3],
                "time_spent": 45
            }
        }

    Response:
        {
            "explanation": "...",
            "examples": ["...", "..."],
            "notes": "...",
            "generated_at": "2025-11-06T10:30:00Z"
        }
    """
    try:
        disabled_response = ensure_llm_enabled()
        if disabled_response:
            return disabled_response
        data = request.get_json(silent=True) or {}
        vocab_id = data.get("vocab_id") or data.get("card_id")

        if not vocab_id:
            return validation_error_response("vocab_id is required")

        # Fetch vocabulary item from database (card_id maps to vocabulary item)
        vocab = db.session.get(VocabularyItem, vocab_id)
        if not vocab:
            return not_found_response("Vocabulary item")

        # Get user context
        user_context = data.get("user_context", {})
        level = validate_level(
            user_context.get("level", vocab.difficulty_level), default=vocab.difficulty_level
        )

        # Build prompt
        template = PROMPT_TEMPLATES["explain_card"]
        system_prompt = template["system"]
        user_prompt = template["user"].format(
            korean=vocab.korean,
            romanisation=vocab.romanization or "N/A",
            english=vocab.english,
            level=level,
            level_name=get_level_name(level),
        )

        # Call LLM
        client = get_llm_client()
        response = client.chat(
            prompt=user_prompt, system=system_prompt, temperature=0.7, max_tokens=500
        )

        return (
            jsonify(
                {
                    "explanation": response,
                    "vocab_id": vocab_id,
                    "generated_at": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error in explain_card: {e}")
        return error_response("Failed to generate explanation", 500)


@llm_bp.route("/llm/generate-examples", methods=["POST"])
@limiter.limit("10/hour")
def generate_examples():
    """
    Generate example sentences for a card

    Request body:
        {
            "card_id": 123
        }

    Response:
        {
            "examples": [
                {
                    "korean": "...",
                    "romanisation": "...",
                    "english": "..."
                },
                ...
            ]
        }
    """
    try:
        disabled_response = ensure_llm_enabled()
        if disabled_response:
            return disabled_response
        data = request.get_json(silent=True) or {}
        vocab_id = data.get("vocab_id") or data.get("card_id")

        if not vocab_id:
            return validation_error_response("vocab_id is required")

        vocab = db.session.get(VocabularyItem, vocab_id)
        if not vocab:
            return not_found_response("Vocabulary item")

        # Build prompt
        template = PROMPT_TEMPLATES["generate_examples"]
        user_prompt = template["user"].format(
            korean=vocab.korean, english=vocab.english, level=vocab.difficulty_level
        )

        # Call LLM
        client = get_llm_client()
        response = client.chat(
            prompt=user_prompt,
            system=template["system"],
            temperature=0.8,
            max_tokens=400,
        )

        return (
            jsonify(
                {
                    "examples_text": response,
                    "vocab_id": vocab_id,
                    "generated_at": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error in generate_examples: {e}")
        return error_response("Failed to generate examples", 500)


@llm_bp.route("/llm/explain-exercise", methods=["POST"])
@limiter.limit("10/hour")
def explain_exercise():
    """
    Explain an exercise answer using LLM

    Request body:
        {
            "exercise_id": 123,
            "user_context": {
                "level": 1
            }
        }
    """
    try:
        disabled_response = ensure_llm_enabled()
        if disabled_response:
            return disabled_response
        data = request.get_json(silent=True) or {}
        exercise_id = data.get("exercise_id")

        if not exercise_id:
            return validation_error_response("exercise_id is required")

        exercise = db.session.get(Exercise, exercise_id)
        if not exercise:
            return not_found_response("Exercise")

        user_context = data.get("user_context", {})
        level = validate_level(user_context.get("level", 0), default=0)

        template = PROMPT_TEMPLATES["exercise_explanation"]
        system_prompt = template["system"]
        user_prompt = template["user"].format(
            question=exercise.question,
            correct_answer=exercise.correct_answer,
            level_name=get_level_name(level),
            korean_text=exercise.korean_text or "N/A",
            romanization=exercise.romanization or "N/A",
            english_text=exercise.english_text or "N/A",
            basic_explanation=exercise.explanation or "N/A",
        )

        client = get_llm_client()
        response = client.chat(
            prompt=user_prompt, system=system_prompt, temperature=0.7, max_tokens=400
        )

        return (
            jsonify(
                {
                    "explanation": response,
                    "exercise_id": exercise_id,
                    "generated_at": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error in explain_exercise: {e}")
        return error_response("Failed to generate explanation", 500)


@llm_bp.route("/llm/translate", methods=["POST"])
@limiter.limit("30/hour")
def translate_text():
    """
    Translate Korean text to English using LLM

    Request body:
        { "text": "한국어 텍스트" }

    Response:
        { "translation": "English text" }
    """
    try:
        disabled_response = ensure_llm_enabled()
        if disabled_response:
            return disabled_response

        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()

        if not text:
            return validation_error_response("text is required")

        if len(text) > 500:
            return validation_error_response("text must be 500 characters or fewer")

        template = PROMPT_TEMPLATES["translate"]
        user_prompt = template["user"].format(text=text)

        client = get_llm_client()
        response = client.chat(
            prompt=user_prompt,
            system=template["system"],
            temperature=0.3,
            max_tokens=200,
        )

        return jsonify({"translation": response}), 200

    except Exception as e:
        logger.error(f"Error in translate_text: {e}")
        return error_response("Failed to translate text", 500)


@llm_bp.route("/llm/conversation", methods=["POST"])
@limiter.limit("10/hour")
def conversation():
    """
    Interactive conversation with AI tutor

    Request body:
        {
            "message": "안녕하세요!",
            "context": {
                "level": 1,
                "conversation_history": [...]
            }
        }

    Response:
        {
            "response": "...",
            "timestamp": "..."
        }
    """
    try:
        disabled_response = ensure_llm_enabled()
        if disabled_response:
            return disabled_response
        data = request.get_json(silent=True) or {}
        raw_message = data.get("message")
        context = data.get("context") or data.get("user_context") or {}

        if not raw_message:
            return validation_error_response('message is required')

        # Sanitize user message to prevent prompt injection
        message, msg_warnings = sanitize_user_input(raw_message, max_length=500)
        if msg_warnings:
            logger.info(f"Input sanitization warnings: {msg_warnings}")

        if not message:
            return validation_error_response('message is required after sanitization')

        level = validate_level(context.get('level', 0), default=0)

        # Validate and sanitize conversation history
        raw_history = context.get("conversation_history", [])
        history_input = normalize_conversation_history(raw_history)
        history, history_warnings = validate_conversation_history(history_input)
        if history_warnings:
            logger.info(f"History validation warnings: {history_warnings}")

        # Build context from sanitized history
        context_str = "\n".join([
            f"Learner: {h.get('user', '')}\nTutor: {h.get('assistant', '')}"
            for h in history
        ])

        # Build prompt
        template = PROMPT_TEMPLATES["conversation"]
        user_prompt = template["user"].format(
            level=level,
            context=context_str or "This is the start of the conversation",
            message=message,
        )

        # Call LLM
        client = get_llm_client()
        response = client.chat(
            prompt=user_prompt,
            system=template["system"],
            temperature=0.9,  # More creative for conversation
            max_tokens=200,
            use_cache=False,  # Don't cache conversations
        )

        return (
            jsonify({"response": response, "timestamp": datetime.now().isoformat()}),
            200,
        )

    except Exception as e:
        logger.error(f"Error in conversation: {e}")
        return error_response("Failed to generate response", 500)


def normalize_conversation_history(history):
    """Normalize history to [{user, assistant}] format."""
    if not isinstance(history, list) or not history:
        return history

    if all(isinstance(h, dict) and "role" in h and "content" in h for h in history):
        exchanges = []
        current = {}
        for message in history:
            role = message.get("role")
            content = message.get("content", "")
            if role == "user":
                if current:
                    exchanges.append(current)
                    current = {}
                current["user"] = content
            elif role == "assistant":
                current["assistant"] = content
                exchanges.append(current)
                current = {}
        if current:
            exchanges.append(current)
        return exchanges

    return history


ELDER_STARTERS = [
    "어디서 오셨어요? 외국에서 오셨습니까?",
    "오늘 날씨가 참 좋네요, 그렇지요?",
    "한국에 오신 지 얼마나 되셨어요?",
    "한국어를 아주 잘 하시네요! 어디서 배우셨어요?",
    "차 한잔 하시겠어요? 앉으세요, 앉으세요.",
]


@llm_bp.route("/llm/conversation/elder", methods=["POST"])
@limiter.limit("10/hour")
def elder_conversation():
    """
    Elder conversation simulator — 할아버지 Mode

    Request body:
        {
            "message": "안녕하세요!",
            "context": {
                "conversation_history": [...],
                "starter_index": 0   // optional: which opener to use on first turn
            }
        }

    Response:
        {
            "response": "...",
            "timestamp": "..."
        }
    """
    import random as _random

    try:
        disabled_response = ensure_llm_enabled()
        if disabled_response:
            return disabled_response

        data = request.get_json(silent=True) or {}
        raw_message = (data.get("message") or "").strip()
        context = data.get("context") or {}

        if not raw_message:
            return validation_error_response("message is required")

        message, msg_warnings = sanitize_user_input(raw_message, max_length=500)
        if msg_warnings:
            logger.info(f"Elder conv sanitization warnings: {msg_warnings}")

        if not message:
            return validation_error_response("message is required after sanitization")

        raw_history = context.get("conversation_history", [])
        history_input = normalize_conversation_history(raw_history)
        history, _ = validate_conversation_history(history_input)

        context_str = "\n".join([
            f"Learner: {h.get('user', '')}\n할아버지: {h.get('assistant', '')}"
            for h in history
        ])
        if not context_str:
            starter_idx = context.get("starter_index")
            if isinstance(starter_idx, int) and 0 <= starter_idx < len(ELDER_STARTERS):
                opener = ELDER_STARTERS[starter_idx]
            else:
                opener = _random.choice(ELDER_STARTERS)
            context_str = f"[Conversation starts. 할아버지 opens with: {opener}]"

        template = PROMPT_TEMPLATES["elder_conversation"]
        user_prompt = template["user"].format(
            context=context_str,
            message=message,
        )

        client = get_llm_client()
        response = client.chat(
            prompt=user_prompt,
            system=template["system"],
            temperature=0.85,
            max_tokens=200,
            use_cache=False,
        )

        return jsonify({"response": response, "timestamp": datetime.now().isoformat()}), 200

    except Exception as e:
        logger.error(f"Error in elder_conversation: {e}")
        return error_response("Failed to generate response", 500)


@llm_bp.route("/llm/conversation/elder/start", methods=["GET"])
def elder_conversation_start():
    """Return a random elder conversation opening line."""
    import random as _random
    idx = _random.randrange(len(ELDER_STARTERS))
    return jsonify({"opening": ELDER_STARTERS[idx], "starter_index": idx}), 200


@llm_bp.route("/llm/listening-practice", methods=["POST"])
@limiter.limit("20/hour")
def listening_practice():
    """
    Generate AI-powered listening comprehension practice.

    Request body:
        {
            "topic": "ordering coffee at a cafe",
            "level": 2
        }

    Response:
        {
            "audio_url": "/api/audio/abc123.mp3",
            "korean_text": "...",
            "romanization": "...",
            "english_translation": "...",
            "question": "...",
            "options": ["...", "...", "...", "..."],
            "answer_key": "...",
            "explanation": "...",
            "generated_at": "..."
        }
    """
    try:
        disabled_response = ensure_llm_enabled()
        if disabled_response:
            return disabled_response

        data = request.get_json(silent=True) or {}
        topic = (data.get("topic") or "").strip()
        level = validate_level(data.get("level", 1), default=1)

        if not topic:
            return validation_error_response("topic is required")

        if len(topic) > 200:
            return validation_error_response("topic must be 200 characters or fewer")

        topic, topic_warnings = sanitize_user_input(topic, max_length=200)
        if topic_warnings:
            logger.info(f"Topic sanitization warnings: {topic_warnings}")

        template = PROMPT_TEMPLATES["listening_practice"]
        user_prompt = template["user"].format(
            topic=topic,
            level=level,
            level_name=get_level_name(level),
        )

        exercise_data = None
        client = get_llm_client()
        try:
            response_text = client.chat(
                prompt=user_prompt,
                system=template["system"],
                temperature=0.8,
                max_tokens=600,
                use_cache=False,
            )

            import json as json_module
            try:
                response_text_cleaned = response_text.strip()
                if response_text_cleaned.startswith("```"):
                    response_text_cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", response_text_cleaned)
                    response_text_cleaned = re.sub(r"\s*```$", "", response_text_cleaned)
                exercise_data = json_module.loads(response_text_cleaned)
            except json_module.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.error(f"Raw response: {response_text[:500]}")
                return error_response("Failed to generate valid exercise. Please try again.", 500)
        except Exception as llm_error:
            logger.warning(f"Using fallback listening exercise because LLM call failed: {llm_error}")
            exercise_data = _build_listening_fallback_exercise(topic, level)

        required_fields = ["korean_text", "question", "options", "correct_answer"]
        for field in required_fields:
            if field not in exercise_data:
                logger.error(f"Missing required field in exercise: {field}")
                return error_response(f"Generated exercise is missing {field}. Please try again.", 500)

        korean_text = exercise_data.get("korean_text")
        question = exercise_data.get("question")
        options_raw = exercise_data.get("options")
        correct_answer_raw = exercise_data.get("correct_answer")

        if not isinstance(korean_text, str) or not korean_text.strip():
            return error_response("Generated exercise has invalid korean_text. Please try again.", 500)

        if not isinstance(question, str) or not question.strip():
            return error_response("Generated exercise has invalid question. Please try again.", 500)

        if not isinstance(options_raw, list) or len(options_raw) != 4:
            return error_response("Generated exercise has invalid options. Please try again.", 500)

        options = []
        for option in options_raw:
            if not isinstance(option, str) or not option.strip():
                return error_response("Generated exercise has invalid options. Please try again.", 500)
            options.append(option.strip())

        if len(set(options)) != len(options):
            return error_response("Generated exercise has duplicate options. Please try again.", 500)

        if not isinstance(correct_answer_raw, str) or not correct_answer_raw.strip():
            return error_response("Generated exercise has invalid correct_answer. Please try again.", 500)

        correct_answer = correct_answer_raw.strip()
        if correct_answer not in options:
            return error_response("Generated exercise has mismatched correct_answer. Please try again.", 500)

        answer_key = _store_listening_answer(correct_answer=correct_answer, options=options)

        from tts_service import get_tts_service

        tts = get_tts_service(current_app.config.get("TTS_CACHE_DIR", "data/audio_cache"))
        slow = level <= 2
        audio_filename = tts.generate_audio(exercise_data["korean_text"], lang="ko", slow=slow)

        if audio_filename:
            audio_url = tts.get_audio_url(audio_filename)
        else:
            audio_url = _get_cached_audio_fallback_url(
                current_app.config.get("TTS_CACHE_DIR", "data/audio_cache")
            )
            if not audio_url:
                return error_response("Failed to generate audio. Please try again.", 500)

        return jsonify({
            "audio_url": audio_url,
            "korean_text": korean_text.strip(),
            "romanization": exercise_data.get("romanization"),
            "english_translation": exercise_data.get("english_translation"),
            "question": question.strip(),
            "options": options,
            "answer_key": answer_key,
            "explanation": exercise_data.get("explanation"),
            "topic": topic,
            "level": level,
            "generated_at": datetime.now().isoformat(),
        }), 200

    except Exception as e:
        logger.error(f"Error in listening_practice: {e}")
        return error_response("Failed to generate listening practice", 500)


@llm_bp.route("/llm/listening-practice/check", methods=["POST"])
@limiter.limit("60/hour")
def listening_practice_check():
    """Validate selected answer for a generated listening exercise."""
    try:
        disabled_response = ensure_llm_enabled()
        if disabled_response:
            return disabled_response

        data = request.get_json(silent=True) or {}
        answer_key = (data.get("answer_key") or "").strip()
        selected_answer = (data.get("selected_answer") or "").strip()

        if not answer_key:
            return validation_error_response("answer_key is required")
        if not selected_answer:
            return validation_error_response("selected_answer is required")

        payload = _consume_listening_answer(answer_key)
        if payload is None:
            return validation_error_response("answer_key is invalid or expired")

        if selected_answer not in payload["options"]:
            return validation_error_response("selected_answer is not in the generated options")

        correct_answer = payload["correct_answer"]
        return jsonify(
            {
                "correct": selected_answer == correct_answer,
                "correct_answer": correct_answer,
            }
        ), 200

    except Exception as e:
        logger.error(f"Error in listening_practice_check: {e}")
        return error_response("Failed to check listening practice answer", 500)
