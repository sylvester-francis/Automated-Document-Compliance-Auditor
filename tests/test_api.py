"""
Tests for the API endpoints.
"""
import io
import json
import pytest
from app.extensions import mongo


class TestAPIEndpoints:
    """Tests for the API endpoints."""

    def test_list_documents(self, client, app):
        """Test the list documents API endpoint."""
        with app.app_context():
            # Make a request to the API endpoint
            response = client.get('/api/documents', headers={'X-API-Key': 'test_api_key'})
            
            # Verify the response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'documents' in data
            assert 'pagination' in data
    
    def test_get_document(self, client, app):
        """Test the get document API endpoint."""
        with app.app_context():
            # Get the test document ID
            document = mongo.db.documents.find_one({})
            document_id = document['document_id']
            
            # Make a request to the API endpoint
            response = client.get(f'/api/documents/{document_id}', headers={'X-API-Key': 'test_api_key'})
            
            # Verify the response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'document_id' in data
            assert data['document_id'] == document_id
    
    def test_get_nonexistent_document(self, client):
        """Test getting a nonexistent document."""
        # Make a request to the API endpoint with a nonexistent ID
        response = client.get('/api/documents/nonexistent-id', headers={'X-API-Key': 'test_api_key'})
        
        # Verify the response
        assert response.status_code == 404
    
    def test_upload_document(self, client):
        """Test uploading a document via the API."""
        # Create a test file
        data = {
            'file': (io.BytesIO(b'This is a test document.'), 'test.txt')
        }
        
        # Make a request to the API endpoint
        response = client.post(
            '/api/documents/upload',
            data=data,
            content_type='multipart/form-data',
            headers={'X-API-Key': 'test_api_key'}
        )
        
        # Verify the response
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'document_id' in data
    
    def test_check_document_compliance(self, client, app):
        """Test checking document compliance via the API."""
        with app.app_context():
            # Get the test document ID
            document = mongo.db.documents.find_one({})
            document_id = document['document_id']
            
            # Make a request to the API endpoint
            response = client.post(
                f'/api/documents/{document_id}/check',
                json={'compliance_types': ['GDPR', 'HIPAA']},
                headers={'X-API-Key': 'test_api_key'}
            )
            
            # Verify the response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'issues' in data
            assert 'score' in data
            assert 'status' in data
    
    def test_get_compliance_rules(self, client):
        """Test getting compliance rules via the API."""
        # Make a request to the API endpoint
        response = client.get('/api/rules', headers={'X-API-Key': 'test_api_key'})
        
        # Verify the response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rules' in data
        assert len(data['rules']) > 0
    
    def test_api_authentication(self, client):
        """Test API authentication."""
        # Make a request without an API key
        response = client.get('/api/documents')
        
        # Verify that authentication is required
        assert response.status_code == 401
        
        # Make a request with an invalid API key
        response = client.get('/api/documents', headers={'X-API-Key': 'invalid_key'})
        
        # Verify that authentication fails
        assert response.status_code == 401
