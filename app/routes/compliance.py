# app/routes/compliance.py

from flask import Blueprint, render_template, request, jsonify, current_app, make_response
from app.services.rule_engine import check_document_compliance
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from app.extensions import mongo

compliance_bp = Blueprint('compliance', __name__, url_prefix='/compliance')


@compliance_bp.route('/check/<document_id>', methods=['GET', 'POST'])
def check_document(document_id):
    """Check document compliance."""
    document = mongo.db.documents.find_one({'_id': document_id})
    if not document:
        return jsonify({'error': 'Document not found'}), 404

    # Get compliance types from query params or use defaults
    compliance_types = request.args.getlist('type') or current_app.config['DEFAULT_COMPLIANCE_TYPES']

    # Check compliance
    results = check_document_compliance(document, compliance_types)

    # Debug output
    print(f"Document ID: {document_id}")
    print(f"Found {len(results['issues'])} compliance issues")
    print(f"Compliance Score: {results['score']}")
    for i, issue in enumerate(results['issues']):
        print(f"Issue {i+1}: {issue.get('issue_id', 'No ID')}")
        print(f"  Paragraph ID: {issue.get('paragraph_id', 'No paragraph ID')}")
        print(f"  Description: {issue.get('description', 'No description')}")
        print(f"  Has suggestions field: {'Yes' if 'suggestions' in issue else 'No'}")
        print(f"  Suggestions: {issue.get('suggestions', [])}")

    # Re-fetch updated document with the updated compliance information
    document = mongo.db.documents.find_one({'_id': document_id})
    
    # Ensure metadata is properly loaded
    if 'metadata' not in document or not document['metadata']:
        document['metadata'] = {}
        
    # Make sure compliance score is available in the template context
    if 'compliance_score' not in document or document['compliance_score'] is None:
        document['compliance_score'] = results['score']
        # Update the document with the score if it's missing
        mongo.db.documents.update_one(
            {'_id': document_id},
            {'$set': {'compliance_score': results['score']}}
        )
        
    # Ensure compliance status is properly set
    if 'compliance_status' not in document or not document['compliance_status']:
        mongo.db.documents.update_one(
            {'_id': document_id},
            {'$set': {'compliance_status': results['status']}}
        )
        document['compliance_status'] = results['status']
        
    # Process document content for display
    if 'paragraphs' in document and document['paragraphs']:
        # If paragraphs exist but are empty or missing IDs, fix them
        processed_paragraphs = []
        for i, para in enumerate(document['paragraphs']):
            if isinstance(para, dict) and para.get('id') and para.get('text'):
                # Dictionary paragraph with ID and text - keep as is
                processed_paragraphs.append(para)
            elif isinstance(para, dict) and not para.get('id') and para.get('text'):
                # Dictionary paragraph without ID but with text - add ID
                para['id'] = f'p{i+1}'
                processed_paragraphs.append(para)
            elif isinstance(para, str) and para.strip():
                # String paragraph - convert to dict with ID
                processed_paragraphs.append({'id': f'p{i+1}', 'text': para})
            # Skip empty paragraphs
        
        if processed_paragraphs:
            document['paragraphs'] = processed_paragraphs
        else:
            # If all paragraphs were invalid/empty, use document text instead
            document['paragraphs'] = []
    
    # If no paragraphs but text exists, create a single paragraph
    if (not document.get('paragraphs') or len(document['paragraphs']) == 0) and document.get('text'):
        document['paragraphs'] = [{'id': 'p1', 'text': document['text']}]

    if request.headers.get('HX-Request'):
        return render_template('compliance/results_partial.html', results=results, document=document)

    return render_template('compliance/results.html', results=results, document=document)


