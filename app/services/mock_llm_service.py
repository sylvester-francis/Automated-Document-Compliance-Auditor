# app/services/mock_llm_service.py
import logging
import random
from typing import Dict

logger = logging.getLogger(__name__)

def generate_mock_suggestion(document: Dict, issue: Dict) -> str:
    """
    Generate a mock suggestion for testing without using Anthropic API
    
    Args:
        document: Document data
        issue: Compliance issue data
        
    Returns:
        Mock suggestion text
    """
    logger.info(f"Generating mock suggestion for issue: {issue.get('issue_id')}")
    
    # Dictionary of mock suggestions by compliance type and issue description keywords
    suggestions = {
        "GDPR": {
            "right to access": "You have the right to access and obtain a copy of your personal data that we process. To exercise this right, please contact us at privacy@example.com with your request.",
            "right to erasure": "You have the right to request the deletion of your personal data in certain circumstances. To exercise your right to erasure, please contact our Data Protection Officer at dpo@example.com.",
            "data processing": "We collect and process your personal data for the following specific purposes: (1) to provide our services to you, (2) to improve our website functionality, (3) to communicate with you about our products and services, and (4) to comply with legal obligations."
        },
        "HIPAA": {
            "notice of privacy": "This Notice of Privacy Practices describes how we may use and disclose your protected health information to carry out treatment, payment, or healthcare operations and for other purposes permitted or required by law.",
            "right to amend": "You have the right to request that we amend your health information if you believe it is incorrect or incomplete. To request an amendment, please submit your request in writing to our Privacy Officer at privacy@example.com.",
            "disclosure accounting": "You have the right to receive an accounting of certain disclosures we have made of your protected health information for purposes other than treatment, payment, healthcare operations, or certain other activities."
        }
    }
    
    compliance_type = issue.get("compliance_type", "GDPR")
    description = issue.get("description", "").lower()
    
    # Try to find a matching suggestion
    if compliance_type in suggestions:
        for keyword, suggestion_text in suggestions[compliance_type].items():
            if keyword in description:
                return suggestion_text
    
    # Fallback generic suggestions
    generic_suggestions = [
        "We recommend adding a clear clause addressing this compliance requirement in this section of your document.",
        "This section should include specific language about user rights and data handling procedures to meet regulatory requirements.",
        "Consider adding language that explicitly outlines the processes and protections in place to address this compliance concern."
    ]
    
    return random.choice(generic_suggestions)