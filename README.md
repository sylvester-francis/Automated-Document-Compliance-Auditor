# Automated Document Compliance Auditor

A GenAI tool that scans contracts and regulatory filings for missing clauses and suggests remediation.

## Overview

The Automated Document Compliance Auditor is a Flask-based web application that helps organizations ensure their documents comply with various regulations such as GDPR and HIPAA. It analyzes documents to identify missing clauses and provides AI-powered suggestions for remediation.

## Key Features

- **Document Processing**: Extract text from PDF, DOCX, and TXT files
- **Rule-based Compliance Checking**: Detect missing clauses using regex and keyword patterns
- **AI-Powered Suggestions**: Generate remediation text using OpenAI API
- **Interactive UI**: Real-time highlighting and inline editing
- **Domain-specific Compliance**: Support for GDPR, HIPAA, and other standards

## Technology Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, JavaScript with HTMX for interactivity
- **Database**: MongoDB for document storage
- **Text Processing**: PyPDF2, python-docx for document parsing
- **AI Integration**: OpenAI API for generating suggestions
- **Styling**: Bootstrap 5 for responsive design

## Getting Started

### Prerequisites

- Python 3.8+
- MongoDB
- OpenAI API key (optional, for AI suggestions)

### Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/Automated-Document-Compliance-Auditor.git
cd Automated-Document-Compliance-Auditor
```
2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Create a `.env` file in the `instance` directory with your configuration
```bash
SECRET_KEY=your-secret-key
MONGO_URI=mongodb://localhost:27017/compliance_auditor
OPENAI_API_KEY=your-openai-api-key  # Optional
```
5. Run the application
```bash
python app.py
```
6. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Upload a document (PDF, DOCX, or TXT)
2. The system will process the document and extract text
3. Check compliance against selected standards (GDPR, HIPAA, etc.)
4. View compliance issues and get AI-powered suggestions for remediation

## Project Structure
```bash
Automated-Document-Compliance-Auditor/
├── app/                   # Flask application
│   ├── init.py            # App initialization
│   ├── config.py          # Configuration settings
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── static/            # Static assets
│   ├── templates/         # Jinja2 templates
│   ├── utils/             # Helper functions
│   └── routes/            # View functions
├── instance/              # Instance-specific data
├── venv/                  # Virtual environment
├── app.py                 # Application runner
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
The system extracts text from various document formats (PDF, DOCX, TXT) and splits it into paragraphs for analysis. It uses PyPDF2 for PDF extraction and python-docx for DOCX files.

### Compliance Rules Engine
The rules engine checks documents against predefined compliance rules using:
- Regular expression matching for specific clause patterns
- Keyword detection for important compliance terms
- Severity classification (High, Medium, Low)

### AI-Powered Suggestions
When a compliance issue is detected, the system can generate remediation suggestions using OpenAI's API, providing context-appropriate clause examples that would satisfy compliance requirements.

### Interactive User Interface
The interface provides:
- Document uploading and management
- Real-time compliance checking
- Highlighted issues in the document view
- Detailed compliance reports
- Interactive suggestion generation

## Future Enhancements

Potential enhancements for this project:
- Support for additional document formats
- More compliance standards (SOX, CCPA, etc.)
- Machine learning model for automatic classification of document type
- User-defined custom compliance rules
- Bulk document processing
- Export of compliance reports to PDF
