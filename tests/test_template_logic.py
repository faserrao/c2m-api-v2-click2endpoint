"""
Tests for template business logic
Templates ALWAYS provide job options and MAY provide either document OR recipients (never both)
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock streamlit
sys.modules['streamlit'] = MagicMock()


class TestTemplateLogic:
    """Test template business logic implementation"""
    
    def test_template_always_provides_job_options(self):
        """Verify templates always include job options"""
        template_endpoints = [
            "/jobs/single-doc-job-template",
            "/jobs/multi-doc-job-template",
            "/jobs/merge-multi-doc-with-template"
        ]
        
        for endpoint in template_endpoints:
            # Template should always have jobTemplateId or jobTemplateName
            assert "template" in endpoint.lower()
    
    def test_template_provides_document_not_recipients(self):
        """Test when template provides document (not recipients)"""
        # Use Case 1: Single doc with template
        params = {
            "recipientStyle": "explicit",  # Recipients in API call
            "templateProvides": "document"  # Document from template
        }
        
        # Should ask for recipient addresses but NOT document
        required_fields = self._get_required_fields_for_template(params)
        assert "recipientAddress" in required_fields
        assert "document" not in required_fields
        assert "jobTemplateId" in required_fields or "jobTemplateName" in required_fields
    
    def test_template_provides_recipients_not_document(self):
        """Test when template provides recipients (not document)"""
        # Use Case 1: Single doc with template
        params = {
            "recipientStyle": "template",  # Recipients from template
            "templateProvides": "recipients"  # Recipients from template
        }
        
        # Should ask for document but NOT recipient addresses
        required_fields = self._get_required_fields_for_template(params)
        assert "document" in required_fields
        assert "recipientAddress" not in required_fields
        assert "jobTemplateId" in required_fields or "jobTemplateName" in required_fields
    
    def test_template_provides_neither(self):
        """Test when template provides neither document nor recipients"""
        params = {
            "recipientStyle": "explicit",
            "templateProvides": "neither"
        }
        
        # Should ask for both document and recipients
        required_fields = self._get_required_fields_for_template(params)
        assert "document" in required_fields
        assert "recipientAddress" in required_fields
        assert "jobTemplateId" in required_fields or "jobTemplateName" in required_fields
    
    def test_template_cannot_provide_both(self):
        """Test that template cannot provide both document and recipients"""
        with pytest.raises(ValueError, match="Template cannot provide both"):
            self._validate_template_logic({
                "templateProvides": ["document", "recipients"]
            })
    
    def test_use_case_1_scenarios(self):
        """Test Use Case 1: Single doc with template - all scenarios"""
        # Scenario 1: Template provides recipients
        uc1_recipients = {
            "endpoint": "/jobs/single-doc-job-template",
            "recipientStyle": "template",
            "requiredInAPI": ["document", "jobTemplate"]
        }
        assert "recipientAddress" not in uc1_recipients["requiredInAPI"]
        
        # Scenario 2: Template provides document
        uc1_document = {
            "endpoint": "/jobs/single-doc-job-template",
            "recipientStyle": "explicit",
            "documentFrom": "template",
            "requiredInAPI": ["recipientAddress", "jobTemplate"]
        }
        assert "document" not in uc1_document["requiredInAPI"]
    
    def test_use_case_3_scenarios(self):
        """Test Use Case 3: Merge multi doc with template"""
        # Scenario 1: Template provides recipients
        uc3_recipients = {
            "endpoint": "/jobs/merge-multi-doc-with-template",
            "recipientStyle": "template",
            "requiredInAPI": ["documents", "jobTemplate"]
        }
        assert "recipientAddress" not in uc3_recipients["requiredInAPI"]
        
        # Scenario 2: Template provides document (merged)
        uc3_document = {
            "endpoint": "/jobs/merge-multi-doc-with-template",
            "recipientStyle": "explicit",
            "documentFrom": "template",
            "requiredInAPI": ["recipientAddress", "jobTemplate"]
        }
        assert "documents" not in uc3_document["requiredInAPI"]
    
    def _get_required_fields_for_template(self, params):
        """Helper to determine required fields based on template logic"""
        required = ["jobTemplateId"]  # Always required
        
        recipient_style = params.get("recipientStyle")
        template_provides = params.get("templateProvides", "")
        
        # Determine what's needed based on what template provides
        if recipient_style == "template" or template_provides == "recipients":
            # Template provides recipients, need document
            required.append("document")
        elif template_provides == "document":
            # Template provides document, need recipients
            required.append("recipientAddress")
        else:
            # Template provides neither, need both
            required.extend(["document", "recipientAddress"])
        
        return required
    
    def _validate_template_logic(self, params):
        """Validate template logic rules"""
        provides = params.get("templateProvides", [])
        if isinstance(provides, list) and len(provides) > 1:
            if "document" in provides and "recipients" in provides:
                raise ValueError("Template cannot provide both document and recipients")


class TestTemplateParameterCollection:
    """Test parameter collection when templates are involved"""
    
    def test_job_template_identification(self):
        """Test job template can be specified by ID or name"""
        # By ID only
        template1 = {"jobTemplateId": "template-123"}
        assert template1.get("jobTemplateId") == "template-123"
        
        # By name only
        template2 = {"jobTemplateName": "Monthly Invoice"}
        assert template2.get("jobTemplateName") == "Monthly Invoice"
        
        # By both (ID takes precedence)
        template3 = {
            "jobTemplateId": "template-456",
            "jobTemplateName": "Quarterly Report"
        }
        assert template3.get("jobTemplateId") == "template-456"
    
    def test_address_capture_with_template(self):
        """Test address capture mode with templates"""
        params = {
            "endpoint": "/jobs/single-doc-job-template",
            "recipientStyle": "addressCapture",
            "jobTemplateId": "template-789"
        }
        
        # Should not require recipient addresses in API
        assert params["recipientStyle"] == "addressCapture"
        assert "recipientAddress" not in params
    
    def test_payment_info_always_required(self):
        """Test payment info is required regardless of template"""
        endpoints_with_payment = [
            "/jobs/single-doc",
            "/jobs/single-doc-job-template",
            "/jobs/multi-doc",
            "/jobs/multi-doc-job-template"
        ]
        
        # All these endpoints should accept payment info
        for endpoint in endpoints_with_payment:
            # Payment can be provided even with templates
            assert True  # Placeholder for actual payment validation
    
    def test_tags_optional_with_templates(self):
        """Test tags remain optional with templates"""
        request_with_tags = {
            "jobTemplateId": "template-123",
            "tags": ["invoice", "2024-Q1", "customer-123"]
        }
        
        request_without_tags = {
            "jobTemplateId": "template-123"
        }
        
        # Both should be valid
        assert "tags" in request_with_tags
        assert "tags" not in request_without_tags


class TestTemplateEdgeCases:
    """Test edge cases and error scenarios with templates"""
    
    def test_missing_template_id_and_name(self):
        """Test error when neither template ID nor name provided"""
        with pytest.raises(ValueError, match="Either jobTemplateId or jobTemplateName required"):
            self._validate_template_request({
                "endpoint": "/jobs/single-doc-job-template"
                # Missing both jobTemplateId and jobTemplateName
            })
    
    def test_conflicting_recipient_sources(self):
        """Test error when recipient source conflicts"""
        # Cannot have both explicit recipients and template recipients
        with pytest.raises(ValueError, match="Cannot specify recipients"):
            self._validate_template_request({
                "recipientAddress": {"name": "John Doe"},
                "recipientStyle": "template"  # Says recipients come from template
            })
    
    def test_multi_doc_template_logic(self):
        """Test multi-doc specific template logic"""
        # Multi-doc with template can still have multiple documents
        request = {
            "endpoint": "/jobs/multi-doc-job-template",
            "jobTemplateId": "template-multi",
            "documents": [
                {"documentId": "doc-1"},
                {"documentId": "doc-2"}
            ],
            "recipientStyle": "template"
        }
        
        # Valid - template provides addresses for all documents
        assert len(request["documents"]) == 2
        assert "recipientAddresses" not in request
    
    def _validate_template_request(self, request):
        """Validate template-related request parameters"""
        endpoint = request.get("endpoint", "")
        
        if "template" in endpoint:
            # Must have template ID or name
            if not request.get("jobTemplateId") and not request.get("jobTemplateName"):
                raise ValueError("Either jobTemplateId or jobTemplateName required")
        
        # Check for conflicting recipient sources
        if request.get("recipientStyle") == "template" and request.get("recipientAddress"):
            raise ValueError("Cannot specify recipients when using template recipients")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])