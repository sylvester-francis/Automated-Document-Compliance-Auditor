from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from app.services.document_service import process_document

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@documents_bp.route('/')
def list_documents():
    """List all documents."""
    from app.extensions import mongo
    documents = list(mongo.db.documents.find())
    return render_template('documents/list.html', documents=documents)

@documents_bp.route('/upload', methods=['GET', 'POST'])
def upload_document():
    """Upload a document."""
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'document' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['document']
        
        # If user does not select file, browser submits an empty file
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Process the document
            document_id = process_document(file_path, filename)
            
            return redirect(url_for('documents.view_document', document_id=document_id))
    
    return render_template('documents/upload.html')

@documents_bp.route('/<document_id>')
def view_document(document_id):
    """View a document."""
    from app.extensions import mongo
    document = mongo.db.documents.find_one({'_id': document_id})
    if not document:
        flash('Document not found')
        return redirect(url_for('documents.list_documents'))
    
    return render_template('documents/view.html', document=document)

@documents_bp.route('/bulk', methods=['GET'])
def bulk_upload_page():
    """Show bulk document upload page"""
    return render_template('documents/bulk_upload.html')

@documents_bp.route('/bulk/jobs', methods=['GET'])
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