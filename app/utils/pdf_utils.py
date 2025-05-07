# First, let's create the basic structure in app/utils/pdf_utils.py

"""
PDF Utility functions for medical document processing.
Tailored for processing healthcare-related documents with a focus on compliance analysis.
"""

import io
import logging

# Common libraries for PDF processing
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str, file_content: bytes = None) -> str:
    """
    Extract full text content from a PDF file with enhanced handling for medical documents.
    
    Args:
        file_path: Path to the PDF file
        file_content: Optional bytes content of the PDF file
        
    Returns:
        Extracted text as a string
    """
    try:
        if file_content:
            # Use bytes content if provided
            file_object = io.BytesIO(file_content)
        else:
            # Otherwise open file from path
            file_object = open(file_path, 'rb')
        
        # Create PDF reader object
        pdf_reader = PdfReader(file_object)
        
        # Extract text from each page
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n\n"
        
        # Close file if it was opened from path
        if not file_content:
            file_object.close()
            
        return text
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")