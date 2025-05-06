from flask import Blueprint, render_template, request, jsonify
from app.services.rule_engine import check_compliance

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
    results = check_compliance(document, compliance_types)
    
    if request.headers.get('HX-Request'):
        # If it's an HTMX request, return just the results partial
        return render_template('compliance/results_partial.html', results=results, document=document)
    
    # Otherwise return the full page
    return render_template('compliance/results.html', results=results, document=document)