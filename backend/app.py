"""Flask application factory

This module implements the application factory pattern for creating
and configuring the Flask application instance.
"""
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from database import db, init_db
from extensions import limiter


def create_app(config_name=None):
    """Application factory for creating Flask app instances

    Args:
        config_name: Configuration name ('development', 'production', 'testing')
                    If None, uses FLASK_ENV environment variable or 'development'

    Returns:
        Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    # Support multiple origins for development (5173, 5174, etc.)
    app.logger.debug(f"CORS_ORIGINS = {app.config['CORS_ORIGINS']}")
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    db.init_app(app)

    # Initialize rate limiter
    if app.config.get("RATELIMIT_ENABLED", True):
        limiter.init_app(app)
        app.logger.info("Rate limiting enabled")

    # Create database tables
    with app.app_context():
        import models_v2  # noqa: F401 - Import to register models with SQLAlchemy
        db.create_all()

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Configure logging to suppress TLS handshake errors
    # These occur when clients try HTTPS on an HTTP server (harmless)
    class TLSFilter(logging.Filter):
        def filter(self, record):
            message = str(record.getMessage())
            # Filter out TLS handshake attempts (clients trying HTTPS on HTTP server)
            if "Bad request version" in message:
                # Check for TLS handshake indicators
                if (
                    "\\x16\\x03" in message
                    or "\\x16" in message
                    or "code 400" in message
                ):
                    return False
            return True

    # Apply filter to Werkzeug logger
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.addFilter(TLSFilter())

    # Also filter Python's http.server logs if present
    http_logger = logging.getLogger("http.server")
    http_logger.addFilter(TLSFilter())

    # Log startup
    app.logger.info(f"Kapp backend started in {config_name} mode")

    return app


def register_blueprints(app):
    """Register Flask blueprints for routes

    Args:
        app: Flask application instance
    """
    # Lesson-based routes (v2.0)
    from routes.courses import courses_bp
    from routes.lessons import lessons_bp
    from routes.progress import progress_bp
    from routes.vocabulary import vocabulary_bp

    # Shared routes (kept from v1)
    from routes.audio import audio_bp
    from routes.llm import llm_bp

    # Register lesson-based blueprints with /api prefix
    app.register_blueprint(courses_bp, url_prefix="/api")
    app.register_blueprint(lessons_bp, url_prefix="/api")
    app.register_blueprint(progress_bp, url_prefix="/api")
    app.register_blueprint(vocabulary_bp, url_prefix="/api")

    # Weakness review routes (feature-flagged)
    from routes.weakness import weakness_bp
    app.register_blueprint(weakness_bp, url_prefix="/api")

    # Exercise SRS review routes (feature-flagged)
    from routes.exercise_review import exercise_review_bp
    app.register_blueprint(exercise_review_bp, url_prefix="/api")

    # Register shared blueprints
    app.register_blueprint(audio_bp, url_prefix="/api")
    app.register_blueprint(llm_bp, url_prefix="/api")

    # Register debug blueprint (development only)
    if app.config.get("DEBUG", False) or app.config.get("TESTING", False):
        from routes.debug import debug_bp

        app.register_blueprint(debug_bp, url_prefix="/api")
        app.logger.info("Debug endpoints enabled at /api/debug/*")

    # Root endpoint - API information
    @app.route("/")
    def root():
        """Root endpoint providing API information"""
        return jsonify(
            {
                "service": "kapp-backend",
                "version": "2.0.0",
                "status": "running",
                "api_base": "/api",
                "endpoints": {
                    "health": "/api/health",
                    "courses": "/api/courses",
                    "lessons": "/api/lessons",
                    "progress": "/api/progress",
                    "vocabulary": "/api/vocabulary",
                    "audio": "/api/audio",
                    "llm": "/api/llm",
                },
            }
        )

    # Health check endpoint
    @app.route("/api/health")
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({"status": "ok", "service": "kapp-backend", "version": "2.0.0"})


def register_error_handlers(app):
    """Register error handlers for common HTTP errors

    Args:
        app: Flask application instance
    """

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        return jsonify({"error": "Resource not found", "status": 404}), 404

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        return (
            jsonify({"error": "Bad request", "message": str(error), "status": 400}),
            400,
        )

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error"""
        app.logger.error(f"Internal error: {error}")
        return jsonify({"error": "Internal server error", "status": 500}), 500

    @app.errorhandler(429)
    def ratelimit_handler(error):
        """Handle 429 Too Many Requests errors"""
        return (
            jsonify(
                {
                    "error": "Rate limit exceeded",
                    "message": str(error.description),
                    "status": 429,
                }
            ),
            429,
        )

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions"""
        app.logger.error(f"Unhandled exception: {error}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred", "status": 500}), 500


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("FLASK_RUN_PORT", 5001))
    app.run(debug=True, host="127.0.0.1", port=port)
