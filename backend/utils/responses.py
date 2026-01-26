"""Standardized API response helpers

Provides consistent response formatting across all API endpoints.
"""
from typing import Any, Optional
from flask import jsonify


def error_response(message: str, status_code: int = 400, details: Optional[str] = None) -> tuple:
    """Create a standardized error response

    Args:
        message: Error message to display
        status_code: HTTP status code (default 400)
        details: Optional additional details about the error

    Returns:
        Tuple of (JSON response, status code)
    """
    response = {
        'error': message,
        'status': status_code
    }
    if details:
        response['details'] = details
    return jsonify(response), status_code


def success_response(data: Any, status_code: int = 200) -> tuple:
    """Create a standardized success response

    Args:
        data: Response data (will be JSON serialized)
        status_code: HTTP status code (default 200)

    Returns:
        Tuple of (JSON response, status code)
    """
    return jsonify(data), status_code


def not_found_response(resource: str = 'Resource') -> tuple:
    """Create a standardized 404 not found response

    Args:
        resource: Name of the resource that wasn't found

    Returns:
        Tuple of (JSON response, 404)
    """
    return error_response(f'{resource} not found', 404)


def validation_error_response(message: str) -> tuple:
    """Create a standardized validation error response

    Args:
        message: Validation error message

    Returns:
        Tuple of (JSON response, 400)
    """
    return error_response(message, 400)
