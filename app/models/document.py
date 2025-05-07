# app/models/document.py
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional

class DocumentType(str, Enum):
    CONTRACT = "contract"
    POLICY = "policy"
    AGREEMENT = "agreement"
    TERMS = "terms"
    PRIVACY = "privacy"
    OTHER = "other"

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    PENDING_REVIEW = "pending_review"

class Document:
    """Document model for MongoDB storage"""
    def __init__(
        self, 
        document_id: str,
        filename: str,
        file_path: str,
        content: str = "",
        document_type: DocumentType = DocumentType.OTHER,
        paragraphs: List[Dict] = None,
        compliance_score: float = 0.0,
        compliance_status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW,
        compliance_issues: List[Dict] = None,
        metadata: Dict = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.document_id = document_id
        self.filename = filename
        self.file_path = file_path
        self.content = content
        self.document_type = document_type
        self.paragraphs = paragraphs or []
        self.compliance_score = compliance_score
        self.compliance_status = compliance_status
        self.compliance_issues = compliance_issues or []
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        
    def to_dict(self):
        """Convert to dictionary for MongoDB storage"""
        return {
            "_id": self.document_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "content": self.content,
            "document_type": self.document_type,
            "paragraphs": self.paragraphs,
            "compliance_score": self.compliance_score,
            "compliance_status": self.compliance_status,
            "compliance_issues": self.compliance_issues,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary retrieved from MongoDB"""
        return cls(
            document_id=data["_id"],
            filename=data["filename"],
            file_path=data["file_path"],
            content=data.get("content", ""),
            document_type=data.get("document_type", DocumentType.OTHER),
            paragraphs=data.get("paragraphs", []),
            compliance_score=data.get("compliance_score", 0.0),
            compliance_status=data.get("compliance_status", ComplianceStatus.PENDING_REVIEW),
            compliance_issues=data.get("compliance_issues", []),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )