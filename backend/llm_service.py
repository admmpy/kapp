"""
LLM Service for OpenAI integration (GPT-4o mini)

This service provides:
- Connection to OpenAI Responses API
- Prompt template management
- Response caching
- Error handling and retries
"""

import requests
import hashlib
import json
import os
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for interacting with OpenAI Responses API"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        timeout: int = 60,
        cache_dir: str = "./data/llm_cache",
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.cache_dir = cache_dir
        self.base_url = "https://api.openai.com/v1"

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
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)

            # Check if cache is still valid (24 hours)
            cached_time = datetime.fromisoformat(cached["timestamp"])
            if datetime.now() - cached_time > timedelta(hours=24):
                return None

            logger.info(f"Cache hit for key: {cache_key}")
            return cached["response"]
        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None

    def _cache_response(self, cache_key: str, response: str):
        """Cache response to disk"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "response": response,
                        "timestamp": datetime.now().isoformat(),
                        "model": self.model,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            logger.info(f"Cached response for key: {cache_key}")
        except Exception as e:
            logger.error(f"Error caching response: {e}")

    def _extract_text(self, response_json: Dict[str, Any]) -> str:
        """Extract output text from Responses API payload."""
        if response_json.get("output_text"):
            return response_json["output_text"]

        output_items = response_json.get("output", [])
        chunks = []
        for item in output_items:
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") in ("output_text", "text"):
                        text = content.get("text")
                        if text:
                            chunks.append(text)
            elif item.get("type") == "output_text":
                text = item.get("text")
                if text:
                    chunks.append(text)

        return "\n".join(chunks).strip()

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def chat(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 500,
        use_cache: bool = True,
    ) -> str:
        """
        Send chat request to OpenAI Responses API

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
        input_messages = []
        if system:
            input_messages.append({"role": "system", "content": system})
        input_messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "input": input_messages,
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            # Send request to OpenAI
            response = requests.post(
                f"{self.base_url}/responses",
                json=payload,
                timeout=self.timeout,
                headers=self._headers(),
            )
            response.raise_for_status()

            # Extract response text
            result = response.json()
            generated_text = self._extract_text(result)
            if not generated_text:
                raise Exception("LLM returned an empty response.")

            # Cache for future use
            if use_cache:
                self._cache_response(cache_key, generated_text)

            return generated_text

        except requests.exceptions.Timeout:
            logger.error("OpenAI request timed out")
            raise Exception("LLM request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to OpenAI")
            raise Exception("LLM service unavailable. Please try again later.")
        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            raise Exception(f"LLM error: {str(e)}")

    def health_check(self) -> Dict[str, Any]:
        """Check if OpenAI service is available"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                timeout=5,
                headers=self._headers(),
            )
            response.raise_for_status()

            models = response.json().get("data", [])
            model_names = [m.get("id") for m in models if m.get("id")]

            return {
                "status": "ok",
                "available": True,
                "models": model_names,
                "configured_model": self.model,
                "model_loaded": self.model in model_names,
            }
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return {"status": "error", "available": False, "error": "OpenAI API unavailable"}


# Prompt templates for different use cases
PROMPT_TEMPLATES = {
    "explain_card": {
        "system": """You are an expert Korean language tutor helping NATIVE ENGLISH SPEAKERS learn Korean.

CRITICAL INSTRUCTIONS:
- Write ALL explanations in ENGLISH ONLY
- Use simple, clear English that beginners can understand
- Only use Korean text when showing example sentences
- Always provide romanization (Korean pronunciation) next to Korean text
- Format Korean examples clearly: Korean (romanization) - English translation

Your goal is to help English speakers understand Korean vocabulary through clear English explanations.""",
        "user": """Explain this Korean vocabulary word to an English speaker:

Word: {korean} ({romanisation})
Meaning: {english}
Student Level: {level_name}

RESPOND IN ENGLISH ONLY. Provide:

1. MEANING & USAGE (in English):
   - Explain what this word means and when to use it
   - Describe the context where it's appropriate

2. EXAMPLE SENTENCES (3 examples, formatted as shown):
   Korean sentence (romanization) - English translation
   
   Format each example like this:
   - 안녕하세요 (annyeonghaseyo) - Hello (formal greeting)

3. COMMON MISTAKES (in English):
   - What errors do learners typically make with this word?
   - How to avoid confusion with similar words

4. CULTURAL NOTES (in English, if relevant):
   - Any cultural context or etiquette related to this word

Remember: All explanatory text must be in ENGLISH. Only show Korean in the example sentences, always with romanization and English translation.""",
    },
    "generate_examples": {
        "system": """You are a Korean language expert creating example sentences for vocabulary practice.
Generate natural, practical sentences appropriate for the learner's level.
Each sentence should demonstrate realistic usage.""",
        "user": """Create 3 example sentences using this Korean word:

Korean: {korean}
English: {english}
Learner Level: TOPIK Level {level}

For each sentence provide:
- Korean sentence
- Romanisation
- English translation

Make sentences progressively more complex.""",
    },
    "exercise_explanation": {
        "system": """You are a Korean language tutor helping learners understand their mistakes.
Explain why the correct answer is correct, identify common pitfalls, and give one concise tip.
Use simple English and keep the response short (4-6 sentences).""",
        "user": """Explain this exercise answer for an English-speaking learner.

Question: {question}
Correct Answer: {correct_answer}
Learner Level: {level_name}

Additional Context (if available):
- Korean Text: {korean_text}
- Romanization: {romanization}
- English Text: {english_text}
- Basic Explanation: {basic_explanation}

Respond in English only. Focus on:
1) Why the correct answer is correct.
2) One common mistake to avoid.
3) One helpful tip for remembering or using it correctly.""",
    },
    "translate": {
        "system": "You are a Korean-to-English translator. Provide a natural, accurate English translation. Return ONLY the translation, no extra commentary.",
        "user": "Translate the following Korean text to English:\n\n{text}",
    },
    "conversation": {
        "system": """You are a friendly Korean language conversation partner.
Help the learner practice by having natural conversations.
Gently correct mistakes by rephrasing correctly in your response.
Keep your responses short (1-2 sentences) and appropriate for their level.
Use mostly Korean with occasional English clarifications for beginners.""",
        "user": """Learner Level: TOPIK Level {level}
Previous context: {context}

Learner says: {message}

Respond naturally in Korean. If they made mistakes, model the correct form in your response without explicitly pointing out errors.""",
    },
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
        5: "Advanced (TOPIK II Level 5-6)",
    }
    return level_names.get(level, "Unknown")
