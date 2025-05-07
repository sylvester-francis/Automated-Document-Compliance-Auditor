# app/models/compliance.py
from enum import Enum
from typing import List, Dict

class ComplianceType(str, Enum):
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    CCPA = "CCPA"
    SOX = "SOX"
    PCI_DSS = "PCI_DSS"
    
class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RuleType(str, Enum):
    REGEX = "regex"
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    
class ComplianceRule:
    """Compliance rule model for MongoDB storage"""
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        compliance_type: ComplianceType,
        rule_type: RuleType,
        pattern: str,
        severity: Severity = Severity.MEDIUM,
        suggestion_template: str = None,
        metadata: Dict = None,
        is_active: bool = True
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.compliance_type = compliance_type
        self.rule_type = rule_type
        self.pattern = pattern
        self.severity = severity
        self.suggestion_template = suggestion_template
        self.metadata = metadata or {}
        self.is_active = is_active
    
    def to_dict(self):
        """Convert to dictionary for MongoDB storage"""
        return {
            "_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "compliance_type": self.compliance_type,
            "rule_type": self.rule_type,
            "pattern": self.pattern,
            "severity": self.severity,
            "suggestion_template": self.suggestion_template,
            "metadata": self.metadata,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary retrieved from MongoDB"""
        return cls(
            rule_id=data["_id"],
            name=data["name"],
            description=data["description"],
            compliance_type=data["compliance_type"],
            rule_type=data["rule_type"],
            pattern=data["pattern"],
            severity=data.get("severity", Severity.MEDIUM),
            suggestion_template=data.get("suggestion_template"),
            metadata=data.get("metadata", {}),
            is_active=data.get("is_active", True)
        )

class ComplianceIssue:
    """Compliance issue found in a document"""
    def __init__(
        self,
        issue_id: str,
        rule_id: str,
        paragraph_id: str,
        description: str,
        severity: Severity,
        compliance_type: ComplianceType,
        suggestions: List[str] = None
    ):
        self.issue_id = issue_id
        self.rule_id = rule_id
        self.paragraph_id = paragraph_id
        self.description = description
        self.severity = severity
        self.compliance_type = compliance_type
        self.suggestions = suggestions or []
    
    def to_dict(self):
        """Convert to dictionary for MongoDB storage"""
        return {
            "issue_id": self.issue_id,
            "rule_id": self.rule_id,
            "paragraph_id": self.paragraph_id,
            "description": self.description,
            "severity": self.severity,
            "compliance_type": self.compliance_type,
            "suggestions": self.suggestions
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary retrieved from MongoDB"""
        return cls(
            issue_id=data["issue_id"],
            rule_id=data["rule_id"],
            paragraph_id=data["paragraph_id"],
            description=data["description"],
            severity=data["severity"],
            compliance_type=data["compliance_type"],
            suggestions=data.get("suggestions", [])
        )