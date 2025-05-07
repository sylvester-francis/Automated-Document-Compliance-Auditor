from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash, jsonify, session
from flask_wtf.csrf import CSRFProtect, validate_csrf
import os
from werkzeug.utils import secure_filename
from app.services.document_service import process_document
from app.utils.pagination import get_pagination
from app.utils.form_validation import validate_document_upload
from app.utils.error_handler import error_handler
from app.utils.cache import cache_document, invalidate_cache
from app.utils.security import csrf

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@documents_bp.route('/')
@error_handler
def list_documents():
    """List all documents with pagination."""
    from app.extensions import mongo
    
    try:
        # Get filter parameters
        search_query = request.args.get('q', '')
        document_type = request.args.get('type', '')
        sort_by = request.args.get('sort', 'created_at')
        sort_dir = -1 if request.args.get('order', 'desc') == 'desc' else 1
        
        # Debug filter parameters
        current_app.logger.info(f"Filter parameters: search={search_query}, type={document_type}, sort={sort_by}, order={'desc' if sort_dir == -1 else 'asc'}")
        
        # Safely convert per_page to integer
        try:
            per_page = int(request.args.get('per_page', 10))
        except (ValueError, TypeError):
            per_page = 10
        
        # Build query
        query = {}
        if search_query:
            query['$or'] = [
                {'filename': {'$regex': search_query, '$options': 'i'}},
                {'content': {'$regex': search_query, '$options': 'i'}}
            ]
        
        # Handle document type filtering
        if document_type:
            # Check if filtering by file format (pdf, docx, txt)
            if document_type in ['pdf', 'docx', 'txt']:
                # Try multiple fields where format info might be stored
                query['$or'] = query.get('$or', []) + [
                    {'file_format': document_type},
                    {'file_format': document_type.upper()},
                    {'document_type': document_type},
                    {'metadata.format': document_type},
                    {'metadata.file_format': document_type}
                ]
                current_app.logger.info(f"Filtering by file format: {document_type}")
            else:
                # Regular document type filtering
                query['document_type'] = document_type
                current_app.logger.info(f"Filtering by document type: {document_type}")
        
        # Get paginated documents
        documents, pagination = get_pagination(
            mongo.db.documents, 
            query=query, 
            per_page=per_page,
            sort_by=sort_by,
            sort_direction=sort_dir
        )
        
        # Process documents to ensure they have all required fields
        processed_documents = []
        for doc in documents:
            # Ensure metadata exists
            if 'metadata' not in doc or not doc['metadata']:
                doc['metadata'] = {}
                
            # Ensure basic fields exist
            if 'filename' not in doc:
                doc['filename'] = 'Unnamed Document'
                
            if 'document_type' not in doc or not doc['document_type']:
                doc['document_type'] = 'other'
                
            if 'compliance_score' not in doc or doc['compliance_score'] is None:
                doc['compliance_score'] = 0
                
            if 'compliance_status' not in doc or not doc['compliance_status']:
                doc['compliance_status'] = 'pending_review'
                
            processed_documents.append(doc)
        
        # Handle HTMX requests for infinite scrolling or pagination
        if request.headers.get('HX-Request'):
            return render_template(
                'documents/list_partial.html', 
                documents=processed_documents, 
                pagination=pagination
            )
        
        # Handle normal requests
        return render_template(
            'documents/list.html', 
            documents=processed_documents, 
            pagination=pagination,
            search_query=search_query,
            document_type=document_type,
            sort_by=sort_by,
            sort_dir='desc' if sort_dir == -1 else 'asc'
        )
    except Exception as e:
        current_app.logger.error(f"Error in list_documents: {str(e)}")
        flash(f"An error occurred while loading documents: {str(e)}", "error")
        return render_template('documents/list.html', documents=[], pagination=None)

@documents_bp.route('/upload', methods=['GET', 'POST'])
@validate_document_upload
@error_handler
def upload_document():
    """Upload a new document"""
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'document' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
            
        # Validate CSRF token
        try:
            validate_csrf(request.form.get('csrf_token'))
        except Exception as e:
            current_app.logger.error(f"CSRF validation error: {str(e)}")
            flash('CSRF token validation failed. Please try again.', 'error')
            return redirect(request.url)
        
        file = request.files['document']
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the document
        document_id = process_document(file_path, filename)
        
        # Show success message
        flash(f'Document "{filename}" uploaded successfully', 'success')
        
        return redirect(url_for('documents.view_document', document_id=document_id))
    
    return render_template('documents/upload.html')

@documents_bp.route('/view/<document_id>')
@error_handler
@cache_document(ttl=300)  # Cache for 5 minutes
def view_document(document_id):
    """View a document's details"""
    from app.extensions import mongo
    from app.utils.error_handler import NotFoundError
    
    document = mongo.db.documents.find_one({'_id': document_id})
    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('documents.list_documents'))
        
    # Ensure metadata is properly loaded
    if 'metadata' not in document or not document['metadata']:
        document['metadata'] = {}
    
    # Make sure document has all required fields
    if 'file_size' not in document:
        try:
            document['file_size'] = document['metadata'].get('file_size', 0)
        except (TypeError, KeyError):
            document['file_size'] = 0
    
    if 'file_format' not in document:
        try:
            document['file_format'] = document['metadata'].get('format', '')
        except (TypeError, KeyError):
            document['file_format'] = ''
    
    # Ensure document_type is set
    if 'document_type' not in document or not document['document_type']:
        document['document_type'] = 'other'
        
    # Log document info for debugging
    current_app.logger.info(f"Document info: type={document.get('document_type')}, size={document.get('file_size')}, format={document.get('file_format')}")
    
    # Ensure document has compliance issues field
    if 'compliance_issues' not in document:
        document['compliance_issues'] = []
    
    # Debug compliance issues
    current_app.logger.info(f"Document compliance issues: {len(document.get('compliance_issues', []))}, type: {type(document.get('compliance_issues'))}")
    if document.get('compliance_issues'):
        # Convert compliance issues to list if it's not already
        if not isinstance(document['compliance_issues'], list):
            try:
                document['compliance_issues'] = list(document['compliance_issues'])
                current_app.logger.info(f"Converted compliance issues to list: {len(document['compliance_issues'])}")
            except Exception as e:
                current_app.logger.error(f"Error converting compliance issues to list: {str(e)}")
                document['compliance_issues'] = []
        
    # Ensure document has compliance score
    if 'compliance_score' not in document or document['compliance_score'] is None:
        document['compliance_score'] = 0
        
    # Ensure document has compliance status
    if 'compliance_status' not in document or not document['compliance_status']:
        document['compliance_status'] = 'pending_review'

    return render_template('documents/view.html', document=document)

@documents_bp.route('/bulk', methods=['GET'])
def bulk_upload_page():
    """Show bulk document upload page"""
    return render_template('documents/bulk_upload.html')

@documents_bp.route('/bulk/jobs', methods=['GET'])
@error_handler
def list_bulk_jobs():
    """List active bulk processing jobs"""
    from app.services.bulk_processor import get_bulk_processor
    
    limit = request.args.get('limit', 10, type=int)
    skip = request.args.get('skip', 0, type=int)
    group_id = request.args.get('group_id')
    
    bulk_processor = get_bulk_processor()
    jobs = bulk_processor.list_jobs(limit=limit, skip=skip, group_id=group_id)
    
    if request.headers.get('HX-Request'):
        # Return partial for HTMX
        return render_template('documents/jobs_list_partial.html', jobs=jobs)
    
    return jsonify(jobs)