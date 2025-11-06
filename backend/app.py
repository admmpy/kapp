"""Flask application factory

This module implements the application factory pattern for creating
and configuring the Flask application instance.
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from database import db, init_db


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
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Log startup
    app.logger.info(f"Kapp backend started in {config_name} mode")
    
    return app


def register_blueprints(app):
    """Register Flask blueprints for routes
    
    Args:
        app: Flask application instance
    """
    from routes.cards import cards_bp
    from routes.reviews import reviews_bp
    from routes.stats import stats_bp
    from routes.audio import audio_bp
    
    # Register blueprints with /api prefix
    app.register_blueprint(cards_bp, url_prefix='/api')
    app.register_blueprint(reviews_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/api')
    app.register_blueprint(audio_bp, url_prefix='/api')
    
    # Register debug blueprint (development only)
    if app.config.get('DEBUG', False) or app.config.get('TESTING', False):
        from routes.debug import debug_bp
        app.register_blueprint(debug_bp, url_prefix='/api')
        app.logger.info("Debug endpoints enabled at /api/debug/*")
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({
            'status': 'ok',
            'service': 'kapp-backend',
            'version': '0.1.0'
        })


def register_error_handlers(app):
    """Register error handlers for common HTTP errors
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        return jsonify({
            'error': 'Resource not found',
            'status': 404
        }), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        return jsonify({
            'error': 'Bad request',
            'message': str(error),
            'status': 400
        }), 400
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error"""
        app.logger.error(f"Internal error: {error}")
        return jsonify({
            'error': 'Internal server error',
            'status': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions"""
        app.logger.error(f"Unhandled exception: {error}", exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred',
            'status': 500
        }), 500


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('FLASK_RUN_PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
