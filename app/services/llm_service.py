# app/services/llm_service.py
import openai
from flask import current_app
from typing import List, Dict, Any

def initialize_openai():
    """Initialize OpenAI API with key from config"""
    openai.api_key = current_app.config['OPENAI_API_KEY']

def generate_suggestion(document: Dict, issue: Dict) -> str:
    """
    Generate suggestion for fixing a compliance issue using OpenAI
    
    Args:
        document: Document data
        issue: Compliance issue data
        
    Returns:
        Suggestion text
    """
    # Check if we have an API key
    if not current_app.config['OPENAI_API_KEY']:
        return "Please configure OpenAI API key to get AI-powered suggestions."
    
    try:
        initialize_openai()
        
        # Get the paragraph with the issue
        paragraph = next((p for p in document.get("paragraphs", []) if p["id"] == issue["paragraph_id"]), None)
        if not paragraph:
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
        
        # Generate suggestion using the ChatCompletion API (newer than Completion API)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a legal and compliance expert specializing in GDPR, HIPAA and other regulatory frameworks."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )
        
        suggestion = response.choices[0].message.content.strip()
        return suggestion
        
    except Exception as e:
        current_app.logger.error(f"Error generating suggestion: {str(e)}")
        return "Error generating suggestion. Please try again later."