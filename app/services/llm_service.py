# app/services/llm_service.py
import logging
import random
from typing import Dict, Any
from flask import current_app
from anthropic import Anthropic

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def generate_suggestion(document: Dict, issue: Dict) -> str:
    """
    Generate suggestion for fixing a compliance issue using Anthropic's Claude
    If API key is not configured or USE_MOCK_LLM is set to True, falls back to mock suggestions
    
    Args:
        document: Document data
        issue: Compliance issue data
        
    Returns:
        Suggestion text
    """
    # Print to standard output to ensure it's visible
    print("===== LLM SERVICE CALL STARTED =====")
    
    # Check if we should use mock service
    use_mock = current_app.config.get('USE_MOCK_LLM', False)
    
    # Check if we have an API key
    api_key = current_app.config.get('ANTHROPIC_API_KEY')
    if not api_key or use_mock:
        logger.warning("Using mock LLM service (no API key or mock mode enabled)")
        return generate_mock_suggestion(document, issue)
    
    try:
        # Log that we're about to make an API call
        logger.info(f"Calling Anthropic API for suggestion on issue: {issue.get('issue_id')}")
        
        # Initialize Anthropic client
        client = Anthropic(api_key=api_key)
        
        # Get the paragraph with the issue
        paragraph_text = ""
        paragraph_id = issue.get("paragraph_id", "")
        
        # Handle different paragraph formats
        if document.get("paragraphs"):
            for p in document.get("paragraphs", []):
                # Handle dictionary paragraphs
                if isinstance(p, dict) and p.get("id") == paragraph_id:
                    paragraph_text = p.get("text", "")
                    break
                # Handle string paragraphs with auto-generated IDs (p1, p2, etc.)
                elif isinstance(p, str) and paragraph_id.startswith('p') and paragraph_id[1:].isdigit():
                    idx = int(paragraph_id[1:]) - 1
                    if idx < len(document.get("paragraphs", [])):
                        if isinstance(document["paragraphs"][idx], str):
                            paragraph_text = document["paragraphs"][idx]
                            break
                        elif isinstance(document["paragraphs"][idx], dict):
                            paragraph_text = document["paragraphs"][idx].get("text", "")
                            break
        
        # If paragraph not found, try using document text
        if not paragraph_text and document.get("text"):
            paragraph_text = document.get("text")
            logger.info(f"Using full document text as paragraph not found")
        
        if not paragraph_text:
            logger.error(f"Could not find paragraph with ID: {paragraph_id}")
            return "Could not find paragraph text for this issue."
        
        # Create prompt
        prompt = f"""
        You are a legal and compliance expert. You need to suggest a fix for the following compliance issue:
        
        Document context: This is a {document.get('document_type', 'document')} that contains the following paragraph:
        
        "{paragraph_text}"
        
        The compliance issue is: {issue['description']}
        
        This issue relates to {issue['compliance_type']} compliance.
        
        Please provide a specific clause or text that could be added or modified to fix this issue.
        Keep your response concise and focused on the solution.
        """
        
        # Generate suggestion using Claude
        logger.info("Sending request to Anthropic API")
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0.5,
            system="You are a legal and compliance expert specializing in GDPR, HIPAA and other regulatory frameworks.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        suggestion = message.content[0].text
        logger.info(f"Received response from Anthropic API: {suggestion[:50]}...")
        print("===== CLAUDE API CALL COMPLETED =====")
        return suggestion
        
    except Exception as e:
        logger.error(f"Error generating suggestion with Anthropic: {str(e)}", exc_info=True)
        return f"Error generating suggestion: {str(e)}"


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
    
    print("===== MOCK LLM CALL COMPLETED =====")
    return random.choice(generic_suggestions)