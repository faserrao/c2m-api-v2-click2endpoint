#!/usr/bin/env python3
"""
Integrated C2M Endpoint Navigator with EBNF Template Parser
Uses hardcoded Level 1 questions and EBNF-driven Level 2 questions
Handles template business logic for Use Cases 1 and 3
"""

import streamlit as st
import sys
from pathlib import Path
import json
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.endpoint_mapper import EndpointMapper
from scripts.ebnf_template_parser import EBNFTemplateParser
import requests

# Initialize components
@st.cache_resource
def get_mapper():
    return EndpointMapper()

@st.cache_resource
def get_parser():
    ebnf_path = Path(__file__).parent.parent.parent / "c2mapiv2-dd.ebnf"
    parser = EBNFTemplateParser(str(ebnf_path))
    parser.parse()
    return parser

# Level 1 Questions - Hardcoded
LEVEL1_QUESTIONS = {
    "start": {
        "question": "What would you like to do?",
        "options": {
            "single": "Send one document",
            "multiple": "Send multiple documents", 
            "merge": "Merge documents",
            "split": "Split a PDF"
        }
    },
    "single": {
        "question": "How will you define the mailing options?",
        "options": {
            "template": "Use a saved template",
            "specify": "Specify all options now"
        }
    },
    "multiple": {
        "question": "How will you handle documents?",
        "options": {
            "separate": "Each document to different recipients",
            "merge": "Merge into one document"
        }
    },
    "multiple_separate": {
        "question": "How will you define the mailing options?",
        "options": {
            "template": "Use a saved template",
            "specify": "Specify all options now"
        }
    },
    "merge": {
        "question": "Will you use a template?",
        "options": {
            "yes": "Yes, use a saved template",
            "no": "No, specify all options now"
        }
    },
    "split": {
        "question": "How are the recipient addresses provided?",
        "options": {
            "external": "I'll provide addresses separately",
            "embedded": "Addresses are in the PDF"
        }
    },
    "split_embedded": {
        "question": "How many PDFs with embedded addresses?",
        "options": {
            "single": "Single PDF with all addresses",
            "multiple": "Multiple PDFs, each with addresses"
        }
    }
}

def process_level1_decision(path):
    """Process Level 1 decision path and return endpoint"""
    if path == ["single", "template"]:
        return "/jobs/single-doc-job-template"
    elif path == ["single", "specify"]:
        return "/jobs/single-doc"
    elif path == ["multiple", "separate", "template"]:
        return "/jobs/multi-docs-job-template"
    elif path == ["multiple", "separate", "specify"]:
        return "/jobs/multi-doc"
    elif path == ["multiple", "merge"] or path == ["merge", "yes"]:
        return "/jobs/multi-doc-merge-job-template"
    elif path == ["merge", "no"]:
        return "/jobs/multi-doc-merge"
    elif path == ["split", "external"]:
        return "/jobs/single-pdf-split"
    elif path == ["split", "embedded", "single"]:
        return "/jobs/single-pdf-split-addressCapture"
    elif path == ["split", "embedded", "multiple"]:
        return "/jobs/multi-pdf-address-capture"
    else:
        return None

