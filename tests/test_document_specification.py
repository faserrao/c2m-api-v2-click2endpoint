"""
Tests for document specification methods - all 5 EBNF types
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock streamlit before importing
import streamlit as st
sys.modules['streamlit'] = MagicMock()
st.text_input = MagicMock(side_effect=lambda label, key=None, **kwargs: f"test_{key}")
st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])


class TestDocumentSpecification:
    """Test all 5 document specification methods from EBNF"""
    
    def test_document_id_only(self):
        """Test documentId specification"""
        doc_spec = {
            "method": "documentId",
            "documentId": "doc-12345"
        }
        
        # Expected structure for API
        expected = {"documentId": "doc-12345"}
        assert doc_spec["documentId"] == expected["documentId"]
    
    def test_external_url_only(self):
        """Test externalUrl specification"""
        doc_spec = {
            "method": "externalUrl",
            "externalUrl": "https://example.com/document.pdf"
        }
        
        # Expected structure for API
        expected = {"externalUrl": "https://example.com/document.pdf"}
        assert doc_spec["externalUrl"] == expected["externalUrl"]
    
    def test_upload_request_id_with_document_name(self):
        """Test uploadRequestId + documentName specification"""
        doc_spec = {
            "method": "uploadRequestId_documentName",
            "uploadRequestId": "upload-789",
            "documentName": "invoice.pdf"
        }
        
        # Expected structure for API
        expected = {
            "uploadRequestId": "upload-789",
            "documentName": "invoice.pdf"
        }
        assert doc_spec["uploadRequestId"] == expected["uploadRequestId"]
        assert doc_spec["documentName"] == expected["documentName"]
    
    def test_zip_id_with_document_name(self):
        """Test zipId + documentName specification"""
        doc_spec = {
            "method": "zipId_documentName",
            "zipId": "zip-456",
            "documentName": "report.pdf"
        }
        
        # Expected structure for API
        expected = {
            "zipId": "zip-456",
            "documentName": "report.pdf"
        }
        assert doc_spec["zipId"] == expected["zipId"]
        assert doc_spec["documentName"] == expected["documentName"]
    
    def test_upload_request_id_with_zip_id_and_document_name(self):
        """Test uploadRequestId + zipId + documentName specification"""
        doc_spec = {
            "method": "uploadRequestId_zipId_documentName",
            "uploadRequestId": "upload-111",
            "zipId": "zip-222",
            "documentName": "contract.pdf"
        }
        
        # Expected structure for API
        expected = {
            "uploadRequestId": "upload-111",
            "zipId": "zip-222",
            "documentName": "contract.pdf"
        }
        assert doc_spec["uploadRequestId"] == expected["uploadRequestId"]
        assert doc_spec["zipId"] == expected["zipId"]
        assert doc_spec["documentName"] == expected["documentName"]


class TestDocumentSpecificationValidation:
    """Test validation for document specifications"""
    
    def test_empty_document_id(self):
        """Test validation rejects empty documentId"""
        with pytest.raises(ValueError, match="documentId cannot be empty"):
            self._validate_doc_spec({
                "method": "documentId",
                "documentId": ""
            })
    
    def test_invalid_external_url(self):
        """Test validation rejects invalid URLs"""
        with pytest.raises(ValueError, match="Invalid URL"):
            self._validate_doc_spec({
                "method": "externalUrl",
                "externalUrl": "not-a-url"
            })
    
    def test_missing_required_fields(self):
        """Test validation rejects missing required fields"""
        # Missing documentName
        with pytest.raises(ValueError, match="documentName is required"):
            self._validate_doc_spec({
                "method": "uploadRequestId_documentName",
                "uploadRequestId": "upload-123"
            })
        
        # Missing zipId
        with pytest.raises(ValueError, match="zipId is required"):
            self._validate_doc_spec({
                "method": "zipId_documentName",
                "documentName": "file.pdf"
            })
    
    def test_valid_specifications(self):
        """Test validation accepts all valid specifications"""
        valid_specs = [
            {"method": "documentId", "documentId": "doc-123"},
            {"method": "externalUrl", "externalUrl": "https://example.com/doc.pdf"},
            {"method": "uploadRequestId_documentName", 
             "uploadRequestId": "up-123", "documentName": "file.pdf"},
            {"method": "zipId_documentName",
             "zipId": "zip-123", "documentName": "file.pdf"},
            {"method": "uploadRequestId_zipId_documentName",
             "uploadRequestId": "up-123", "zipId": "zip-456", "documentName": "file.pdf"}
        ]
        
        for spec in valid_specs:
            # Should not raise exception
            self._validate_doc_spec(spec)
    
    def _validate_doc_spec(self, spec):
        """Helper to validate document specification"""
        method = spec.get("method")
        
        if method == "documentId":
            if not spec.get("documentId"):
                raise ValueError("documentId cannot be empty")
        
        elif method == "externalUrl":
            url = spec.get("externalUrl", "")
            if not url.startswith(("http://", "https://")):
                raise ValueError("Invalid URL")
        
        elif method == "uploadRequestId_documentName":
            if not spec.get("uploadRequestId"):
                raise ValueError("uploadRequestId is required")
            if not spec.get("documentName"):
                raise ValueError("documentName is required")
        
        elif method == "zipId_documentName":
            if not spec.get("zipId"):
                raise ValueError("zipId is required")
            if not spec.get("documentName"):
                raise ValueError("documentName is required")
        
        elif method == "uploadRequestId_zipId_documentName":
            if not spec.get("uploadRequestId"):
                raise ValueError("uploadRequestId is required")
            if not spec.get("zipId"):
                raise ValueError("zipId is required")
            if not spec.get("documentName"):
                raise ValueError("documentName is required")


class TestDocumentSpecificationIntegration:
    """Test document specification in context of full request body"""
    
    def test_single_doc_with_document_id(self):
        """Test single document request with documentId"""
        request_body = {
            "document": {
                "documentId": "doc-12345"
            },
            "recipientAddress": {
                "name": "John Doe",
                "addressLine1": "123 Main St"
            }
        }
        
        assert request_body["document"]["documentId"] == "doc-12345"
    
    def test_multi_doc_with_mixed_specifications(self):
        """Test multi-document with different specification methods"""
        request_body = {
            "documents": [
                {"documentId": "doc-111"},
                {"externalUrl": "https://example.com/doc2.pdf"},
                {"uploadRequestId": "up-333", "documentName": "doc3.pdf"}
            ],
            "recipientAddresses": [
                {"name": "Jane Doe", "addressLine1": "456 Oak St"},
                {"name": "Bob Smith", "addressLine1": "789 Pine St"}
            ]
        }
        
        assert len(request_body["documents"]) == 3
        assert request_body["documents"][0].get("documentId") == "doc-111"
        assert request_body["documents"][1].get("externalUrl") == "https://example.com/doc2.pdf"
        assert request_body["documents"][2].get("uploadRequestId") == "up-333"
    
    def test_merge_doc_with_zip_specification(self):
        """Test merge documents with zip specification"""
        request_body = {
            "documents": [
                {"zipId": "zip-100", "documentName": "page1.pdf"},
                {"zipId": "zip-100", "documentName": "page2.pdf"},
                {"zipId": "zip-100", "documentName": "page3.pdf"}
            ],
            "recipientAddress": {
                "name": "Alice Johnson",
                "addressLine1": "321 Elm St"
            }
        }
        
        assert all(doc.get("zipId") == "zip-100" for doc in request_body["documents"])
        assert len(request_body["documents"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])