# Automated Document Compliance Auditor

A GenAI tool that scans contracts and regulatory filings for missing clauses and suggests remediation.

## Overview

The Automated Document Compliance Auditor is a Flask-based web application that helps organizations ensure their documents comply with various regulations such as GDPR and HIPAA. It analyzes documents to identify missing clauses and provides AI-powered suggestions for remediation.

## Key Features

- **Document Processing**: Extract text from PDF, DOCX, and TXT files
- **Rule-based Compliance Checking**: Detect missing clauses using regex and keyword patterns
- **AI-Powered Suggestions**: Generate remediation text using Anthropic's Claude API
- **Interactive UI**: Real-time highlighting and inline editing
- **Domain-specific Compliance**: Support for GDPR, HIPAA, and other standards

## Technology Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, JavaScript with HTMX for interactivity
- **Database**: MongoDB for document storage
- **Text Processing**: PyPDF2, python-docx for document parsing
- **AI Integration**: Anthropic Claude API for generating suggestions
- **Styling**: Bootstrap 5 for responsive design

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB
- Anthropic API key (for AI suggestions)

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
```
5. Run the app
```bash
python app.py
```
6. Open your browser and navigate to http://localhost:5000

## Usage

1. Upload a document (PDF, DOCX, or TXT)
2. The system will process the document and extract text
3. Check compliance against selected standards (GDPR, HIPAA, etc.)
4. View compliance issues and get AI-powered suggestions for remediation
5. Generate suggestions using the "Generate Suggestion (Claude)" button

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
│   │   ├── llm_service.py         # Claude API integration
│   │   ├── mock_llm_service.py    # Fallback mock service
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
│       ├── pdf_utils.py    # PDF processing utilities
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
When a compliance issue is detected, the system generates remediation suggestions using Anthropic's Claude API (llm_service.py), providing context-appropriate clause examples that would satisfy compliance requirements. A fallback mock service (mock_llm_service.py) is available for testing without API access.
### Interactive User Interface
The interface provides:

1. Document uploading and management
2. Real-time compliance checking
3. Highlighted issues in the document view
4. Detailed compliance reports
5. Interactive suggestion generation with Claude
6. Debug tools for testing API integration

## Future Enhancements
### Potential enhancements for this project:

1. Support for additional document formats
2. More compliance standards (SOX, CCPA, etc.)
3. Machine learning model for automatic classification of document type
4. User-defined custom compliance rules
5. Bulk document processing
6. Export of compliance reports to PDF
7. Advanced Claude prompt engineering for even more precise suggestions

