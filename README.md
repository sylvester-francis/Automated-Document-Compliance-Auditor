# Automated Document Compliance Auditor

![Compliance Auditor Banner](https://img.shields.io/badge/Compliance-Auditor-blue) ![Python](https://img.shields.io/badge/Python-3.9+-green) ![Flask](https://img.shields.io/badge/Flask-3.1.0-lightgrey) ![MongoDB](https://img.shields.io/badge/MongoDB-4.12.1-green) ![Anthropic Claude](https://img.shields.io/badge/Claude-API-purple)

A GenAI-powered tool that scans contracts and regulatory filings for missing clauses and suggests remediation using Anthropic's Claude API.

## Overview

The Automated Document Compliance Auditor is a Flask-based web application that helps organizations ensure their documents comply with various regulations such as GDPR and HIPAA. It analyzes documents to identify missing clauses and provides AI-powered suggestions for remediation using Anthropic's Claude API.

![Application Screenshot](https://via.placeholder.com/800x400?text=Document+Compliance+Auditor)

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

## Application Screenshots

### Document List View
![Document List](https://via.placeholder.com/800x400?text=Document+List+View)
*Browse uploaded documents with filtering and sorting options*

### Document View
![Document View](https://via.placeholder.com/800x400?text=Document+View)
*View document content with compliance issues highlighted*

### Compliance Check Results
![Compliance Results](https://via.placeholder.com/800x400?text=Compliance+Results)
*View detailed compliance issues and get AI-powered suggestions*

### Dark Mode Support
![Dark Mode](https://via.placeholder.com/800x400?text=Dark+Mode)
*Toggle between light and dark mode for comfortable viewing*

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Browser                           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Flask Web Server                        │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   Routes    │───▶│  Services   │───▶│  Document Parser    │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│         │                  │                      │              │
│         ▼                  ▼                      ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Templates   │    │ Rule Engine │    │ PDF Export Service  │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
┌─────────────────┐ ┌─────────────────┐ ┌───────────────────┐
│    MongoDB      │ │  Anthropic API  │ │  Cache System     │
│  (Document DB)  │ │  (Claude LLM)   │ │  (Flask-Caching)  │
└─────────────────┘ └─────────────────┘ └───────────────────┘
```

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
- **PDF Generation**: ReportLab for PDF report generation
- **Background Processing**: APScheduler for handling long-running tasks

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB
- Anthropic API key (for AI suggestions)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/sylvester-francis/Automated-Document-Compliance-Auditor.git
cd Automated-Document-Compliance-Auditor
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
# venv\Scripts\activate
```

3. **Install the dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up MongoDB**

Make sure MongoDB is running on your system. You can install it following the [official MongoDB installation guide](https://docs.mongodb.com/manual/installation/).

5. **Create the instance directory and .env file**

```bash
mkdir -p instance
touch instance/.env
```

Edit the `.env` file and add the following configuration:

```bash
SECRET_KEY=your-secret-key
MONGO_URI=mongodb://localhost:27017/compliance_auditor
ANTHROPIC_API_KEY=your-anthropic-api-key
USE_MOCK_LLM=False  # Set to True to use mock LLM service instead of Claude API
API_KEY=your-api-key  # For accessing the API endpoints
MAX_CONTENT_LENGTH=10485760  # Maximum file size (10MB)
ALLOWED_EXTENSIONS=pdf,docx,txt  # Allowed file extensions
```

> **Note:** You'll need to obtain an Anthropic API key from [Anthropic's website](https://www.anthropic.com/). If you don't have one, you can set `USE_MOCK_LLM=True` to use the mock LLM service for testing.

6. **Run the application**

```bash
python app.py
```

7. **Access the application**

Open your browser and navigate to http://localhost:5006

## Docker Deployment

The application can also be deployed using Docker for easier setup and consistent environments.

### Using Docker Compose (Recommended)

1. **Clone the repository**

```bash
git clone https://github.com/sylvester-francis/Automated-Document-Compliance-Auditor.git
cd Automated-Document-Compliance-Auditor
```

2. **Set your Anthropic API key as an environment variable**

```bash
export ANTHROPIC_API_KEY=your_anthropic_api_key

# Alternatively, to use the mock LLM service (no API key required)
export USE_MOCK_LLM=True
```

3. **Start the application with Docker Compose**

```bash
docker-compose up -d
```

4. **Access the application**

Open your browser and navigate to http://localhost:5006

### Using Docker without Compose

1. **Build the Docker image**

```bash
docker build -t document-compliance-auditor .
```

2. **Run the container**

```bash
docker run -p 5006:5006 \
  -e MONGO_URI=your_mongo_uri \
  -e ANTHROPIC_API_KEY=your_api_key \
  -e SECRET_KEY=your_secret_key \
  document-compliance-auditor
```

> **Note:** When using Docker without Compose, you'll need to set up MongoDB separately and provide the correct connection URI.

## Usage

### Document Management

1. **Upload Documents**
   - Click the "Upload New Document" button on the documents list page
   - Select a file (PDF, DOCX, or TXT) from your computer
   - The system will process the document and extract text and metadata

2. **Browse Documents**
   - Use the search bar to find documents by filename or content
   - Filter documents by type (PDF, DOCX, TXT) using the dropdown menu
   - Sort documents by date, name, or compliance score
   - Toggle between ascending and descending order

3. **View Document Details**
   - Click on a document card to view its details
   - Navigate between document content, compliance issues, and metadata using the tabs
   - Toggle between light and dark mode using the theme switch in the navigation bar

### Compliance Checking

1. **Run Compliance Check**
   - Click the "Run Compliance Check" button on the document view page
   - The system will analyze the document against selected compliance standards
   - View the compliance score and issues found

2. **Review Compliance Issues**
   - Issues are highlighted in the document content
   - Click on an issue to see details and suggestions
   - Generate AI-powered suggestions using the "Generate Suggestion (Claude)" button

3. **Export Compliance Report**
   - Click the "Export PDF Report" button to generate a PDF report
   - The report includes document details, compliance score, issues, and suggestions

### API Access

All functionality is also available through the API. See the [API Documentation](#api-documentation) section for details.

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

## Development

### Code Quality

This project uses ruff and flake8 for code quality checks. To run these checks locally:

1. **Run ruff**:

```bash
# Navigate to your project directory
cd /Users/sylvester/Desktop/Automated-Document-Compliance-Auditor

# Activate virtual environment
source venv/bin/activate

# Run ruff on the entire codebase
ruff check .

# To automatically fix some issues
ruff check --fix .
```

2. **Run flake8**:

```bash
# Run flake8 on the entire codebase
flake8 .
```

### CI/CD Pipeline

This project includes a GitHub Actions workflow for continuous integration and deployment. The workflow is defined in `.github/workflows/ci-cd.yml` and includes the following stages:

1. **Lint**: Runs ruff and flake8 to check code quality
2. **Test**: Runs pytest with coverage reporting
3. **Build**: Builds and pushes a Docker image to DockerHub (on main/master branch)
4. **Deploy**: Deploys the application to production (on main/master branch)

The CI/CD pipeline uses GitHub Container Registry (GHCR) to store Docker images, which is free for public repositories. The pipeline automatically handles authentication using GitHub Actions' built-in secrets.

If you're using the deployment step, you'll need to set up the following GitHub secrets:

- `DEPLOY_USER`: SSH username for deployment (if using SSH deployment)
- `DEPLOY_HOST`: SSH host for deployment (if using SSH deployment)

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

