"""
LLM routes for AI-powered learning features

Endpoints:
- POST /api/llm/explain - Explain vocabulary card
- POST /api/llm/generate-examples - Generate example sentences
- POST /api/llm/conversation - Interactive conversation
- GET /api/llm/health - Check LLM service status
"""

from flask import Blueprint, request, jsonify, current_app
from models import Card, db
from llm_service import OllamaClient, PROMPT_TEMPLATES, get_level_name
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


# Initialise LLM client (lazy loading)
_llm_client = None


def get_llm_client() -> OllamaClient:
    """Get or create LLM client instance"""
    global _llm_client
    if _llm_client is None:
        model = current_app.config.get("LLM_MODEL", "open-llama-2-ko-7b")
        base_url = current_app.config.get("LLM_BASE_URL", "http://localhost:11434")
        cache_dir = current_app.config.get("LLM_CACHE_DIR", "data/llm_cache")
        _llm_client = OllamaClient(base_url=base_url, model=model, cache_dir=cache_dir)
    return _llm_client


@llm_bp.route("/llm/health", methods=["GET"])
def health_check():
    """Check if LLM service is available"""
    try:
        client = get_llm_client()
        health = client.health_check()
        return jsonify(health), 200 if health["available"] else 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error", "available": False, "error": str(e)}), 503


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
        data = request.get_json()
        card_id = data.get("card_id")

        if not card_id:
            return validation_error_response("card_id is required")

        # Fetch card from database
        card = db.session.get(Card, card_id)
        if not card:
            return not_found_response("Card")

        # Get user context
        user_context = data.get("user_context", {})
        level = validate_level(
            user_context.get("level", card.level), default=card.level
        )

        # Build prompt
        template = PROMPT_TEMPLATES["explain_card"]
        system_prompt = template["system"]
        user_prompt = template["user"].format(
            korean=card.front_korean,
            romanisation=card.front_romanization or "N/A",
            english=card.back_english,
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
                    "card_id": card_id,
                    "generated_at": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error in explain_card: {e}")
        return error_response("Failed to generate explanation", 500, str(e))


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
        data = request.get_json()
        card_id = data.get("card_id")

        if not card_id:
            return validation_error_response("card_id is required")

        card = db.session.get(Card, card_id)
        if not card:
            return not_found_response("Card")

        # Build prompt
        template = PROMPT_TEMPLATES["generate_examples"]
        user_prompt = template["user"].format(
            korean=card.front_korean, english=card.back_english, level=card.level
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
                    "card_id": card_id,
                    "generated_at": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error in generate_examples: {e}")
        return error_response("Failed to generate examples", 500, str(e))


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
        data = request.get_json()
        raw_message = data.get('message')
        context = data.get('context', {})

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
        raw_history = context.get('conversation_history', [])
        history, history_warnings = validate_conversation_history(raw_history)
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
        return error_response("Failed to generate response", 500, str(e))
