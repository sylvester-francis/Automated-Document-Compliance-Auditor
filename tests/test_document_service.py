"""
Tests for the document service.
"""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from app.services.document_service import process_document
from app.models.document import DocumentType, ComplianceStatus
from app.extensions import mongo


class TestDocumentService:
    """Tests for the document service."""

    @patch('app.services.extraction_service.get_extraction_service')
    def test_process_document_txt(self, mock_get_extraction_service, app):
        """Test processing a text document."""
        # Create a mock extraction service
        mock_extraction_service = MagicMock()
        mock_extraction_service.extract_text.return_value = {
            'text': 'This is a test document.\nIt has multiple lines.\nIt is used for testing.',
            'paragraphs': [{'id': 'p1', 'text': 'This is a test document.'}, 
                          {'id': 'p2', 'text': 'It has multiple lines.'}, 
                          {'id': 'p3', 'text': 'It is used for testing.'}],
            'metadata': {'format': 'txt', 'file_size': 100},
            'statistics': {'char_count': 79, 'word_count': 15, 'line_count': 3}
        }
        mock_get_extraction_service.return_value = mock_extraction_service
        
        with app.app_context():
            # Create a temporary text file
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                f.write(b'This is a test document.\nIt has multiple lines.\nIt is used for testing.')
                file_path = f.name
            
            try:
                # Process the document
                document_id = process_document(file_path, os.path.basename(file_path))
                
                # Check that the document was created in the database
                document = mongo.db.documents.find_one({'_id': document_id})
                
                # Verify document properties
                assert document is not None
                assert document['filename'] == os.path.basename(file_path)
                assert document['file_path'] == file_path
                assert 'This is a test document.' in document['content']
                assert len(document['paragraphs']) > 0
                assert document['document_type'] == DocumentType.OTHER
                assert document['compliance_status'] == ComplianceStatus.PENDING_REVIEW
                assert document['metadata']['format'] == 'txt'
                assert document['metadata']['file_size'] > 0
            finally:
                # Clean up the temporary file
                if os.path.exists(file_path):
                    os.unlink(file_path)
    
    @patch('app.services.extraction_service.get_extraction_service')
    def test_process_document_nonexistent_file(self, mock_get_extraction_service, app):
        """Test processing a nonexistent file."""
        # Configure the mock to raise an exception
        mock_extraction_service = MagicMock()
        mock_extraction_service.extract_text.side_effect = FileNotFoundError("File not found")
        mock_get_extraction_service.return_value = mock_extraction_service
        
        with app.app_context():
            # Try to process a nonexistent file
            with pytest.raises(Exception):
                process_document('/path/to/nonexistent/file.txt', 'nonexistent.txt')
    
    @patch('app.services.extraction_service.get_extraction_service')
    def test_process_document_empty_file(self, mock_get_extraction_service, app):
        """Test processing an empty file."""
        # Create a mock extraction service that returns empty content
        mock_extraction_service = MagicMock()
        mock_extraction_service.extract_text.return_value = {
            'text': '',
            'paragraphs': [],
            'metadata': {'format': 'txt', 'file_size': 0},
            'statistics': {'char_count': 0, 'word_count': 0, 'line_count': 0}
        }
        mock_get_extraction_service.return_value = mock_extraction_service
        
        with app.app_context():
            # Create an empty temporary file
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                file_path = f.name
            
            try:
                # Process the document
                document_id = process_document(file_path, os.path.basename(file_path))
                
                # Check that the document was created in the database
                document = mongo.db.documents.find_one({'_id': document_id})
                
                # Verify document properties
                assert document is not None
                assert document['filename'] == os.path.basename(file_path)
                assert document['content'] == ''
                assert document['metadata']['file_size'] == 0
            finally:
                # Clean up the temporary file
                if os.path.exists(file_path):
                    os.unlink(file_path)
