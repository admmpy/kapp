"""Debug endpoints for TTS troubleshooting (development only)

This blueprint provides diagnostic tools for monitoring and debugging
the text-to-speech service and audio cache.

Endpoints:
- GET /api/debug/tts-status - Check TTS service health
- GET /api/debug/audio-cache - View cache statistics
- POST /api/debug/regenerate-audio/:card_id - Force regenerate audio for specific card
- GET /api/debug/test-audio - Test gTTS API connectivity
"""
from flask import Blueprint, jsonify, current_app, request
from database import db
from models_v2 import VocabularyItem
from tts_service import get_tts_service
from gtts import gTTS
from pathlib import Path
from utils import error_response, not_found_response
import os

debug_bp = Blueprint("debug", __name__)


@debug_bp.route("/debug/tts-status", methods=["GET"])
def tts_status():
    """Check TTS service health and cache statistics

    Returns:
        JSON with TTS service status and cache information
    """
    try:
        tts = get_tts_service(current_app.config["TTS_CACHE_DIR"])
        cache_stats = tts.get_cache_size()

        return jsonify(
            {
                "status": "ok",
                "cache_directory": str(tts.cache_dir),
                "cache_exists": tts.cache_dir.exists(),
                "cache_writable": os.access(tts.cache_dir, os.W_OK),
                "file_count": cache_stats["file_count"],
                "total_size_mb": cache_stats["total_size_mb"],
                "total_size_bytes": cache_stats["total_size_bytes"],
            }
        )
    except Exception as e:
        current_app.logger.error(f"Error checking TTS status: {e}", exc_info=True)
        return error_response("Failed to check TTS status", 500, str(e))


@debug_bp.route("/debug/audio-cache", methods=["GET"])
def audio_cache_details():
    """Get detailed audio cache information

    Query parameters:
        limit: Maximum number of files to list (default 50)

    Returns:
        JSON with detailed cache file information
    """
    try:
        limit = request.args.get("limit", default=50, type=int)
        tts = get_tts_service(current_app.config["TTS_CACHE_DIR"])

        # Get all audio files
        files = list(tts.cache_dir.glob("*.mp3"))
        files.sort(
            key=lambda f: f.stat().st_mtime, reverse=True
        )  # Sort by modification time

        # Build file list with details
        file_list = []
        for f in files[:limit]:
            stat = f.stat()
            file_list.append(
                {
                    "filename": f.name,
                    "size_kb": round(stat.st_size / 1024, 2),
                    "modified": stat.st_mtime,
                    "url": f"/api/audio/{f.name}",
                }
            )

        cache_stats = tts.get_cache_size()

        return jsonify(
            {
                "cache_directory": str(tts.cache_dir),
                "total_files": cache_stats["file_count"],
                "total_size_mb": cache_stats["total_size_mb"],
                "files_shown": len(file_list),
                "files": file_list,
            }
        )
    except Exception as e:
        current_app.logger.error(f"Error getting cache details: {e}", exc_info=True)
        return error_response("Failed to get cache details", 500, str(e))


@debug_bp.route("/debug/regenerate-audio/<int:vocab_id>", methods=["POST"])
def regenerate_audio(vocab_id):
    """Force regenerate audio for a specific vocabulary item

    Args:
        vocab_id: Vocabulary item ID to regenerate audio for

    Returns:
        JSON with regeneration result
    """
    try:
        # Get vocabulary item
        vocab = db.session.get(VocabularyItem, vocab_id)
        if not vocab:
            return not_found_response("Vocabulary item")

        # Get TTS service
        tts = get_tts_service(current_app.config["TTS_CACHE_DIR"])

        # Generate cache key and remove old file if exists
        slow = vocab.difficulty_level <= 1
        cache_key = tts._generate_cache_key(vocab.korean, "ko", slow)
        cache_path = tts._get_cache_path(cache_key)

        old_file_existed = cache_path.exists()
        if old_file_existed:
            cache_path.unlink()
            current_app.logger.info(f"Deleted old audio file: {cache_key}.mp3")

        # Generate new audio
        audio_filename = tts.generate_audio(
            text=vocab.korean, lang="ko", slow=slow
        )

        if audio_filename:
            return jsonify(
                {
                    "success": True,
                    "vocab_id": vocab_id,
                    "korean_text": vocab.korean,
                    "old_file_existed": old_file_existed,
                    "audio_filename": audio_filename,
                    "audio_url": tts.get_audio_url(audio_filename),
                    "slow_speed": slow,
                }
            )
        else:
            return error_response("Failed to generate audio", 500)

    except Exception as e:
        current_app.logger.error(
            f"Error regenerating audio for card {card_id}: {e}", exc_info=True
        )
        return error_response("Failed to regenerate audio", 500, str(e))


@debug_bp.route("/debug/test-audio", methods=["GET"])
def test_audio():
    """Test gTTS API connectivity with a simple Korean phrase

    Returns:
        JSON with test result
    """
    try:
        # Test with a simple Korean phrase
        test_text = "안녕하세요"
        tts = get_tts_service(current_app.config["TTS_CACHE_DIR"])

        current_app.logger.info(f"Testing gTTS API with: {test_text}")

        # Generate audio (will use cache if available)
        audio_filename = tts.generate_audio(text=test_text, lang="ko", slow=False)

        if audio_filename:
            return jsonify(
                {
                    "success": True,
                    "test_text": test_text,
                    "audio_filename": audio_filename,
                    "audio_url": tts.get_audio_url(audio_filename),
                    "message": "gTTS API is working correctly",
                }
            )
        else:
            return error_response(
                "Failed to generate test audio", 500, "gTTS API may be unreachable"
            )

    except Exception as e:
        current_app.logger.error(f"Error testing gTTS API: {e}", exc_info=True)
        return error_response("gTTS API test failed", 500, str(e))


@debug_bp.route("/debug/clear-cache", methods=["POST"])
def clear_cache():
    """Clear audio cache

    Query parameters:
        older_than_days: Only delete files older than this many days (optional)

    Returns:
        JSON with clear result
    """
    try:
        older_than_days = request.args.get("older_than_days", type=int)

        tts = get_tts_service(current_app.config["TTS_CACHE_DIR"])
        deleted_count = tts.clear_cache(older_than_days=older_than_days)

        return jsonify(
            {
                "success": True,
                "deleted_count": deleted_count,
                "older_than_days": older_than_days,
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error clearing cache: {e}", exc_info=True)
        return error_response("Failed to clear cache", 500, str(e))
