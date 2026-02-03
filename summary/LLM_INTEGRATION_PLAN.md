# Local LLM Integration Plan for Kapp

## Executive Summary

This document outlines a comprehensive plan for integrating a local Large Language Model (LLM) into the Kapp Korean learning application using either Ollama or LM Studio. The integration will enhance the learning experience with AI-powered features whilst maintaining data privacy and eliminating dependency on external APIs.

---

## 1. How Duolingo Uses LLMs (GPT-4/5)

### Overview
Duolingo has become OpenAI's largest API customer, integrating GPT-4 and GPT-5 across multiple features to create an AI-enhanced learning experience.

### Key LLM-Powered Features in Duolingo

#### 1. **Explain My Answer**
- **What it does**: When users make mistakes, they can tap "Explain" to get a contextual explanation
- **LLM role**: Analyses the user's incorrect answer, identifies the specific error, and generates a personalised explanation
- **Example**: User writes "나는 학교에 가요" instead of "나는 학교에 갔어요"
  - LLM explains: "You used present tense (가요) but the sentence requires past tense (갔어요). The context suggests a completed action."

#### 2. **Roleplay Conversations**
- **What it does**: Interactive conversation practice with AI characters in realistic scenarios
- **LLM role**: Maintains context, responds naturally to learner input, adapts difficulty
- **Example**: Ordering food at a Korean restaurant, the AI plays the server role

#### 3. **Video Call Feature** (Max tier)
- **What it does**: Live video practice sessions with AI tutor
- **LLM role**: Real-time conversational AI with voice interaction
- **Technical**: Combines speech-to-text, LLM processing, and text-to-speech

#### 4. **Adaptive Exercise Generation**
- **What it does**: Creates personalised practice exercises based on learner weaknesses
- **LLM role**: Analyses learning history and generates targeted exercises
- **Example**: If user struggles with particles (이/가 vs 은/는), generates focused exercises

#### 5. **Contextual Hints**
- **What it does**: Provides progressive hints without giving away the answer
- **LLM role**: Generates graduated hints based on difficulty and learner level

### Technical Architecture (Duolingo's Approach)
```
Frontend (React/Mobile)
    ↓
API Gateway (Rate limiting, auth)
    ↓
Backend Services (Python/Go)
    ↓
OpenAI API (GPT-4/5)
    ↓
Prompt Engineering Layer
    - System prompts for each feature
    - Context injection (user level, learning history)
    - Response formatting
    ↓
Caching Layer
    - Cache similar queries
    - Reduce API costs
```

### Key Insights from Duolingo's Implementation

1. **Prompt Engineering is Critical**: Each feature has carefully crafted system prompts
2. **Context Matters**: User level, learning history, and card difficulty inform LLM responses
3. **Caching Reduces Costs**: Similar queries are cached (e.g., standard explanations)
4. **Graceful Degradation**: If LLM fails, app continues without AI features
5. **Progressive Enhancement**: LLM features are additive, not core requirements

---

## 2. Use Cases for Kapp (Korean Learning App)

Based on your current architecture and Duolingo's approach, here are prioritised LLM features:

### Phase 1: Core LLM Features (MVP)

#### A. **Contextual Card Explanations**
- **Trigger**: Button on flashcard back (after revealing answer)
- **Input**: Korean word/phrase, English translation, user's time spent on card
- **Output**: 
  - Grammar explanation (if applicable)
  - Usage context and examples
  - Common mistakes to avoid
  - Related vocabulary
- **API Endpoint**: `POST /api/llm/explain`

#### B. **Example Sentence Generation**
- **Trigger**: When viewing a card that lacks `example_sentence`
- **Input**: Korean word, English translation, TOPIK level
- **Output**: 2-3 contextually appropriate example sentences
- **API Endpoint**: `POST /api/llm/generate-examples`

#### C. **Translation Assistance During Review**
- **Trigger**: "I don't understand" button during review
- **Input**: Current card, user's rating history for this card
- **Output**: Simplified explanation, mnemonic device, visual description
- **API Endpoint**: `POST /api/llm/assist`

