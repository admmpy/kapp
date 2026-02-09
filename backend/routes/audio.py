"""Audio file serving endpoints

This blueprint handles serving TTS-generated audio files.

Endpoints:
- GET /api/audio/:filename - Serve audio file from cache
- POST /api/audio/generate - Generate TTS audio for text
"""
from flask import Blueprint, send_from_directory, current_app, abort, request, jsonify
from pathlib import Path
from extensions import limiter
from tts_service import get_tts_service
import os
import logging

logger = logging.getLogger(__name__)

audio_bp = Blueprint("audio", __name__)


@audio_bp.route("/audio/<path:filename>", methods=["GET"])
def serve_audio(filename):
    """Serve audio file from cache

    Args:
        filename: Audio filename (e.g., 'abc123.mp3')

    Returns:
        Audio file with proper headers
    """
    try:
        # Validate filename (security: prevent directory traversal)
        if ".." in filename or filename.startswith("/"):
            current_app.logger.warning(f"Invalid filename attempt: {filename}")
            abort(400, description="Invalid filename")

        # Ensure .mp3 extension
        if not filename.endswith(".mp3"):
            abort(400, description="Invalid file type")

        # Get audio cache directory
        audio_dir = Path(current_app.root_path) / current_app.config["TTS_CACHE_DIR"]

        # Check if file exists
        file_path = audio_dir / filename
        if not file_path.exists():
            current_app.logger.warning(f"Audio file not found: {filename}")
            abort(404, description="Audio file not found")

        # Serve file with caching headers
        response = send_from_directory(audio_dir, filename, mimetype="audio/mpeg")

        # Add caching headers (cache for 7 days)
        response.headers["Cache-Control"] = "public, max-age=604800"

        return response

    except Exception as e:
        current_app.logger.error(
            f"Error serving audio file {filename}: {e}", exc_info=True
        )
        abort(500, description="Failed to serve audio file")


@audio_bp.route("/audio/generate", methods=["POST"])
@limiter.limit("30/hour")
def generate_audio():
    """Generate TTS audio for given text.

    Request body:
        { "text": "한국어 텍스트", "lang": "ko", "slow": false }

    Returns:
        { "filename": "<md5hash>.mp3" }
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "text is required"}), 400

    if len(text) > 500:
        return jsonify({"error": "text must be 500 characters or fewer"}), 400

    lang = data.get("lang", "ko")
    slow = bool(data.get("slow", False))

    try:
        tts = get_tts_service(
            cache_dir=current_app.config.get("TTS_CACHE_DIR", "data/audio_cache")
        )
        filename = tts.generate_audio(text, lang=lang, slow=slow)

        if not filename:
            return jsonify({"error": "Failed to generate audio"}), 500

        return jsonify({"filename": filename}), 200
    except Exception as e:
        logger.error(f"Error generating audio: {e}", exc_info=True)
        return jsonify({"error": "Failed to generate audio"}), 500
