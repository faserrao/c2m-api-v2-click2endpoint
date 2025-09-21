"""
Parameter Questions for C2M API V2 Endpoints
Direct mapping of Level 2 questions based on endpoint selection
"""

from typing import Dict, List, Any

class ParameterQuestions:
    """Provides parameter questions for each endpoint"""
    
    # Parameter questions mapping
    ENDPOINT_PARAMETERS = {
        "/jobs/single-doc-job-template": {
            "description": "Send one document using a job template",
            "questions": [
                {
                    "id": "doc_or_template",
                    "type": "choice",
                    "question": "How will you provide the document?",
                    "options": [
                        {"value": "template", "label": "Use document from template", "next": "recipient_source"},
                        {"value": "api", "label": "Provide document in API call", "next": "document_source"}
                    ]
                },
                {
                    "id": "document_source",
                    "type": "choice",
                    "question": "How will you provide the document?",
                    "options": [
                        {"value": "document_id", "label": "Document ID (previously uploaded)", "next": "document_id_input"},
                        {"value": "external_url", "label": "External URL", "next": "url_input"},
                        {"value": "upload_request", "label": "Upload request ID", "next": "upload_input"}
                    ]
                },
                {
                    "id": "document_id_input",
                    "type": "text",
                    "question": "Enter the document ID:",
                    "field": "documentId",
                    "next": "recipient_source"
                },
                {
                    "id": "url_input",
                    "type": "text",
                    "question": "Enter the external URL:",
                    "field": "externalUrl",
                    "next": "recipient_source"
                },
                {
                    "id": "upload_input",
                    "type": "text",
                    "question": "Enter the upload request ID:",
                    "field": "uploadRequestId",
                    "next": "recipient_source"
                },
                {
                    "id": "recipient_source",
                    "type": "choice",
                    "question": "How will you provide recipient addresses?",
                    "options": [
                        {"value": "template", "label": "Use addresses from template", "next": "job_template"},
                        {"value": "api", "label": "Provide addresses in API call", "next": "address_type"}
                    ]
                },
                {
                    "id": "address_type",
                    "type": "choice",
                    "question": "How will you specify the recipient address(es)?",
                    "options": [
                        {"value": "new_address", "label": "Enter new address", "next": "new_address_input"},
                        {"value": "list_id", "label": "Use address list ID", "next": "list_id_input"},
                        {"value": "single_id", "label": "Use saved address ID", "next": "single_id_input"}
                    ]
                },
                {
                    "id": "new_address_input",
                    "type": "address",
                    "question": "Enter recipient address details:",
                    "fields": ["firstName", "lastName", "address1", "city", "state", "zip"],
                    "next": "job_template"
                },
                {
                    "id": "list_id_input",
                    "type": "text",
                    "question": "Enter the address list ID:",
                    "field": "addressListId",
                    "next": "job_template"
                },
                {
                    "id": "single_id_input",
                    "type": "text",
                    "question": "Enter the saved address ID:",
                    "field": "addressId",
                    "next": "job_template"
                },
                {
                    "id": "job_template",
                    "type": "text",
                    "question": "Which saved job template will you use?",
                    "field": "jobTemplateId",
                    "required": True,
                    "next": "payment"
                },
                {
                    "id": "payment",
                    "type": "choice",
                    "question": "How would you like to pay?",
                    "options": [
                        {"value": "credit_card", "label": "Credit Card", "next": "credit_card_input"},
                        {"value": "invoice", "label": "Invoice", "next": "invoice_input"},
                        {"value": "account_credit", "label": "Account Credit", "next": "tags"}
                    ]
                },
                {
                    "id": "credit_card_input",
                    "type": "credit_card",
                    "question": "Enter credit card details:",
                    "fields": ["cardType", "cardNumber", "expirationMonth", "expirationYear"],
                    "next": "tags"
                },
                {
                    "id": "invoice_input",
                    "type": "text",
                    "question": "Enter invoice number:",
                    "field": "invoiceNumber",
                    "next": "tags"
                },
                {
                    "id": "tags",
                    "type": "text_list",
                    "question": "Would you like to add tags? (optional)",
                    "field": "tags",
                    "optional": True
                }
            ]
        },
        
        "/jobs/single-doc": {
            "description": "Send one document to multiple recipients",
            "questions": [
                {
                    "id": "document_source",
                    "type": "choice",
                    "question": "How will you provide the document?",
                    "options": [
                        {"value": "document_id", "label": "Document ID (previously uploaded)", "next": "document_id_input"},
                        {"value": "external_url", "label": "External URL", "next": "url_input"},
                        {"value": "upload_request", "label": "Upload request ID", "next": "upload_input"}
                    ]
                },
                {
                    "id": "document_id_input",
                    "type": "text",
                    "question": "Enter the document ID:",
                    "field": "documentId",
                    "next": "recipients"
                },
                {
                    "id": "url_input",
                    "type": "text",
                    "question": "Enter the external URL:",
                    "field": "externalUrl",
                    "next": "recipients"
                },
                {
                    "id": "upload_input",
                    "type": "text",
                    "question": "Enter the upload request ID:",
                    "field": "uploadRequestId",
                    "next": "recipients"
                },
                {
                    "id": "recipients",
                    "type": "address_list",
                    "question": "Enter recipient addresses (you can add multiple):",
                    "field": "recipients",
                    "next": "job_options"
                },
                {
                    "id": "job_options",
                    "type": "job_options",
                    "question": "Configure printing and mailing options:",
                    "fields": ["documentClass", "layout", "mailClass", "paperType", "printOption", "color"],
                    "next": "payment"
                },
                {
                    "id": "payment",
                    "type": "choice",
                    "question": "How would you like to pay?",
                    "options": [
                        {"value": "credit_card", "label": "Credit Card", "next": "credit_card_input"},
                        {"value": "invoice", "label": "Invoice", "next": "invoice_input"},
                        {"value": "account_credit", "label": "Account Credit", "next": "tags"}
                    ]
                },
                {
                    "id": "credit_card_input",
                    "type": "credit_card",
                    "question": "Enter credit card details:",
                    "fields": ["cardType", "cardNumber", "expirationMonth", "expirationYear"],
                    "next": "tags"
                },
                {
                    "id": "invoice_input",
                    "type": "text",
                    "question": "Enter invoice number:",
                    "field": "invoiceNumber",
                    "next": "tags"
                },
                {
                    "id": "tags",
                    "type": "text_list",
                    "question": "Would you like to add tags? (optional)",
                    "field": "tags",
                    "optional": True
                }
            ]
        }
        
        # Add other endpoints as needed
    }
    
    @classmethod
    def get_questions(cls, endpoint: str) -> List[Dict[str, Any]]:
        """Get parameter questions for an endpoint"""
        return cls.ENDPOINT_PARAMETERS.get(endpoint, {}).get("questions", [])
    
    @classmethod
    def get_question_by_id(cls, endpoint: str, question_id: str) -> Dict[str, Any]:
        """Get a specific question by ID"""
        questions = cls.get_questions(endpoint)
        for q in questions:
            if q["id"] == question_id:
                return q
        return None