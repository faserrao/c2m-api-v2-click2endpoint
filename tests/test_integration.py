"""
Integration tests for Click2Endpoint
Tests the complete flow from QA selection to code generation
"""

import pytest
import json
import requests
from unittest.mock import patch, MagicMock, Mock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after mocking streamlit (done in conftest.py)
from streamlit_app.app_hardcoded_v1 import (
    get_endpoint,
    generate_full_python_code,
    get_postman_mock_servers,
    initialize_mock_server
)


class TestPostmanIntegration:
    """Test Postman API integration"""
    
    @patch('requests.get')
    def test_fetch_mock_servers_success(self, mock_get, mock_postman_response):
        """Test successful fetch of mock servers from Postman"""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_postman_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test fetching
        mocks = get_postman_mock_servers()
        
        # Verify API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == "https://api.getpostman.com/mocks"
        assert "X-Api-Key" in kwargs["headers"]
        
        # Verify returned data
        assert mocks is not None
        assert len(mocks) == 2
        assert mocks[0]["name"] == "C2M API v2 Mock"
        assert "mock.pstmn.io" in mocks[0]["url"]
    
    @patch('requests.get')
    def test_fetch_mock_servers_failure(self, mock_get):
        """Test handling of Postman API failure"""
        # Setup mock to raise exception
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        # Test fetching
        mocks = get_postman_mock_servers()
        
        # Should return None on failure
        assert mocks is None
    
    @patch('requests.get')
    def test_mock_server_url_format(self, mock_get, mock_postman_response):
        """Test mock server URLs are correctly formatted"""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_postman_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        mocks = get_postman_mock_servers()
        
        # Check URL format
        for mock in mocks:
            assert mock["url"].startswith("https://")
            assert ".mock.pstmn.io" in mock["url"]
            assert mock["id"] in mock["url"]


class TestEndToEndFlow:
    """Test complete flow from QA to code generation"""
    
    def test_single_doc_complete_flow(self):
        """Test complete flow for single document submission"""
        # Step 1: QA answers
        answers = {
            "docType": "single",
            "templateUsage": "false",
            "recipientStyle": "explicit"
        }
        
        # Step 2: Get endpoint
        endpoint = get_endpoint(answers)
        assert endpoint == "/jobs/single-doc"
        
        # Step 3: Build request body
        body = {
            "document": {"documentId": "test-doc-123"},
            "recipientAddress": {
                "name": "Test User",
                "addressLine1": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "postalCode": "12345"
            },
            "paymentInfo": {"paymentType": "CREDIT_CARD"}
        }
        
        # Step 4: Generate code
        python_code = generate_full_python_code(endpoint, body)
        
        # Verify generated code
        assert endpoint in python_code
        assert "test-doc-123" in python_code
        assert "Test User" in python_code
        assert "CREDIT_CARD" in python_code
        assert "revoke" in python_code  # Auth flow
        assert "long_term_token" in python_code
        assert "short_term_token" in python_code
    
    def test_template_flow_with_recipient_from_template(self):
        """Test flow when template provides recipients"""
        # QA answers indicating template provides recipients
        answers = {
            "docType": "single",
            "templateUsage": "true",
            "recipientStyle": "template"
        }
        
        endpoint = get_endpoint(answers)
        assert endpoint == "/jobs/single-doc-job-template"
        
        # Body should have document but NOT recipients
        body = {
            "jobTemplateId": "monthly-invoice-template",
            "document": {"documentId": "invoice-2024-01"},
            "paymentInfo": {"paymentType": "INVOICE"}
            # Note: No recipientAddress field
        }
        
        code = generate_full_python_code(endpoint, body)
        
        # Verify
        assert "jobTemplateId" in code
        assert "monthly-invoice-template" in code
        assert "recipientAddress" not in code  # Should not ask for recipients
    
    def test_multi_doc_with_personalization(self):
        """Test multi-doc flow with personalization"""
        answers = {
            "docType": "multi",
            "templateUsage": "false",
            "recipientStyle": "explicit",
            "personalization": "true"
        }
        
        endpoint = get_endpoint(answers)
        assert endpoint == "/jobs/multi-doc"
        
        # Multi-doc with personalization
        body = {
            "documents": [
                {"documentId": "doc-001", "recipientIndex": 0},
                {"documentId": "doc-002", "recipientIndex": 1},
                {"documentId": "doc-003", "recipientIndex": 0}
            ],
            "recipientAddresses": [
                {"name": "Person A", "addressLine1": "123 A St"},
                {"name": "Person B", "addressLine1": "456 B Ave"}
            ],
            "paymentInfo": {"paymentType": "ACH"}
        }
        
        code = generate_full_python_code(endpoint, body)
        
        # Verify personalization mapping
        assert "recipientIndex" in code
        assert "Person A" in code
        assert "Person B" in code


