"""Audio file serving endpoints

This blueprint handles serving TTS-generated audio files.

Endpoints:
- GET /api/audio/:filename - Serve audio file from cache
"""
from flask import Blueprint, send_from_directory, current_app, abort
from pathlib import Path
import os

audio_bp = Blueprint('audio', __name__)


@audio_bp.route('/audio/<path:filename>', methods=['GET'])
def serve_audio(filename):
    """Serve audio file from cache
    
    Args:
        filename: Audio filename (e.g., 'abc123.mp3')
    
    Returns:
        Audio file with proper headers
    """
    try:
        # Validate filename (security: prevent directory traversal)
        if '..' in filename or filename.startswith('/'):
            current_app.logger.warning(f"Invalid filename attempt: {filename}")
            abort(400, description="Invalid filename")
        
        # Ensure .mp3 extension
        if not filename.endswith('.mp3'):
            abort(400, description="Invalid file type")
        
        # Get audio cache directory
        audio_dir = Path(current_app.root_path) / current_app.config['TTS_CACHE_DIR']
        
        # Check if file exists
        file_path = audio_dir / filename
        if not file_path.exists():
            current_app.logger.warning(f"Audio file not found: {filename}")
            abort(404, description="Audio file not found")
        
        # Serve file with caching headers
        response = send_from_directory(
            audio_dir,
            filename,
            mimetype='audio/mpeg'
        )
        
        # Add caching headers (cache for 7 days)
        response.headers['Cache-Control'] = 'public, max-age=604800'
        
        return response
    
    except Exception as e:
        current_app.logger.error(f"Error serving audio file {filename}: {e}", exc_info=True)
        abort(500, description="Failed to serve audio file")