### Phase 2: Interactive Features

#### D. **Conversational Practice Mode**
- **Trigger**: New "Conversation" mode button on dashboard
- **Input**: User message in Korean (or English prompt)
- **Output**: Natural Korean response with difficulty appropriate to user level
- **Features**:
  - Context retention across conversation
  - Gentle corrections embedded in responses
  - Session summary with learning points
- **API Endpoint**: `POST /api/llm/conversation`

#### E. **Dynamic Quiz Generation**
- **Trigger**: "Practice weak areas" button
- **Input**: User's review history (cards with low ratings)
- **Output**: Custom exercises targeting problem areas
- **API Endpoint**: `POST /api/llm/generate-quiz`

### Phase 3: Advanced Features

#### F. **Smart Review Hints**
- Progressive hint system (3 levels)
- Integrated into review session
- Doesn't directly reveal answer

#### G. **Learning Path Recommendations**
- Analyses progress and suggests next decks
- Identifies knowledge gaps

#### H. **Cultural Context Enrichment**
- Korean cultural notes related to vocabulary
- Etiquette tips, honorific usage guidance

---

## 3. Technical Architecture

### 3.1 Local LLM Options Comparison

| Feature | Ollama | LM Studio |
|---------|--------|-----------|
| **Interface** | CLI-first, API-focused | GUI with API server |
| **Installation** | Lightweight, quick | Desktop app, larger |
| **API Compatibility** | OpenAI-compatible | OpenAI-compatible |
| **Model Management** | `ollama pull <model>` | GUI download manager |
| **Performance** | Optimised for servers | Optimised for desktops |
| **GPU Support** | CUDA, Metal, ROCm | CUDA, Metal, Vulkan (Intel/AMD integrated) |
| **Best For** | Production, scripting | Development, experimentation |

**Recommendation**: Start with **Ollama** for production, use **LM Studio** for development/testing.

### 3.2 Recommended Models

For Korean language learning, prioritise models with multilingual support:

| Model | Size | Memory | Use Case |
|-------|------|--------|----------|
| **Llama 3.2 3B** | 3B params | ~4GB | Fast responses, simple explanations |
| **Llama 3.1 8B** | 8B params | ~8GB | Balanced performance, good for conversation |
| **Qwen2.5 7B** | 7B params | ~7GB | Strong multilingual (Chinese/Korean/Japanese) |
| **Gemma 2 9B** | 9B params | ~10GB | High quality, good reasoning |
| **Mistral 7B** | 7B params | ~8GB | Fast, coherent, general-purpose |

**Primary Recommendation**: **Qwen2.5 7B** - Excellent Korean language support due to Chinese language pre-training (shared characters).

**Fallback**: **Llama 3.1 8B** - Strong general performance, good multilingual capabilities.

### 3.3 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│  - ReviewSession.tsx (explanation buttons)                  │
│  - ConversationMode.tsx (new component)                     │
│  - Dashboard.tsx (practice modes)                           │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP Requests
                     ↓
┌─────────────────────────────────────────────────────────────┐
│               Flask Backend (Port 5001)                     │
│                                                             │
│  Existing Routes:                                           │
│  - /api/cards    - /api/reviews                            │
│  - /api/stats    - /api/audio                              │
│                                                             │
│  New LLM Routes (Blueprint):                               │
│  - /api/llm/explain          (card explanations)           │
│  - /api/llm/generate-examples (example sentences)          │
│  - /api/llm/assist           (translation help)            │
│  - /api/llm/conversation     (chat interface)              │
│  - /api/llm/health           (check LLM status)            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│            LLM Service Layer (llm_service.py)              │
│                                                             │
│  - OllamaClient class                                       │
│  - Prompt templates                                         │
│  - Context builders                                         │
│  - Response parsers                                         │
│  - Error handling & retries                                │
│  - Response caching (Redis/file-based)                     │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP POST
                     ↓
