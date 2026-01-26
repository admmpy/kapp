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
    # Handle both relative and absolute paths cross-platform
    db_url = os.getenv('DATABASE_URL', 'sqlite:///data/kapp.db')
    
    # If it's a relative SQLite path, convert to absolute
    if db_url.startswith('sqlite:///') and not (db_url[10:11] in ('/', '\\') or db_url[11:12] == ':'):
        # Relative path detected (sqlite:///data/... without drive letter)
        db_path = basedir / db_url.replace('sqlite:///', '')
        # Convert to absolute path with forward slashes for cross-platform compatibility
        DATABASE_URL = f"sqlite:///{db_path.as_posix()}"
    else:
        DATABASE_URL = db_url
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # TTS configuration
    TTS_CACHE_DIR = os.getenv('TTS_CACHE_DIR', 'data/audio_cache')
    
    # LLM Configuration
    LLM_MODEL = os.getenv('LLM_MODEL', 'open-llama-2-ko-7b')
    LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'http://localhost:11434')
    LLM_CACHE_DIR = os.getenv('LLM_CACHE_DIR', 'data/llm_cache')
    LLM_ENABLED = os.getenv('LLM_ENABLED', 'true').lower() == 'true'
    
    # CORS configuration - Allow both common Vite ports by default
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174').split(',')

    # Rate limiting configuration
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '200/day')
    RATELIMIT_LLM = os.getenv('RATELIMIT_LLM', '10/hour')
    RATELIMIT_STORAGE_URI = os.getenv('RATELIMIT_STORAGE_URI', 'memory://')
    
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
        
        # Ensure LLM cache directory exists
        llm_cache_dir = Path(app.root_path) / app.config['LLM_CACHE_DIR']
        llm_cache_dir.mkdir(parents=True, exist_ok=True)
        
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
