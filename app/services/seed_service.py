# app/services/seed_service.py
import uuid
from app.models.compliance import ComplianceRule, ComplianceType, RuleType, Severity

def seed_compliance_rules():
    """Seed the database with sample compliance rules"""
    from app.extensions import mongo
    
    # Check if rules already exist
    if mongo.db.compliance_rules.count_documents({}) > 0:
        return
    
    # Create sample GDPR rules
    gdpr_rules = [
        ComplianceRule(
            rule_id=str(uuid.uuid4()),
            name="GDPR Right to Access",
            description="Document must include information about the right to access personal data",
            compliance_type=ComplianceType.GDPR,
            rule_type=RuleType.REGEX,
            pattern=r"right\s+to\s+access|access\s+to\s+(?:your|their)\s+(?:data|information)|request\s+(?:access|copy)",
            severity=Severity.HIGH,
            suggestion_template="You have the right to access your personal data that we process. To request access, please contact us at [CONTACT DETAILS]."
        ),
        ComplianceRule(
            rule_id=str(uuid.uuid4()),
            name="GDPR Right to Erasure",
            description="Document must include information about the right to erasure (right to be forgotten)",
            compliance_type=ComplianceType.GDPR,
            rule_type=RuleType.REGEX,
            pattern=r"right\s+to\s+(?:erasure|be\s+forgotten)|delete\s+(?:your|their)\s+(?:data|information)",
            severity=Severity.HIGH,
            suggestion_template="You have the right to request the erasure of your personal data in certain circumstances. To request erasure, please contact us at [CONTACT DETAILS]."
        ),
        ComplianceRule(
            rule_id=str(uuid.uuid4()),
            name="GDPR Data Processing Purposes",
            description="Document must clearly state the purposes of data processing",
            compliance_type=ComplianceType.GDPR,
            rule_type=RuleType.KEYWORD,
            pattern="purpose,processing,collect,use,data",
            severity=Severity.MEDIUM,
            suggestion_template="We collect and process your personal data for the following purposes: [LIST PURPOSES]."
        )
    ]
    
    # Create sample HIPAA rules
    hipaa_rules = [
        ComplianceRule(
            rule_id=str(uuid.uuid4()),
            name="HIPAA Notice of Privacy Practices",
            description="Document must include information about the Notice of Privacy Practices",
            compliance_type=ComplianceType.HIPAA,
            rule_type=RuleType.REGEX,
            pattern=r"notice\s+of\s+privacy\s+practices|privacy\s+notice|privacy\s+practices",
            severity=Severity.HIGH,
            suggestion_template="This Notice of Privacy Practices describes how we may use and disclose your protected health information to carry out treatment, payment, or healthcare operations and for other purposes permitted or required by law."
        ),
        ComplianceRule(
            rule_id=str(uuid.uuid4()),
            name="HIPAA Right to Amend",
            description="Document must include information about the right to amend health information",
            compliance_type=ComplianceType.HIPAA,
            rule_type=RuleType.REGEX,
            pattern=r"right\s+to\s+amend|amend\s+(?:your|their)\s+(?:information|record)",
            severity=Severity.MEDIUM,
            suggestion_template="You have the right to request an amendment to your protected health information if you believe it is incorrect or incomplete. To request an amendment, please submit your request in writing to [CONTACT DETAILS]."
        ),
        ComplianceRule(
            rule_id=str(uuid.uuid4()),
            name="HIPAA Disclosure Accounting",
            description="Document must include information about the right to an accounting of disclosures",
            compliance_type=ComplianceType.HIPAA,
            rule_type=RuleType.KEYWORD,
            pattern="accounting,disclosure,disclosures",
            severity=Severity.MEDIUM,
            suggestion_template="You have the right to request an accounting of certain disclosures we have made of your protected health information for purposes other than treatment, payment, healthcare operations, or certain other activities."
        )
    ]
    
    # Insert rules into MongoDB
    all_rules = gdpr_rules + hipaa_rules
    rules_dicts = [rule.to_dict() for rule in all_rules]
    mongo.db.compliance_rules.insert_many(rules_dicts)