┌─────────────────────────────────────────────────────────────┐
│         Ollama Local Server (Port 11434)                   │
│                                                             │
│  - Model: Qwen2.5:7b (or Llama 3.1:8b)                    │
│  - OpenAI-compatible API                                    │
│  - Runs on same machine or separate GPU server            │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 Data Flow Example: "Explain This Card"

```
1. User clicks "Explain" button on flashcard
   ↓
2. Frontend sends POST /api/llm/explain
   {
     card_id: 123,
     user_context: {
       level: 1,
       previous_ratings: [2, 3, 2],
       time_spent: 45
     }
   }
   ↓
3. Flask route (routes/llm.py) receives request
   ↓
4. Validate input, fetch card from database
   ↓
5. Call llm_service.explain_card(card, user_context)
   ↓
6. llm_service builds prompt:
   - System prompt: "You are a Korean language tutor..."
   - User prompt: "Explain the word '안녕하세요'..."
   - Context: TOPIK level 1, beginner
   ↓
7. Check cache (MD5 hash of prompt)
   - If cached: return cached response (fast!)
   - If not: continue to step 8
   ↓
8. Send request to Ollama API (http://localhost:11434/v1/chat/completions)
   ↓
9. Ollama processes with local Qwen2.5 model (~1-3 seconds)
   ↓
10. Parse response, extract explanation
   ↓
11. Cache response for future use
   ↓
12. Return to frontend as JSON
   {
     explanation: "안녕하세요 is the most common...",
     examples: ["선생님, 안녕하세요!", ...],
     grammar_notes: "This is the formal greeting...",
     generated_at: "2025-11-06T10:30:00Z"
   }
   ↓
13. Frontend displays in modal/expandable section
```

---

## 4. Implementation Roadmap

### Branch Strategy

**Branch Name**: `feature/local-llm-integration`

**Base Branch**: `development`

### Phase 1: Setup & Infrastructure (Week 1)

#### 1.1 Install Ollama
```bash
# macOS
brew install ollama

# Start Ollama service
ollama serve

# Pull recommended model
ollama pull qwen2.5:7b

# Test
ollama run qwen2.5:7b "Translate to Korean: Hello, how are you?"
```

#### 1.2 Create LLM Service Layer

**File**: `backend/llm_service.py`

