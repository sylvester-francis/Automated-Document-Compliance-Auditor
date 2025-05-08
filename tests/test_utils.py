"""
Tests for the utility functions.
"""
import pytest
from app.utils.text_processing import extract_paragraphs_with_ids, clean_text
from app.utils.pagination import get_pagination
from app.models.document import Document, DocumentType, ComplianceStatus


class TestTextProcessing:
    """Tests for the text processing utilities."""

    def test_extract_paragraphs_with_ids(self):
        """Test extracting paragraphs with IDs."""
        # Test with a multi-paragraph text
        text = "This is paragraph one.\n\nThis is paragraph two.\n\nThis is paragraph three."
        paragraphs = extract_paragraphs_with_ids(text)
        
        # Verify the result
        assert len(paragraphs) == 3
        assert all('id' in p for p in paragraphs)
        assert all('text' in p for p in paragraphs)
        assert paragraphs[0]['text'] == "This is paragraph one."
        assert paragraphs[1]['text'] == "This is paragraph two."
        assert paragraphs[2]['text'] == "This is paragraph three."
        
        # Test with a single paragraph text
        text = "This is a single paragraph."
        paragraphs = extract_paragraphs_with_ids(text)
        
        # Verify the result
        assert len(paragraphs) == 1
        assert 'id' in paragraphs[0]
        assert 'text' in paragraphs[0]
        assert paragraphs[0]['text'] == "This is a single paragraph."
        
        # Test with an empty text
        text = ""
        paragraphs = extract_paragraphs_with_ids(text)
        
        # Verify the result
        assert len(paragraphs) == 0
    
    def test_clean_text(self):
        """Test cleaning text."""
        # Test removing extra whitespace
        text = "This   has   extra   spaces."
        cleaned = clean_text(text)
        assert cleaned == "This has extra spaces."
        
        # Test removing control characters
        text = "This has\x00control\x01characters."
        cleaned = clean_text(text)
        assert cleaned == "This hascontrolcharacters."
        
        # Test trimming whitespace
        text = "  This has leading and trailing whitespace.  "
        cleaned = clean_text(text)
        assert cleaned == "This has leading and trailing whitespace."


class TestPagination:
    """Tests for the pagination utility."""

    def test_get_pagination(self, app):
        """Test getting pagination."""
        with app.app_context():
            # Create a list of test items
            items = [{'id': i, 'name': f'Item {i}'} for i in range(1, 101)]
            
            # Insert items into a test collection
            collection = app.mongo.db.test_pagination
            collection.delete_many({})
            collection.insert_many(items)
            
            # Test pagination with default parameters
            result, pagination = get_pagination(collection)
            
            # Verify the result
            assert len(result) == 10  # Default per_page is 10
            assert pagination['page'] == 1
            assert pagination['per_page'] == 10
            assert pagination['total'] == 100
            assert pagination['pages'] == 10
            
            # Test pagination with custom parameters
            result, pagination = get_pagination(
                collection,
                page=2,
                per_page=20,
                sort_by='id',
                sort_direction=-1
            )
            
            # Verify the result
            assert len(result) == 20
            assert pagination['page'] == 2
            assert pagination['per_page'] == 20
            assert pagination['total'] == 100
            assert pagination['pages'] == 5
            
            # Test pagination with a query
            result, pagination = get_pagination(
                collection,
                query={'id': {'$lt': 10}}
            )
            
            # Verify the result
            assert len(result) == 9
            assert pagination['total'] == 9


class TestDocumentModel:
    """Tests for the Document model."""

    def test_document_model(self):
        """Test the Document model."""
        # Create a document
        document = Document(
            document_id='test-doc-id',
            filename='test.txt',
            file_path='/path/to/test.txt',
            content='This is a test document.',
            paragraphs=[{'id': 'p1', 'text': 'This is a test document.'}],
            metadata={'format': 'txt', 'file_size': 100},
            document_type=DocumentType.OTHER,
            compliance_status=ComplianceStatus.PENDING_REVIEW
        )
        
        # Verify the document properties
        assert document.document_id == 'test-doc-id'
        assert document.filename == 'test.txt'
        assert document.file_path == '/path/to/test.txt'
        assert document.content == 'This is a test document.'
        assert len(document.paragraphs) == 1
        assert document.metadata['format'] == 'txt'
        assert document.document_type == DocumentType.OTHER
        assert document.compliance_status == ComplianceStatus.PENDING_REVIEW
        
        # Test to_dict method
        document_dict = document.to_dict()
        assert document_dict['document_id'] == 'test-doc-id'
        assert document_dict['filename'] == 'test.txt'
        assert document_dict['content'] == 'This is a test document.'
        assert document_dict['document_type'] == DocumentType.OTHER.value
        assert document_dict['compliance_status'] == ComplianceStatus.PENDING_REVIEW.value
