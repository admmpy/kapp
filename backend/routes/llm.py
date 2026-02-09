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
from datetime import datetime
import logging

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


def get_llm_client() -> OpenAIClient:
    """Get or create LLM client instance"""
    global _llm_client
    if _llm_client is None:
        model = current_app.config.get("OPENAI_MODEL", "gpt-4o-mini")
        api_key = current_app.config.get("OPENAI_API_KEY")
        cache_dir = current_app.config.get("LLM_CACHE_DIR", "data/llm_cache")
        _llm_client = OpenAIClient(api_key=api_key, model=model, cache_dir=cache_dir)
    return _llm_client


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
