# Tests for Automated Document Compliance Auditor

This directory contains pytest tests for the Automated Document Compliance Auditor application.

## Test Structure

The tests are organized into the following files:

- `conftest.py`: Contains test fixtures and setup code
- `test_document_service.py`: Tests for the document service
- `test_rule_engine.py`: Tests for the rule engine
- `test_extraction_service.py`: Tests for the extraction service
- `test_api.py`: Tests for the API endpoints
- `test_routes.py`: Tests for the web routes
- `test_utils.py`: Tests for utility functions and models

## Running Tests

To run the tests, make sure you have pytest installed and MongoDB running, then run:

```bash
# Navigate to the project directory
cd /Users/sylvester/Desktop/Automated-Document-Compliance-Auditor

# Activate the virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=app

# Run a specific test file
pytest tests/test_document_service.py

# Run a specific test
pytest tests/test_document_service.py::TestDocumentService::test_process_document_txt
```

## Test Requirements

The tests require:

1. MongoDB running on localhost:27017
2. Python packages: pytest, pytest-cov
3. All application dependencies installed

## Adding New Tests

When adding new tests:

1. Follow the existing pattern of test classes and methods
2. Use fixtures from conftest.py where appropriate
3. Make sure tests are isolated and don't depend on each other
4. Clean up any resources created during tests

## Test Coverage

To generate a test coverage report:

```bash
# Run tests with coverage
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html
```

The HTML coverage report will be available in the `htmlcov` directory.
