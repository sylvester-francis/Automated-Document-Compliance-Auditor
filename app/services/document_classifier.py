# Create app/services/document_classifier.py

"""
Document Classification Service using rule-based and machine learning approaches.
Classifies documents into various types like privacy policies, medical records, etc.
"""

import logging
import os
from typing import Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib


from app.utils.text_processing import detect_document_type

logger = logging.getLogger(__name__)

class DocumentClassifier:
    """Document classification service"""
    
    def __init__(self):
        # Try to load a pre-trained model if available
        try:
            self.model_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'models', 
                'doc_classifier.joblib'
            )
            
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info(f"Loaded document classifier model")
            else:
                # Create a simple model if no pre-trained model exists
                self._create_simple_model()
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            # Fall back to rule-based approach
            self.model = None
            logger.info("Using rule-based classification only")
    
    def _create_simple_model(self):
        """Create a simple classifier model with training data"""
        # Create a pipeline with TF-IDF and Naive Bayes
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000)),
            ('clf', MultinomialNB())
        ])
        
        # Generate some training data for medical documents
        X_train = [
            "Patient Name: John Doe, DOB: 01/15/1980, MRN: 12345678",
            "HIPAA AUTHORIZATION FOR RELEASE OF INFORMATION",
            "PRIVACY POLICY: This notice describes how medical information about you may be used",
            "DISCHARGE SUMMARY: Patient was admitted for pneumonia",
            "CONSENT FOR MEDICAL TREATMENT"
        ]
        
        y_train = [
            "medical_record",
            "hipaa_authorization",
            "privacy_policy",
            "discharge_summary",
            "consent_form"
        ]
        
        # Train the model
        self.model.fit(X_train, y_train)
        logger.info("Simple document classifier model created")


            
        
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify document based on text content
        
        Args:
            text: Document text content
            
        Returns:
            Dictionary with classification results
        """
        # Use the rule-based detection from text_processing
        doc_type = detect_document_type(text)
        
        # Calculate a mock confidence score
        confidence = 0.8 if doc_type != 'unknown' else 0.3
        
        return {
            "type": doc_type,
            "confidence": confidence
        }
    
    def classify_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Classify document from file
        
        Args:
            file_path: Path to document file
            
        Returns:
            Classification results dictionary
        """
        from app.utils.pdf_utils import extract_text_from_pdf
        
        try:
            # Extract text based on file extension
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            if ext == '.pdf':
                text = extract_text_from_pdf(file_path)
            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            else:
                return {"type": "unknown", "confidence": 0.0, "error": "Unsupported file format"}
            
            # Classify the text
            result = self.classify(text)
            
            # Add file information
            result["filename"] = os.path.basename(file_path)
            result["extension"] = ext
            
            return result
            
        except Exception as e:
            logger.error(f"Error classifying file {file_path}: {str(e)}")
            return {
                "type": "unknown", 
                "confidence": 0.0,
                "error": str(e),
                "filename": os.path.basename(file_path)
            }

# Singleton instance
_classifier_instance = None

def get_classifier():
    """Get or create the document classifier singleton instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = DocumentClassifier()
    return _classifier_instance