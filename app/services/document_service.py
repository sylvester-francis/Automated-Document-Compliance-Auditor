# app/services/document_service.py
import os
import uuid
from datetime import datetime
from flask import current_app

from app.models.document import Document, DocumentType, ComplianceStatus

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
    from app.services.extraction_service import get_extraction_service
    
    try:
        # Get extraction service to access full extraction results including metadata
        extraction_service = get_extraction_service()
        extraction_result = extraction_service.extract_text(file_path)
        
        # Log extraction result for debugging
        current_app.logger.info(f"Extraction result: {extraction_result}")
        
        # Extract text and paragraphs from the document
        full_text = extraction_result.get('text', '')
        paragraphs = extraction_result.get('paragraphs', [])
        if not paragraphs and full_text:
            # If no paragraphs were extracted, split the full text into paragraphs
            paragraphs = [p for p in full_text.split('\n\n') if p.strip()]
        
        # Extract metadata and ensure it's properly formatted
        metadata = extraction_result.get('metadata', {})
        
        # Add file information to metadata if not present
        if 'file_size' not in metadata:
            try:
                metadata['file_size'] = os.path.getsize(file_path)
            except OSError as e:
                current_app.logger.warning(f"Could not get file size: {e}")
                metadata['file_size'] = 0
                
        # Extract file format from filename
        _, ext = os.path.splitext(filename)
        if 'format' not in metadata:
            metadata['format'] = ext.lstrip('.').lower()
            
        # Determine document type from file format
        file_format = metadata.get('format', '').lower()
        if file_format in ['pdf']:
            document_type = DocumentType.CONTRACT
        elif file_format in ['docx', 'doc']:
            document_type = DocumentType.AGREEMENT
        elif file_format in ['txt']:
            document_type = DocumentType.OTHER
        else:
            document_type = DocumentType.OTHER
            
        # Add file format and size to metadata if not present
        if 'file_format' not in metadata:
            metadata['file_format'] = file_format
            
        # Get file size
        try:
            file_size = os.path.getsize(file_path)
            metadata['file_size'] = file_size
        except OSError as e:
            current_app.logger.warning(f"Could not get file size: {e}")
            file_size = 0
            metadata['file_size'] = 0
        
        # Extract statistics and add to metadata
        statistics = extraction_result.get("statistics", {})
        if statistics:
            metadata.update({
                "character_count": statistics.get("char_count", 0),
                "word_count": statistics.get("word_count", 0),
                "line_count": statistics.get("line_count", 0)
            })
        
        # Generate a unique ID for the document
        document_id = str(uuid.uuid4())
        
        # Create document object
        document = Document(
            document_id=document_id,
            filename=filename,
            file_path=file_path,
            content=full_text,
            paragraphs=paragraphs,
            metadata=metadata,
            document_type=document_type,  # Use the determined document type
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