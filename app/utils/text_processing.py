# Create app/utils/text_processing.py

"""
Text processing utilities for medical document analysis and compliance checking.
Focused on extracting structured information from healthcare and compliance documents.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def split_into_paragraphs(text: str) -> List[str]:
    """
    Split text content into paragraphs, optimized for medical documents
    
    Args:
        text: Document text content
        
    Returns:
        List of paragraph strings
    """
    # Split on double newlines (common paragraph separator)
    paragraphs = re.split(r'\n\s*\n', text)
    
    # Clean up paragraphs
    clean_paragraphs = []
    for para in paragraphs:
        # Remove excessive whitespace and join lines within paragraphs
        cleaned = re.sub(r'\s+', ' ', para).strip()
        if cleaned:  # Skip empty paragraphs
            clean_paragraphs.append(cleaned)
    
    return clean_paragraphs

def extract_paragraphs_with_ids(text: str) -> List[Dict[str, str]]:
    """
    Split text into paragraphs and assign unique IDs
    
    Args:
        text: Document text content
        
    Returns:
        List of paragraph dictionaries with IDs
    """
    paragraphs = split_into_paragraphs(text)
    
    result = []
    for i, paragraph in enumerate(paragraphs):
        # Create unique ID for paragraph
        para_id = f"p{i+1}"
        result.append({
            "id": para_id,
            "text": paragraph
        })
    
    return result

def detect_document_type(text: str) -> str:
    """
    Detect document type from text content
    
    Args:
        text: Document text content
        
    Returns:
        Document type string
    """
    text_lower = text.lower()
    
    # Check for privacy policy keywords
    privacy_keywords = ['privacy policy', 'privacy notice', 'privacy statement', 
                        'personal data', 'personal information']
    if any(keyword in text_lower for keyword in privacy_keywords):
        return 'privacy_policy'
    
    # Check for medical document keywords
    medical_keywords = ['patient name', 'date of birth', 'medical record', 'diagnosis']
    if any(keyword in text_lower for keyword in medical_keywords):
        return 'medical_record'
    
    # Default
    return 'unknown'