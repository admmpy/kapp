"""Audio file serving endpoints

This blueprint handles serving TTS-generated audio files.

Endpoints:
- GET /api/audio/:filename - Serve audio file from cache

TODO: Implement GET /api/audio/:filename endpoint
TODO: Use Flask's send_from_directory for file serving
TODO: Set proper MIME type (audio/mpeg)
TODO: Add caching headers (Cache-Control)
TODO: Handle file not found errors (404)
"""
