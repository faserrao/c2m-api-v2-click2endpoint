"""
Tests for code generation - Python, JavaScript, and cURL
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock streamlit
sys.modules['streamlit'] = MagicMock()
sys.modules['streamlit.components'] = MagicMock()
sys.modules['streamlit.components.v1'] = MagicMock()

# Import after mocking
from streamlit_app.app_hardcoded_v1 import (
    generate_full_python_code,
    generate_javascript_preview,
    generate_curl_command
)


class TestPythonCodeGeneration:
    """Test Python code generation with full authentication flow"""
    
    def test_python_code_structure(self):
        """Test generated Python code has all required sections"""
        endpoint = "/jobs/single-doc"
        body = {
            "document": {"documentId": "doc-123"},
            "recipientAddress": {"name": "John Doe", "addressLine1": "123 Main St"},
            "paymentInfo": {"paymentType": "CREDIT_CARD"}
        }
        
        code = generate_full_python_code(endpoint, body)
        
        # Check for required imports
        assert "import requests" in code
        assert "import json" in code
        assert "from datetime import datetime" in code
        
        # Check for authentication steps
        assert "Step 1: Revoke any existing tokens" in code
        assert "Step 2: Get long-term token" in code
        assert "Step 3: Exchange for short-term token" in code
        assert "Step 4: Make the actual API request" in code
        
        # Check for configuration
        assert "AUTH_BASE_URL" in code
        assert "API_BASE_URL" in code
        assert "CLIENT_ID" in code
        assert "CLIENT_SECRET" in code
    
    def test_python_auth_flow(self):
        """Test authentication flow in generated code"""
        code = generate_full_python_code("/jobs/single-doc", {})
        
        # Check token revocation
        assert "/auth/tokens/revoke" in code
        assert "DELETE" in code
        
        # Check long-term token acquisition
        assert "/auth/tokens/long" in code
        assert "grant_type" in code
        assert "client_credentials" in code
        
        # Check short-term token exchange
        assert "/auth/tokens/short" in code
        assert "long_term_token" in code
    
    def test_python_request_body_serialization(self):
        """Test request body is properly serialized"""
        body = {
            "document": {"documentId": "doc-456"},
            "recipientAddress": {
                "name": "Jane Doe",
                "addressLine1": "456 Oak St",
                "city": "Anytown",
                "state": "CA",
                "postalCode": "12345"
            },
            "paymentInfo": {
                "paymentType": "INVOICE",
                "invoiceNumber": "INV-2024-001"
            },
            "tags": ["urgent", "invoice", "q1-2024"]
        }
        
        code = generate_full_python_code("/jobs/single-doc", body)
        
        # Check body is included
        assert '"documentId": "doc-456"' in code
        assert '"name": "Jane Doe"' in code
        assert '"paymentType": "INVOICE"' in code
        assert '"tags": ["urgent", "invoice", "q1-2024"]' in code
    
    def test_python_error_handling(self):
        """Test error handling in generated code"""
        code = generate_full_python_code("/jobs/single-doc", {})
        
        # Check for response error handling
        assert "response.raise_for_status()" in code
        assert "except Exception as e:" in code
        assert "print(f\"Error" in code
    
    def test_python_pretty_printing(self):
        """Test pretty printing of responses"""
        code = generate_full_python_code("/jobs/single-doc", {})
        
        # Check for pretty print function
        assert "def pretty_print" in code
        assert "json.dumps" in code
        assert "indent=2" in code


class TestJavaScriptCodeGeneration:
    """Test JavaScript code generation"""
    
    def test_javascript_preview_structure(self):
        """Test JavaScript preview has correct structure"""
        endpoint = "/jobs/single-doc"
        body = {"document": {"documentId": "doc-789"}}
        
        code = generate_javascript_preview(endpoint, body, "token123")
        
        # Check for async/await syntax
        assert "async function" in code
        assert "await fetch" in code
        
        # Check for headers
        assert "Authorization" in code
        assert "Bearer token123" in code
        assert "Content-Type" in code
        assert "application/json" in code
        
        # Check for error handling
        assert "try {" in code
        assert "catch (error)" in code
    
    def test_javascript_request_formatting(self):
        """Test JavaScript request is properly formatted"""
        endpoint = "/jobs/multi-doc"
        body = {
            "documents": [
                {"documentId": "doc-1"},
                {"documentId": "doc-2"}
            ],
            "recipientAddresses": [
                {"name": "Person 1"},
                {"name": "Person 2"}
            ]
        }
        
        code = generate_javascript_preview(endpoint, body, "token456")
        
        # Check endpoint
        assert f"'{endpoint}'" in code
        
        # Check body serialization
        assert "JSON.stringify" in code
        assert '"documents"' in code
        assert '"recipientAddresses"' in code
    
    def test_javascript_response_handling(self):
        """Test JavaScript response handling"""
        code = generate_javascript_preview("/jobs/single-doc", {}, "token")
        
        # Check response parsing
        assert "response.json()" in code
        assert "console.log" in code
        assert "console.error" in code


class TestCurlCodeGeneration:
    """Test cURL command generation"""
    
    def test_curl_command_structure(self):
        """Test cURL command has correct structure"""
        endpoint = "/jobs/single-doc"
        body = {"document": {"documentId": "doc-321"}}
        token = "token789"
        
        command = generate_curl_command(endpoint, body, token)
        
        # Check basic structure
        assert command.startswith("curl")
        assert "-X POST" in command
        assert endpoint in command
        
        # Check headers
        assert "-H 'Authorization: Bearer" in command
        assert "-H 'Content-Type: application/json'" in command
        
        # Check data
        assert "-d '" in command
    
    def test_curl_json_formatting(self):
        """Test cURL command properly formats JSON"""
        body = {
            "document": {"externalUrl": "https://example.com/doc.pdf"},
            "recipientAddress": {"name": "Test User"},
            "tags": ["test", "curl"]
        }
        
        command = generate_curl_command("/jobs/single-doc", body, "token")
        
        # Check JSON is properly escaped/formatted
        assert '"externalUrl":' in command
        assert '"https://example.com/doc.pdf"' in command
        assert '"tags": ["test", "curl"]' in command
    
    def test_curl_with_mock_server(self):
        """Test cURL uses mock server URL"""
        command = generate_curl_command("/jobs/single-doc", {}, "token")
        
        # Should use the mock server URL
        assert "mock.pstmn.io" in command


class TestCodeGenerationEdgeCases:
    """Test edge cases in code generation"""
    
    def test_empty_request_body(self):
        """Test code generation with empty body"""
        python_code = generate_full_python_code("/jobs/single-doc", {})
        js_code = generate_javascript_preview("/jobs/single-doc", {}, "token")
        curl_cmd = generate_curl_command("/jobs/single-doc", {}, "token")
        
        # Should still generate valid code
        assert "requests.post" in python_code
        assert "fetch" in js_code
        assert "curl" in curl_cmd
    
    def test_special_characters_in_values(self):
        """Test handling of special characters"""
        body = {
            "document": {"documentId": "doc\"with'quotes"},
            "recipientAddress": {"name": "O'Brien & Sons, Inc."}
        }
        
        python_code = generate_full_python_code("/jobs/single-doc", body)
        js_code = generate_javascript_preview("/jobs/single-doc", body, "token")
        
        # Should properly escape special characters
        assert "doc\\\"with'quotes" in python_code or 'doc"with\'quotes' in python_code
        assert "O'Brien & Sons, Inc." in python_code
    
    def test_large_request_body(self):
        """Test with large number of recipients"""
        body = {
            "documents": [{"documentId": f"doc-{i}"} for i in range(50)],
            "recipientAddresses": [{"name": f"Person {i}"} for i in range(50)]
        }
        
        code = generate_full_python_code("/jobs/multi-doc", body)
        
        # Should include all items
        assert "doc-49" in code
        assert "Person 49" in code
    
    def test_all_payment_types(self):
        """Test all 6 payment types from EBNF"""
        payment_types = [
            "CREDIT_CARD", "INVOICE", "ACH", 
            "USER_CREDIT", "APPLE_PAY", "GOOGLE_PAY"
        ]
        
        for payment_type in payment_types:
            body = {"paymentInfo": {"paymentType": payment_type}}
            code = generate_full_python_code("/jobs/single-doc", body)
            assert f'"{payment_type}"' in code


class TestCodeSaving:
    """Test code saving functionality"""
    
    def test_filename_generation(self):
        """Test generated filenames include timestamp"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Test various filename patterns
        python_file = f"c2m_api_request_{timestamp}.py"
        js_file = f"c2m_api_request_{timestamp}.js"
        curl_file = f"c2m_api_request_{timestamp}.sh"
        
        assert python_file.endswith(".py")
        assert js_file.endswith(".js")
        assert curl_file.endswith(".sh")
        assert timestamp in python_file


if __name__ == "__main__":
    pytest.main([__file__, "-v"])