```python
"""
LLM Service for local AI integration using Ollama

This service provides:
- Connection to local Ollama instance
- Prompt template management
- Response caching
- Error handling and retries
"""

import requests
import hashlib
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with local Ollama LLM"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5:7b",
        timeout: int = 30,
        cache_dir: str = "./data/llm_cache"
    ):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.cache_dir = cache_dir
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
    def _get_cache_key(self, prompt: str, system: str = "") -> str:
        """Generate cache key from prompt"""
        content = f"{system}|{prompt}|{self.model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Retrieve cached response if exists and valid"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            
            # Check if cache is still valid (24 hours)
            cached_time = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - cached_time > timedelta(hours=24):
                return None
            
            logger.info(f"Cache hit for key: {cache_key}")
            return cached['response']
        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache response to disk"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'response': response,
                    'timestamp': datetime.now().isoformat(),
                    'model': self.model
                }, f, ensure_ascii=False, indent=2)
            logger.info(f"Cached response for key: {cache_key}")
        except Exception as e:
            logger.error(f"Error caching response: {e}")
    
    def chat(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 500,
        use_cache: bool = True
    ) -> str:
        """
        Send chat request to Ollama
        
        Args:
            prompt: User prompt
            system: System prompt (instructions)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            use_cache: Whether to use cached responses
        
        Returns:
            Generated text response
        """
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(prompt, system)
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
        
        # Prepare request
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            # Send request to Ollama
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Extract response text
            result = response.json()
            generated_text = result['choices'][0]['message']['content']
            
            # Cache for future use
            if use_cache:
                self._cache_response(cache_key, generated_text)
            
            return generated_text
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            raise Exception("LLM request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to Ollama")
            raise Exception("LLM service unavailable. Ensure Ollama is running.")
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise Exception(f"LLM error: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            return {
                'status': 'ok',
                'available': True,
                'models': model_names,
                'configured_model': self.model,
                'model_loaded': self.model in model_names
            }
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return {
                'status': 'error',
                'available': False,
                'error': str(e)
            }


# Prompt templates for different use cases
PROMPT_TEMPLATES = {
    'explain_card': {
        'system': """You are an expert Korean language tutor helping English speakers learn Korean.
Your explanations are clear, concise, and appropriate for the learner's level.
Focus on practical usage and common mistakes.
Use simple English and provide examples in both Korean and romanisation when helpful.""",
        
        'user': """Explain this Korean vocabulary:

Korean: {korean}
Romanisation: {romanisation}
English: {english}
Learner Level: {level_name} (TOPIK Level {level})

Please provide:
1. A clear explanation of the meaning and usage
2. 2-3 example sentences showing different contexts
3. Common mistakes learners make with this word
4. Any important grammar or cultural notes

Keep your response concise (under 200 words) and beginner-friendly."""
    },
    
    'generate_examples': {
        'system': """You are a Korean language expert creating example sentences for vocabulary practice.
Generate natural, practical sentences appropriate for the learner's level.
Each sentence should demonstrate realistic usage.""",
        
        'user': """Create 3 example sentences using this Korean word:

Korean: {korean}
English: {english}
Learner Level: TOPIK Level {level}

For each sentence provide:
- Korean sentence
- Romanisation
- English translation

Make sentences progressively more complex."""
    },
    
    'conversation': {
        'system': """You are a friendly Korean language conversation partner.
Help the learner practice by having natural conversations.
Gently correct mistakes by rephrasing correctly in your response.
Keep your responses short (1-2 sentences) and appropriate for their level.
Use mostly Korean with occasional English clarifications for beginners.""",
        
        'user': """Learner Level: TOPIK Level {level}
Previous context: {context}

Learner says: {message}

Respond naturally in Korean. If they made mistakes, model the correct form in your response without explicitly pointing out errors."""
    }
}


# Utility functions
def get_level_name(level: int) -> str:
    """Convert numeric level to descriptive name"""
    level_names = {
        0: "Absolute Beginner",
        1: "Beginner (TOPIK I Level 1)",
        2: "Elementary (TOPIK I Level 2)",
        3: "Intermediate (TOPIK II Level 3)",
        4: "Upper-Intermediate (TOPIK II Level 4)",
        5: "Advanced (TOPIK II Level 5-6)"
    }
    return level_names.get(level, "Unknown")
```

#### 1.3 Create LLM Routes Blueprint

**File**: `backend/routes/llm.py`

```python
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
import logging

logger = logging.getLogger(__name__)

llm_bp = Blueprint('llm', __name__)

# Initialise LLM client (lazy loading)
_llm_client = None

def get_llm_client() -> OllamaClient:
    """Get or create LLM client instance"""
    global _llm_client
    if _llm_client is None:
        model = current_app.config.get('LLM_MODEL', 'qwen2.5:7b')
        base_url = current_app.config.get('LLM_BASE_URL', 'http://localhost:11434')
        _llm_client = OllamaClient(base_url=base_url, model=model)
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
```

#### 1.4 Register LLM Blueprint

**File**: `backend/app.py` (update `register_blueprints` function)

```python
def register_blueprints(app):
    """Register Flask blueprints for routes"""
    from routes.cards import cards_bp
    from routes.reviews import reviews_bp
    from routes.stats import stats_bp
    from routes.audio import audio_bp
    from routes.llm import llm_bp  # NEW
    
    app.register_blueprint(cards_bp, url_prefix='/api')
    app.register_blueprint(reviews_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/api')
    app.register_blueprint(audio_bp, url_prefix='/api')
    app.register_blueprint(llm_bp, url_prefix='/api')  # NEW
```

