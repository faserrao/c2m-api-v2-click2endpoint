"""
Click2Endpoint - Phase 1: Fully Hardcoded Version
Beautiful UI with complete endpoint selection and code generation
"""

import streamlit as st
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="Click2Endpoint - C2M API v2",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Exact copy from original app.py
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Reduce default streamlit padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Hide default radio buttons */
    .stRadio > label {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #1f2937 !important;
        margin-bottom: 1rem !important;
    }
    
    .stRadio > div {
        gap: 1rem !important;
    }
    
    .stRadio > div > label {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        border: 2px solid transparent !important;
        display: block !important;
        text-align: center !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }
    
    /* Better readability for selectbox options */
    .stSelectbox label {
        color: #FF6B35 !important;
        font-weight: 600 !important;
    }
    
    .stRadio label {
        color: #FF6B35 !important;
        font-weight: 600 !important;
    }
    
    .stRadio > div > label:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Selected state */
    .stRadio > div > label[data-baseweb="radio"] > div:first-child {
        display: none !important;
    }
    
    /* Recommendation box */
    .recommendation-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border: 2px solid #2196f3;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 25px rgba(33, 150, 243, 0.2);
        text-align: center;
    }
    
    .endpoint-url {
        font-family: 'Courier New', monospace;
        font-size: 1.8rem;
        font-weight: bold;
        color: #1976d2;
        margin: 1rem 0;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Visual choice cards */
    .choice-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        min-height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .choice-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        border-color: #667eea;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Code block styling */
    .stCodeBlock {
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: transparent;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 0.8rem 2rem;
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        color: #666;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        border-color: #667eea;
        color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
    
    /* Address input section */
    .address-entry {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "current_step" not in st.session_state:
    st.session_state.current_step = "q1"
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "endpoint" not in st.session_state:
    st.session_state.endpoint = None
if "level2_params" not in st.session_state:
    st.session_state.level2_params = {}
if "address_entries" not in st.session_state:
    st.session_state.address_entries = []

# Hardcoded endpoint mapping based on QA_TREE_ALL_PATHS.md
def get_endpoint(answers):
    """Determine endpoint based on answers"""
    doc_type = answers.get("docType")
    template_usage = answers.get("templateUsage")
    
    if doc_type == "single":
        if template_usage == "true":
            return "/jobs/single-doc-job-template"
        else:
            return "/jobs/single-doc"
    elif doc_type == "multi":
        if template_usage == "true":
            return "/jobs/multi-docs-job-template"
        else:
            return "/jobs/multi-doc"
    elif doc_type == "merge":
        return "/jobs/multi-doc-merge-job-template"
    elif doc_type == "pdfSplit":
        return "/jobs/single-pdf-split"
    return None

def render_visual_choice(field, options, current_value=None):
    """Render visual icon-based choice buttons - from original app"""
    # Icon mapping
    icons = {
        "single": "📄",
        "multi": "📚", 
        "merge": "🔗",
        "pdfSplit": "✂️",
        "true": "✅",
        "false": "❌",
        "explicit": "📝",
        "template": "📋",
        "addressCapture": "🔍"
    }
    
    # First, render all cards in a row
    card_cols = st.columns(len(options))
    
    for idx, (col, opt) in enumerate(zip(card_cols, options)):
        with col:
            # Get icon
            icon = icons.get(opt["value"], "📌")
            
            # Check if selected
            is_selected = current_value == opt["value"]
            
            # Create card
            card_html = f"""
            <div class="choice-card" style="{'border-color: #667eea; background: linear-gradient(135deg, #f3f4ff 0%, #e9ecff 100%);' if is_selected else ''}">
                <div>
                    <div style="font-size: 72px; margin-bottom: 15px;">{icon}</div>
                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 8px; color: {'#667eea' if is_selected else '#1f2937'};">{opt['label']}</div>
                    <div style="font-size: 14px; color: #6b7280; line-height: 1.4;">{opt.get('description', '')}</div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    
    # Spacing
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Then render buttons
    button_cols = st.columns(len(options))
    selected = None
    
    for idx, (col, opt) in enumerate(zip(button_cols, options)):
        with col:
            is_selected = current_value == opt["value"]
            
            if st.button(
                "✓ Selected" if is_selected else "Select",
                key=f"{field}_{opt['value']}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                selected = opt["value"]
    
    return selected

def render_level1_questions():
    """Render Level 1 questions"""
    st.header("🎯 Find Your Perfect Endpoint")
    
    # Question 1: Document Type
    if st.session_state.current_step == "q1":
        st.subheader("Step 1: What type of document submission do you need?")
        
        options = [
            {"value": "single", "label": "Single document", "description": "One document going to one or more recipients"},
            {"value": "multi", "label": "Multiple separate documents", "description": "Multiple individual documents, each processed separately"},
            {"value": "merge", "label": "Multiple documents to merge", "description": "Multiple documents combined into one mailing"},
            {"value": "pdfSplit", "label": "Split a combined PDF", "description": "One PDF containing multiple documents that need to be separated"}
        ]
        
        selected = render_visual_choice("docType", options, st.session_state.answers.get("docType"))
        
        if selected:
            st.session_state.answers["docType"] = selected
            # Determine next question
            if selected in ["single", "multi", "merge"]:
                st.session_state.current_step = "q2"
            else:  # pdfSplit
                st.session_state.current_step = "q3"
            st.rerun()
    
    # Question 2: Template Usage
    elif st.session_state.current_step == "q2":
        st.subheader("Step 2: Will you use a saved job template?")
        
        options = [
            {"value": "true", "label": "Yes - Use saved template", "description": "Reuse settings from a previously saved job template"},
            {"value": "false", "label": "No - Configure manually", "description": "Set up all job parameters from scratch"}
        ]
        
        selected = render_visual_choice("templateUsage", options, st.session_state.answers.get("templateUsage"))
        
        if selected:
            st.session_state.answers["templateUsage"] = selected
            st.session_state.current_step = "q3"
            st.rerun()
    
    # Question 3: Recipient Style
    elif st.session_state.current_step == "q3":
        st.subheader("Step 3: How will recipient addresses be provided?")
        
        options = [
            {"value": "explicit", "label": "Provided in API call", "description": "Addresses sent as part of the API request"},
            {"value": "template", "label": "From template/mailing list", "description": "Use addresses saved in template or mailing list"},
            {"value": "addressCapture", "label": "Extract from document", "description": "Automatically capture addresses from the document content"}
        ]
        
        selected = render_visual_choice("recipientStyle", options, st.session_state.answers.get("recipientStyle"))
        
        if selected:
            st.session_state.answers["recipientStyle"] = selected
            # Check if we need Q4
            doc_type = st.session_state.answers.get("docType")
            if doc_type in ["multi", "merge"]:
                st.session_state.current_step = "q4"
            else:
                # Done with Level 1
                st.session_state.endpoint = get_endpoint(st.session_state.answers)
                st.session_state.current_step = "level2"
            st.rerun()
    
    # Question 4: Personalization
    elif st.session_state.current_step == "q4":
        st.subheader("Step 4: Is each document personalized for its recipient?")
        
        options = [
            {"value": "true", "label": "Yes - Unique per recipient", "description": "Each document has recipient-specific content"},
            {"value": "false", "label": "No - Same for all", "description": "Same document content for all recipients"}
        ]
        
        selected = render_visual_choice("personalized", options, st.session_state.answers.get("personalized"))
        
        if selected:
            st.session_state.answers["personalized"] = selected
            st.session_state.endpoint = get_endpoint(st.session_state.answers)
            st.session_state.current_step = "level2"
            st.rerun()

def render_document_specification(key_suffix=""):
    """Helper to render document specification with all 5 EBNF options"""
    # Show info about all options
    with st.expander("ℹ️ Document Specification Options", expanded=False):
        st.markdown("""
        **According to the EBNF, documents can be specified in 5 ways:**
        1. **Document ID** - Reference an existing document by its ID
        2. **External URL** - Provide a URL to fetch the document
        3. **Upload Request + Name** - Reference by upload request ID and document name
        4. **Zip + Document Name** - Reference within a zip file by name
        5. **Upload Request + Zip + Name** - Reference within a zip in an upload request
        """)
    
    doc_type = st.selectbox(
        "How will you specify the document?",
        ["Document ID", "External URL", "Upload Request + Name", "Zip + Document Name", "Upload Request + Zip + Name"],
        key=f"doc_spec_{key_suffix}",
        help="Select one of the 5 EBNF-defined methods"
    )
    
    # Render appropriate inputs based on selection
    if doc_type == "Document ID":
        st.text_input("📄 Document ID", key="param_doc_id", placeholder="doc_12345")
    elif doc_type == "External URL":
        st.text_input("🌐 External URL", key="param_doc_url", placeholder="https://example.com/document.pdf")
    elif doc_type == "Upload Request + Name":
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Upload Request ID", key="param_upload_id", placeholder="upload_789")
        with col2:
            st.text_input("Document Name", key="param_doc_name", placeholder="contract.pdf")
    elif doc_type == "Zip + Document Name":
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Zip ID", key="param_zip_id", placeholder="zip_456")
        with col2:
            st.text_input("Document Name", key="param_doc_name", placeholder="contract.pdf")
    else:  # Upload Request + Zip + Name
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("Upload Request ID", key="param_upload_id", placeholder="upload_789")
        with col2:
            st.text_input("Zip ID", key="param_zip_id", placeholder="zip_456")
        with col3:
            st.text_input("Document Name", key="param_doc_name", placeholder="contract.pdf")
    
    return doc_type

def render_address_inputs():
    """Render dynamic address input section"""
    st.subheader("📮 Recipient Addresses")
    
    # Add new recipient button
    if st.button("➕ Add Recipient", use_container_width=True):
        st.session_state.address_entries.append({
            'type': 'addressListId',
            'value': '',
            'address_data': {}
        })
        st.rerun()
    
    # Show existing entries
    for idx, entry in enumerate(st.session_state.address_entries):
        with st.container():
            st.markdown(f'<div class="address-entry">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 7, 1])
            
            with col1:
                entry['type'] = st.selectbox(
                    "Type",
                    ["addressListId", "addressId", "newAddress"],
                    format_func=lambda x: {
                        "addressListId": "Address List ID",
                        "addressId": "Single Address ID",
                        "newAddress": "New Address"
                    }[x],
                    key=f"addr_type_{idx}",
                    index=["addressListId", "addressId", "newAddress"].index(entry['type'])
                )
            
            with col2:
                if entry['type'] == "addressListId":
                    entry['value'] = st.text_input(
                        "List ID",
                        key=f"addr_value_{idx}",
                        placeholder="list_12345",
                        value=entry.get('value', '')
                    )
                elif entry['type'] == "addressId":
                    entry['value'] = st.text_input(
                        "Address ID",
                        key=f"addr_value_{idx}",
                        placeholder="addr_67890",
                        value=entry.get('value', '')
                    )
                else:  # newAddress
                    with st.expander("📝 Enter Address Details", expanded=True):
                        addr_col1, addr_col2 = st.columns(2)
                        
                        with addr_col1:
                            entry['address_data']['firstName'] = st.text_input(
                                "First Name",
                                key=f"fname_{idx}"
                            )
                            entry['address_data']['address1'] = st.text_input(
                                "Address Line 1",
                                key=f"addr1_{idx}"
                            )
                            entry['address_data']['city'] = st.text_input(
                                "City",
                                key=f"city_{idx}"
                            )
                            entry['address_data']['zip'] = st.text_input(
                                "ZIP Code",
                                key=f"zip_{idx}"
                            )
                        
                        with addr_col2:
                            entry['address_data']['lastName'] = st.text_input(
                                "Last Name",
                                key=f"lname_{idx}"
                            )
                            entry['address_data']['address2'] = st.text_input(
                                "Address Line 2 (optional)",
                                key=f"addr2_{idx}"
                            )
                            entry['address_data']['state'] = st.text_input(
                                "State",
                                key=f"state_{idx}"
                            )
                            entry['address_data']['country'] = st.text_input(
                                "Country",
                                key=f"country_{idx}",
                                value="USA"
                            )
            
            with col3:
                if st.button("🗑️", key=f"del_{idx}", help="Remove this address"):
                    st.session_state.address_entries.pop(idx)
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

def render_level2_parameters():
    """Render Level 2 parameter collection"""
    endpoint = st.session_state.endpoint
    
    # Show recommendation
    st.markdown(f"""
    <div class="recommendation-box">
        <h2>🎯 Recommended Endpoint</h2>
        <div class="endpoint-url">{endpoint}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("📝 Provide Required Parameters")
    
    # Hardcoded parameter forms based on endpoint
    if endpoint == "/jobs/single-doc-job-template":
        # First check Q3 answer about recipient style
        recipient_style = st.session_state.answers.get("recipientStyle")
        
        if recipient_style == "template":
            # Recipients come from template - only question is about document
            st.info("📋 Recipients will be provided by the template/mailing list")
            
            doc_option = st.selectbox(
                "How will the document be provided?",
                ["Document from template", "Document from API call"],
                key="doc_option"
            )
            
            if doc_option == "Document from API call":
                render_document_specification("template_recipients")
            # else document comes from template - no input needed
            
        elif recipient_style == "explicit":
            # Recipients provided in API call
            st.info("📝 You will provide recipient addresses in the API call")
            
            # Ask about document source
            doc_option = st.selectbox(
                "How will the document be provided?",
                ["Document from template", "Document from API call"],
                key="doc_option"
            )
            
            if doc_option == "Document from API call":
                render_document_specification("explicit_recipients")
            
            # Always need addresses when explicit
            render_address_inputs()
            
        else:  # addressCapture
            st.info("🔍 Recipients will be extracted from the document")
            render_document_specification("address_capture")
        
        # Always need template ID and optionally name
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("📋 Job Template ID", key="param_template_id", placeholder="template_12345", help="Required: Unique identifier for the template")
        with col2:
            st.text_input("📝 Job Template Name", key="param_template_name", placeholder="My Template", help="Optional: Human-readable name for the template")
    
    elif endpoint == "/jobs/single-doc":
        render_document_specification("single_doc")
        
        if st.session_state.answers.get("recipientStyle") == "explicit":
            render_address_inputs()
        
        # Job options
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Document Class", ["businessLetter", "personalLetter"], key="param_docclass")
            st.selectbox("Layout", ["portrait", "landscape"], key="param_layout")
            st.selectbox("Mail Class", ["firstClassMail", "priorityMail", "largeEnvelope"], key="param_mailclass")
        with col2:
            st.selectbox("Paper Type", ["letter", "legal", "postcard"], key="param_paper")
            st.selectbox("Print Option", ["color", "grayscale", "none"], key="param_print")
            st.selectbox("Envelope", ["flat", "windowedFlat", "letter", "legal", "postcard"], key="param_envelope")
    
    # Add more endpoint-specific forms...
    
    # Payment details (common to all)
    st.subheader("💳 Payment Details")
    payment_type = st.selectbox(
        "Payment Method",
        ["CREDIT_CARD", "INVOICE", "ACH", "USER_CREDIT", "APPLE_PAY", "GOOGLE_PAY"],
        key="param_payment"
    )
    
    if payment_type == "CREDIT_CARD":
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Card Number", key="param_cardnum", placeholder="1234 5678 9012 3456")
            st.text_input("Expiration", key="param_exp", placeholder="MM/YY")
        with col2:
            st.selectbox("Card Type", ["visa", "mastercard", "discover", "americanExpress"], key="param_cardtype")
            st.text_input("CVV", key="param_cvv", placeholder="123")
    elif payment_type == "INVOICE":
        st.text_input("Invoice Number", key="param_invoice_num", placeholder="INV-12345")
    elif payment_type == "ACH":
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Routing Number", key="param_routing", placeholder="123456789")
        with col2:
            st.text_input("Account Number", key="param_account", placeholder="9876543210")
    elif payment_type == "USER_CREDIT":
        st.number_input("Credit Amount", key="param_credit_amount", min_value=0.0, step=0.01, format="%.2f")
    elif payment_type in ["APPLE_PAY", "GOOGLE_PAY"]:
        st.info(f"💳 {payment_type.replace('_', ' ').title()} will be handled by the mobile wallet")
    
    # Tags
    st.text_input("🏷️ Tags (comma-separated)", key="param_tags", placeholder="campaign2024, bulk-mail")
    
    # Generate button
    if st.button("🚀 Generate API Call & Code", type="primary", use_container_width=True):
        st.session_state.current_step = "generate"
        st.rerun()

def generate_api_call():
    """Generate API call and code"""
    endpoint = st.session_state.endpoint
    
    # Build request body
    body = {}
    
    # Store params in session state first
    for key in st.session_state:
        if key.startswith("param_"):
            st.session_state.level2_params[key] = st.session_state[key]
    
    # Add document based on type - documentSourceIdentifier is a single value OR object
    if st.session_state.level2_params.get("param_doc_id"):
        body["documentSourceIdentifier"] = st.session_state.level2_params["param_doc_id"]
    elif st.session_state.level2_params.get("param_doc_url"):
        body["documentSourceIdentifier"] = st.session_state.level2_params["param_doc_url"]
    elif st.session_state.level2_params.get("param_upload_id") and st.session_state.level2_params.get("param_doc_name"):
        if st.session_state.level2_params.get("param_zip_id"):
            # Upload + Zip + Name
            body["documentSourceIdentifier"] = {
                "uploadRequestId": st.session_state.level2_params["param_upload_id"],
                "zipId": st.session_state.level2_params["param_zip_id"],
                "documentName": st.session_state.level2_params["param_doc_name"]
            }
        else:
            # Upload + Name
            body["documentSourceIdentifier"] = {
                "uploadRequestId": st.session_state.level2_params["param_upload_id"],
                "documentName": st.session_state.level2_params["param_doc_name"]
            }
    elif st.session_state.level2_params.get("param_zip_id") and st.session_state.level2_params.get("param_doc_name"):
        # Zip + Name
        body["documentSourceIdentifier"] = {
            "zipId": st.session_state.level2_params["param_zip_id"],
            "documentName": st.session_state.level2_params["param_doc_name"]
        }
    
    # Add recipients
    if st.session_state.address_entries:
        recipients = []
        for entry in st.session_state.address_entries:
            if entry['type'] == 'addressListId' and entry.get('value'):
                recipients.append({"addressListId": entry['value']})
            elif entry['type'] == 'addressId' and entry.get('value'):
                recipients.append({"addressId": entry['value']})
            elif entry['type'] == 'newAddress' and entry.get('address_data'):
                addr = entry['address_data']
                if addr.get('firstName') and addr.get('lastName'):
                    recipients.append({
                        "recipientAddress": {
                            "firstName": addr['firstName'],
                            "lastName": addr['lastName'],
                            "address1": addr.get('address1', ''),
                            "city": addr.get('city', ''),
                            "state": addr.get('state', ''),
                            "zip": addr.get('zip', ''),
                            "country": addr.get('country', 'USA')
                        }
                    })
        
        if recipients:
            body["recipientAddressSources"] = recipients
    
    # Add template - prefer ID over name
    if st.session_state.level2_params.get("param_template_id"):
        body["jobTemplate"] = st.session_state.level2_params["param_template_id"]
    elif st.session_state.level2_params.get("param_template_name"):
        body["jobTemplate"] = st.session_state.level2_params["param_template_name"]
    
    # Add payment details with proper structure
    if st.session_state.level2_params.get("param_payment"):
        payment_type = st.session_state.level2_params["param_payment"]
        payment_details = {"type": payment_type}
        
        if payment_type == "CREDIT_CARD":
            if st.session_state.level2_params.get("param_cardnum"):
                payment_details["creditCardDetails"] = {
                    "cardNumber": st.session_state.level2_params.get("param_cardnum", ""),
                    "cardType": st.session_state.level2_params.get("param_cardtype", ""),
                    "expirationDate": st.session_state.level2_params.get("param_exp", ""),
                    "cvv": st.session_state.level2_params.get("param_cvv", "")
                }
        elif payment_type == "INVOICE":
            if st.session_state.level2_params.get("param_invoice_num"):
                payment_details["invoiceDetails"] = {
                    "invoiceNumber": st.session_state.level2_params["param_invoice_num"]
                }
        elif payment_type == "ACH":
            if st.session_state.level2_params.get("param_routing"):
                payment_details["achDetails"] = {
                    "routingNumber": st.session_state.level2_params.get("param_routing", ""),
                    "accountNumber": st.session_state.level2_params.get("param_account", "")
                }
        elif payment_type == "USER_CREDIT":
            if st.session_state.level2_params.get("param_credit_amount"):
                payment_details["creditAmount"] = st.session_state.level2_params["param_credit_amount"]
        
        body["paymentDetails"] = payment_details
    
    # Add tags
    if st.session_state.level2_params.get("param_tags"):
        tags = [t.strip() for t in st.session_state.level2_params["param_tags"].split(",")]
        if tags:
            body["tags"] = tags
    
    return body

def render_code_generation():
    """Render generated code"""
    st.header("🚀 Your Generated API Call")
    
    body = generate_api_call()
    endpoint = st.session_state.endpoint
    
    # Create tabs for different code formats
    tab1, tab2, tab3, tab4 = st.tabs(["📋 JSON", "🐍 Python", "🟨 JavaScript", "🔧 cURL"])
    
    with tab1:
        st.subheader("Request Body")
        st.json(body)
    
    with tab2:
        st.subheader("Python Code")
        python_code = f'''import requests

url = "https://api.c2m.com/v2{endpoint}"
headers = {{
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}}

payload = {json.dumps(body, indent=4)}

response = requests.post(url, json=payload, headers=headers)
print(response.json())'''
        st.code(python_code, language="python")
    
    with tab3:
        st.subheader("JavaScript Code")
        js_code = f'''const axios = require('axios');

const url = 'https://api.c2m.com/v2{endpoint}';
const headers = {{
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}};

const payload = {json.dumps(body, indent=2)};

axios.post(url, payload, {{ headers }})
    .then(response => {{
        console.log(response.data);
    }})
    .catch(error => {{
        console.error('Error:', error);
    }});'''
        st.code(js_code, language="javascript")
    
    with tab4:
        st.subheader("cURL Command")
        curl_cmd = f'''curl -X POST https://api.c2m.com/v2{endpoint} \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(body)}'
'''
        st.code(curl_cmd, language="bash")

def main():
    st.title("🎯 Click2Endpoint - C2M API v2")
    
    # Progress indicator
    if st.session_state.current_step.startswith("q"):
        progress = {
            "q1": 0.25,
            "q2": 0.5,
            "q3": 0.75,
            "q4": 1.0
        }.get(st.session_state.current_step, 0)
        st.progress(progress)
    
    # Render appropriate section
    if st.session_state.current_step in ["q1", "q2", "q3", "q4"]:
        render_level1_questions()
    elif st.session_state.current_step == "level2":
        render_level2_parameters()
    elif st.session_state.current_step == "generate":
        # Store Level 2 params before generating
        for key in st.session_state:
            if key.startswith("param_"):
                st.session_state.level2_params[key] = st.session_state[key]
        render_code_generation()
    
    # Back button
    if st.session_state.current_step != "q1":
        st.markdown("---")
        if st.button("⬅️ Back"):
            # Determine previous step
            if st.session_state.current_step == "q2":
                st.session_state.current_step = "q1"
            elif st.session_state.current_step == "q3":
                if st.session_state.answers.get("docType") == "pdfSplit":
                    st.session_state.current_step = "q1"
                else:
                    st.session_state.current_step = "q2"
            elif st.session_state.current_step == "q4":
                st.session_state.current_step = "q3"
            elif st.session_state.current_step == "level2":
                if st.session_state.answers.get("docType") in ["multi", "merge"]:
                    st.session_state.current_step = "q4"
                else:
                    st.session_state.current_step = "q3"
            elif st.session_state.current_step == "generate":
                st.session_state.current_step = "level2"
            st.rerun()

if __name__ == "__main__":
    main()