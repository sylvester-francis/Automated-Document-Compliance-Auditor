"""
Form validation utilities for the application.
"""
import re
from functools import wraps
from flask import request, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from app.utils.error_handler import ValidationError

def validate_document_upload(f):
    """Decorator to validate document uploads."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            # Check if the post request has the file part
            if 'document' not in request.files:
                flash('No file part', 'error')
                return redirect(request.url)
            
            file = request.files['document']
            
            # If user does not select file, browser submits an empty file
            if file.filename == '':
                flash('No selected file', 'error')
                return redirect(request.url)
            
            # Check file extension
            allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'docx', 'doc', 'txt'})
            if not allowed_file(file.filename, allowed_extensions):
                flash(f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}', 'error')
                return redirect(request.url)
            
            # Check file size
            max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # Default 16MB
            if file.content_length and file.content_length > max_size:
                flash(f'File too large. Maximum size: {max_size / (1024 * 1024):.1f}MB', 'error')
                return redirect(request.url)
            
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename, allowed_extensions=None):
    """Check if a file has an allowed extension."""
    if allowed_extensions is None:
        allowed_extensions = {'pdf', 'docx', 'doc', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def sanitize_input(text):
    """Sanitize user input to prevent XSS attacks."""
    if text is None:
        return None
    # Remove potentially dangerous HTML tags
    sanitized = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
    sanitized = re.sub(r'<.*?>', '', sanitized)
    return sanitized

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present in the data."""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    return True