#### 1.5 Add Configuration

**File**: `backend/config.py` (add to Config class)

```python
class Config:
    # ... existing config ...
    
    # LLM Configuration
    LLM_MODEL = os.getenv('LLM_MODEL', 'qwen2.5:7b')
    LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'http://localhost:11434')
    LLM_CACHE_DIR = os.path.join(BASE_DIR, 'data', 'llm_cache')
    LLM_ENABLED = os.getenv('LLM_ENABLED', 'true').lower() == 'true'
```

#### 1.6 Update Requirements

**File**: `backend/requirements.txt` (add)

```
# Existing dependencies...

# LLM integration
requests==2.31.0  # Already included, but ensure it's there
```

### Phase 2: Frontend Integration (Week 2)

#### 2.1 Create LLM API Client

**File**: `frontend/src/api/llm.ts` (new file)

```typescript
/**
 * LLM API client for AI-powered features
 */

const API_BASE = 'http://localhost:5001/api';

export interface LLMExplanation {
  explanation: string;
  card_id: number;
  generated_at: string;
}

export interface LLMExamples {
  examples_text: string;
  card_id: number;
  generated_at: string;
}

export interface ConversationResponse {
  response: string;
  timestamp: string;
}

export interface LLMHealth {
  status: string;
  available: boolean;
  models?: string[];
  configured_model?: string;
  model_loaded?: boolean;
  error?: string;
}

class LLMClient {
  private async request<T>(
    endpoint: string,
    method: string = 'GET',
    body?: any
  ): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }));
      throw new Error(error.error || error.details || 'Request failed');
    }

    return response.json();
  }

  /**
   * Check if LLM service is available
   */
  async healthCheck(): Promise<LLMHealth> {
    return this.request<LLMHealth>('/llm/health');
  }

  /**
   * Get explanation for a vocabulary card
   */
  async explainCard(
    cardId: number,
    userContext?: {
      level?: number;
      previous_ratings?: number[];
      time_spent?: number;
    }
  ): Promise<LLMExplanation> {
    return this.request<LLMExplanation>('/llm/explain', 'POST', {
      card_id: cardId,
      user_context: userContext || {},
    });
  }

  /**
   * Generate example sentences for a card
   */
  async generateExamples(cardId: number): Promise<LLMExamples> {
    return this.request<LLMExamples>('/llm/generate-examples', 'POST', {
      card_id: cardId,
    });
  }

  /**
   * Send message in conversation mode
   */
  async sendMessage(
    message: string,
    context: {
      level?: number;
      conversation_history?: Array<{ user: string; assistant: string }>;
    }
  ): Promise<ConversationResponse> {
    return this.request<ConversationResponse>('/llm/conversation', 'POST', {
      message,
      context,
    });
  }
}

export const llmClient = new LLMClient();
```

#### 2.2 Update FlashCard Component

**File**: `frontend/src/components/FlashCard.tsx`

Add "Explain" button that appears on the back of the card:

```typescript
// Add after the back-english div
{showBack && (
  <button 
    className="explain-button"
    onClick={(e) => {
      e.stopPropagation();
      onExplain?.(card.id);
    }}
  >
    💡 Explain This
  </button>
)}
```

**File**: `frontend/src/components/FlashCard.css`

```css
.explain-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.explain-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}
```

#### 2.3 Create Explanation Modal

**File**: `frontend/src/components/ExplanationModal.tsx` (new file)

