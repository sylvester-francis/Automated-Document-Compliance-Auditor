"""
Tests for the document service.
"""
import os
import tempfile
import pytest
from app.services.document_service import process_document
from app.models.document import DocumentType, ComplianceStatus
from app.extensions import mongo


class TestDocumentService:
    """Tests for the document service."""

    def test_process_document_txt(self, app):
        """Test processing a text document."""
        with app.app_context():
            # Create a temporary text file
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                f.write(b'This is a test document.\nIt has multiple lines.\nIt is used for testing.')
                file_path = f.name
            
            try:
                # Process the document
                document_id = process_document(file_path, os.path.basename(file_path))
                
                # Check that the document was created in the database
                document = mongo.db.documents.find_one({'document_id': document_id})
                
                # Verify document properties
                assert document is not None
                assert document['filename'] == os.path.basename(file_path)
                assert document['file_path'] == file_path
                assert 'This is a test document.' in document['content']
                assert len(document['paragraphs']) > 0
                assert document['document_type'] == DocumentType.OTHER.value
                assert document['compliance_status'] == ComplianceStatus.PENDING_REVIEW.value
                assert document['metadata']['format'] == 'txt'
                assert document['metadata']['file_size'] > 0
            finally:
                # Clean up the temporary file
                if os.path.exists(file_path):
                    os.unlink(file_path)
    
    def test_process_document_nonexistent_file(self, app):
        """Test processing a nonexistent file."""
        with app.app_context():
            # Try to process a nonexistent file
            with pytest.raises(Exception):
                process_document('/path/to/nonexistent/file.txt', 'nonexistent.txt')
    
    def test_process_document_empty_file(self, app):
        """Test processing an empty file."""
        with app.app_context():
            # Create an empty temporary file
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                file_path = f.name
            
            try:
                # Process the document
                document_id = process_document(file_path, os.path.basename(file_path))
                
                # Check that the document was created in the database
                document = mongo.db.documents.find_one({'document_id': document_id})
                
                # Verify document properties
                assert document is not None
                assert document['filename'] == os.path.basename(file_path)
                assert document['content'] == ''
                assert document['metadata']['file_size'] == 0
            finally:
                # Clean up the temporary file
                if os.path.exists(file_path):
                    os.unlink(file_path)