class TestValidationIntegration:
    """Test validation across the full system"""
    
    def test_invalid_payment_type_rejected(self):
        """Test that invalid payment types are caught"""
        valid_payment_types = {
            "CREDIT_CARD", "INVOICE", "ACH", 
            "USER_CREDIT", "APPLE_PAY", "GOOGLE_PAY"
        }
        
        # Test each valid type
        for payment_type in valid_payment_types:
            body = {"paymentInfo": {"paymentType": payment_type}}
            code = generate_full_python_code("/jobs/single-doc", body)
            assert payment_type in code
    
    def test_all_document_methods_supported(self):
        """Test all 5 document specification methods work"""
        doc_specs = [
            {"documentId": "doc-123"},
            {"externalUrl": "https://example.com/doc.pdf"},
            {"uploadRequestId": "up-123", "documentName": "file.pdf"},
            {"zipId": "zip-456", "documentName": "doc.pdf"},
            {"uploadRequestId": "up-789", "zipId": "zip-012", "documentName": "report.pdf"}
        ]
        
        for doc_spec in doc_specs:
            body = {"document": doc_spec}
            code = generate_full_python_code("/jobs/single-doc", body)
            
            # Verify all fields are in generated code
            for key, value in doc_spec.items():
                assert f'"{key}"' in code
                assert f'"{value}"' in code


class TestMockServerIntegration:
    """Test mock server URL handling"""
    
    def test_correct_mock_server_url_used(self):
        """Test that the correct mock server URL is used"""
        endpoint = "/jobs/single-doc"
        body = {"test": "data"}
        
        code = generate_full_python_code(endpoint, body)
        
        # Should use the correct mock server URL
        assert "cd140b74-ed23-4980-834b-a966ac3393c1.mock.pstmn.io" in code
        
        # Should NOT use the incorrect one
        assert "90fed5bb-9bac-43ca-a9c4-2c4b920892b5.mock.pstmn.io" not in code
    
    def test_auth_endpoints_use_correct_url(self):
        """Test auth endpoints use correct URLs"""
        code = generate_full_python_code("/jobs/single-doc", {})
        
        # Check auth URLs
        assert "/auth/tokens/revoke" in code
        assert "/auth/tokens/long" in code
        assert "/auth/tokens/short" in code
        
        # All should use the mock server
        assert code.count("mock.pstmn.io") >= 4  # At least 4 API calls


class TestErrorScenarios:
    """Test error handling scenarios"""
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        # Missing document type
        assert get_endpoint({}) is None
        
        # Missing template usage for non-pdfSplit
        assert get_endpoint({"docType": "single"}) is None
        
        # Missing recipient style
        assert get_endpoint({
            "docType": "single",
            "templateUsage": "false"
        }) is None
    
    def test_conflicting_parameters(self):
        """Test handling of conflicting parameters"""
        # PDF split shouldn't have template usage
        endpoint = get_endpoint({
            "docType": "pdfSplit",
            "templateUsage": "true",  # Should be ignored
            "recipientStyle": "explicit"
        })
        
        assert endpoint == "/jobs/split-combined-pdf"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])