```typescript
/**
 * Modal for displaying LLM-generated explanations
 */
import { useState, useEffect } from 'react';
import { llmClient } from '../api/llm';
import type { Card } from '../types';
import './ExplanationModal.css';

interface Props {
  card: Card;
  isOpen: boolean;
  onClose: () => void;
  userContext?: {
    level?: number;
    previous_ratings?: number[];
    time_spent?: number;
  };
}

export default function ExplanationModal({ card, isOpen, onClose, userContext }: Props) {
  const [explanation, setExplanation] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && !explanation) {
      fetchExplanation();
    }
  }, [isOpen, card.id]);

  const fetchExplanation = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await llmClient.explainCard(card.id, userContext);
      setExplanation(result.explanation);
    } catch (err) {
      console.error('Error fetching explanation:', err);
      setError(err instanceof Error ? err.message : 'Failed to load explanation');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>💡 Explanation</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="card-reference">
            <div className="korean">{card.front_korean}</div>
            <div className="english">{card.back_english}</div>
          </div>

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Generating explanation...</p>
            </div>
          )}

          {error && (
            <div className="error">
              <p>❌ {error}</p>
              <button onClick={fetchExplanation} className="retry-button">
                Try Again
              </button>
            </div>
          )}

          {explanation && !loading && (
            <div className="explanation-text">
              {explanation.split('\n').map((paragraph, i) => (
                <p key={i}>{paragraph}</p>
              ))}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button onClick={onClose} className="button button-primary">
            Got It!
          </button>
        </div>
      </div>
    </div>
  );
}
```

**File**: `frontend/src/components/ExplanationModal.css` (new file)

```css
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 2rem;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  line-height: 32px;
  transition: color 0.2s;
}

.close-button:hover {
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.card-reference {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  text-align: center;
}

.card-reference .korean {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.card-reference .english {
  font-size: 1rem;
  opacity: 0.9;
}

.explanation-text {
  line-height: 1.6;
  color: #333;
}

.explanation-text p {
  margin-bottom: 1rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e0e0e0;
  text-align: right;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

#### 2.4 Integrate into ReviewSession

**File**: `frontend/src/components/ReviewSession.tsx`

```typescript
// Add imports
import ExplanationModal from './ExplanationModal';

// Add state
const [showExplanation, setShowExplanation] = useState(false);

// Add handler
const handleExplain = (cardId: number) => {
  setShowExplanation(true);
};

// Update FlashCard component call
<FlashCard 
  card={currentCard} 
  showBack={showBack} 
  onFlip={() => setShowBack(prev => !prev)}
  onExplain={handleExplain}
/>

// Add modal before closing div
{showExplanation && currentCard && (
  <ExplanationModal
    card={currentCard}
    isOpen={showExplanation}
    onClose={() => setShowExplanation(false)}
    userContext={{
      level: currentCard.level,
      time_spent: (Date.now() - startTime) / 1000
    }}
  />
)}
```

### Phase 3: Testing & Optimisation (Week 3)

#### 3.1 Testing Checklist

- [ ] Ollama service starts and model loads successfully
- [ ] `/api/llm/health` endpoint returns correct status
- [ ] Card explanations generate within 3 seconds
- [ ] Explanations are cached (second request is instant)
- [ ] Modal displays correctly on mobile and desktop
- [ ] Graceful error handling when Ollama is offline
- [ ] Multiple concurrent requests don't crash backend
- [ ] Cache directory is created automatically

#### 3.2 Performance Optimisation

**Backend:**
- Implement request queuing to prevent Ollama overload
- Add timeout handling (30s max)
- Monitor cache hit rate

**Frontend:**
- Show skeleton loader whilst generating
- Implement optimistic UI updates
- Add retry logic with exponential backoff

#### 3.3 Documentation

Create `LLM_USAGE_GUIDE.md` with:
- Installation instructions
- Model recommendations
- Troubleshooting common issues
- Example prompts and responses

### Phase 4: Advanced Features (Week 4+)

#### 4.1 Conversation Mode
- New route component: `ConversationMode.tsx`
- Chat interface with message history
- "Practice Conversation" button on dashboard

#### 4.2 Smart Hints System
- Progressive hint levels (3 stages)
- Integration into review session
- Tracks hint usage for statistics

#### 4.3 Analytics Integration
- Track LLM usage (explanations requested, conversations held)
- Measure learning outcomes (cards with explanations vs without)
- Display insights on dashboard

---

## 5. Configuration & Environment Setup

### 5.1 Environment Variables

**File**: `backend/.env` (add)

```bash
# LLM Configuration
LLM_ENABLED=true
LLM_MODEL=qwen2.5:7b
LLM_BASE_URL=http://localhost:11434
LLM_CACHE_DIR=./data/llm_cache
```

### 5.2 Ollama Service Management

**macOS/Linux:**
```bash
# Start Ollama service (runs in background)
ollama serve

