"""Environment configuration

This module loads and validates environment variables using python-dotenv.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = Path(__file__).parent
load_dotenv(basedir / '.env')


class Config:
    """Base configuration with default values"""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/korean_learning.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # TTS configuration
    TTS_CACHE_DIR = os.getenv('TTS_CACHE_DIR', 'data/audio_cache')
    
    # CORS configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
    
    @staticmethod
    def init_app(app):
        """Initialize app with configuration
        
        Args:
            app: Flask application instance
        """
        # Ensure required directories exist
        data_dir = Path(app.root_path) / 'data'
        data_dir.mkdir(exist_ok=True)
        
        audio_cache_dir = Path(app.root_path) / app.config['TTS_CACHE_DIR']
        audio_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate required configuration
        required_vars = ['SECRET_KEY', 'DATABASE_URL']
        missing = [var for var in required_vars if not app.config.get(var)]
        
        if missing and app.config.get('ENV') == 'production':
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific setup
        if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
            raise ValueError("Must set SECRET_KEY in production!")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
