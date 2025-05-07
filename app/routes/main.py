from flask import Blueprint, render_template, current_app
from datetime import datetime

# Create the Blueprint first, before defining any routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page."""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@main_bp.route('/debug')
def debug():
    """Debug page."""
    return render_template('compliance/debug.html', config=current_app.config, now=datetime.now)

@main_bp.route('/test-claude')
def test_claude():
    """Test Claude integration."""
    try:
        from app.services.llm_service import generate_suggestion
        
        # Create a dummy document and issue
        document = {
            "_id": "test-doc",
            "paragraphs": [
                {"id": "test-para", "text": "This is a test paragraph for compliance checking."}
            ]
        }
        
        issue = {
            "issue_id": "test-issue",
            "paragraph_id": "test-para",
            "description": "Document must include information about the right to access personal data",
            "compliance_type": "GDPR"
        }
        
        print("Testing Claude API integration...")
        suggestion = generate_suggestion(document, issue)
        print(f"Received suggestion: {suggestion[:50]}...")
        
        return f"""
        <div class="alert alert-success">
            <p><strong>Claude integration working!</strong></p>
            <p>Suggestion: {suggestion}</p>
        </div>
        """
    except Exception as e:
        print(f"Error testing Claude API: {str(e)}")
        return f"""
        <div class="alert alert-danger">
            <p><strong>Error testing Claude API:</strong></p>
            <p>{str(e)}</p>
        </div>
        """