# Check service status
curl http://localhost:11434/api/tags

# Pull models
ollama pull qwen2.5:7b
ollama pull llama3.1:8b

# List loaded models
ollama list

# Run model test
ollama run qwen2.5:7b "Explain the Korean word 안녕하세요"
```

**Windows:**
```powershell
# Ollama service starts automatically after installation
# Check with:
curl http://localhost:11434/api/tags

# Pull models:
ollama pull qwen2.5:7b
```

### 5.3 Resource Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 8GB | 16GB |
| **Disk Space** | 10GB | 20GB (for multiple models) |
| **CPU** | 4 cores | 8 cores |
| **GPU** | None (CPU works) | NVIDIA/AMD/Apple Silicon |

**Model Loading Times:**
- First load: 5-10 seconds
- Subsequent requests: <1 second (model stays in memory)

**Response Times:**
- With GPU: 1-2 seconds
- CPU only: 3-8 seconds (depending on model size)

---

## 6. API Documentation

### Endpoint Reference

#### `GET /api/llm/health`

Check LLM service availability.

**Response:**
```json
{
  "status": "ok",
  "available": true,
  "models": ["qwen2.5:7b", "llama3.1:8b"],
  "configured_model": "qwen2.5:7b",
  "model_loaded": true
}
```

#### `POST /api/llm/explain`

Get explanation for a vocabulary card.

**Request:**
```json
{
  "card_id": 123,
  "user_context": {
    "level": 1,
    "previous_ratings": [2, 3, 2],
    "time_spent": 45
  }
}
```

**Response:**
```json
{
  "explanation": "안녕하세요 (annyeonghaseyo) is the most common...",
  "card_id": 123,
  "generated_at": "2025-11-06T10:30:00Z"
}
```

#### `POST /api/llm/generate-examples`

Generate example sentences.

**Request:**
```json
{
  "card_id": 123
}
```

**Response:**
```json
{
  "examples_text": "1. 선생님, 안녕하세요!\n   (Seonsaengnim, annyeonghaseyo!)\n   Hello, teacher!...",
  "card_id": 123,
  "generated_at": "2025-11-06T10:30:00Z"
}
```

#### `POST /api/llm/conversation`

Interactive conversation with AI tutor.

**Request:**
```json
{
  "message": "오늘 날씨가 어때요?",
  "context": {
    "level": 1,
    "conversation_history": [
      {"user": "안녕하세요!", "assistant": "안녕하세요! 오늘 기분이 어때요?"}
    ]
  }
}
```

**Response:**
```json
{
  "response": "오늘 날씨가 좋아요. 햇빛이 많이 나요. ☀️",
  "timestamp": "2025-11-06T10:30:00Z"
}
```

---

## 7. Troubleshooting Guide

### Common Issues

#### Issue: "LLM service unavailable"

**Symptoms:** Health check fails, explanations don't load

**Solutions:**
1. Check if Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```
2. Start Ollama service:
   ```bash
   ollama serve
   ```
3. Verify model is loaded:
   ```bash
   ollama list
   ```

#### Issue: "Request timed out"

**Symptoms:** Explanations take >30 seconds or fail

**Solutions:**
1. Model too large for hardware - switch to smaller model:
   ```bash
   ollama pull llama3.2:3b
   ```
2. Increase timeout in `llm_service.py`:
   ```python
   timeout: int = 60  # Increase from 30
   ```

#### Issue: "Out of memory"

**Symptoms:** Ollama crashes, system freezes

**Solutions:**
1. Use smaller model (3B instead of 7B)
2. Close other applications
3. Reduce max_tokens in prompts (500 → 300)

