"""
Click2Endpoint with Template Integration
Combines attractive UI with EBNF-based template handling
"""

import streamlit as st
import sys
from pathlib import Path
import json
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.endpoint_mapper import EndpointMapper
from scripts.ebnf_template_parser import EBNFTemplateParser

# Page configuration
st.set_page_config(
    page_title="Click2Endpoint - C2M API v2",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with enhanced styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Card container */
    .card-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    /* Card styling */
    .option-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .option-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    
    .option-card.selected {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        border: 3px solid #2e7d32;
    }
    
    .card-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .card-description {
        font-size: 0.9rem;
        opacity: 0.9;
        line-height: 1.4;
    }
    
    /* Template option card */
    .template-option-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        color: #1565C0;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .template-option-card:hover {
        border-color: #1565C0;
        transform: translateX(5px);
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
    
    .endpoint-display {
        font-family: 'Courier New', monospace;
        font-size: 1.6rem;
        font-weight: bold;
        color: #1976d2;
        margin: 1rem 0;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* API Call box */
    .api-call-box {
        background: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
    }
    
    /* Progress indicator */
    .step-indicator {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
        gap: 1rem;
    }
    
    .step {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 500;
    }
    
    .step.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .step.completed {
        background: #4CAF50;
        color: white;
    }
    
    .step.pending {
        background: #e0e0e0;
        color: #666;
    }
    
    /* Address input styling */
    .address-entry {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .stButton > button[kind="secondary"] {
        background: #f44336;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

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

# Helper functions
def render_option_card(key, icon, title, description, selected=False):
    """Render an option card with click handling"""
    card_class = "option-card selected" if selected else "option-card"
    card_html = f"""
    <div class="{card_class}" onclick="window.location.hash='{key}'">
        <div class="card-icon">{icon}</div>
        <div class="card-title">{title}</div>
        <div class="card-description">{description}</div>
    </div>
    """
    return card_html

def render_template_option_card(option_text, selected=False):
    """Render a template option card"""
    card_class = "template-option-card selected" if selected else "template-option-card"
    return f"""
    <div class="{card_class}">
        <div>{option_text}</div>
    </div>
    """

# Level 1 Navigation
LEVEL1_CARDS = {
    "single": {
        "icon": "📄",
        "title": "Single document",
        "description": "One document going to one or more recipients"
    },
    "multiple": {
        "icon": "📚",
        "title": "Multiple documents",
        "description": "Multiple individual documents, each processed separately"
    },
    "merge": {
        "icon": "🔗",
        "title": "Merge documents",
        "description": "Multiple documents combined into one mailing"
    },
    "split": {
        "icon": "✂️",
        "title": "Split a PDF",
        "description": "One PDF containing multiple documents that need to be separated"
    }
}

def show_level1():
    """Show Level 1 card-based navigation"""
    st.header("Step 1: What type of document submission do you need?")
    
    # Create card grid
    cols = st.columns(4)
    for idx, (key, card_info) in enumerate(LEVEL1_CARDS.items()):
        with cols[idx]:
            if st.button(
                f"{card_info['icon']}\n\n**{card_info['title']}**\n\n{card_info['description']}",
                key=f"card_{key}",
                use_container_width=True,
                help=card_info['description']
            ):
                st.session_state.level1_choice = key
                st.session_state.current_step = "level1_sub"
                st.rerun()

def show_level1_sub():
    """Show sub-questions for Level 1"""
    choice = st.session_state.level1_choice
    
    if choice == "single":
        st.header("Step 2: Will you use a saved job template?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "📌\n\n**Yes - Use saved template**\n\nReuse settings from a previously saved job template",
                key="single_template",
                use_container_width=True
            ):
                st.session_state.endpoint = "/jobs/single-doc-job-template"
                st.session_state.current_step = "level2"
                st.rerun()
        with col2:
            if st.button(
                "⚙️\n\n**No - Configure manually**\n\nSet up all job parameters from scratch",
                key="single_specify",
                use_container_width=True
            ):
                st.session_state.endpoint = "/jobs/single-doc"
                st.session_state.current_step = "level2"
                st.rerun()
    
    elif choice == "multiple":
        st.header("Step 2: How should the documents be handled?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "📬\n\n**Separate mailings**\n\nEach document goes to different recipients",
                key="multi_separate",
                use_container_width=True
            ):
                st.session_state.multi_type = "separate"
                st.session_state.current_step = "multi_template"
                st.rerun()
        with col2:
            if st.button(
                "🔗\n\n**Merge into one**\n\nCombine all documents before sending",
                key="multi_merge",
                use_container_width=True
            ):
                st.session_state.endpoint = "/jobs/multi-doc-merge-job-template"
                st.session_state.current_step = "level2"
                st.rerun()
    
    # Add more sub-questions for merge and split...

def show_level2():
    """Show Level 2 parameter collection with template logic"""
    mapper = get_mapper()
    parser = get_parser()
    
    endpoint = st.session_state.endpoint
    endpoint_name = mapper.endpoint_to_usecase(endpoint)
    
    if not endpoint_name:
        st.error(f"No EBNF mapping found for endpoint: {endpoint}")
        return
    
    # Show recommendation box
    st.markdown(f"""
    <div class="recommendation-box">
        <h2>🎯 Recommended Endpoint</h2>
        <div class="endpoint-display">{endpoint}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get UI flow
    ui_flow = parser.generate_ui_flow(endpoint_name)
    
    # Initialize parameter collection
    if 'parameters' not in st.session_state:
        st.session_state.parameters = {}
    
    # Handle template logic
    if ui_flow.get('has_template_logic'):
        st.header("Step 3: Configure Template Options")
        
        # Template choice question
        template_q = ui_flow['questions'][0]
        st.subheader(template_q['question'])
        
        # Show template options as cards
        for opt in template_q['options']:
            if st.button(
                opt['label'],
                key=f"template_opt_{opt['value']}",
                use_container_width=True
            ):
                st.session_state.selected_template_option = opt
                st.rerun()
        
        # Handle selected option
        if 'selected_template_option' in st.session_state:
            selected_opt = st.session_state.selected_template_option
            
            # Check if document choice is needed
            if selected_opt.get('requires_document_choice', False):
                st.markdown("---")
                st.subheader("How will the document be provided?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(
                        "📋 Document from template",
                        key="doc_from_template",
                        use_container_width=True
                    ):
                        st.session_state.document_from_template = True
                        st.rerun()
                with col2:
                    if st.button(
                        "📄 Document in API call",
                        key="doc_from_api",
                        use_container_width=True
                    ):
                        st.session_state.document_from_template = False
                        st.rerun()
                
                # Determine what to show based on document choice
                if 'document_from_template' in st.session_state:
                    if st.session_state.document_from_template:
                        params_to_show = ['recipientAddressSource']
                    else:
                        params_to_show = selected_opt['from_api']
                else:
                    return  # Wait for document choice
            else:
                params_to_show = selected_opt['from_api']
            
            # Show required parameters
            if params_to_show:
                st.markdown("---")
                st.subheader("Required Information")
                
                for param in params_to_show:
                    if param == 'documentSourceIdentifier':
                        st.text_input(
                            "Document ID or URL",
                            key="param_doc",
                            placeholder="e.g., doc_12345 or https://example.com/document.pdf"
                        )
                    elif param == 'recipientAddressSource':
                        show_recipient_address_inputs()
                    elif param == 'documentsToMerge':
                        st.text_area(
                            "Documents to Merge (one per line)",
                            key="param_docs_merge",
                            placeholder="doc_123\ndoc_456\ndoc_789"
                        )
            
            # Always required parameters
            st.markdown("---")
            st.subheader("Additional Required Information")
            
            st.text_input("Job Template ID", key="param_template_id", placeholder="template_12345")
            
            payment_type = st.selectbox(
                "Payment Method",
                ["CREDIT_CARD", "INVOICE", "ACH", "USER_CREDIT", "APPLE_PAY", "GOOGLE_PAY"],
                key="param_payment"
            )
            
            st.text_input("Tags (optional)", key="param_tags", placeholder="campaign2024, bulk-mail")
            
            # Generate API call button
            if st.button("🚀 Generate API Call", type="primary", use_container_width=True):
                generate_api_call(endpoint, st.session_state)

def show_recipient_address_inputs():
    """Show dynamic recipient address input fields"""
    st.write("**Recipient Addresses**")
    
    # Initialize address list in session state
    if 'address_entries' not in st.session_state:
        st.session_state.address_entries = []
    
    # Address type options (hardcoded for now)
    address_types = {
        "addressListId": "Address List ID",
        "addressId": "Single Address ID", 
        "newAddress": "New Address Details"
    }
    
    # Show existing entries
    for idx, entry in enumerate(st.session_state.address_entries):
        col1, col2, col3 = st.columns([3, 5, 1])
        
        with col1:
            # Address type selector
            selected_type = st.selectbox(
                "Type",
                options=list(address_types.keys()),
                format_func=lambda x: address_types[x],
                key=f"addr_type_{idx}",
                index=list(address_types.keys()).index(entry['type'])
            )
            entry['type'] = selected_type
        
        with col2:
            # Input based on type
            if selected_type == "addressListId":
                entry['value'] = st.text_input(
                    "List ID",
                    key=f"addr_value_{idx}",
                    placeholder="list_12345",
                    value=entry.get('value', '')
                )
            elif selected_type == "addressId":
                entry['value'] = st.text_input(
                    "Address ID",
                    key=f"addr_value_{idx}",
                    placeholder="addr_67890",
                    value=entry.get('value', '')
                )
            else:  # newAddress
                # Show expandable form for new address
                with st.expander("Address Details", expanded=True):
                    if 'address_data' not in entry:
                        entry['address_data'] = {}
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        entry['address_data']['firstName'] = st.text_input(
                            "First Name",
                            key=f"addr_fname_{idx}",
                            value=entry.get('address_data', {}).get('firstName', '')
                        )
                        entry['address_data']['address1'] = st.text_input(
                            "Address Line 1",
                            key=f"addr_line1_{idx}",
                            value=entry.get('address_data', {}).get('address1', '')
                        )
                        entry['address_data']['city'] = st.text_input(
                            "City",
                            key=f"addr_city_{idx}",
                            value=entry.get('address_data', {}).get('city', '')
                        )
                        entry['address_data']['zip'] = st.text_input(
                            "ZIP Code",
                            key=f"addr_zip_{idx}",
                            value=entry.get('address_data', {}).get('zip', '')
                        )
                    with col_b:
                        entry['address_data']['lastName'] = st.text_input(
                            "Last Name",
                            key=f"addr_lname_{idx}",
                            value=entry.get('address_data', {}).get('lastName', '')
                        )
                        entry['address_data']['address2'] = st.text_input(
                            "Address Line 2 (optional)",
                            key=f"addr_line2_{idx}",
                            value=entry.get('address_data', {}).get('address2', '')
                        )
                        entry['address_data']['state'] = st.text_input(
                            "State",
                            key=f"addr_state_{idx}",
                            value=entry.get('address_data', {}).get('state', '')
                        )
                        entry['address_data']['country'] = st.text_input(
                            "Country",
                            key=f"addr_country_{idx}",
                            value=entry.get('address_data', {}).get('country', 'USA')
                        )
        
        with col3:
            # Remove button
            if st.button("🗑️", key=f"remove_{idx}", help="Remove this address"):
                st.session_state.address_entries.pop(idx)
                st.rerun()
    
    # Add new entry button
    if st.button("➕ Add Recipient", key="add_address", use_container_width=True):
        st.session_state.address_entries.append({
            'type': 'addressListId',
            'value': ''
        })
        st.rerun()

def generate_api_call(endpoint, params):
    """Generate and display the API call"""
    # Build request body based on collected parameters
    body = {}
    
    # Add parameters based on what was collected
    if params.get('param_doc'):
        body['documentSourceIdentifier'] = params.param_doc
    
    # Handle recipient addresses
    if 'address_entries' in params and params.address_entries:
        # Build recipient array based on address entries
        recipients = []
        for entry in params.address_entries:
            if entry['type'] == 'addressListId' and entry.get('value'):
                recipients.append({
                    'addressListId': entry['value']
                })
            elif entry['type'] == 'addressId' and entry.get('value'):
                recipients.append({
                    'addressId': entry['value']
                })
            elif entry['type'] == 'newAddress' and entry.get('address_data'):
                # Build recipient address object
                addr = entry['address_data']
                recipient = {
                    'recipientAddress': {
                        'firstName': addr.get('firstName', ''),
                        'lastName': addr.get('lastName', ''),
                        'address1': addr.get('address1', ''),
                        'city': addr.get('city', ''),
                        'state': addr.get('state', ''),
                        'zip': addr.get('zip', ''),
                        'country': addr.get('country', 'USA')
                    }
                }
                # Add optional fields
                if addr.get('address2'):
                    recipient['recipientAddress']['address2'] = addr['address2']
                recipients.append(recipient)
        
        if recipients:
            body['recipientAddressSources'] = recipients
    
    if params.get('param_docs_merge'):
        docs = params.param_docs_merge.strip().split('\n')
        body['documentsToMerge'] = docs
    
    if params.get('param_template_id'):
        body['jobTemplate'] = params.param_template_id
    
    if params.get('param_payment'):
        body['paymentDetails'] = {
            "type": params.param_payment
        }
    
    if params.get('param_tags'):
        body['tags'] = params.param_tags.split(',')
    
    # Display API call
    st.markdown("### Generated API Call")
    
    api_call = f"""
**Endpoint:** `POST {endpoint}`

**Request Body:**
```json
{json.dumps(body, indent=2)}
```

**cURL Command:**
```bash
curl -X POST https://api.c2m.com/v2{endpoint} \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -d '{json.dumps(body)}'
```
    """
    
    st.markdown(api_call)
    
    # Add copy buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Copy JSON", use_container_width=True):
            st.write("JSON copied to clipboard!")
    with col2:
        if st.button("📋 Copy cURL", use_container_width=True):
            st.write("cURL command copied to clipboard!")

def main():
    st.title("🎯 Click2Endpoint - C2M API v2")
    st.markdown("Navigate to the perfect API endpoint with intelligent template handling")
    
    # Initialize session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'level1'
    
    # Show progress
    steps = ['Select Type', 'Choose Options', 'Configure']
    current_idx = 0
    if st.session_state.current_step == 'level1_sub':
        current_idx = 1
    elif st.session_state.current_step == 'level2':
        current_idx = 2
    
    # Progress bar
    st.markdown("""
    <div class="step-indicator">
    """, unsafe_allow_html=True)
    
    for idx, step in enumerate(steps):
        if idx < current_idx:
            st.markdown(f'<span class="step completed">{step}</span>', unsafe_allow_html=True)
        elif idx == current_idx:
            st.markdown(f'<span class="step active">{step}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="step pending">{step}</span>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Navigation
    if st.session_state.current_step == 'level1':
        show_level1()
    elif st.session_state.current_step == 'level1_sub':
        show_level1_sub()
    elif st.session_state.current_step == 'level2':
        show_level2()
    
    # Back button
    if st.session_state.current_step != 'level1':
        st.markdown("---")
        if st.button("⬅️ Back"):
            if st.session_state.current_step == 'level2':
                st.session_state.current_step = 'level1_sub'
            else:
                st.session_state.current_step = 'level1'
            # Clear selections
            for key in ['selected_template_option', 'document_from_template']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()