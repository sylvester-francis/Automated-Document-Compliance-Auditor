import uuid
from typing import Dict, List, Any, Set
from enum import Enum
from app.extensions import mongo

class RuleType(Enum):
    REGEX = "regex"
    KEYWORD = "keyword"

class ComplianceIssue:
    def __init__(self, issue_id: str, rule_id: str, paragraph_id: str, description: str, 
                 severity: str, compliance_type: str, suggestions: List[str] = None):
        self.issue_id = issue_id
        self.rule_id = rule_id
        self.paragraph_id = paragraph_id
        self.description = description
        self.severity = severity
        self.compliance_type = compliance_type
        self.suggestions = suggestions if suggestions is not None else []
    
    def to_dict(self) -> Dict:
        return {
            "issue_id": self.issue_id,
            "rule_id": self.rule_id,
            "paragraph_id": self.paragraph_id,
            "description": self.description,
            "severity": self.severity,
            "compliance_type": self.compliance_type,
            "suggestions": self.suggestions
        }

def get_compliance_rules(compliance_types: List[str]) -> List[Dict]:
    """
    Get compliance rules for specified compliance types
    
    Args:
        compliance_types: List of compliance type names
        
    Returns:
        List of compliance rule objects
    """
    # In a real application, these would come from a database
    rules = []
    
    if "GDPR" in compliance_types:
        rules.extend([
            {
                "rule_id": "gdpr-001",
                "rule_type": RuleType.KEYWORD,
                "compliance_type": "GDPR",
                "description": "Missing information about the right to access personal data",
                "severity": "high",
                "keywords": ["right to access", "access your data", "access personal information"],
                "suggestion_template": "You have the right to access and obtain a copy of your personal data that we process. To exercise this right, please contact us at privacy@example.com with your request."
            },
            {
                "rule_id": "gdpr-002",
                "rule_type": RuleType.KEYWORD,
                "compliance_type": "GDPR",
                "description": "Missing information about the right to erasure (right to be forgotten)",
                "severity": "high",
                "keywords": ["right to erasure", "right to be forgotten", "delete your data"],
                "suggestion_template": "You have the right to request the deletion of your personal data in certain circumstances. To exercise your right to erasure, please contact our Data Protection Officer at dpo@example.com."
            },
            {
                "rule_id": "gdpr-003",
                "rule_type": RuleType.KEYWORD,
                "compliance_type": "GDPR",
                "description": "Missing information about data processing purposes",
                "severity": "medium",
                "keywords": ["data processing purposes", "why we process", "purposes of processing"],
                "suggestion_template": "We collect and process your personal data for the following specific purposes: (1) to provide our services to you, (2) to improve our website functionality, (3) to communicate with you about our products and services, and (4) to comply with legal obligations."
            }
        ])
    
    if "HIPAA" in compliance_types:
        rules.extend([
            {
                "rule_id": "hipaa-001",
                "rule_type": RuleType.KEYWORD,
                "compliance_type": "HIPAA",
                "description": "Missing Notice of Privacy Practices",
                "severity": "high",
                "keywords": ["notice of privacy practices", "privacy notice", "privacy practices"],
                "suggestion_template": "This Notice of Privacy Practices describes how we may use and disclose your protected health information to carry out treatment, payment, or healthcare operations and for other purposes permitted or required by law."
            },
            {
                "rule_id": "hipaa-002",
                "rule_type": RuleType.KEYWORD,
                "compliance_type": "HIPAA",
                "description": "Missing information about the right to amend health information",
                "severity": "medium",
                "keywords": ["right to amend", "amend your information", "correct your information"],
                "suggestion_template": "You have the right to request that we amend your health information if you believe it is incorrect or incomplete. To request an amendment, please submit your request in writing to our Privacy Officer at privacy@example.com."
            },
            {
                "rule_id": "hipaa-003",
                "rule_type": RuleType.KEYWORD,
                "compliance_type": "HIPAA",
                "description": "Missing information about disclosure accounting",
                "severity": "medium",
                "keywords": ["disclosure accounting", "disclosures of your information", "log of disclosures"],
                "suggestion_template": "You have the right to receive an accounting of certain disclosures we have made of your protected health information for purposes other than treatment, payment, healthcare operations, or certain other activities."
            }
        ])
    
    # Convert dictionaries to objects
    rule_objects = []
    for rule_dict in rules:
        rule = type('Rule', (), rule_dict)
        rule_objects.append(rule)
    
    return rule_objects

def check_regex_rule(rule, paragraph):
    """Check if paragraph matches a regex rule"""
    import re
    pattern = re.compile(rule.pattern, re.IGNORECASE)
    return not bool(pattern.search(paragraph["text"]))

def check_keyword_rule(rule, paragraph):
    """Check if paragraph does NOT contain any of the required keywords"""
    text = paragraph["text"].lower()
    
    # Rule matches if NONE of the keywords are present
    # (meaning there's a compliance issue)
    return not any(keyword.lower() in text for keyword in rule.keywords)

def check_document_compliance(document: Dict, compliance_types: List[str]) -> Dict[str, Any]:
    """
    Check a document for compliance issues
    
    Args:
        document: Document data
        compliance_types: List of compliance types to check
        
    Returns:
        Dictionary with compliance issues and score
    """
    # Get compliance rules
    rules = get_compliance_rules(compliance_types)
    
    # Initialize results
    issues = []
    paragraphs_with_issues = set()
    
    # Check each paragraph against each rule
    for paragraph in document.get("paragraphs", []):
        for rule in rules:
            # Skip if already found an issue for this rule in this paragraph
            if any(issue["rule_id"] == rule.rule_id and issue["paragraph_id"] == paragraph["id"] for issue in issues):
                continue
            
            # Check if paragraph matches rule
            matches = False
            if rule.rule_type == RuleType.REGEX:
                matches = check_regex_rule(rule, paragraph)
            elif rule.rule_type == RuleType.KEYWORD:
                matches = check_keyword_rule(rule, paragraph)
            
            # If matches, create issue
            if matches:
                issue_id = str(uuid.uuid4())
                issue = ComplianceIssue(
                    issue_id=issue_id,
                    rule_id=rule.rule_id,
                    paragraph_id=paragraph["id"],
                    description=rule.description,
                    severity=rule.severity,
                    compliance_type=rule.compliance_type,
                    suggestions=[] # Initialize with empty list to ensure the button appears
                )
                issues.append(issue.to_dict())
                paragraphs_with_issues.add(paragraph["id"])
    
    # Calculate compliance score
    total_paragraphs = len(document.get("paragraphs", []))
    if total_paragraphs > 0:
        compliance_score = 100 * (1 - len(paragraphs_with_issues) / total_paragraphs)
    else:
        compliance_score = 100
    
    # Determine compliance status
    if not issues:
        compliance_status = "compliant"
    elif compliance_score < 50:
        compliance_status = "non_compliant"
    else:
        compliance_status = "partially_compliant"
    
    # Update document with compliance results
    mongo.db.documents.update_one(
        {"_id": document["_id"]},
        {"$set": {
            "compliance_issues": issues,
            "compliance_score": compliance_score,
            "compliance_status": compliance_status
        }}
    )
    
    return {
        "issues": issues,
        "score": compliance_score,
        "status": compliance_status
    }