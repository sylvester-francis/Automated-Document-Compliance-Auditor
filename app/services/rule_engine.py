# app/services/rule_engine.py
import re
import uuid
from typing import List, Dict, Any
from flask import current_app

from app.models.compliance import ComplianceType, RuleType, Severity, ComplianceRule, ComplianceIssue

def get_compliance_rules(compliance_types: List[str]) -> List[ComplianceRule]:
    """
    Get compliance rules for the specified compliance types
    
    Args:
        compliance_types: List of compliance types (e.g., ['GDPR', 'HIPAA'])
        
    Returns:
        List of ComplianceRule objects
    """
    from app.extensions import mongo
    
    rules_data = list(mongo.db.compliance_rules.find({
        "compliance_type": {"$in": compliance_types},
        "is_active": True
    }))
    
    return [ComplianceRule.from_dict(rule_data) for rule_data in rules_data]

def check_regex_rule(rule: ComplianceRule, paragraph: Dict) -> bool:
    """
    Check if a paragraph matches a regex rule
    
    Args:
        rule: ComplianceRule object
        paragraph: Paragraph data
        
    Returns:
        True if rule matches, False otherwise
    """
    try:
        pattern = re.compile(rule.pattern, re.IGNORECASE)
        return bool(pattern.search(paragraph["text"]))
    except Exception as e:
        current_app.logger.error(f"Error checking regex rule: {str(e)}")
        return False

def check_keyword_rule(rule: ComplianceRule, paragraph: Dict) -> bool:
    """
    Check if a paragraph matches a keyword rule
    
    Args:
        rule: ComplianceRule object
        paragraph: Paragraph data
        
    Returns:
        True if rule matches, False otherwise
    """
    keywords = rule.pattern.split(',')
    paragraph_text = paragraph["text"].lower()
    
    for keyword in keywords:
        if keyword.strip().lower() in paragraph_text:
            return True
    
    return False

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
                    suggestions=[rule.suggestion_template] if rule.suggestion_template else []
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
    from app.extensions import mongo
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