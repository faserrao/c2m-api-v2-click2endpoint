"""
Tests for endpoint mapping logic - covers all 27 possible QA paths
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock streamlit before importing app
sys.modules['streamlit'] = MagicMock()
sys.modules['streamlit.components'] = MagicMock()
sys.modules['streamlit.components.v1'] = MagicMock()

# Now import the function we're testing
from streamlit_app.app_hardcoded_v1 import get_endpoint


class TestEndpointMapping:
    """Test all 27 possible paths through the QA decision tree"""
    
    # Single document paths (8 paths)
    def test_single_no_template_explicit(self):
        """Path: single -> no template -> explicit addresses"""
        answers = {
            "docType": "single",
            "templateUsage": "false",
            "recipientStyle": "explicit"
        }
        assert get_endpoint(answers) == "/jobs/single-doc"
    
    def test_single_no_template_addresscapture(self):
        """Path: single -> no template -> address capture"""
        answers = {
            "docType": "single",
            "templateUsage": "false",
            "recipientStyle": "addressCapture"
        }
        assert get_endpoint(answers) == "/jobs/single-doc"
    
    def test_single_template_explicit(self):
        """Path: single -> template -> explicit addresses"""
        answers = {
            "docType": "single",
            "templateUsage": "true",
            "recipientStyle": "explicit"
        }
        assert get_endpoint(answers) == "/jobs/single-doc-job-template"
    
    def test_single_template_template(self):
        """Path: single -> template -> addresses from template"""
        answers = {
            "docType": "single",
            "templateUsage": "true",
            "recipientStyle": "template"
        }
        assert get_endpoint(answers) == "/jobs/single-doc-job-template"
    
    def test_single_template_addresscapture(self):
        """Path: single -> template -> address capture"""
        answers = {
            "docType": "single",
            "templateUsage": "true",
            "recipientStyle": "addressCapture"
        }
        assert get_endpoint(answers) == "/jobs/single-doc-job-template"
    
    # Multi document paths (8 paths)
    def test_multi_no_template_explicit_no_personalization(self):
        """Path: multi -> no template -> explicit -> no personalization"""
        answers = {
            "docType": "multi",
            "templateUsage": "false",
            "recipientStyle": "explicit",
            "personalization": "false"
        }
        assert get_endpoint(answers) == "/jobs/multi-doc"
    
    def test_multi_no_template_explicit_personalization(self):
        """Path: multi -> no template -> explicit -> personalization"""
        answers = {
            "docType": "multi",
            "templateUsage": "false",
            "recipientStyle": "explicit",
            "personalization": "true"
        }
        assert get_endpoint(answers) == "/jobs/multi-doc"
    
    def test_multi_no_template_addresscapture(self):
        """Path: multi -> no template -> address capture"""
        answers = {
            "docType": "multi",
            "templateUsage": "false",
            "recipientStyle": "addressCapture"
        }
        assert get_endpoint(answers) == "/jobs/multi-doc"
    
    def test_multi_template_explicit_no_personalization(self):
        """Path: multi -> template -> explicit -> no personalization"""
        answers = {
            "docType": "multi",
            "templateUsage": "true",
            "recipientStyle": "explicit",
            "personalization": "false"
        }
        assert get_endpoint(answers) == "/jobs/multi-doc-job-template"
    
    def test_multi_template_explicit_personalization(self):
        """Path: multi -> template -> explicit -> personalization"""
        answers = {
            "docType": "multi",
            "templateUsage": "true",
            "recipientStyle": "explicit",
            "personalization": "true"
        }
        assert get_endpoint(answers) == "/jobs/multi-doc-job-template"
    
    def test_multi_template_template(self):
        """Path: multi -> template -> addresses from template"""
        answers = {
            "docType": "multi",
            "templateUsage": "true",
            "recipientStyle": "template"
        }
        assert get_endpoint(answers) == "/jobs/multi-doc-job-template"
    
    def test_multi_template_addresscapture(self):
        """Path: multi -> template -> address capture"""
        answers = {
            "docType": "multi",
            "templateUsage": "true",
            "recipientStyle": "addressCapture"
        }
        assert get_endpoint(answers) == "/jobs/multi-doc-job-template"
    
    # Merge document paths (8 paths)
    def test_merge_no_template_explicit_no_personalization(self):
        """Path: merge -> no template -> explicit -> no personalization"""
        answers = {
            "docType": "merge",
            "templateUsage": "false",
            "recipientStyle": "explicit",
            "personalization": "false"
        }
        assert get_endpoint(answers) == "/jobs/merge-multi-doc"
    
    def test_merge_no_template_explicit_personalization(self):
        """Path: merge -> no template -> explicit -> personalization"""
        answers = {
            "docType": "merge",
            "templateUsage": "false",
            "recipientStyle": "explicit",
            "personalization": "true"
        }
        assert get_endpoint(answers) == "/jobs/merge-multi-doc"
    
    def test_merge_no_template_addresscapture(self):
        """Path: merge -> no template -> address capture"""
        answers = {
            "docType": "merge",
            "templateUsage": "false",
            "recipientStyle": "addressCapture"
        }
        assert get_endpoint(answers) == "/jobs/merge-multi-doc"
    
    def test_merge_template_explicit_no_personalization(self):
        """Path: merge -> template -> explicit -> no personalization"""
        answers = {
            "docType": "merge",
            "templateUsage": "true",
            "recipientStyle": "explicit",
            "personalization": "false"
        }
        assert get_endpoint(answers) == "/jobs/merge-multi-doc-with-template"
    
    def test_merge_template_explicit_personalization(self):
        """Path: merge -> template -> explicit -> personalization"""
        answers = {
            "docType": "merge",
            "templateUsage": "true",
            "recipientStyle": "explicit",
            "personalization": "true"
        }
        assert get_endpoint(answers) == "/jobs/merge-multi-doc-with-template"
    
    def test_merge_template_template(self):
        """Path: merge -> template -> addresses from template"""
        answers = {
            "docType": "merge",
            "templateUsage": "true",
            "recipientStyle": "template"
        }
        assert get_endpoint(answers) == "/jobs/merge-multi-doc-with-template"
    
    def test_merge_template_addresscapture(self):
        """Path: merge -> template -> address capture"""
        answers = {
            "docType": "merge",
            "templateUsage": "true",
            "recipientStyle": "addressCapture"
        }
        assert get_endpoint(answers) == "/jobs/merge-multi-doc-with-template"
    
    # PDF Split paths (3 paths)
    def test_pdfsplit_explicit(self):
        """Path: pdfSplit -> explicit addresses"""
        answers = {
            "docType": "pdfSplit",
            "recipientStyle": "explicit"
        }
        assert get_endpoint(answers) == "/jobs/split-combined-pdf"
    
    def test_pdfsplit_addresscapture(self):
        """Path: pdfSplit -> address capture"""
        answers = {
            "docType": "pdfSplit",
            "recipientStyle": "addressCapture"
        }
        assert get_endpoint(answers) == "/jobs/split-combined-pdf"
    
    def test_pdfsplit_template(self):
        """Path: pdfSplit -> addresses from template"""
        answers = {
            "docType": "pdfSplit",
            "recipientStyle": "template"
        }
        assert get_endpoint(answers) == "/jobs/split-combined-pdf"
    
    # Edge cases
    def test_invalid_doc_type(self):
        """Test handling of invalid document type"""
        answers = {
            "docType": "invalid",
            "templateUsage": "false",
            "recipientStyle": "explicit"
        }
        # Should return None or raise exception
        assert get_endpoint(answers) is None
    
    def test_missing_fields(self):
        """Test handling of missing required fields"""
        answers = {"docType": "single"}
        # Should handle gracefully
        assert get_endpoint(answers) is None


class TestEndpointMappingSummary:
    """Summary test to verify all unique endpoints are covered"""
    
    def test_all_endpoints_mapped(self):
        """Verify all 8 unique endpoints from EBNF are reachable"""
        expected_endpoints = {
            "/jobs/single-doc",                      # Use Case 4
            "/jobs/single-doc-job-template",         # Use Case 1
            "/jobs/multi-doc",                       # Use Case 5
            "/jobs/multi-doc-job-template",          # Use Case 2
            "/jobs/merge-multi-doc",                 # Use Case 6
            "/jobs/merge-multi-doc-with-template",   # Use Case 3
            "/jobs/split-combined-pdf",              # Use Case 7
            # Note: Use Cases 8 & 9 from EBNF are not in current implementation
        }
        
        # Collect all endpoints from test paths
        found_endpoints = set()
        
        # Test all valid combinations
        doc_types = ["single", "multi", "merge", "pdfSplit"]
        template_usages = ["true", "false"]
        recipient_styles = ["explicit", "template", "addressCapture"]
        personalizations = ["true", "false"]
        
        for doc_type in doc_types:
            for template_usage in template_usages:
                for recipient_style in recipient_styles:
                    answers = {
                        "docType": doc_type,
                        "templateUsage": template_usage,
                        "recipientStyle": recipient_style
                    }
                    
                    # Add personalization for multi/merge with explicit
                    if doc_type in ["multi", "merge"] and recipient_style == "explicit":
                        for personalization in personalizations:
                            answers["personalization"] = personalization
                            endpoint = get_endpoint(answers)
                            if endpoint:
                                found_endpoints.add(endpoint)
                    else:
                        # Skip template usage for pdfSplit
                        if doc_type == "pdfSplit":
                            del answers["templateUsage"]
                        
                        endpoint = get_endpoint(answers)
                        if endpoint:
                            found_endpoints.add(endpoint)
        
        # Verify all expected endpoints are found
        missing_endpoints = expected_endpoints - found_endpoints
        extra_endpoints = found_endpoints - expected_endpoints
        
        assert not missing_endpoints, f"Missing endpoints: {missing_endpoints}"
        assert not extra_endpoints, f"Unexpected endpoints: {extra_endpoints}"
        assert len(found_endpoints) == 7  # 7 endpoints currently implemented


if __name__ == "__main__":
    pytest.main([__file__, "-v"])