"""
User settings routes

Endpoints:
- GET /api/settings - Get current user settings
- PUT /api/settings - Update user settings
"""
from flask import Blueprint, request, jsonify, current_app
from database import db
from models_v2 import UserSettings
from utils import error_response, validation_error_response
from routes.helpers import get_current_user_id
import logging

logger = logging.getLogger(__name__)

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings", methods=["GET"])
def get_settings():
    """Get current user settings, creating defaults if not exists."""
    if not current_app.config.get("IMMERSION_MODE_ENABLED"):
        return jsonify({"immersion_level": 1}), 200

    try:
        user_id = get_current_user_id()
        settings = db.session.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()

        if not settings:
            settings = UserSettings(user_id=user_id, immersion_level=1)
            db.session.add(settings)
            db.session.commit()

        return jsonify({"immersion_level": settings.immersion_level}), 200

    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        db.session.rollback()
        return error_response("Failed to get settings", 500)


@settings_bp.route("/settings", methods=["PUT"])
def update_settings():
    """Update user settings."""
    if not current_app.config.get("IMMERSION_MODE_ENABLED"):
        return error_response("Immersion mode is not enabled", 403)

    try:
        data = request.get_json()
        if not data:
            return validation_error_response("Request body required")

        immersion_level = data.get("immersion_level")
        if immersion_level is None:
            return validation_error_response("immersion_level is required")

        if not isinstance(immersion_level, int) or immersion_level not in (1, 2, 3):
            return validation_error_response("immersion_level must be 1, 2, or 3")

        user_id = get_current_user_id()
        settings = db.session.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()

        if not settings:
            settings = UserSettings(user_id=user_id, immersion_level=immersion_level)
            db.session.add(settings)
        else:
            settings.immersion_level = immersion_level

        db.session.commit()

        return jsonify({"immersion_level": settings.immersion_level}), 200

    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        db.session.rollback()
        return error_response("Failed to update settings", 500)
