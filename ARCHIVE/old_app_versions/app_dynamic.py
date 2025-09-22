"""
Click2Endpoint - Dynamic EBNF-based flow
Focuses on single document with template flow
"""

import streamlit as st
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import jsonlines

# Page configuration
st.set_page_config(
    page_title="Click2Endpoint - Dynamic Flow",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Use the same beautiful CSS from the original
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
    
    /* Main title styling */
    .main-title {
        font-size: 5rem !important;
        font-weight: 900 !important;
        margin-bottom: 0.5rem !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    
    /* Question section styling */
    .question-section {
        background: #f8f9fa;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Choice cards */
    .choice-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .choice-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        border-color: #667eea;
    }
    
    /* Form styling */
    .form-field {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 2px solid #e5e7eb;
    }
    
    .form-field:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
</style>
""", unsafe_allow_html=True)

class DynamicNavigator:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.qa_tree = self._load_qa_tree()
        
        # Initialize session state
        if "answers" not in st.session_state:
            st.session_state.answers = {}
        if "current_tier" not in st.session_state:
            st.session_state.current_tier = 1
        if "form_data" not in st.session_state:
            st.session_state.form_data = {}
    
    def _load_qa_tree(self):
        """Load the dynamic Q&A tree"""
        qa_path = self.data_dir / "qa_tree_dynamic.yaml"
        with open(qa_path, "r") as f:
            return yaml.safe_load(f)
    
    def render_header(self):
        """Render the app header"""
        st.markdown('<div style="text-align: center; padding-top: 1rem;">', unsafe_allow_html=True)
        st.markdown('<h1 class="main-title">Click2Endpoint</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 1.5rem; color: #ff0000;">🔴 DYNAMIC VERSION - Payment Required!</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col3:
            if st.button("🔄 Reset", type="secondary"):
                st.session_state.answers = {}
                st.session_state.form_data = {}
                st.session_state.current_tier = 1
                st.rerun()
    
    def render_visual_choice(self, field, options, current_value=None):
        """Render visual choice buttons"""
        icons = {
            "single": "📄",
            "documentOnly": "📄",
            "addressListOnly": "📋",
            "neither": "❓",
            "url": "🔗",
            "base64": "💾",
            "s3": "☁️",
            "inline": "📝",
            "csv": "📊",
            "mailingListId": "📑",
            "creditCard": "💳",
            "ach": "🏦",
            "invoice": "📃",
            "prepaid": "💰"
        }
        
        # First, render all cards in a row
        card_cols = st.columns(len(options))
        
        for idx, (col, opt) in enumerate(zip(card_cols, options)):
            with col:
                # Get icon or use default
                icon = icons.get(opt["value"], "📌")
                
                # Check if this is selected
                is_selected = current_value == opt["value"]
                
                # Create card with fixed height
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
        
        # Add spacing between cards and buttons
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # Then render all buttons in a separate row at the same level
        button_cols = st.columns(len(options))
        selected = None
        
        for idx, (col, opt) in enumerate(zip(button_cols, options)):
            with col:
                # Check if this is selected
                is_selected = current_value == opt["value"]
                
                # All buttons at same level
                if st.button(
                    "✓ Selected" if is_selected else "Select",
                    key=f"{field}_{opt['value']}",  # EXACT same key format as working app
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    selected = opt["value"]
        
        return selected
    
    def render_form_fields(self, tier_config):
        """Render form fields for data collection"""
        st.markdown(f"### {tier_config['question']}")
        
        form_data = {}
        for field in tier_config['fields']:
            value = st.text_input(
                field['label'],
                value=st.session_state.form_data.get(field['name'], ""),
                help=f"Pattern: {field.get('pattern', 'Any format')}" if 'pattern' in field else None,
                key=f"form_{field['name']}"
            )
            form_data[field['name']] = value
        
        # Save button
        if st.button("Save and Continue", type="primary"):
            # Validate patterns if specified
            all_valid = True
            for field in tier_config['fields']:
                if 'pattern' in field:
                    import re
                    if not re.match(field['pattern'], form_data[field['name']]):
                        st.error(f"Invalid format for {field['label']}")
                        all_valid = False
            
            if all_valid:
                st.session_state.answers[tier_config['field']] = form_data
                st.session_state.form_data.update(form_data)
                st.rerun()
    
    def render_multitext_field(self, tier_config):
        """Render multi-text field for tags"""
        st.markdown(f"### {tier_config['question']}")
        st.caption(tier_config.get('description', ''))
        
        # Text area for tags
        tags = st.text_area(
            "Enter tags (one per line)",
            value="\n".join(st.session_state.answers.get('tags', [])),
            height=100
        )
        
        if st.button("Save Tags", type="primary"):
            tag_list = [tag.strip() for tag in tags.split('\n') if tag.strip()]
            st.session_state.answers['tags'] = tag_list
            st.rerun()
    
    def render_questionnaire(self):
        """Render the dynamic questionnaire"""
        st.markdown("<h2 style='text-align: center; font-size: 2.5rem; margin-bottom: 2rem;'>🎯 Configure Your Request</h2>", unsafe_allow_html=True)
        
        # Show current path
        if st.session_state.answers:
            path_items = []
            if 'docType' in st.session_state.answers:
                path_items.append(f"📄 {st.session_state.answers['docType']}")
            if 'templateUsage' in st.session_state.answers:
                path_items.append("✅ Template" if st.session_state.answers['templateUsage'] else "❌ No Template")
            if 'templateContents' in st.session_state.answers:
                path_items.append(f"📦 {st.session_state.answers['templateContents']}")
            
            if path_items:
                st.markdown(f"**Current path:** {' → '.join(path_items)}")
        
        # Debug: show current answers
        with st.expander("Debug: Current Answers"):
            st.json(st.session_state.answers)
        
        # Find the next question to ask
        for tier_config in self.qa_tree["decision_tree"]:
            # Check if this question has already been answered
            if tier_config["field"] in st.session_state.answers:
                continue
            
            # Check conditions
            if "conditions" in tier_config:
                should_show = True
                for field, values in tier_config["conditions"].items():
                    answer_value = st.session_state.answers.get(field)
                    st.write(f"Debug: Checking {field}={answer_value} in {values}")
                    if answer_value not in values:
                        should_show = False
                        break
                if not should_show:
                    continue
            
            # Check if optional and not enabled
            if tier_config.get("optional", False):
                if not st.checkbox(f"Configure {tier_config['question'].lower()}?", key=f"optional_{tier_config['field']}"):
                    continue
            
            # Render the question
            with st.container():
                st.markdown('<div class="question-section">', unsafe_allow_html=True)
                
                if tier_config.get("type") == "form":
                    self.render_form_fields(tier_config)
                elif tier_config.get("type") == "multitext":
                    self.render_multitext_field(tier_config)
                else:
                    # Regular choice question
                    st.markdown(f"### Step {tier_config['tier']}: {tier_config['question']}")
                    selected = self.render_visual_choice(
                        tier_config["field"],
                        tier_config["options"],
                        st.session_state.answers.get(tier_config["field"])
                    )
                    
                    if selected:
                        st.session_state.answers[tier_config["field"]] = selected
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            break  # Only show one question at a time
        
        # Show completion message when all required questions are answered
        self.check_completion()
    
    def check_completion(self):
        """Check if we have enough info to build the request"""
        # For single doc with template, check what we need
        if (st.session_state.answers.get('docType') == 'single' and 
            st.session_state.answers.get('templateUsage') == True):
            
            template_contents = st.session_state.answers.get('templateContents')
            if not template_contents:
                return
            
            # Check if we have all required data based on template contents
            ready = True
            if template_contents in ['addressListOnly', 'neither']:
                if 'documentSource' not in st.session_state.answers:
                    ready = False
            
            if template_contents in ['documentOnly', 'neither']:
                if 'recipientSource' not in st.session_state.answers:
                    ready = False
            
            # Payment is now REQUIRED
            if 'paymentMethod' not in st.session_state.answers:
                ready = False
            else:
                # Check if payment details are complete
                payment_method = st.session_state.answers.get('paymentMethod')
                if payment_method == 'creditCard' and 'creditCardInfo' not in st.session_state.answers:
                    ready = False
                elif payment_method == 'ach' and 'achInfo' not in st.session_state.answers:
                    ready = False
            
            if ready:
                st.markdown("---")
                st.success("✅ All required information collected!")
                
                # Show the data structure that will be sent
                st.markdown("### Generated Request Structure")
                request_data = self.build_request_structure()
                st.json(request_data)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🚀 Generate SDK Code", type="primary", use_container_width=True):
                        self.generate_code()
    
    def build_request_structure(self):
        """Build the request structure based on answers"""
        answers = st.session_state.answers
        request = {
            "jobTemplate": "your-template-id"
        }
        
        # Add document if needed
        template_contents = answers.get('templateContents')
        if template_contents in ['addressListOnly', 'neither']:
            doc_source = answers.get('documentSource', 'url')
            if doc_source == 'url':
                request["documentSourceIdentifier"] = {"url": "https://example.com/document.pdf"}
            elif doc_source == 'base64':
                request["documentSourceIdentifier"] = {"base64": "base64_encoded_content"}
            elif doc_source == 's3':
                request["documentSourceIdentifier"] = {"s3": "s3://bucket/path/document.pdf"}
        
        # Add recipients if needed
        if template_contents in ['documentOnly', 'neither']:
            recip_source = answers.get('recipientSource', 'exactlyOneNewAddress')
            if recip_source == 'exactlyOneNewAddress':
                request["recipientAddressSource"] = {
                    "exactlyOneNewAddress": {
                        "firstName": "John",
                        "lastName": "Doe",
                        "address1": "123 Main St",
                        "city": "Anytown",
                        "state": "CA",
                        "zip": "12345",
                        "country": "USA"
                    }
                }
            elif recip_source == 'exactlyOneListId':
                request["recipientAddressSource"] = {"exactlyOneListId": "list-123"}
            elif recip_source == 'exactlyOneId':
                request["recipientAddressSource"] = {"exactlyOneId": "saved-address-456"}
        
        # Add payment (REQUIRED)
        payment_method = answers.get('paymentMethod')
        if payment_method:
            if payment_method == 'creditCard':
                card_info = answers.get('creditCardInfo', {})
                request["paymentDetails"] = {
                    "method": "creditCard",
                    "card": {
                        "number": card_info.get('cardNumber', '****'),
                        "expiry": card_info.get('expiry', '**/**'),
                        "cvv": "***"
                    }
                }
            elif payment_method == 'ach':
                ach_info = answers.get('achInfo', {})
                request["paymentDetails"] = {
                    "method": "ach",
                    "account": {
                        "routing": ach_info.get('routingNumber', '*********'),
                        "number": "******" + ach_info.get('accountNumber', '****')[-4:]
                    }
                }
            elif payment_method == 'invoice':
                request["paymentDetails"] = {"method": "invoice", "poNumber": "PO-12345"}
            elif payment_method == 'prepaid':
                request["paymentDetails"] = {"method": "prepaid", "accountId": "prepaid-account-id"}
            elif payment_method == 'applePay':
                request["paymentDetails"] = {"method": "applePay", "applePaymentDetails": "TBD"}
            elif payment_method == 'googlePay':
                request["paymentDetails"] = {"method": "googlePay", "googlePaymentDetails": "TBD"}
        
        # Add tags if provided
        if answers.get('tags'):
            request["tags"] = answers['tags']
        
        return request
    
    def generate_code(self):
        """Generate SDK code"""
        st.markdown("### Generated Python Code")
        
        request_structure = self.build_request_structure()
        
        code = f'''#!/usr/bin/env python3
"""
C2M API - Single Document with Template
Generated based on your configuration
"""

import requests
import json

# Configuration
API_URL = "https://api.c2m.com/jobs/single-doc-job-template"
API_KEY = "your-api-key"

# Your request payload
payload = {json.dumps(request_structure, indent=4)}

# Make the request
headers = {{
    "Authorization": f"Bearer {{API_KEY}}",
    "Content-Type": "application/json"
}}

response = requests.post(API_URL, json=payload, headers=headers)

if response.status_code == 200:
    print("✅ Job submitted successfully!")
    print(response.json())
else:
    print(f"❌ Error: {{response.status_code}}")
    print(response.text)
'''
        
        st.code(code, language='python')
        
        # Download button
        st.download_button(
            label="📥 Download Code",
            data=code,
            file_name="c2m_single_doc_template.py",
            mime="text/x-python"
        )
    
    def run(self):
        """Main app runner"""
        self.render_header()
        self.render_questionnaire()
        
        # Show current state in sidebar
        with st.sidebar:
            st.markdown("### 📊 Current Configuration")
            if st.session_state.answers:
                for field, value in st.session_state.answers.items():
                    if isinstance(value, dict):
                        st.write(f"**{field}:**")
                        for k, v in value.items():
                            st.write(f"  - {k}: {v}")
                    else:
                        st.write(f"**{field}:** {value}")
            else:
                st.write("No selections yet")

def main():
    navigator = DynamicNavigator()
    navigator.run()

if __name__ == "__main__":
    main()