"""
Tests for the rule engine.
"""
from app.services.rule_engine import (
    check_document_compliance,
    check_regex_rule,
    check_keyword_rule,
    get_compliance_rules
)


class TestRuleEngine:
    """Tests for the rule engine."""

    def test_get_compliance_rules(self, app):
        """Test getting compliance rules."""
        with app.app_context():
            # Get rules for GDPR
            rules = get_compliance_rules(['GDPR'])
            
            # Verify that we got GDPR rules
            assert len(rules) > 0
            for rule in rules:
                assert rule['compliance_type'] == 'GDPR'
            
            # Get rules for HIPAA
            rules = get_compliance_rules(['HIPAA'])
            
            # Verify that we got HIPAA rules
            assert len(rules) > 0
            for rule in rules:
                assert rule['compliance_type'] == 'HIPAA'
            
            # Get rules for both GDPR and HIPAA
            rules = get_compliance_rules(['GDPR', 'HIPAA'])
            
            # Verify that we got both GDPR and HIPAA rules
            assert len(rules) > 0
            gdpr_rules = [rule for rule in rules if rule['compliance_type'] == 'GDPR']
            hipaa_rules = [rule for rule in rules if rule['compliance_type'] == 'HIPAA']
            assert len(gdpr_rules) > 0
            assert len(hipaa_rules) > 0
    
    def test_check_regex_rule(self):
        """Test checking a regex rule."""
        # Create a test rule
        rule = {
            'rule_id': 'test-regex-001',
            'rule_type': 'regex',
            'pattern': r'confidential',
            'description': 'Contains confidential information'
        }
        
        # Test with a paragraph that matches the rule
        paragraph = {'id': 'p1', 'text': 'This document contains confidential information.'}
        assert check_regex_rule(rule, paragraph) is True
        
        # Test with a paragraph that doesn't match the rule
        paragraph = {'id': 'p2', 'text': 'This document contains public information.'}
        assert check_regex_rule(rule, paragraph) is False
        
        # Test with a paragraph as a string
        paragraph = 'This document contains confidential information.'
        assert check_regex_rule(rule, paragraph) is True
    
    def test_check_keyword_rule(self):
        """Test checking a keyword rule."""
        # Create a test rule
        rule = {
            'rule_id': 'test-keyword-001',
            'rule_type': 'keyword',
            'keywords': ['privacy', 'data protection', 'personal data'],
            'description': 'Missing privacy information'
        }
        
        # Test with a paragraph that doesn't contain any keywords (rule matches)
        paragraph = {'id': 'p1', 'text': 'This document contains general information.'}
        assert check_keyword_rule(rule, paragraph) is True
        
        # Test with a paragraph that contains a keyword (rule doesn't match)
        paragraph = {'id': 'p2', 'text': 'This document contains information about privacy.'}
        assert check_keyword_rule(rule, paragraph) is False
        
        # Test with a paragraph as a string
        paragraph = 'This document contains information about data protection.'
        assert check_keyword_rule(rule, paragraph) is False
    
    def test_check_document_compliance(self, app):
        """Test checking document compliance."""
        with app.app_context():
            # Create a test document
            document = {
                '_id': 'test-compliance-id',
                'document_id': 'test-compliance-id',
                'paragraphs': [
                    {'id': 'p1', 'text': 'This is a test document.'},
                    {'id': 'p2', 'text': 'It does not mention privacy or data protection.'},
                    {'id': 'p3', 'text': 'It does not include a notice of privacy practices.'}
                ]
            }
            
            # Check compliance for GDPR
            results = check_document_compliance(document, ['GDPR'])
            
            # Verify results
            assert 'issues' in results
            assert 'score' in results
            assert 'status' in results
            
            # There should be issues because the document doesn't mention privacy
            assert len(results['issues']) > 0
            
            # Check compliance for HIPAA
            results = check_document_compliance(document, ['HIPAA'])
            
            # Verify results
            assert 'issues' in results
            assert 'score' in results
            assert 'status' in results
            
            # There should be issues because the document doesn't mention privacy practices
            assert len(results['issues']) > 0