@compliance_bp.route('/suggest/<document_id>/<issue_id>', methods=['GET'])
def get_suggestion(document_id, issue_id):
    """Get AI suggestion for fixing a compliance issue."""
    print(f"⭐️ Generating suggestion for document: {document_id}, issue: {issue_id} ⭐️")
    from app.extensions import mongo

    document = mongo.db.documents.find_one({'_id': document_id})
    if not document:
        print("Document not found")
        return jsonify({'error': 'Document not found'}), 404

    compliance_issues = document.get('compliance_issues', [])
    print(f"Document has {len(compliance_issues)} compliance issues")
    for i, issue in enumerate(compliance_issues):
        print(f"Issue {i+1} ID: {issue.get('issue_id')}")

    # Find the issue by ID
    issue = next((i for i in compliance_issues if i.get('issue_id') == issue_id), None)
    if not issue:
        print(f"Issue not found for ID: {issue_id}")
        error_message = f"Compliance issue with ID '{issue_id}' not found"
        
        # Handle HTMX requests differently to show error in UI
        if request.headers.get('HX-Request'):
            return f'<div class="alert alert-danger">{error_message}</div>'
        
        return jsonify({'error': error_message}), 404

    print(f"Calling generate_suggestion for issue {issue_id}")
    try:
        from app.services.llm_service import generate_suggestion
        suggestion = generate_suggestion(document, issue)

        print(f"Suggestion received: {suggestion[:50]}...")

        # Update DB with the new suggestion
        if suggestion and suggestion not in issue.get('suggestions', []):
            mongo.db.documents.update_one(
                {"_id": document_id, "compliance_issues.issue_id": issue_id},
                {"$addToSet": {"compliance_issues.$.suggestions": suggestion}}
            )

        if request.headers.get('HX-Request'):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                return render_template(
                    'compliance/suggestion_partial.html',
                    suggestion=suggestion,
                    timestamp=timestamp
                )
            except Exception as template_error:
                print(f"Template error: {str(template_error)}")
                return f"""
                <div class="suggestion-card mt-2">
                    <p><strong>AI Suggestion from Claude:</strong></p>
                    <p>{suggestion}</p>
                    <small class="text-muted">Generated {timestamp}</small>
                </div>
                """

        return jsonify({'suggestion': suggestion})

    except Exception as e:
        print(f"Error generating suggestion: {str(e)}")
        error_message = f"Error generating suggestion: {str(e)}"
        if request.headers.get('HX-Request'):
            return f'<div class="alert alert-danger">{error_message}</div>'
        return jsonify({'error': error_message}), 500

@compliance_bp.route('/bulk/upload', methods=['POST'])
def upload_bulk_documents():
    """Handle bulk document upload and processing"""
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files[]')
    
    # Prepare file info for bulk processor
    file_info_list = []
    for file in files:
        # Save file to uploads directory
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Add to file info list
        file_info_list.append({
            "filename": filename,
            "path": file_path,
            "compliance_types": request.form.getlist('compliance_types') or ["GDPR", "HIPAA"]
        })
    
    # Start bulk processing job
    from app.services.bulk_processor import get_bulk_processor
    bulk_processor = get_bulk_processor()
    job = bulk_processor.start_bulk_job(file_info_list, job_name=request.form.get('job_name'))
    
    return jsonify({
        'message': f'Bulk processing job started with {len(files)} files',
        'job_id': job['job_id']
    })

@compliance_bp.route('/bulk/status/<job_id>', methods=['GET'])
def get_bulk_job_status(job_id):
    """Get status of a bulk processing job"""
    from app.services.bulk_processor import get_bulk_processor
    bulk_processor = get_bulk_processor()
    job_status = bulk_processor.get_job_status(job_id)
    
    return jsonify(job_status)

@compliance_bp.route('/export/<document_id>', methods=['GET'])
def export_compliance_report(document_id):
    """Export compliance report as PDF"""
    try:
        # First get the document - do error handling here
        document = mongo.db.documents.find_one({'_id': document_id})
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Generate PDF report by passing the document directly
        from app.services.pdf_exporter import get_pdf_exporter
        pdf_exporter = get_pdf_exporter()
        
        # Pass the document directly to avoid redundant lookup
        pdf_data = pdf_exporter.generate_compliance_report(document)
        
        # Return PDF file
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=compliance_report_{document_id}.pdf'
        return response
    
    except Exception as e:
        current_app.logger.error(f"Error in export_compliance_report: {str(e)}")
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500
    