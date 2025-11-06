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
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

llm_bp = Blueprint('llm', __name__)

# Initialise LLM client (lazy loading)
_llm_client = None

def get_llm_client() -> OllamaClient:
    """Get or create LLM client instance"""
    global _llm_client
    if _llm_client is None:
        model = current_app.config.get('LLM_MODEL', 'open-llama-2-ko-7b')
        base_url = current_app.config.get('LLM_BASE_URL', 'http://localhost:11434')
        cache_dir = current_app.config.get('LLM_CACHE_DIR', 'data/llm_cache')
        _llm_client = OllamaClient(base_url=base_url, model=model, cache_dir=cache_dir)
    return _llm_client


@llm_bp.route('/llm/health', methods=['GET'])
def health_check():
    """Check if LLM service is available"""
    try:
        client = get_llm_client()
        health = client.health_check()
        return jsonify(health), 200 if health['available'] else 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'available': False,
            'error': str(e)
        }), 503


@llm_bp.route('/llm/explain', methods=['POST'])
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
        card_id = data.get('card_id')
        
        if not card_id:
            return jsonify({'error': 'card_id is required'}), 400
        
        # Fetch card from database
        card = db.session.get(Card, card_id)
        if not card:
            return jsonify({'error': 'Card not found'}), 404
        
        # Get user context
        user_context = data.get('user_context', {})
        level = user_context.get('level', card.level)
        
        # Build prompt
        template = PROMPT_TEMPLATES['explain_card']
        system_prompt = template['system']
        user_prompt = template['user'].format(
            korean=card.front_korean,
            romanisation=card.front_romanization or "N/A",
            english=card.back_english,
            level=level,
            level_name=get_level_name(level)
        )
        
        # Call LLM
        client = get_llm_client()
        response = client.chat(
            prompt=user_prompt,
            system=system_prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        return jsonify({
            'explanation': response,
            'card_id': card_id,
            'generated_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in explain_card: {e}")
        return jsonify({
            'error': 'Failed to generate explanation',
            'details': str(e)
        }), 500


@llm_bp.route('/llm/generate-examples', methods=['POST'])
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
        card_id = data.get('card_id')
        
        if not card_id:
            return jsonify({'error': 'card_id is required'}), 400
        
        card = db.session.get(Card, card_id)
        if not card:
            return jsonify({'error': 'Card not found'}), 404
        
        # Build prompt
        template = PROMPT_TEMPLATES['generate_examples']
        user_prompt = template['user'].format(
            korean=card.front_korean,
            english=card.back_english,
            level=card.level
        )
        
        # Call LLM
        client = get_llm_client()
        response = client.chat(
            prompt=user_prompt,
            system=template['system'],
            temperature=0.8,
            max_tokens=400
        )
        
        return jsonify({
            'examples_text': response,
            'card_id': card_id,
            'generated_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in generate_examples: {e}")
        return jsonify({
            'error': 'Failed to generate examples',
            'details': str(e)
        }), 500


@llm_bp.route('/llm/conversation', methods=['POST'])
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
        message = data.get('message')
        context = data.get('context', {})
        
        if not message:
            return jsonify({'error': 'message is required'}), 400
        
        level = context.get('level', 0)
        history = context.get('conversation_history', [])
        
        # Build context from history
        context_str = "\n".join([
            f"Learner: {h.get('user', '')}\nTutor: {h.get('assistant', '')}"
            for h in history[-3:]  # Last 3 exchanges
        ])
        
        # Build prompt
        template = PROMPT_TEMPLATES['conversation']
        user_prompt = template['user'].format(
            level=level,
            context=context_str or "This is the start of the conversation",
            message=message
        )
        
        # Call LLM
        client = get_llm_client()
        response = client.chat(
            prompt=user_prompt,
            system=template['system'],
            temperature=0.9,  # More creative for conversation
            max_tokens=200,
            use_cache=False  # Don't cache conversations
        )
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in conversation: {e}")
        return jsonify({
            'error': 'Failed to generate response',
            'details': str(e)
        }), 500

