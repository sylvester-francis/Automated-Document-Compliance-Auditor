# Automated Document Compliance Auditor

A GenAI tool that scans contracts and regulatory filings for missing clauses and suggests remediation.

## Overview

The Automated Document Compliance Auditor is a Flask-based web application that helps organizations ensure their documents comply with various regulations such as GDPR and HIPAA. It analyzes documents to identify missing clauses and provides AI-powered suggestions for remediation using Anthropic's Claude API.

## Key Features

- **Document Processing**: Extract text from PDF, DOCX, and TXT files
- **Rule-based Compliance Checking**: Detect missing clauses using regex and keyword patterns
- **AI-Powered Suggestions**: Generate remediation text using Anthropic's Claude API
- **Interactive UI**: Real-time highlighting and inline editing with dark mode support
- **Domain-specific Compliance**: Support for GDPR, HIPAA, and other standards
- **Error Handling**: Centralized error handling system with user-friendly feedback
- **Performance Optimization**: Caching, pagination, and background task processing
- **Security**: Input validation, CSRF protection, and rate limiting
- **API Access**: RESTful API for programmatic access to all features
- **PDF Export**: Generate PDF reports for compliance results

## Technology Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, JavaScript with HTMX for interactivity
- **Database**: MongoDB for document storage
- **Text Processing**: PyPDF2, python-docx for document parsing
- **AI Integration**: Anthropic Claude API for generating suggestions
- **Styling**: Bootstrap 5 for responsive design with dark mode support
- **Caching**: In-memory caching with Flask-Caching
- **Security**: Flask-WTF for CSRF protection, input sanitization with Bleach
- **API**: RESTful API with rate limiting via Flask-Limiter
- **PDF Generation**: WeasyPrint for PDF report generation
- **Background Processing**: APScheduler for handling long-running tasks

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB
- Anthropic API key (for AI suggestions)
- ruff and flake8 (for code quality checks)

### Installation

1. Clone the repository

```bash
git clone https://github.com/sylvester-francis/Automated-Document-Compliance-Auditor.git
cd Automated-Document-Compliance-Auditor
```
2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install the dependencies
```bash
pip install -r requirements.txt
```
4. Create a .env file in the instance directory with your configuration
```bash
SECRET_KEY=your-secret-key
MONGO_URI=mongodb://localhost:27017/compliance_auditor
ANTHROPIC_API_KEY=your-anthropic-api-key
USE_MOCK_LLM=False  # Set to True to use mock LLM service instead of Claude API
API_KEY=your-api-key  # For accessing the API endpoints
CORS_ORIGINS=*  # Comma-separated list of allowed origins for CORS
MAX_CONTENT_LENGTH=10485760  # Maximum file size (10MB)
ALLOWED_EXTENSIONS=pdf,docx,txt  # Allowed file extensions
```
5. Run the app
```bash
python app.py
```
6. Open your browser and navigate to http://localhost:5000

## Usage

1. Upload a document (PDF, DOCX, or TXT)
2. The system will process the document and extract text and metadata
3. Check compliance against selected standards (GDPR, HIPAA, etc.)
4. View compliance issues and get AI-powered suggestions for remediation
5. Generate suggestions using the "Generate Suggestion (Claude)" button
6. Export compliance reports as PDF for documentation
7. Toggle between light and dark mode for comfortable viewing
8. Use the search and filtering options to find specific documents
9. Access all functionality programmatically through the API

## Project Structure
```bash
Automated-Document-Compliance-Auditor/
├── app/                    # Flask application
│   ├── __init__.py         # App initialization
│   ├── config.py           # Configuration settings
│   ├── extensions.py       # Flask extensions
│   ├── models/             # Data models
│   │   ├── __init__.py
│   │   ├── compliance.py   # Compliance models
│   │   └── document.py     # Document models
│   ├── routes/             # View functions
│   │   ├── __init__.py
│   │   ├── main.py         # Main routes
│   │   ├── documents.py    # Document management routes
│   │   └── compliance.py   # Compliance checking routes
│   ├── services/           # Business logic
│   │   ├── __init__.py
│   │   ├── document_service.py    # Document handling
│   │   ├── extraction_service.py  # Text extraction
│   │   ├── llm_service.py         # Claude API integration with fallback mock service
│   │   ├── rule_engine.py         # Compliance rules
│   │   └── seed_service.py        # Data seeding
│   ├── static/             # Static assets
│   │   ├── css/            # Stylesheets
│   │   ├── js/             # JavaScript files
│   │   └── img/            # Images
│   ├── templates/          # Jinja2 templates
│   │   ├── base.html       # Base template
│   │   ├── index.html      # Homepage
│   │   ├── about.html      # About page
│   │   ├── compliance/     # Compliance templates
│   │   │   ├── debug.html          # Debug page
│   │   │   ├── results.html        # Results page
│   │   │   ├── results_partial.html # HTMX partial for results
│   │   │   └── suggestions_partial.html # HTMX partial for suggestions
│   │   └── documents/      # Document templates
│   │       ├── list.html   # Document list
│   │       ├── upload.html # Upload form
│   │       └── view.html   # Document viewer
│   └── utils/              # Utility functions
│       ├── __init__.py
│       ├── background_tasks.py # Background task processing
│       ├── cache.py        # Caching utilities
│       ├── error_handler.py # Centralized error handling
│       ├── form_validation.py # Form validation utilities
│       ├── pdf_export.py   # PDF export utilities
│       ├── pdf_utils.py    # PDF processing utilities
│       ├── pagination.py   # Pagination utilities
│       ├── rate_limiter.py # Rate limiting utilities
│       ├── security.py     # Security utilities
│       └── text_processing.py # Text processing utilities
├── instance/              # Instance-specific data
│   └── uploads/           # Uploaded documents
├── app.py                 # Application runner
├── app.log                # Application logs
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```
## Portfolio Project Notes
This project demonstrates:

