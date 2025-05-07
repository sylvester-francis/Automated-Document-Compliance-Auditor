"""
Centralized error handling for the application.
"""
import logging
import traceback
from functools import wraps
from flask import flash, jsonify, request

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base exception class for application errors."""
    def __init__(self, message, status_code=500, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        rv['code'] = self.status_code
        return rv

def handle_error(error):
    """Convert exceptions to appropriate responses."""
    # Log the error
    logger.error(f"Error: {str(error)}")
    logger.error(traceback.format_exc())
    
    # If it's our custom error
    if isinstance(error, AppError):
        if request.headers.get('HX-Request'):
            # For HTMX requests, return error message that can be inserted into DOM
            return f'<div class="alert alert-danger">{error.message}</div>', error.status_code
        elif request.is_json or request.headers.get('Accept') == 'application/json':
            # For API requests
            return jsonify(error.to_dict()), error.status_code
        else:
            # For normal requests, flash and redirect to a safe page
            flash(error.message, 'error')
            
            # If it's a NotFoundError, redirect to home page
            if isinstance(error, NotFoundError):
                from flask import redirect, url_for
                return redirect(url_for('main.index'))
                
            return error.message, error.status_code
    
    # For standard exceptions
    message = str(error) or "An unexpected error occurred"
    if request.headers.get('HX-Request'):
        return f'<div class="alert alert-danger">{message}</div>', 500
    elif request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({'status': 'error', 'message': message}), 500
    else:
        flash(message, 'error')
        return message, 500

def error_handler(f):
    """Decorator to handle exceptions in routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return handle_error(e)
    return decorated_function

# Common error classes
class NotFoundError(AppError):
    """Resource not found error."""
    def __init__(self, message="Resource not found", payload=None):
        super().__init__(message, 404, payload)

class ValidationError(AppError):
    """Validation error."""
    def __init__(self, message="Validation error", payload=None):
        super().__init__(message, 400, payload)

class AuthorizationError(AppError):
    """Authorization error."""
    def __init__(self, message="Not authorized", payload=None):
        super().__init__(message, 403, payload)
