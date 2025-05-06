# app/routes/compliance.py
from flask import Blueprint, render_template, request, jsonify, current_app
from app.services.rule_engine import check_document_compliance
from app.services.llm_service import generate_suggestion

compliance_bp = Blueprint('compliance', __name__, url_prefix='/compliance')

@compliance_bp.route('/check/<document_id>', methods=['GET', 'POST'])
def check_document(document_id):
    """Check document compliance."""
    from app.extensions import mongo
    document = mongo.db.documents.find_one({'_id': document_id})
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Get compliance types from query params or use defaults
    compliance_types = request.args.getlist('type') or current_app.config['DEFAULT_COMPLIANCE_TYPES']
    
    # Check compliance
    results = check_document_compliance(document, compliance_types)
    
    # Get the updated document with compliance issues
    document = mongo.db.documents.find_one({'_id': document_id})
    
    if request.headers.get('HX-Request'):
        # If it's an HTMX request, return just the results partial
        return render_template('compliance/results_partial.html', results=results, document=document)
    
    # Otherwise return the full page
    return render_template('compliance/results.html', results=results, document=document)

@compliance_bp.route('/suggest/<document_id>/<issue_id>', methods=['GET'])
def get_suggestion(document_id, issue_id):
    """Get AI suggestion for fixing a compliance issue."""
    from app.extensions import mongo
    document = mongo.db.documents.find_one({'_id': document_id})
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Find the specific issue
    issue = next((i for i in document.get('compliance_issues', []) if i['issue_id'] == issue_id), None)
    if not issue:
        return jsonify({'error': 'Issue not found'}), 404
    
    # Generate suggestion
    suggestion = generate_suggestion(document, issue)
    
    # Update issue with suggestion
    if suggestion and suggestion not in issue.get('suggestions', []):
        mongo.db.documents.update_one(
            {"_id": document_id, "compliance_issues.issue_id": issue_id},
            {"$addToSet": {"compliance_issues.$.suggestions": suggestion}}
        )
    
    if request.headers.get('HX-Request'):
        # If it's an HTMX request, return just the suggestion partial
        return render_template('compliance/suggestion_partial.html', suggestion=suggestion)
    
    # Otherwise return JSON
    return jsonify({'suggestion': suggestion})