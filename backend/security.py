"""
Security utilities for input validation and sanitization

This module provides functions to protect against prompt injection attacks
and validate user input before it reaches the LLM.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Maximum allowed lengths for user inputs
MAX_MESSAGE_LENGTH = 500
MAX_HISTORY_EXCHANGES = 5
MAX_HISTORY_MESSAGE_LENGTH = 300

# Patterns that indicate potential prompt injection attempts
INJECTION_PATTERNS = [
    r'ignore\s+(all\s+)?previous\s+instructions?',
    r'ignore\s+(all\s+)?above\s+instructions?',
    r'disregard\s+(all\s+)?previous',
    r'forget\s+(all\s+)?previous',
    r'new\s+instructions?:',
    r'system\s*:\s*',
    r'assistant\s*:\s*',
    r'human\s*:\s*',
    r'\[system\]',
    r'\[assistant\]',
    r'\[human\]',
    r'<\s*system\s*>',
    r'<\s*assistant\s*>',
    r'<\s*human\s*>',
    r'you\s+are\s+now\s+',
    r'act\s+as\s+(if\s+you\s+are\s+)?',
    r'pretend\s+(to\s+be|you\s+are)',
    r'roleplay\s+as',
    r'jailbreak',
    r'bypass\s+(your\s+)?restrictions?',
    r'override\s+(your\s+)?instructions?',
]

# Compile patterns for efficiency
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def sanitize_user_input(
    text: str,
    max_length: int = MAX_MESSAGE_LENGTH,
    check_injection: bool = True
) -> tuple[str, list[str]]:
    """
    Sanitize user input text for safe use in LLM prompts.

    Args:
        text: The user input to sanitize
        max_length: Maximum allowed length (default 500)
        check_injection: Whether to check for injection patterns

    Returns:
        Tuple of (sanitized_text, list of warnings)
    """
    warnings = []

    if not text:
        return '', []

    # Ensure it's a string
    if not isinstance(text, str):
        text = str(text)

    # Strip whitespace
    text = text.strip()

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
        warnings.append(f'Input truncated to {max_length} characters')

    # Check for injection patterns
    if check_injection:
        for pattern in COMPILED_PATTERNS:
            if pattern.search(text):
                # Log the attempt but don't expose details to user
                logger.warning(f'Potential prompt injection detected: pattern matched')
                warnings.append('Input contains potentially harmful patterns')
                # Replace the matched pattern with [FILTERED]
                text = pattern.sub('[FILTERED]', text)

    # Remove control characters except newlines and tabs
    text = ''.join(
        char for char in text
        if char == '\n' or char == '\t' or (ord(char) >= 32 and ord(char) != 127)
    )

    return text, warnings


def validate_conversation_history(
    history: list,
    max_exchanges: int = MAX_HISTORY_EXCHANGES,
    max_message_length: int = MAX_HISTORY_MESSAGE_LENGTH
) -> tuple[list, list[str]]:
    """
    Validate and sanitize conversation history from client.

    Args:
        history: List of conversation exchanges from client
        max_exchanges: Maximum number of exchanges to keep
        max_message_length: Maximum length per message

    Returns:
        Tuple of (validated_history, list of warnings)
    """
    warnings = []

    if not history:
        return [], []

    if not isinstance(history, list):
        logger.warning('Conversation history is not a list')
        return [], ['Invalid history format']

    validated = []

    # Only keep the most recent exchanges
    recent_history = history[-max_exchanges:]
    if len(history) > max_exchanges:
        warnings.append(f'History truncated to last {max_exchanges} exchanges')

    for i, exchange in enumerate(recent_history):
        if not isinstance(exchange, dict):
            warnings.append(f'Skipping invalid exchange at position {i}')
            continue

        validated_exchange = {}

        # Validate 'user' field
        user_msg = exchange.get('user', '')
        if user_msg:
            sanitized, msg_warnings = sanitize_user_input(
                user_msg,
                max_length=max_message_length,
                check_injection=True
            )
            validated_exchange['user'] = sanitized
            warnings.extend(msg_warnings)

        # Validate 'assistant' field
        assistant_msg = exchange.get('assistant', '')
        if assistant_msg:
            # Assistant messages should be trusted but still length-limited
            if isinstance(assistant_msg, str):
                validated_exchange['assistant'] = assistant_msg[:max_message_length]
            else:
                validated_exchange['assistant'] = str(assistant_msg)[:max_message_length]

        if validated_exchange:
            validated.append(validated_exchange)

    return validated, warnings


def is_safe_input(text: str) -> bool:
    """
    Quick check if input appears safe (no injection patterns detected).

    Args:
        text: The text to check

    Returns:
        True if no injection patterns found, False otherwise
    """
    if not text or not isinstance(text, str):
        return True

    for pattern in COMPILED_PATTERNS:
        if pattern.search(text):
            return False

    return True
