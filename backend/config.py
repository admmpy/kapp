"""Environment configuration

This module loads and validates environment variables using python-dotenv.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = Path(__file__).parent
load_dotenv(basedir / ".env")


class Config:
    """Base configuration with default values"""

    # Flask configuration
    # SECRET_KEY must be set in .env - no default fallback for security
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Weak/placeholder keys that should be rejected
    WEAK_SECRET_KEYS = {
        'dev-secret-key-change-in-production',
        'your-secret-key-here-change-in-production',
        'your-generated-secret-key-here',
        'changeme',
        'secret',
        None,
        '',
    }
    
    # Database configuration
    # Handle both relative and absolute paths cross-platform
    db_url = os.getenv("DATABASE_URL", "sqlite:///data/kapp.db")

    # If it's a relative SQLite path, convert to absolute
    if db_url.startswith("sqlite:///") and not (
        db_url[10:11] in ("/", "\\") or db_url[11:12] == ":"
    ):
        # Relative path detected (sqlite:///data/... without drive letter)
        db_path = basedir / db_url.replace("sqlite:///", "")
        # Convert to absolute path with forward slashes for cross-platform compatibility
        DATABASE_URL = f"sqlite:///{db_path.as_posix()}"
    else:
        DATABASE_URL = db_url

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # TTS configuration
    TTS_CACHE_DIR = os.getenv("TTS_CACHE_DIR", "data/audio_cache")

    # LLM Configuration (OpenAI)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    LLM_CACHE_DIR = os.getenv("LLM_CACHE_DIR", "data/llm_cache")
    LLM_ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true"
    WEAK_OPENAI_KEYS = {
        None,
        "",
        "changeme",
        "your-openai-api-key-here",
        "your-openai-api-key",
    }

    # CORS configuration - Allow both common Vite ports by default
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174",
    ).split(",")

    # Rate limiting configuration
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "true").lower() == "true"
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200/day")
    RATELIMIT_LLM = os.getenv("RATELIMIT_LLM", "10/hour")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    # Feature flags
    GRAMMAR_MASTERY_ENABLED = os.getenv("GRAMMAR_MASTERY_ENABLED", "false").lower() == "true"
    WEAKNESS_REVIEW_ENABLED = os.getenv("WEAKNESS_REVIEW_ENABLED", "false").lower() == "true"
    SENTENCE_SRS_ENABLED = os.getenv("SENTENCE_SRS_ENABLED", "false").lower() == "true"
    IMMERSION_MODE_ENABLED = os.getenv("IMMERSION_MODE_ENABLED", "false").lower() == "true"

    @staticmethod
    def init_app(app):
        """Initialize app with configuration

        Args:
            app: Flask application instance
        """
        # Ensure required directories exist
        data_dir = Path(app.root_path) / "data"
        data_dir.mkdir(exist_ok=True)

        audio_cache_dir = Path(app.root_path) / app.config['TTS_CACHE_DIR']
        audio_cache_dir.mkdir(parents=True, exist_ok=True)

        # Ensure LLM cache directory exists
        llm_cache_dir = Path(app.root_path) / app.config["LLM_CACHE_DIR"]
        llm_cache_dir.mkdir(parents=True, exist_ok=True)

        # Validate SECRET_KEY in all environments
        secret_key = app.config.get('SECRET_KEY')
        if secret_key in Config.WEAK_SECRET_KEYS:
            raise ValueError(
                "SECRET_KEY is missing or weak! "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if len(secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters for security!")

        # Validate OpenAI API key when LLM is enabled
        if app.config.get("LLM_ENABLED", True):
            openai_key = app.config.get("OPENAI_API_KEY")
            if openai_key in Config.WEAK_OPENAI_KEYS:
                raise ValueError(
                    "OPENAI_API_KEY is missing or weak! "
                    "Set it in backend/.env as OPENAI_API_KEY=..."
                )


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
        # Base class already validates SECRET_KEY


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Use a fixed test key (only for testing)
    SECRET_KEY = 'test-secret-key-only-for-automated-testing-not-production'


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
