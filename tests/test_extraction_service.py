"""
Tests for the extraction service.
"""
import os
import tempfile
import pytest
from app.services.extraction_service import (
    get_extraction_service,
    extract_document_text
)


class TestExtractionService:
    """Tests for the extraction service."""

    def test_get_extraction_service(self):
        """Test getting the extraction service singleton."""
        # Get the extraction service
        service1 = get_extraction_service()
        service2 = get_extraction_service()
        
        # Verify that we got the same instance both times
        assert service1 is service2
        
        # Verify that the service has the expected methods
        assert hasattr(service1, 'extract_text')
        assert hasattr(service1, 'extract_from_txt')
        assert hasattr(service1, 'extract_from_pdf')
        assert hasattr(service1, 'extract_from_docx')
    
    def test_extract_text_from_txt(self):
        """Test extracting text from a TXT file."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'This is a test document.\nIt has multiple lines.\nIt is used for testing.')
            file_path = f.name
        
        try:
            # Get the extraction service
            service = get_extraction_service()
            
            # Extract text from the file
            result = service.extract_text(file_path)
            
            # Verify the result
            assert 'text' in result
            assert 'This is a test document.' in result['text']
            assert 'metadata' in result
            assert 'format' in result['metadata']
            assert result['metadata']['format'] == 'txt'
            assert 'statistics' in result
            assert 'char_count' in result['statistics']
            assert 'word_count' in result['statistics']
            assert 'line_count' in result['statistics']
            assert result['statistics']['line_count'] >= 3
        finally:
            # Clean up the temporary file
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    def test_extract_document_text(self):
        """Test the extract_document_text wrapper function."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'This is a test document.\nIt has multiple lines.\nIt is used for testing.')
            file_path = f.name
        
        try:
            # Extract text from the file
            text, paragraphs = extract_document_text(file_path)
            
            # Verify the result
            assert 'This is a test document.' in text
            assert len(paragraphs) > 0
            assert 'id' in paragraphs[0]
            assert 'text' in paragraphs[0]
        finally:
            # Clean up the temporary file
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    def test_extract_text_unsupported_format(self):
        """Test extracting text from an unsupported file format."""
        # Create a temporary file with an unsupported extension
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            f.write(b'This is a test document with an unsupported format.')
            file_path = f.name
        
        try:
            # Get the extraction service
            service = get_extraction_service()
            
            # Extract text from the file
            result = service.extract_text(file_path)
            
            # Verify the result
            assert 'text' in result
            assert 'This is a test document with an unsupported format.' in result['text']
            assert 'metadata' in result
            assert 'warning' in result['metadata']
            assert 'Unsupported file format' in result['metadata']['warning']
        finally:
            # Clean up the temporary file
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    def test_extract_text_nonexistent_file(self):
        """Test extracting text from a nonexistent file."""
        # Get the extraction service
        service = get_extraction_service()
        
        # Try to extract text from a nonexistent file
        result = service.extract_text('/path/to/nonexistent/file.txt')
        
        # Verify the result
        assert 'error' in result
