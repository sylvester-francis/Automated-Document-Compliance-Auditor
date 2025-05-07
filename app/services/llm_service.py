# app/services/llm_service.py
import logging
from typing import Dict, Any
from flask import current_app
from anthropic import Anthropic

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def generate_suggestion(document: Dict, issue: Dict) -> str:
    """
    Generate suggestion for fixing a compliance issue using Anthropic's Claude
    
    Args:
        document: Document data
        issue: Compliance issue data
        
    Returns:
        Suggestion text
    """
    # Print to standard output to ensure it's visible
    print("===== CLAUDE API CALL STARTED =====")
    
    # Check if we have an API key
    api_key = current_app.config.get('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("No Anthropic API key configured")
        return "Please configure Anthropic API key to get AI-powered suggestions."
    
    try:
        # Log that we're about to make an API call
        logger.info(f"Calling Anthropic API for suggestion on issue: {issue.get('issue_id')}")
        
        # Initialize Anthropic client
        client = Anthropic(api_key=api_key)
        
        # Get the paragraph with the issue
        paragraph = next((p for p in document.get("paragraphs", []) if p["id"] == issue["paragraph_id"]), None)
        if not paragraph:
            logger.error(f"Could not find paragraph with ID: {issue.get('paragraph_id')}")
            return "Could not find paragraph."
        
        # Create prompt
        prompt = f"""
        You are a legal and compliance expert. You need to suggest a fix for the following compliance issue:
        
        Document context: This is a {document.get('document_type', 'document')} that contains the following paragraph:
        
        "{paragraph['text']}"
        
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