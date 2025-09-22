"""
Pytest configuration and fixtures for Click2Endpoint tests
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def mock_streamlit():
    """Automatically mock streamlit for all tests"""
    # Create mock module
    streamlit_mock = MagicMock()
    
    # Mock common streamlit functions
    streamlit_mock.set_page_config = MagicMock()
    streamlit_mock.title = MagicMock()
    streamlit_mock.header = MagicMock()
    streamlit_mock.subheader = MagicMock()
    streamlit_mock.write = MagicMock()
    streamlit_mock.markdown = MagicMock()
    streamlit_mock.code = MagicMock()
    streamlit_mock.error = MagicMock()
    streamlit_mock.warning = MagicMock()
    streamlit_mock.info = MagicMock()
    streamlit_mock.success = MagicMock()
    streamlit_mock.button = MagicMock(return_value=False)
    streamlit_mock.text_input = MagicMock(return_value="")
    streamlit_mock.text_area = MagicMock(return_value="")
    streamlit_mock.selectbox = MagicMock(return_value=None)
    streamlit_mock.radio = MagicMock(return_value=None)
    streamlit_mock.checkbox = MagicMock(return_value=False)
    streamlit_mock.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
    streamlit_mock.container = MagicMock()
    streamlit_mock.expander = MagicMock()
    streamlit_mock.sidebar = MagicMock()
    streamlit_mock.download_button = MagicMock(return_value=False)
    
    # Mock session state
    streamlit_mock.session_state = {}
    
    # Mock components
    components_mock = MagicMock()
    components_mock.v1 = MagicMock()
    components_mock.v1.html = MagicMock()
    
    # Register mocks
    sys.modules['streamlit'] = streamlit_mock
    sys.modules['streamlit.components'] = components_mock
    sys.modules['streamlit.components.v1'] = components_mock.v1
    
    yield streamlit_mock
    
    # Cleanup
    if 'streamlit' in sys.modules:
        del sys.modules['streamlit']
    if 'streamlit.components' in sys.modules:
        del sys.modules['streamlit.components']
    if 'streamlit.components.v1' in sys.modules:
        del sys.modules['streamlit.components.v1']


@pytest.fixture
def sample_request_bodies():
    """Sample request bodies for different endpoints"""
    return {
        "single_doc": {
            "document": {"documentId": "doc-12345"},
            "recipientAddress": {
                "name": "John Doe",
                "addressLine1": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "postalCode": "12345"
            },
            "paymentInfo": {
                "paymentType": "CREDIT_CARD",
                "lastFourDigits": "1234"
            },
            "tags": ["invoice", "2024-Q1"]
        },
        "multi_doc": {
            "documents": [
                {"documentId": "doc-001"},
                {"documentId": "doc-002"},
                {"documentId": "doc-003"}
            ],
            "recipientAddresses": [
                {
                    "name": "Jane Smith",
                    "addressLine1": "456 Oak Ave"
                },
                {
                    "name": "Bob Johnson",
                    "addressLine1": "789 Pine St"
                }
            ],
            "paymentInfo": {"paymentType": "INVOICE"}
        },
        "template": {
            "jobTemplateId": "template-monthly-invoice",
            "recipientAddress": {
                "name": "Alice Brown",
                "addressLine1": "321 Elm Dr"
            },
            "paymentInfo": {"paymentType": "ACH"}
        }
    }


@pytest.fixture
def mock_postman_response():
    """Mock response from Postman API"""
    return {
        "mocks": [
            {
                "id": "cd140b74-ed23-4980-834b-a966ac3393c1",
                "name": "C2M API v2 Mock",
                "environment": "production"
            },
            {
                "id": "90fed5bb-9bac-43ca-a9c4-2c4b920892b5",
                "name": "C2M API v2 Dev Mock",
                "environment": "development"
            }
        ]
    }


@pytest.fixture
def all_endpoints():
    """All valid endpoints from EBNF"""
    return [
        "/jobs/single-doc",                      # Use Case 4
        "/jobs/single-doc-job-template",         # Use Case 1
        "/jobs/multi-doc",                       # Use Case 5
        "/jobs/multi-doc-job-template",          # Use Case 2
        "/jobs/merge-multi-doc",                 # Use Case 6
        "/jobs/merge-multi-doc-with-template",   # Use Case 3
        "/jobs/split-combined-pdf",              # Use Case 7
        # Future endpoints:
        # "/jobs/pdf-split-address-capture",     # Use Case 8
        # "/jobs/single-doc-address-capture",    # Use Case 9
    ]


@pytest.fixture
def qa_paths():
    """All 27 possible QA decision paths"""
    paths = []
    
    # Generate all combinations
    doc_types = ["single", "multi", "merge", "pdfSplit"]
    
    for doc_type in doc_types:
        if doc_type == "pdfSplit":
            # PDF split only has recipient style choice
            for recipient_style in ["explicit", "template", "addressCapture"]:
                paths.append({
                    "docType": doc_type,
                    "recipientStyle": recipient_style
                })
        else:
            # Others have template usage choice
            for template_usage in ["true", "false"]:
                if doc_type == "single" or (doc_type in ["multi", "merge"] and template_usage == "true"):
                    # Single always has recipient style
                    # Multi/merge with template have recipient style
                    for recipient_style in ["explicit", "template", "addressCapture"]:
                        path = {
                            "docType": doc_type,
                            "templateUsage": template_usage,
                            "recipientStyle": recipient_style
                        }
                        paths.append(path)
                else:
                    # Multi/merge without template
                    for recipient_style in ["explicit", "addressCapture"]:
                        path = {
                            "docType": doc_type,
                            "templateUsage": template_usage,
                            "recipientStyle": recipient_style
                        }
                        # Explicit multi/merge may have personalization
                        if recipient_style == "explicit":
                            for personalization in ["true", "false"]:
                                path_with_personal = path.copy()
                                path_with_personal["personalization"] = personalization
                                paths.append(path_with_personal)
                        else:
                            paths.append(path)
    
    return paths