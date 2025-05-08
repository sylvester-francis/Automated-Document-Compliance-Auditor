"""
Test fixtures for the Automated Document Compliance Auditor application.
"""
import os
import sys
import tempfile
import pytest
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Add the parent directory to sys.path to make app imports work in both local and CI environments
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import mongo

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file to use as a test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Create the app with test config
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test_secret_key',
        'MONGO_URI': 'mongodb://localhost:27017/test_compliance_auditor',
        'ANTHROPIC_API_KEY': 'test_api_key',
        'API_KEY': 'test_api_key',  # Add API key for API authentication
        'USE_MOCK_LLM': True,  # Use mock LLM for testing
        'UPLOAD_FOLDER': tempfile.mkdtemp(),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max upload
        'ALLOWED_EXTENSIONS': {'pdf', 'docx', 'txt'}
    })
    
    # Setup application context
    with app.app_context():
        # Check if MongoDB is available
        try:
            # Create a test database
            client = MongoClient('mongodb://localhost:27017/')
            client.admin.command('ping')
            
            # Clear test database before tests
            mongo.db.documents.delete_many({})
            mongo.db.compliance_rules.delete_many({})
            
            # Insert test data
            insert_test_data()
            
        except ConnectionFailure:
            pytest.skip("MongoDB server not available")
    
    yield app
    
    # Cleanup after tests
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


def insert_test_data():
    """Insert test data into the database."""
    # Insert test compliance rules
    rules = [
        {
            "rule_id": "test-gdpr-001",
            "rule_type": "keyword",
            "compliance_type": "GDPR",
            "description": "Missing information about the right to access personal data",
            "severity": "high",
            "keywords": ["right to access", "access your data", "access personal information"],
            "suggestion_template": "You have the right to access your personal data."
        },
        {
            "rule_id": "test-hipaa-001",
            "rule_type": "keyword",
            "compliance_type": "HIPAA",
            "description": "Missing Notice of Privacy Practices",
            "severity": "high",
            "keywords": ["notice of privacy practices", "privacy notice", "privacy practices"],
            "suggestion_template": "This document should include a Notice of Privacy Practices."
        }
    ]
    
    mongo.db.compliance_rules.insert_many(rules)
    
    # Insert a test document
    test_document = {
        "_id": "test-document-id",
        "document_id": "test-document-id",
        "filename": "test_document.txt",
        "file_path": "/tmp/test_document.txt",
        "content": "This is a test document for compliance checking.",
        "paragraphs": [
            {"id": "p1", "text": "This is a test document for compliance checking."}
        ],
        "metadata": {
            "format": "txt",
            "file_size": 100
        },
        "document_type": "OTHER",
        "compliance_status": "PENDING_REVIEW",
        "created_at": "2025-05-07T00:00:00.000Z",
        "updated_at": "2025-05-07T00:00:00.000Z"
    }
    
    mongo.db.documents.insert_one(test_document)
