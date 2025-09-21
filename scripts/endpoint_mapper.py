"""
Endpoint Mapper for C2M API V2
Maps Level 1 decision tree answers to EBNF use cases and endpoints
"""

from typing import Dict, Optional, List, Any

class EndpointMapper:
    """Maps user decisions to appropriate endpoints"""
    
    # Mapping from endpoints to EBNF use case names
    ENDPOINT_TO_USECASE = {
        "/jobs/single-doc": "singleDocJobParams",
        "/jobs/single-doc-job-template": "submitSingleDocWithTemplateParams",
        "/jobs/multi-doc": "submitMultiDocParams",
        "/jobs/multi-docs-job-template": "submitMultiDocWithTemplateParams",
        "/jobs/multi-doc-merge": "mergeMultiDocParams",
        "/jobs/multi-doc-merge-job-template": "mergeMultiDocWithTemplateParams",
        "/jobs/single-pdf-split": "splitPdfParams",
        "/jobs/single-pdf-split-addressCapture": "splitPdfWithCaptureParams",
        "/jobs/multi-pdf-address-capture": "multiPdfWithCaptureParams"
    }
    
    def endpoint_to_usecase(self, endpoint: str) -> Optional[str]:
        """Convert endpoint path to EBNF use case name"""
        return self.ENDPOINT_TO_USECASE.get(endpoint)
    
    # Level 1 decision tree (hardcoded as per existing qa_tree.yaml structure)
    DECISION_TREE = {
        "initial": {
            "question": "How many documents do you need to send?",
            "options": {
                "single": {
                    "next": "single_template"
                },
                "multiple": {
                    "next": "multiple_action"
                },
                "pdf_split": {
                    "next": "pdf_split_address"
                }
            }
        },
        "single_template": {
            "question": "Will you use a job template?",
            "options": {
                "yes": {
                    "endpoint": "/jobs/single-doc-job-template"
                },
                "no": {
                    "endpoint": "/jobs/single-doc"
                }
            }
        },
        "multiple_action": {
            "question": "What do you want to do with multiple documents?",
            "options": {
                "separate": {
                    "next": "multiple_template"
                },
                "merge": {
                    "next": "merge_template"
                }
            }
        },
        "multiple_template": {
            "question": "Will you use a job template?",
            "options": {
                "yes": {
                    "endpoint": "/jobs/multi-docs-job-template"
                },
                "no": {
                    "endpoint": "/jobs/multi-doc"
                }
            }
        },
        "merge_template": {
            "question": "Will you use a job template for the merged document?",
            "options": {
                "yes": {
                    "endpoint": "/jobs/multi-doc-merge-job-template"
                },
                "no": {
                    "endpoint": "/jobs/multi-doc-merge"
                }
            }
        },
        "pdf_split_address": {
            "question": "How will you provide recipient addresses?",
            "options": {
                "capture_from_pdf": {
                    "endpoint": "/jobs/single-pdf-split-addressCapture"
                },
                "provide_separately": {
                    "endpoint": "/jobs/single-pdf-split"
                }
            }
        }
    }
    
    @classmethod
    def get_initial_question(cls) -> Dict[str, Any]:
        """Get the initial question for Level 1 decision tree"""
        return {
            "id": "initial",
            "question": cls.DECISION_TREE["initial"]["question"],
            "options": [
                {"value": "single", "label": "Single document", "description": "One document to one or more recipients"},
                {"value": "multiple", "label": "Multiple documents", "description": "Multiple separate documents"},
                {"value": "pdf_split", "label": "Split PDF", "description": "Split a large PDF into sections"}
            ]
        }
    
    @classmethod
    def get_question_by_id(cls, question_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific question by its ID"""
        if question_id not in cls.DECISION_TREE:
            return None
            
        node = cls.DECISION_TREE[question_id]
        
        # Format options
        options = []
        for opt_key, opt_value in node["options"].items():
            label = opt_key.replace("_", " ").title()
            options.append({
                "value": opt_key,
                "label": label,
                "description": cls._get_option_description(question_id, opt_key)
            })
            
        return {
            "id": question_id,
            "question": node["question"],
            "options": options
        }
    
    @classmethod
    def get_next_question(cls, current_id: str, answer: str) -> Optional[Dict[str, Any]]:
        """Get the next question based on current position and answer"""
        if current_id not in cls.DECISION_TREE:
            return None
            
        current_node = cls.DECISION_TREE[current_id]
        if answer not in current_node["options"]:
            return None
            
        option = current_node["options"][answer]
        
        # If we've reached an endpoint
        if "endpoint" in option:
            return {
                "type": "endpoint",
                "endpoint": option["endpoint"],
                "use_case": cls.ENDPOINT_TO_USECASE.get(option["endpoint"])
            }
            
        # If there's another question
        if "next" in option:
            next_id = option["next"]
            next_node = cls.DECISION_TREE.get(next_id)
            if next_node:
                # Format options for the next question
                options = []
                for opt_key, opt_value in next_node["options"].items():
                    label = opt_key.replace("_", " ").title()
                    options.append({
                        "value": opt_key,
                        "label": label,
                        "description": cls._get_option_description(next_id, opt_key)
                    })
                    
                return {
                    "type": "question",
                    "id": next_id,
                    "question": next_node["question"],
                    "options": options
                }
                
        return None
    
    @classmethod
    def _get_option_description(cls, node_id: str, option: str) -> str:
        """Get description for an option"""
        descriptions = {
            "multiple_action": {
                "separate": "Send each document to its own recipient",
                "merge": "Combine documents into one before sending"
            },
            "single_template": {
                "yes": "Use predefined mail settings from a template",
                "no": "Specify mail settings with this request"
            },
            "multiple_template": {
                "yes": "Use predefined mail settings from a template",
                "no": "Specify mail settings with this request"
            },
            "merge_template": {
                "yes": "Use predefined mail settings from a template",
                "no": "Specify mail settings with this request"
            },
            "pdf_split_address": {
                "capture_from_pdf": "Extract addresses from the PDF content",
                "provide_separately": "Provide addresses in the API request"
            }
        }
        
        return descriptions.get(node_id, {}).get(option, "")
    
    @classmethod
    def get_endpoint_info(cls, endpoint: str) -> Dict[str, Any]:
        """Get information about an endpoint"""
        info = {
            "/jobs/single-doc": {
                "name": "Single Document",
                "description": "Send one document to multiple recipients without a template",
                "use_case": "singleDocJobParams"
            },
            "/jobs/single-doc-job-template": {
                "name": "Single Document with Template",
                "description": "Send one document using a predefined job template",
                "use_case": "submitSingleDocWithTemplateParams"
            },
            "/jobs/multi-doc": {
                "name": "Multiple Documents",
                "description": "Send multiple documents, each to different recipients",
                "use_case": "submitMultiDocParams"
            },
            "/jobs/multi-docs-job-template": {
                "name": "Multiple Documents with Template",
                "description": "Send multiple documents using a job template",
                "use_case": "submitMultiDocWithTemplateParams"
            },
            "/jobs/multi-doc-merge": {
                "name": "Merge Documents",
                "description": "Merge multiple documents into one before sending",
                "use_case": "mergeMultiDocParams"
            },
            "/jobs/multi-doc-merge-job-template": {
                "name": "Merge Documents with Template",
                "description": "Merge multiple documents using a job template",
                "use_case": "mergeMultiDocWithTemplateParams"
            },
            "/jobs/single-pdf-split": {
                "name": "Split PDF",
                "description": "Split a large PDF into sections for different recipients",
                "use_case": "splitPdfParams"
            },
            "/jobs/single-pdf-split-addressCapture": {
                "name": "Split PDF with Address Capture",
                "description": "Split PDF and extract addresses from the content",
                "use_case": "splitPdfWithCaptureParams"
            },
            "/jobs/multi-pdf-addressCapture": {
                "name": "Multiple PDFs with Address Capture",
                "description": "Process multiple PDFs and capture addresses from each",
                "use_case": "multiPdfWithCaptureParams"
            }
        }
        
        return info.get(endpoint, {})
    
    @classmethod
    def get_all_endpoints(cls) -> List[str]:
        """Get list of all supported endpoints"""
        return list(cls.ENDPOINT_TO_USECASE.keys())