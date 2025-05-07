"""
API routes for the application.
"""
from flask import Blueprint, request, jsonify, send_file
from bson.json_util import dumps
import json

from app.utils.error_handler import error_handler, AppError, NotFoundError
from app.utils.security import require_api_key, validate_id
from app.utils.rate_limiter import api_rate_limit, rate_limit
from app.utils.pdf_export import generate_compliance_pdf, generate_document_pdf

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/documents', methods=['GET'])
@require_api_key
@rate_limit(api_rate_limit)
@error_handler
def list_documents_api():
    """List all documents (API endpoint)."""
    from app.extensions import mongo
    from app.utils.pagination import get_pagination
    
    # Get filter parameters
    search_query = request.args.get('q', '')
    document_type = request.args.get('type', '')
    sort_by = request.args.get('sort', 'created_at')
    sort_dir = -1 if request.args.get('order', 'desc') == 'desc' else 1
    per_page = int(request.args.get('per_page', 10))
    
    # Build query
    query = {}
    if search_query:
        query['$or'] = [
            {'filename': {'$regex': search_query, '$options': 'i'}},
            {'content': {'$regex': search_query, '$options': 'i'}}
        ]
    if document_type:
        query['document_type'] = document_type
    
    # Get paginated documents
    documents, pagination = get_pagination(
        mongo.db.documents, 
        query=query, 
        per_page=per_page,
        sort_by=sort_by,
        sort_direction=sort_dir
    )
    
    # Convert documents to JSON
    result = {
        'documents': json.loads(dumps(documents)),
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total_count,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }
    
    return jsonify(result)

@api_bp.route('/documents/<document_id>', methods=['GET'])
@require_api_key
@rate_limit(api_rate_limit)
@error_handler
def get_document_api(document_id):
    """Get a document by ID (API endpoint)."""
    from app.extensions import mongo
    
    if not validate_id(document_id):
        raise AppError('Invalid document ID format', status_code=400)
    
    document = mongo.db.documents.find_one({'_id': document_id})
    if not document:
        raise NotFoundError(f'Document with ID {document_id} not found')
    
    # Convert document to JSON
    return json.loads(dumps(document))

@api_bp.route('/documents/<document_id>/compliance', methods=['GET'])
@require_api_key
@rate_limit(api_rate_limit)
@error_handler
def get_document_compliance_api(document_id):
    """Get compliance information for a document (API endpoint)."""
    from app.extensions import mongo
    
    if not validate_id(document_id):
        raise AppError('Invalid document ID format', status_code=400)
    
    document = mongo.db.documents.find_one({'_id': document_id})
    if not document:
        raise NotFoundError(f'Document with ID {document_id} not found')
    
    # Extract compliance information
    compliance_info = {
        'document_id': document_id,
        'filename': document.get('filename', ''),
        'compliance_score': document.get('compliance_score', 0),
        'compliance_status': document.get('compliance_status', 'pending_review'),
        'compliance_issues': document.get('compliance_issues', []),
        'last_checked': document.get('updated_at', None)
    }
    
    # Convert to JSON
    return json.loads(dumps(compliance_info))

@api_bp.route('/documents/<document_id>/check', methods=['POST'])
@require_api_key
@rate_limit(api_rate_limit)
@error_handler
def check_document_compliance_api(document_id):
    """Check compliance for a document (API endpoint)."""
    from app.extensions import mongo
    from app.services.compliance_service import check_document_compliance
    
    if not validate_id(document_id):
        raise AppError('Invalid document ID format', status_code=400)
    
    document = mongo.db.documents.find_one({'_id': document_id})
    if not document:
        raise NotFoundError(f'Document with ID {document_id} not found')
    
    # Get compliance rules to check
    data = request.get_json() or {}
    rule_ids = data.get('rule_ids', [])
    
    # Check compliance
    compliance_results = check_document_compliance(document, rule_ids)
    
    # Return results
    return json.loads(dumps(compliance_results))

@api_bp.route('/documents/<document_id>/export/pdf', methods=['GET'])
@require_api_key
@rate_limit(api_rate_limit)
@error_handler
def export_document_pdf_api(document_id):
    """Export a document as PDF (API endpoint)."""
    from app.extensions import mongo
    
    if not validate_id(document_id):
        raise AppError('Invalid document ID format', status_code=400)
    
    document = mongo.db.documents.find_one({'_id': document_id})
    if not document:
        raise NotFoundError(f'Document with ID {document_id} not found')
    
    # Generate PDF
    pdf_path = generate_document_pdf(document)
    
    # Send file
    return send_file(
        pdf_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{document.get('filename', 'document')}.pdf"
    )

@api_bp.route('/documents/<document_id>/compliance/export/pdf', methods=['GET'])
@require_api_key
@rate_limit(api_rate_limit)
@error_handler
def export_compliance_pdf_api(document_id):
    """Export compliance report as PDF (API endpoint)."""
    from app.extensions import mongo
    
    if not validate_id(document_id):
        raise AppError('Invalid document ID format', status_code=400)
    
    document = mongo.db.documents.find_one({'_id': document_id})
    if not document:
        raise NotFoundError(f'Document with ID {document_id} not found')
    
    # Get compliance results
    compliance_results = {
        'compliance_score': document.get('compliance_score', 0),
        'compliance_status': document.get('compliance_status', 'pending_review'),
        'compliance_issues': document.get('compliance_issues', [])
    }
    
    # Generate PDF
    pdf_path = generate_compliance_pdf(document, compliance_results)
    
    # Send file
    return send_file(
        pdf_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{document.get('filename', 'document')}_compliance_report.pdf"
    )

@api_bp.route('/rules', methods=['GET'])
@require_api_key
@rate_limit(api_rate_limit)
@error_handler
def list_compliance_rules_api():
    """List all compliance rules (API endpoint)."""
    from app.extensions import mongo
    
    rules = list(mongo.db.compliance_rules.find())
    
    # Convert to JSON
    return json.loads(dumps(rules))

@api_bp.route('/stats', methods=['GET'])
@require_api_key
@rate_limit(api_rate_limit)
@error_handler
def get_stats_api():
    """Get application statistics (API endpoint)."""
    from app.extensions import mongo
    
    # Get document statistics
    total_documents = mongo.db.documents.count_documents({})
    compliant_documents = mongo.db.documents.count_documents({'compliance_score': {'$gte': 80}})
    non_compliant_documents = mongo.db.documents.count_documents({'compliance_score': {'$lt': 80, '$ne': None}})
    pending_documents = mongo.db.documents.count_documents({'compliance_status': 'pending_review'})
    
    # Get document types
    document_types = mongo.db.documents.distinct('document_type')
    type_counts = {}
    for doc_type in document_types:
        if doc_type:
            type_counts[doc_type] = mongo.db.documents.count_documents({'document_type': doc_type})
    
    # Compile statistics
    stats = {
        'documents': {
            'total': total_documents,
            'compliant': compliant_documents,
            'non_compliant': non_compliant_documents,
            'pending': pending_documents,
            'by_type': type_counts
        },
        'rules': {
            'total': mongo.db.compliance_rules.count_documents({})
        }
    }
    
    return jsonify(stats)
