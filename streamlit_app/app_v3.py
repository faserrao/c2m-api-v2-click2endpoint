"""
Click2Endpoint v3 - Beautiful Card-Based UI with Template Integration
"""

import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

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

# Custom CSS - Exact match to original beautiful design
st.markdown("""
<style>
    /* Reset and base styles */
    .main {
        padding: 0rem 1rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Card container */
    .card-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    /* Beautiful option cards */
    .option-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 20px;
        padding: 2.5rem 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        min-height: 250px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .option-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }
    
    .option-card.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .option-card.selected .card-icon,
    .option-card.selected .card-title,
    .option-card.selected .card-description {
        color: white !important;
    }
    
    .card-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        color: #667eea;
    }
    
    .card-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .card-description {
        font-size: 0.95rem;
        color: #718096;
        line-height: 1.5;
    }
    
    /* Select button styling */
    .select-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.7rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        margin-top: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9rem;
    }
    
    .select-button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Step header styling */
    .step-header {
        text-align: center;
        margin: 2rem 0 3rem 0;
    }
    
    .step-header h1 {
        color: #2d3748;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .step-header p {
        color: #718096;
        font-size: 1.1rem;
    }
    
    /* Template option cards */
    .template-option-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .template-option-card:hover {
        border-color: #667eea;
        background: #f7fafc;
    }
    
    .template-option-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
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
    
    /* Address input section */
    .address-section {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .address-entry {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Hide Streamlit's default button styling */
    .stButton > button {
        width: 100%;
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

def render_step_1():
    """Render Step 1 with beautiful cards"""
    # Header
    st.markdown("""
    <div class="step-header">
        <h1>Step 1: What type of document submission do you need?</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Card options
    cards_html = '<div class="card-container">'
    
    cards = [
        {
            "id": "single",
            "icon": "📄",
            "title": "Single document",
            "description": "One document going to one or more recipients"
        },
        {
            "id": "multiple",
            "icon": "📚", 
            "title": "Multiple separate documents",
            "description": "Multiple individual documents, each processed separately"
        },
        {
            "id": "merge",
            "icon": "🔗",
            "title": "Multiple documents to merge",
            "description": "Multiple documents combined into one mailing"
        },
        {
            "id": "split",
            "icon": "✂️",
            "title": "Split a combined PDF",
            "description": "One PDF containing multiple documents that need to be separated"
        }
    ]
    
    selected = st.session_state.get('step1_choice', None)
    
    for card in cards:
        selected_class = "selected" if selected == card["id"] else ""
        cards_html += f"""
        <div class="option-card {selected_class}" onclick="window.dispatchEvent(new CustomEvent('select_card', {{detail: '{card["id"]}'}}))">
            <div class="card-icon">{card["icon"]}</div>
            <div class="card-title">{card["title"]}</div>
            <div class="card-description">{card["description"]}</div>
        </div>
        """
    
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)
    
    # Selection buttons
    cols = st.columns(4)
    for idx, card in enumerate(cards):
        with cols[idx]:
            if st.button(
                "✓ SELECT",
                key=f"select_{card['id']}",
                disabled=(selected != card['id']) if selected else False
            ):
                st.session_state.step1_choice = card['id']
                st.session_state.current_step = 'step2'
                st.rerun()

