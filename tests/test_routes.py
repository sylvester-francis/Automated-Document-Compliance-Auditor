"""
Tests for the application routes.
"""
import io
import pytest
from app.extensions import mongo


class TestRoutes:
    """Tests for the application routes."""

    def test_index_route(self, client):
        """Test the index route."""
        # Make a request to the index route
        response = client.get('/')
        
        # Verify the response
        assert response.status_code == 200
        assert b'Document Compliance Auditor' in response.data
    
    def test_document_list_route(self, client):
        """Test the document list route."""
        # Make a request to the document list route
        response = client.get('/documents')
        
        # Verify the response
        assert response.status_code == 200
        assert b'Documents' in response.data
    
    def test_document_upload_route(self, client):
        """Test the document upload route."""
        # Make a request to the document upload route
        response = client.get('/documents/upload')
        
        # Verify the response
        assert response.status_code == 200
        assert b'Upload Document' in response.data
    
    def test_document_upload_post(self, client):
        """Test uploading a document via the web interface."""
        # Create a test file
        data = {
            'file': (io.BytesIO(b'This is a test document.'), 'test.txt')
        }
        
        # Make a request to the document upload route
        response = client.post(
            '/documents/upload',
            data=data,
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        # Verify the response
        assert response.status_code == 200
        assert b'Document uploaded successfully' in response.data
    
    def test_document_view_route(self, client, app):
        """Test the document view route."""
        with app.app_context():
            # Get the test document ID
            document = mongo.db.documents.find_one({})
            document_id = document['document_id']
            
            # Make a request to the document view route
            response = client.get(f'/documents/{document_id}')
            
            # Verify the response
            assert response.status_code == 200
            assert document['filename'].encode() in response.data
    
    def test_compliance_check_route(self, client, app):
        """Test the compliance check route."""
        with app.app_context():
            # Get the test document ID
            document = mongo.db.documents.find_one({})
            document_id = document['document_id']
            
            # Make a request to the compliance check route
            response = client.get(f'/compliance/check/{document_id}')
            
            # Verify the response
            assert response.status_code == 200
            assert b'Compliance Check Results' in response.data
    
    def test_compliance_check_post(self, client, app):
        """Test submitting a compliance check."""
        with app.app_context():
            # Get the test document ID
            document = mongo.db.documents.find_one({})
            document_id = document['document_id']
            
            # Make a request to the compliance check route
            response = client.post(
                f'/compliance/check/{document_id}',
                data={'compliance_types': ['GDPR', 'HIPAA']},
                follow_redirects=True
            )
            
            # Verify the response
            assert response.status_code == 200
            assert b'Compliance Score' in response.data
    
    def test_generate_suggestion_route(self, client, app):
        """Test the generate suggestion route."""
        with app.app_context():
            # Get the test document ID
            document = mongo.db.documents.find_one({})
            document_id = document['document_id']
            
            # Make a request to the generate suggestion route
            response = client.post(
                f'/compliance/suggestion/{document_id}',
                json={
                    'issue_id': 'test-issue-id',
                    'rule_id': 'test-gdpr-001',
                    'paragraph_id': 'p1'
                },
                content_type='application/json'
            )
            
            # Verify the response
            assert response.status_code == 200
            assert b'suggestion' in response.data
    
    def test_export_pdf_route(self, client, app):
        """Test the export PDF route."""
        with app.app_context():
            # Get the test document ID
            document = mongo.db.documents.find_one({})
            document_id = document['document_id']
            
            # Make a request to the export PDF route
            response = client.get(f'/documents/{document_id}/export/pdf')
            
            # Verify the response
            assert response.status_code == 200
            assert response.mimetype == 'application/pdf'
