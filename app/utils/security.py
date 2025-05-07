"""
Security utilities for the application.
"""
from flask import request, abort
from flask_wtf.csrf import CSRFProtect
import re
import bleach
from functools import wraps

# Initialize CSRF protection
csrf = CSRFProtect()

# Export csrf for use in other modules
__all__ = ['csrf', 'init_security', 'sanitize_input', 'validate_id', 'require_api_key']

def init_security(app):
    """
    Initialize security features for the application.
    
    Args:
        app: Flask application instance
    """
    # Enable CSRF protection
    csrf.init_app(app)
    
    # Exempt API routes from CSRF protection
    csrf.exempt("api_bp")
    
    # Set secure headers
    @app.after_request
    def set_secure_headers(response):
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self';"
        )
        
        # Other security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Remove Server header
        response.headers.pop('Server', None)
        
        return response
    
    return csrf

def sanitize_input(text):
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if text is None:
        return None
    
    # Define allowed tags and attributes
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'span']
    allowed_attrs = {
        '*': ['class', 'style'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
    }
    
    # Clean the text
    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

def validate_id(id_string):
    """
    Validate that an ID is safe to use in database queries.
    
    Args:
        id_string: ID string to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation for MongoDB ObjectId or UUID
    return bool(re.match(r'^[a-zA-Z0-9\-_]{3,64}$', str(id_string)))

def require_api_key(f):
    """
    Decorator to require an API key for a route.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import current_app
        
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != current_app.config.get('API_KEY'):
            abort(401, description="Invalid API key")
        
        return f(*args, **kwargs)
    
    return decorated