1. Full-stack development with Python (Flask) and modern frontend techniques (HTMX)
2. Integration of NLP techniques and AI technologies
3. Document processing and text analysis
4. Database design and integration
5. User interface design for complex data visualization

## Features in Detail
### Document Processing
The system extracts text from various document formats (PDF, DOCX, TXT) and splits it into paragraphs for analysis. It uses PyPDF2 for PDF extraction and python-docx for DOCX files, with specialized utilities in the utils module.
### Compliance Rules Engine
The rules engine (rule_engine.py) checks documents against predefined compliance rules using:

1. Regular expression matching for specific clause patterns
2. Keyword detection for important compliance terms
3. Severity classification (High, Medium, Low)

### AI-Powered Suggestions
When a compliance issue is detected, the system generates remediation suggestions using Anthropic's Claude API (llm_service.py), providing context-appropriate clause examples that would satisfy compliance requirements. A fallback mock service is integrated directly into the LLM service and can be enabled by setting USE_MOCK_LLM=True in your environment variables or .env file.
### Interactive User Interface
The interface provides:

1. Document uploading and management
2. Real-time compliance checking
3. Highlighted issues in the document view
4. Detailed compliance reports
5. Interactive suggestion generation with Claude
6. Debug tools for testing API integration

## Recent Improvements

1. **Error Handling**:
   - Implemented a centralized error handling system with custom `AppError` class
   - Added decorators for route error handling with user-friendly feedback

2. **User Experience**:
   - Added toast notification system for improved user feedback
   - Implemented dark mode support for better accessibility
   - Enhanced mobile responsiveness for all device sizes

3. **Performance Optimization**:
   - Added document caching to improve retrieval speed
   - Implemented pagination for document lists to handle large datasets
   - Added background task processing for long-running operations

4. **Security Enhancements**:
   - Implemented input validation and sanitization to prevent XSS attacks
   - Added CSRF protection for all forms
   - Implemented rate limiting to prevent abuse
   - Added API key authentication for API endpoints

5. **Feature Additions**:
   - Created a RESTful API for programmatic access to all features
   - Added PDF export functionality for compliance reports
   - Implemented advanced search and filtering for documents
   - Added health check endpoints for monitoring

6. **Code Quality**:
   - Fixed metadata loading and compliance score display issues
   - Consolidated LLM services by integrating mock functionality
   - Added configuration options for toggling features
   - Improved error handling and debugging information

## Future Enhancements
### Potential enhancements for this project:

1. Support for additional document formats (HTML, XML, etc.)
2. More compliance standards (SOX, CCPA, etc.)
3. Machine learning model for automatic classification of document type
4. User-defined custom compliance rules with a rule builder interface
5. Advanced analytics dashboard with compliance trends and insights
6. Integration with document management systems (SharePoint, Google Drive)
7. Multi-language support for international compliance standards
8. Collaborative review features with user roles and permissions
9. Automated scheduled compliance checks for document repositories
10. Advanced Claude prompt engineering for even more precise suggestions
11. Improved test coverage and CI/CD integration

## API Documentation

The application provides a RESTful API for programmatic access to all features. API endpoints are secured with API key authentication and rate limiting.

### Authentication

All API requests require an API key to be included in the request headers:

```
X-API-Key: your-api-key
```

### Endpoints

- `GET /api/documents` - List all documents with pagination and filtering
- `GET /api/documents/{document_id}` - Get a specific document by ID
- `GET /api/documents/{document_id}/compliance` - Get compliance information for a document
- `POST /api/documents/{document_id}/check` - Check compliance for a document
- `GET /api/documents/{document_id}/export/pdf` - Export a document as PDF
- `GET /api/documents/{document_id}/compliance/export/pdf` - Export compliance report as PDF
- `GET /api/rules` - List all compliance rules
- `GET /api/stats` - Get application statistics

