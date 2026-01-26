"""Flask extensions

Shared extension instances to avoid circular imports.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate limiter instance - initialized in app.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],  # No default limits - apply explicitly per route
    storage_uri="memory://",
)