#### Issue: Slow response times

**Symptoms:** >5 seconds per explanation

**Solutions:**
1. Enable GPU acceleration (if available)
2. Use LM Studio instead of Ollama (better GPU utilisation)
3. Implement request queuing to prevent overload
4. Increase cache hit rate by standardising prompts

---

## 8. Future Enhancements

### Short-term (1-3 months)

1. **Fine-tuned Model**
   - Create custom Korean-learning model
   - Train on common learner mistakes
   - Integrate with Ollama using Modelfile

2. **Voice Integration**
   - Combine TTS with LLM responses
   - Generate pronunciation guides
   - Voice-to-text for conversation mode

3. **Persistent Conversations**
   - Store conversation history in database
   - "Continue conversation" feature
   - Conversation analytics

### Long-term (3-6 months)

4. **Multimodal Learning**
   - Image-based vocabulary (using vision models)
   - Video content explanation
   - Handwriting recognition for Hangul

5. **Personalised Learning Paths**
   - LLM analyses user progress
   - Generates custom study plans
   - Adaptive difficulty adjustment

6. **Community Features**
   - Share LLM-generated study materials
   - Collaborative conversation mode
   - Peer review with LLM assistance

---

## 9. Cost-Benefit Analysis

### Benefits of Local LLM

✅ **Privacy**: All data stays on local machine
✅ **Cost**: No per-request API fees
✅ **Speed**: No network latency
✅ **Customisation**: Full control over prompts and models
✅ **Offline**: Works without internet (after model download)

### Drawbacks vs OpenAI API

❌ **Hardware Requirements**: Needs decent computer (8GB+ RAM)
❌ **Model Quality**: Local models < GPT-4 quality (but acceptable)
❌ **Maintenance**: User must manage Ollama service
❌ **Limited Capabilities**: No vision, audio, or advanced reasoning

### Recommendation

Local LLM is **ideal** for Kapp because:
- Personal learning app (not SaaS)
- Privacy-focused users
- Explanations don't require GPT-4 level reasoning
- Can fine-tune for Korean specifically
- Cost-effective for single users

For a commercial SaaS version, consider hybrid approach:
- Local LLM for basic features
- OpenAI API for advanced features (premium tier)

---

## 10. Success Metrics

Track these metrics to measure LLM integration success:

### Usage Metrics
- % of cards with explanation requested
- Average explanations per session
- Conversation mode engagement
- Feature adoption rate over time

### Quality Metrics
- User satisfaction (thumbs up/down on explanations)
- Explanation relevance score
- Cache hit rate (should be >60%)
- Response time (target: <3s for 90th percentile)

### Learning Outcomes
- Card retention rate (with vs without explanations)
- Review session completion rate
- Time-to-mastery improvement
- User-reported helpfulness

---

## Conclusion

This plan provides a comprehensive roadmap for integrating local LLM capabilities into Kapp using Ollama or LM Studio. The phased approach allows for:

1. **Quick MVP** (Week 1-2): Basic explanation feature
2. **Enhanced UX** (Week 2-3): Polished frontend integration
3. **Advanced Features** (Week 4+): Conversation mode, analytics

The architecture is designed to be:
- **Modular**: Easy to add/remove features
- **Scalable**: Can handle multiple concurrent users
- **Maintainable**: Clear separation of concerns
- **Extensible**: Foundation for future AI features

By following this plan, you'll create a powerful, privacy-focused, AI-enhanced Korean learning application that rivals commercial solutions whilst remaining fully under your control.

---

**Next Steps:**

1. Create feature branch: `git checkout -b feature/local-llm-integration`
2. Install Ollama and pull Qwen2.5:7b model
3. Implement Phase 1 backend (llm_service.py, routes/llm.py)
4. Test with curl/Postman
5. Implement Phase 2 frontend (ExplanationModal)
6. Integration testing
7. Documentation and deployment

Good luck! 🚀