def render_step_2():
    """Render Step 2 based on Step 1 choice"""
    choice = st.session_state.step1_choice
    
    if choice == "single":
        st.markdown("""
        <div class="step-header">
            <h1>Step 2: Will you use a saved job template?</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Two card options
        cards_html = '<div class="card-container" style="grid-template-columns: repeat(2, 1fr); max-width: 800px; margin: 0 auto;">'
        
        options = [
            {
                "id": "template",
                "icon": "📌",
                "title": "Yes - Use saved template",
                "description": "Reuse settings from a previously saved job template"
            },
            {
                "id": "manual",
                "icon": "⚙️",
                "title": "No - Configure manually",
                "description": "Set up all job parameters from scratch"
            }
        ]
        
        selected = st.session_state.get('step2_choice', None)
        
        for opt in options:
            selected_class = "selected" if selected == opt["id"] else ""
            cards_html += f"""
            <div class="option-card {selected_class}">
                <div class="card-icon">{opt["icon"]}</div>
                <div class="card-title">{opt["title"]}</div>
                <div class="card-description">{opt["description"]}</div>
            </div>
            """
        
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)
        
        # Selection buttons
        cols = st.columns(2)
        with cols[0]:
            if st.button("✓ SELECT", key="select_template"):
                st.session_state.step2_choice = "template"
                st.session_state.endpoint = "/jobs/single-doc-job-template"
                st.session_state.current_step = 'step3'
                st.rerun()
        with cols[1]:
            if st.button("✓ SELECT", key="select_manual"):
                st.session_state.step2_choice = "manual"
                st.session_state.endpoint = "/jobs/single-doc"
                st.session_state.current_step = 'step3'
                st.rerun()
    
    # Add other Step 2 variations for multiple, merge, split...

def render_step_3_template():
    """Render Step 3 - Template configuration with parameters"""
    mapper = get_mapper()
    parser = get_parser()
    
    endpoint = st.session_state.endpoint
    endpoint_name = mapper.endpoint_to_usecase(endpoint)
    
    # Show recommendation
    st.markdown(f"""
    <div class="recommendation-box">
        <h2>🎯 Recommended Endpoint</h2>
        <div class="endpoint-display">{endpoint}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not endpoint_name:
        st.error("Endpoint mapping not found")
        return
    
    # Get UI flow
    ui_flow = parser.generate_ui_flow(endpoint_name)
    
    if ui_flow.get('has_template_logic'):
        st.header("Step 3: How will recipient addresses be provided?")
        
        # Template options
        template_q = ui_flow['questions'][0]
        
        # Initialize selection
        if 'template_selection' not in st.session_state:
            st.session_state.template_selection = None
        
        # Show options as nice cards
        for idx, opt in enumerate(template_q['options']):
            selected = st.session_state.template_selection == idx
            
            with st.container():
                if st.button(
                    opt['label'],
                    key=f"template_opt_{idx}",
                    use_container_width=True
                ):
                    st.session_state.template_selection = idx
                    st.session_state.selected_template_option = opt
                    st.rerun()
        
        # Show parameter inputs based on selection
        if st.session_state.template_selection is not None:
            selected_opt = st.session_state.selected_template_option
            
            st.markdown("---")
            
            # Check if document choice is needed
            if selected_opt.get('requires_document_choice', False):
                st.subheader("How will the document be provided?")
                doc_choice = st.radio(
                    "",
                    ["Document comes from the job template", "Document provided in API call"],
                    key="doc_source_choice"
                )
                
                if doc_choice == "Document comes from the job template":
                    params_to_show = ['recipientAddressSource']
                else:
                    params_to_show = selected_opt['from_api']
            else:
                params_to_show = selected_opt['from_api']
            
            # Show required parameters
            if params_to_show:
                st.subheader("Required Information")
                
                for param in params_to_show:
                    if param == 'documentSourceIdentifier':
                        st.text_input(
                            "📄 Document ID or URL",
                            key="param_doc",
                            placeholder="e.g., doc_12345 or https://example.com/document.pdf"
                        )
                    elif param == 'recipientAddressSource':
                        show_recipient_inputs()
            
            # Additional required fields
            st.markdown("---")
            st.subheader("Job Configuration")
            
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("📋 Job Template ID", key="param_template_id")
            with col2:
                st.selectbox(
                    "💳 Payment Method",
                    ["CREDIT_CARD", "INVOICE", "ACH", "USER_CREDIT"],
                    key="param_payment"
                )
            
            st.text_input("🏷️ Tags (optional, comma-separated)", key="param_tags")
            
            # Generate button
            if st.button("🚀 Generate API Call", type="primary", use_container_width=True):
                generate_api_call()

def show_recipient_inputs():
    """Show recipient address inputs with add/remove functionality"""
    st.markdown('<div class="address-section">', unsafe_allow_html=True)
    st.write("**📮 Recipient Addresses**")
    
    # Initialize
    if 'recipients' not in st.session_state:
        st.session_state.recipients = []
    
    # Show existing recipients
    for idx, recipient in enumerate(st.session_state.recipients):
        with st.container():
            col1, col2, col3 = st.columns([2, 6, 1])
            
            with col1:
                recipient['type'] = st.selectbox(
                    "Type",
                    ["Address List ID", "Address ID", "New Address"],
                    key=f"rtype_{idx}",
                    index=["Address List ID", "Address ID", "New Address"].index(recipient.get('type', 'Address List ID'))
                )
            
            with col2:
                if recipient['type'] == "Address List ID":
                    recipient['value'] = st.text_input(
                        "List ID",
                        key=f"rval_{idx}",
                        value=recipient.get('value', '')
                    )
                elif recipient['type'] == "Address ID":
                    recipient['value'] = st.text_input(
                        "Address ID", 
                        key=f"rval_{idx}",
                        value=recipient.get('value', '')
                    )
                else:
                    # New address form
                    if st.button(f"📝 Edit Details", key=f"edit_{idx}"):
                        st.session_state[f'expand_{idx}'] = not st.session_state.get(f'expand_{idx}', False)
                    
                    if st.session_state.get(f'expand_{idx}', False):
                        show_address_form(idx, recipient)
            
            with col3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.recipients.pop(idx)
                    st.rerun()
    
    # Add button
    if st.button("➕ Add Recipient", use_container_width=True):
        st.session_state.recipients.append({
            'type': 'Address List ID',
            'value': ''
        })
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_address_form(idx, recipient):
    """Show address form fields"""
    if 'address_data' not in recipient:
        recipient['address_data'] = {}
    
    addr = recipient['address_data']
    
    col1, col2 = st.columns(2)
    with col1:
        addr['firstName'] = st.text_input("First Name", key=f"fname_{idx}", value=addr.get('firstName', ''))
        addr['address1'] = st.text_input("Address Line 1", key=f"addr1_{idx}", value=addr.get('address1', ''))
        addr['city'] = st.text_input("City", key=f"city_{idx}", value=addr.get('city', ''))
    with col2:
        addr['lastName'] = st.text_input("Last Name", key=f"lname_{idx}", value=addr.get('lastName', ''))
        addr['state'] = st.text_input("State", key=f"state_{idx}", value=addr.get('state', ''))
        addr['zip'] = st.text_input("ZIP", key=f"zip_{idx}", value=addr.get('zip', ''))

def generate_api_call():
    """Generate and display the API call"""
    body = {}
    
    # Document
    if st.session_state.get('param_doc'):
        body['documentSourceIdentifier'] = st.session_state.param_doc
    
    # Recipients
    if st.session_state.get('recipients'):
        recipients = []
        for r in st.session_state.recipients:
            if r['type'] == 'Address List ID' and r.get('value'):
                recipients.append({'addressListId': r['value']})
            elif r['type'] == 'Address ID' and r.get('value'):
                recipients.append({'addressId': r['value']})
            elif r['type'] == 'New Address' and r.get('address_data'):
                recipients.append({'recipientAddress': r['address_data']})
        
        if recipients:
            body['recipientAddressSources'] = recipients
    
    # Other params
    if st.session_state.get('param_template_id'):
        body['jobTemplate'] = st.session_state.param_template_id
    
    if st.session_state.get('param_payment'):
        body['paymentDetails'] = {'type': st.session_state.param_payment}
    
    if st.session_state.get('param_tags'):
        body['tags'] = [t.strip() for t in st.session_state.param_tags.split(',')]
    
    # Display
    st.markdown("### 📋 Generated API Call")
    
    endpoint = st.session_state.endpoint
    
    st.code(f"""
POST {endpoint}

{json.dumps(body, indent=2)}
""", language="json")
    
    st.code(f"""
curl -X POST https://api.c2m.com/v2{endpoint} \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -d '{json.dumps(body)}'
""", language="bash")

def main():
    st.title("🎯 Click2Endpoint - C2M API v2")
    
    # Initialize
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'step1'
    
    # Render current step
    if st.session_state.current_step == 'step1':
        render_step_1()
    elif st.session_state.current_step == 'step2':
        render_step_2()
    elif st.session_state.current_step == 'step3':
        render_step_3_template()
    
    # Back button
    if st.session_state.current_step != 'step1':
        st.markdown("---")
        if st.button("⬅️ Back to previous step"):
            if st.session_state.current_step == 'step2':
                st.session_state.current_step = 'step1'
            elif st.session_state.current_step == 'step3':
                st.session_state.current_step = 'step2'
            st.rerun()

if __name__ == "__main__":
    main()