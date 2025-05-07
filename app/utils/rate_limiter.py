"""
Rate limiting utilities for the application.
"""
from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps

# Initialize limiter
limiter = None

def init_limiter(app):
    """
    Initialize the rate limiter.
    
    Args:
        app: Flask application instance
    """
    global limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
        strategy="fixed-window"
    )
    
    # Register error handler for rate limit exceeded
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "error": "Rate limit exceeded",
            "message": str(e.description),
            "status_code": 429
        }), 429
    
    return limiter

def rate_limit(limit_value):
    """
    Decorator to apply rate limiting to a route.
    
    Args:
        limit_value: Rate limit string (e.g., "5 per minute")
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if limiter is None:
                return f(*args, **kwargs)
            
            # Apply rate limit
            limiter.limit(limit_value)(f)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Specific rate limits for different operations
api_rate_limit = "60 per minute"
upload_rate_limit = "10 per minute"
compliance_check_rate_limit = "20 per minute"
download_rate_limit = "30 per minute"
search_rate_limit = "30 per minute"