def render_card(title, description, icon):
    """Render a styled card"""
    st.markdown(f"""
    <div class="endpoint-card">
        <div style="font-size: 2em; margin-bottom: 10px;">{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

def show_level1_questions():
    """Display Level 1 questions to identify endpoint"""
    st.header("🎯 Level 1: Find Your Endpoint")
    
    # Initialize session state
    if 'level1_path' not in st.session_state:
        st.session_state.level1_path = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = "start"
    
    # Show current question
    current_q = LEVEL1_QUESTIONS.get(st.session_state.current_question, {})
    
    if current_q:
        st.write(f"**{current_q['question']}**")
        
        # Create columns for options
        cols = st.columns(len(current_q['options']))
        
        for idx, (key, label) in enumerate(current_q['options'].items()):
            with cols[idx]:
                if st.button(label, key=f"opt_{key}", use_container_width=True):
                    # Add to path
                    st.session_state.level1_path.append(key)
                    
                    # Determine next question
                    if st.session_state.current_question == "start":
                        if key == "single":
                            st.session_state.current_question = "single"
                        elif key == "multiple":
                            st.session_state.current_question = "multiple"
                        elif key == "merge":
                            st.session_state.current_question = "merge"
                        elif key == "split":
                            st.session_state.current_question = "split"
                    elif st.session_state.current_question == "single":
                        # Complete - found endpoint
                        st.session_state.endpoint = process_level1_decision(st.session_state.level1_path)
                        st.session_state.show_level2 = True
                    elif st.session_state.current_question == "single_template":
                        # Complete - found endpoint
                        st.session_state.endpoint = process_level1_decision(st.session_state.level1_path)
                        st.session_state.show_level2 = True
                    elif st.session_state.current_question == "multiple":
                        if key == "separate":
                            st.session_state.current_question = "multiple_separate"
                        else:
                            # Complete - found endpoint
                            st.session_state.endpoint = process_level1_decision(st.session_state.level1_path)
                            st.session_state.show_level2 = True
                    elif st.session_state.current_question == "multiple_separate":
                        # Complete - found endpoint
                        st.session_state.endpoint = process_level1_decision(st.session_state.level1_path)
                        st.session_state.show_level2 = True
                    elif st.session_state.current_question == "merge":
                        # Complete - found endpoint
                        st.session_state.endpoint = process_level1_decision(st.session_state.level1_path)
                        st.session_state.show_level2 = True
                    elif st.session_state.current_question == "split":
                        if key == "embedded":
                            st.session_state.current_question = "split_embedded"
                        else:
                            # Complete - found endpoint
                            st.session_state.endpoint = process_level1_decision(st.session_state.level1_path)
                            st.session_state.show_level2 = True
                    elif st.session_state.current_question == "split_embedded":
                        # Complete - found endpoint
                        st.session_state.endpoint = process_level1_decision(st.session_state.level1_path)
                        st.session_state.show_level2 = True
                    
                    st.rerun()
        
        # Show breadcrumb
        if st.session_state.level1_path:
            st.markdown("---")
            breadcrumb = " → ".join([f"**{p}**" for p in st.session_state.level1_path])
            st.write(f"Path: {breadcrumb}")
            
            if st.button("↩️ Start Over"):
                st.session_state.level1_path = []
                st.session_state.current_question = "start"
                st.session_state.show_level2 = False
                if 'endpoint' in st.session_state:
                    del st.session_state.endpoint
                st.rerun()

def show_level2_questions():
    """Display Level 2 parameter collection based on EBNF"""
    st.header("📝 Level 2: Provide Parameters")
    
    mapper = get_mapper()
    parser = get_parser()
    
    # Get the endpoint production name
    endpoint_name = mapper.endpoint_to_usecase(st.session_state.endpoint)
    
    if not endpoint_name:
        st.error(f"No EBNF mapping found for endpoint: {st.session_state.endpoint}")
        return
    
    st.info(f"**Endpoint:** `{st.session_state.endpoint}`")
    
    # Generate UI flow
    ui_flow = parser.generate_ui_flow(endpoint_name)
    
    # Initialize parameter storage
    if 'parameters' not in st.session_state:
        st.session_state.parameters = {}
    
    # Check if this endpoint has template logic
    if ui_flow.get('has_template_logic'):
        st.subheader("Template Configuration")
        
        # Show template choice question
        template_q = ui_flow['questions'][0]  # First question is always template choice
        
        template_choice = st.selectbox(
            template_q['question'],
            options=[opt['label'] for opt in template_q['options']],
            key="template_choice_select"
        )
        
        # Find selected option details
        selected_opt = None
        for opt in template_q['options']:
            if opt['label'] == template_choice:
                selected_opt = opt
                break
        
        if selected_opt:
            st.session_state.parameters['_template_choice'] = {
                'from_template': selected_opt['from_template'],
                'from_api': selected_opt['from_api']
            }
            
            # Check if this option requires a document choice (Use Case 1, option 3)
            if selected_opt.get('requires_document_choice', False):
                st.markdown("### Document Source")
                doc_choice = st.radio(
                    "How will the document be provided?",
                    ["Document comes from the job template", "Document provided in API call"],
                    key="document_source_choice"
                )
                
                if doc_choice == "Document comes from the job template":
                    # Document from template, only need recipients
                    st.session_state.parameters['_document_from_template'] = True
                    params_to_show = ['recipientAddressSource']
                else:
                    # Document from API call, need both
                    st.session_state.parameters['_document_from_template'] = False
                    params_to_show = selected_opt['from_api']
            else:
                params_to_show = selected_opt['from_api']
            
            # Show what needs to be provided based on template choice
            if params_to_show:
                st.markdown("### You need to provide:")
                for param in params_to_show:
                    # Find the parameter definition
                    if param in parser.parameters:
                        p = parser.parameters[param]
                        render_parameter_input(param, p)
                    else:
                        # Default input for unrecognized parameters
                        st.text_input(f"Please provide {param}", key=f"param_{param}")
        
        # Show other required parameters (always required)
        st.markdown("### Additional Required Information:")
        for q in ui_flow['questions'][1:]:  # Skip template choice
            param_name = q['id']
            if param_name in parser.parameters:
                p = parser.parameters[param_name]
                render_parameter_input(param_name, p)
            else:
                # Use question from UI flow
                if q['type'] == 'choice':
                    st.selectbox(q['question'], ['Option 1', 'Option 2'], key=f"param_{param_name}")
                else:
                    st.text_input(q['question'], key=f"param_{param_name}")
    else:
        # Standard endpoint without template logic
        st.subheader("Required Parameters")
        
        # For now, show basic inputs based on endpoint
        # This would be expanded to use EBNF parser for all parameters
        st.info("Standard parameter collection would go here based on EBNF definition")

def render_parameter_input(param_name, param_def):
    """Render appropriate input widget for a parameter"""
    if param_def.param_type == 'choice':
        # For payment types
        if param_name == 'paymentDetails':
            options = ['CREDIT_CARD', 'INVOICE', 'ACH', 'USER_CREDIT', 'APPLE_PAY', 'GOOGLE_PAY']
            value = st.selectbox(param_def.question, options, key=f"param_{param_name}")
            st.session_state.parameters[param_name] = value
        else:
            st.selectbox(param_def.question, ['Option 1', 'Option 2'], key=f"param_{param_name}")
    elif param_def.param_type == 'address':
        # Special handling for addresses
        with st.expander(f"📍 {param_def.question}"):
            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input("First Name", key=f"{param_name}_fname")
                addr1 = st.text_input("Address Line 1", key=f"{param_name}_addr1")
                city = st.text_input("City", key=f"{param_name}_city")
            with col2:
                lname = st.text_input("Last Name", key=f"{param_name}_lname")
                addr2 = st.text_input("Address Line 2 (optional)", key=f"{param_name}_addr2")
                state = st.text_input("State", key=f"{param_name}_state")
            zip_code = st.text_input("ZIP Code", key=f"{param_name}_zip")
            country = st.text_input("Country", value="USA", key=f"{param_name}_country")
    elif param_def.is_repeatable:
        # Multiple values allowed
        st.text_area(f"{param_def.question} (one per line)", key=f"param_{param_name}")
    else:
        # Standard text input
        value = st.text_input(param_def.question, key=f"param_{param_name}")
        st.session_state.parameters[param_name] = value

def main():
    st.set_page_config(
        page_title="C2M Endpoint Navigator - Template Integrated",
        page_icon="🚀",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .endpoint-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        text-align: center;
        transition: transform 0.2s;
    }
    .endpoint-card:hover {
        transform: translateY(-5px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🚀 C2M Endpoint Navigator - Template Integrated")
    st.markdown("Navigate to the right C2M API endpoint with intelligent template handling")
    
    # Initialize session state
    if 'show_level2' not in st.session_state:
        st.session_state.show_level2 = False
    
    # Main navigation
    if not st.session_state.show_level2:
        show_level1_questions()
    else:
        show_level2_questions()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Level 1", use_container_width=True):
                st.session_state.show_level2 = False
                st.session_state.level1_path = []
                st.session_state.current_question = "start"
                if 'endpoint' in st.session_state:
                    del st.session_state.endpoint
                if 'parameters' in st.session_state:
                    del st.session_state.parameters
                st.rerun()
        
        with col2:
            if st.button("✅ Generate API Request", type="primary", use_container_width=True):
                st.success(f"Ready to submit to: {st.session_state.endpoint}")
                
                # Show collected parameters
                if st.session_state.parameters:
                    st.json(st.session_state.parameters)

if __name__ == "__main__":
    main()