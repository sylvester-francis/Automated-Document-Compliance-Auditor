# app/services/document_service.py
import os
import uuid
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

from app.models.document import Document, DocumentType, ComplianceStatus
from app.services.extraction_service import extract_document_text

def process_document(file_path, filename):
    """
    Process an uploaded document and store it in the database.
    
    Args:
        file_path: Path to the uploaded file
        filename: Original filename
    
    Returns:
        document_id: ID of the processed document
    """
    from app.extensions import mongo
    
    try:
        # Extract text from document
        full_text, paragraphs = extract_document_text(file_path)
        
        # Generate a unique ID for the document
        document_id = str(uuid.uuid4())
        
        # Create document object
        document = Document(
            document_id=document_id,
            filename=filename,
            file_path=file_path,
            content=full_text,
            paragraphs=paragraphs,
            compliance_status=ComplianceStatus.PENDING_REVIEW,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Insert document into MongoDB
        mongo.db.documents.insert_one(document.to_dict())
        
        return document_id
        
    except Exception as e:
        current_app.logger.error(f"Error processing document: {str(e)}")
        raise