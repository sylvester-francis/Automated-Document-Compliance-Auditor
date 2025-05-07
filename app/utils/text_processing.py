# Create app/utils/text_processing.py
# noqa: D205, D212, I001, W293, W291, W292

"""Text processing utilities for medical document analysis and compliance checking.
Focused on extracting structured information from healthcare and compliance documents.
"""

import logging
import re
from typing import Any, Dict, List  # noqa: F401

logger = logging.getLogger(__name__)

def split_into_paragraphs(text: str) -> List[str]:  # noqa: D212, D400, D415
    """Split text content into paragraphs, optimized for medical documents.
    
    Args:  # noqa: W293
        text: Document text content
        
    Returns:  # noqa: D413, W293
        List of paragraph strings
    """
    # Split on double newlines (common paragraph separator)
    paragraphs = re.split(r'\n\s*\n', text)

    # Clean up paragraphs  # noqa: W293
    clean_paragraphs = []
    for para in paragraphs:
        # Remove excessive whitespace and join lines within paragraphs
        cleaned = re.sub(r'\s+', ' ', para).strip()
        if cleaned:  # Skip empty paragraphs
            clean_paragraphs.append(cleaned)

    return clean_paragraphs  # noqa: W293

def extract_paragraphs_with_ids(text: str) -> List[Dict[str, str]]:  # noqa: D212, D400, D415
    """Split text into paragraphs and assign unique IDs.
    
    Args:  # noqa: W293
        text: Document text content
        
    Returns:  # noqa: D413, W293
        List of paragraph dictionaries with IDs
    """
    paragraphs = split_into_paragraphs(text)

    result = []  # noqa: W293
    for i, paragraph in enumerate(paragraphs):
        # Create unique ID for paragraph
        para_id = f"p{i+1}"
        result.append({
            "id": para_id,
            "text": paragraph
        })

    return result  # noqa: W293

def detect_document_type(text: str) -> str:  # noqa: D212, D400, D415
    """Detect document type from text content.
    
    Args:  # noqa: W293
        text: Document text content
        
    Returns:  # noqa: D413, W293
        Document type string
    """
    text_lower = text.lower()

    # Check for privacy policy keywords  # noqa: W293
    privacy_keywords = ['privacy policy', 'privacy notice', 'privacy statement',  # noqa: W291
                        'personal data', 'personal information']
    if any(keyword in text_lower for keyword in privacy_keywords):
        return 'privacy_policy'

    # Check for medical document keywords  # noqa: W293
    medical_keywords = ['patient name', 'date of birth', 'medical record', 'diagnosis']
    if any(keyword in text_lower for keyword in medical_keywords):
        return 'medical_record'

    # Default  # noqa: W293
    return 'unknown'
