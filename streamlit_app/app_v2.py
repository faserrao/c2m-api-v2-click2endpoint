"""
Click2Endpoint v2 - C2M API v2 Endpoint Finder
Based on EBNF Data Dictionary and OpenAPI Specification
"""

import streamlit as st
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import jsonlines
import streamlit.components.v1 as components
from postman_api import PostmanAPI

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
    
    /* Question sections */
    .question-section {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border: 1px solid #e5e7eb;
    }
    
    /* Job options grid */
    .job-options-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-top: 1rem;
    }
    
    .job-option-card {
        background: #f9fafb;
        border-radius: 10px;
        padding: 1.5rem;
        border: 2px solid #e5e7eb;
        transition: all 0.2s;
    }
    
    .job-option-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
    }
    
    .job-option-title {
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.75rem;
        font-size: 1.1rem;
    }
    
    /* Selected state for options */
    .option-selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Choice cards */
    .choice-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        border: 3px solid #e5e7eb;
        transition: all 0.3s ease;
        cursor: pointer;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .choice-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        border-color: #667eea;
    }
    
    /* Recommendation box */
    .recommendation-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border: 2px solid #2196f3;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 25px rgba(33, 150, 243, 0.2);
    }
    
    .endpoint-path {
        font-family: 'Courier New', monospace;
        background: #1e293b;
        color: #60a5fa;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        font-size: 1.1rem;
        margin: 1rem 0;
    }
    
    /* Info box */
    .info-box {
        background: #f0f9ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)


class Click2EndpointV2:
    def __init__(self):
        # Initialize session state
        if "initial_answers" not in st.session_state:
            st.session_state.initial_answers = {}
        if "endpoint_answers" not in st.session_state:
            st.session_state.endpoint_answers = {}
        if "selected_endpoint" not in st.session_state:
            st.session_state.selected_endpoint = None
        if "job_options" not in st.session_state:
            st.session_state.job_options = {}
        if "doc_base_url" not in st.session_state:
            st.session_state.doc_base_url = "http://localhost:8080"
            
        # Load configuration files
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        
        self.config = self._load_config()
        self.qa_tree = self._load_qa_tree()
        self.endpoints = self._load_endpoints()
        
    def _load_config(self):
        with open(self.base_dir / "config.yaml", "r") as f:
            return yaml.safe_load(f)
    
    def _load_qa_tree(self):
        with open(self.data_dir / "qa_tree.yaml", "r") as f:
            return yaml.safe_load(f)
    
    def _load_endpoints(self):
        with open(self.data_dir / "endpoints.json", "r") as f:
            data = json.load(f)
            return {ep["id"]: ep for ep in data["endpoints"]}
    
    def render_header(self):
        """Render the app header"""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h1 style='text-align: center;'>🎯 Click2Endpoint</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #6b7280; font-size: 1.2rem;'>Find the perfect C2M API endpoint for your mail scenario</p>", unsafe_allow_html=True)
        
        # Controls bar
        with st.container():
            col1, col2, col3 = st.columns([2, 3, 2])
            with col3:
                if st.button("🔄 Start Over", type="secondary", use_container_width=True):
                    for key in ["initial_answers", "endpoint_answers", "selected_endpoint", "job_options"]:
                        if key in st.session_state:
                            st.session_state[key] = {} if key != "selected_endpoint" else None
                    st.rerun()
    
    def render_initial_questions(self):
        """Render the 3 initial questions to determine endpoint"""
        st.markdown("### 📝 Answer these questions to find your endpoint")
        
        questions_complete = True
        
        for question_config in self.qa_tree["initial_questions"]:
            # Check if this question should be shown based on conditions
            if "conditions" in question_config:
                conditions = question_config["conditions"]
                should_show = all(
                    st.session_state.initial_answers.get(field) in values
                    for field, values in conditions.items()
                )
                if not should_show:
                    continue
            
            with st.container():
                st.markdown('<div class="question-section">', unsafe_allow_html=True)
                st.markdown(f"**{question_config['question']}**")
                
                # Render options
                current_value = st.session_state.initial_answers.get(question_config['field'])
                
                # Create columns for options
                cols = st.columns(len(question_config['options']))
                
                for idx, (col, option) in enumerate(zip(cols, question_config['options'])):
                    with col:
                        # Check if this option has conditions
                        if "conditions" in option:
                            conditions = option["conditions"]
                            should_show_option = all(
                                st.session_state.initial_answers.get(field) in values
                                for field, values in conditions.items()
                            )
                            if not should_show_option:
                                continue
                        
                        is_selected = current_value == option['value']
                        
                        # Card display
                        card_style = "border-color: #667eea; background: #f3f4ff;" if is_selected else ""
                        st.markdown(f"""
                        <div class="choice-card" style="{card_style}">
                            <h4>{option['label']}</h4>
                            <p style="color: #6b7280; margin-top: 0.5rem;">{option.get('description', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(
                            "✓ Selected" if is_selected else "Select",
                            key=f"{question_config['field']}_{option['value']}",
                            use_container_width=True,
                            type="primary" if is_selected else "secondary"
                        ):
                            st.session_state.initial_answers[question_config['field']] = option['value']
                            st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Check if question is answered
                if question_config.get('required', True) and question_config['field'] not in st.session_state.initial_answers:
                    questions_complete = False
                    break  # Don't show next questions until this one is answered
        
        return questions_complete
    
    def determine_endpoint(self) -> Optional[str]:
        """Determine which endpoint to use based on initial answers"""
        answers = st.session_state.initial_answers
        
        # Special case for PDF split with address capture
        if answers.get('docType') == 'split' and answers.get('addressSource') == 'addressCapture':
            return 'splitPdfWithAddressCapture'
        elif answers.get('docType') == 'split':
            return 'splitPdf'
        
        # Special case for multi PDFs with address capture
        if answers.get('docType') == 'multi' and answers.get('addressSource') == 'addressCapture':
            return 'multiPdfAddressCapture'
        
        # Look through endpoint configs for matching conditions
        for endpoint_id, config in self.qa_tree['endpoint_configs'].items():
            conditions = config.get('conditions', {})
            
            # Check if all conditions match
            if all(answers.get(field) == value for field, value in conditions.items()):
                return endpoint_id
        
        return None
    
    def render_job_options(self, job_options_config: Dict[str, Any]):
        """Render job options selection UI"""
        st.markdown("### ⚙️ Configure Job Options")
        st.markdown('<div class="info-box">💡 These options control how your documents will be printed and mailed</div>', unsafe_allow_html=True)
        
        # Store selected values
        if 'job_options' not in st.session_state:
            st.session_state.job_options = {}
        
        for subsection in job_options_config['subsections']:
            field = subsection['field']
            label = subsection['label']
            required = subsection.get('required', True)
            options = subsection['options']
            
            st.markdown(f"**{label}**{' *' if required else ''}")
            
            # Create a row of buttons for each option
            cols = st.columns(len(options))
            current_value = st.session_state.job_options.get(field)
            
            for col, option in zip(cols, options):
                with col:
                    is_selected = current_value == option['value']
                    if st.button(
                        option['label'],
                        key=f"job_{field}_{option['value']}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state.job_options[field] = option['value']
                        st.rerun()
            
            if required and field not in st.session_state.job_options:
                st.warning(f"Please select a {label.lower()}")
            
            st.markdown("---")
    
    def render_endpoint_questions(self, endpoint_id: str):
        """Render endpoint-specific questions"""
        endpoint_config = self.qa_tree['endpoint_configs'].get(endpoint_id)
        if not endpoint_config:
            return
        
        st.markdown(f"### 🎯 Configure {self.endpoints[endpoint_id]['description']}")
        
        for question_config in endpoint_config.get('questions', []):
            with st.container():
                st.markdown('<div class="question-section">', unsafe_allow_html=True)
                st.markdown(f"**{question_config['question']}**")
                
                if 'info' in question_config:
                    st.info(question_config['info'])
                
                # Handle job options specially
                if question_config['field'] == 'jobOptions' and 'subsections' in question_config:
                    self.render_job_options(question_config)
                else:
                    # Regular options
                    if question_config.get('multiselect', False):
                        # Multi-select checkboxes
                        selected_values = st.session_state.endpoint_answers.get(question_config['field'], [])
                        for option in question_config['options']:
                            is_checked = option['value'] in selected_values
                            if st.checkbox(
                                f"{option['label']} - {option['description']}",
                                value=is_checked,
                                key=f"ms_{question_config['field']}_{option['value']}"
                            ):
                                if option['value'] not in selected_values:
                                    selected_values.append(option['value'])
                            else:
                                if option['value'] in selected_values:
                                    selected_values.remove(option['value'])
                        st.session_state.endpoint_answers[question_config['field']] = selected_values
                    else:
                        # Single select
                        current_value = st.session_state.endpoint_answers.get(question_config['field'])
                        cols = st.columns(len(question_config['options']))
                        
                        for col, option in zip(cols, question_config['options']):
                            with col:
                                is_selected = current_value == option['value']
                                if st.button(
                                    option['label'],
                                    key=f"eq_{question_config['field']}_{option['value']}",
                                    use_container_width=True,
                                    type="primary" if is_selected else "secondary"
                                ):
                                    st.session_state.endpoint_answers[question_config['field']] = option['value']
                                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    def render_recommendation(self, endpoint_id: str):
        """Render the endpoint recommendation"""
        endpoint = self.endpoints[endpoint_id]
        
        st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
        st.markdown("## 🎯 Recommended Endpoint")
        st.markdown(f"<div class='endpoint-path'>{endpoint['method']} {endpoint['path']}</div>", unsafe_allow_html=True)
        st.markdown(f"**Description:** {endpoint['description']}")
        st.markdown(f"**Use Case #{endpoint['useCase']}**")
        
        # Show use cases
        st.markdown("**Perfect for:**")
        for use_case in endpoint.get('useCases', []):
            st.markdown(f"- {use_case}")
        
        # Show configuration summary
        st.markdown("### 📋 Your Configuration")
        
        # Initial answers
        st.markdown("**Basic Settings:**")
        for field, value in st.session_state.initial_answers.items():
            field_name = {
                'docType': 'Document Type',
                'useTemplate': 'Use Template',
                'addressSource': 'Address Source'
            }.get(field, field)
            st.markdown(f"- {field_name}: `{value}`")
        
        # Job options (if applicable)
        if st.session_state.job_options:
            st.markdown("**Job Options:**")
            for field, value in st.session_state.job_options.items():
                st.markdown(f"- {field}: `{value}`")
        
        # Endpoint-specific answers
        if st.session_state.endpoint_answers:
            st.markdown("**Additional Settings:**")
            for field, value in st.session_state.endpoint_answers.items():
                if isinstance(value, list):
                    st.markdown(f"- {field}: {', '.join(value)}")
                else:
                    st.markdown(f"- {field}: `{value}`")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # View documentation
            doc_url = f"{st.session_state.doc_base_url}/{endpoint.get('docPath', '')}"
            st.markdown(f"[📖 View API Docs]({doc_url})")
        
        with col2:
            # Download SDK code
            languages = ["Python", "JavaScript"]
            selected_lang = st.selectbox("Select SDK", languages, key="sdk_lang")
            
            if selected_lang == "Python":
                code = self.generate_python_sdk(endpoint)
                filename = f"c2m_{endpoint['id'].lower()}.py"
            else:
                code = self.generate_javascript_sdk(endpoint)
                filename = f"c2m_{endpoint['id'].lower()}.js"
            
            st.download_button(
                "📥 Download SDK Code",
                data=code,
                file_name=filename,
                mime="text/plain",
                type="primary"
            )
        
        with col3:
            # Copy curl example
            if st.button("📋 Copy curl Example"):
                curl_example = self.generate_curl_example(endpoint)
                st.code(curl_example, language="bash")
    
    def generate_python_sdk(self, endpoint: Dict[str, Any]) -> str:
        """Generate Python SDK code for the endpoint"""
        # This would be similar to the existing implementation
        # but adapted for the new endpoint structure
        return f"""#!/usr/bin/env python3
\"\"\"
C2M API - {endpoint['description']}
Endpoint: {endpoint['method']} {endpoint['path']}
Use Case: #{endpoint['useCase']}
\"\"\"

import requests
import json

# Configuration
API_BASE_URL = "https://api.c2m.com"
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# TODO: Implement based on endpoint requirements
# Required params: {', '.join(endpoint.get('requiredParams', []))}
# Optional params: {', '.join(endpoint.get('optionalParams', []))}
"""
    
    def generate_javascript_sdk(self, endpoint: Dict[str, Any]) -> str:
        """Generate JavaScript SDK code for the endpoint"""
        return f"""/**
 * C2M API - {endpoint['description']}
 * Endpoint: {endpoint['method']} {endpoint['path']}
 * Use Case: #{endpoint['useCase']}
 */

const axios = require('axios');

// Configuration
const API_BASE_URL = 'https://api.c2m.com';
const CLIENT_ID = 'YOUR_CLIENT_ID';
const CLIENT_SECRET = 'YOUR_CLIENT_SECRET';

// TODO: Implement based on endpoint requirements
// Required params: {', '.join(endpoint.get('requiredParams', []))}
// Optional params: {', '.join(endpoint.get('optionalParams', []))}
"""
    
    def generate_curl_example(self, endpoint: Dict[str, Any]) -> str:
        """Generate curl example for the endpoint"""
        return f"""# Get authentication token
curl -X POST https://api.c2m.com/auth/tokens/long \\
  -H "Content-Type: application/json" \\
  -d '{{"grant_type": "client_credentials", "client_id": "YOUR_CLIENT_ID", "client_secret": "YOUR_CLIENT_SECRET"}}'

# Call endpoint
curl -X {endpoint['method']} https://api.c2m.com{endpoint['path']} \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    # Add required parameters here
    # {', '.join(endpoint.get('requiredParams', []))}
  }}'"""
    
    def run(self):
        """Main application flow"""
        self.render_header()
        
        # Step 1: Initial questions
        if not st.session_state.selected_endpoint:
            questions_complete = self.render_initial_questions()
            
            if questions_complete:
                # Determine endpoint based on answers
                endpoint_id = self.determine_endpoint()
                if endpoint_id:
                    st.session_state.selected_endpoint = endpoint_id
                    st.rerun()
                else:
                    st.error("Could not determine endpoint based on your answers. Please check your selections.")
        
        # Step 2: Endpoint-specific questions
        else:
            endpoint_id = st.session_state.selected_endpoint
            
            # Show selected endpoint info
            endpoint = self.endpoints[endpoint_id]
            st.success(f"Selected endpoint: **{endpoint['path']}**")
            
            # Render endpoint-specific questions
            self.render_endpoint_questions(endpoint_id)
            
            # Show recommendation
            self.render_recommendation(endpoint_id)
            
            # Log session
            self.log_session(endpoint_id)


    def log_session(self, endpoint_id: str):
        """Log the session for analytics"""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "initial_answers": st.session_state.initial_answers,
            "endpoint_answers": st.session_state.endpoint_answers,
            "job_options": st.session_state.job_options,
            "selected_endpoint": endpoint_id,
            "endpoint_path": self.endpoints[endpoint_id]["path"]
        }
        
        # Create logs directory if it doesn't exist
        log_dir = self.base_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Append to JSONL log
        with jsonlines.open(log_dir / "sessions_v2.jsonl", mode="a") as writer:
            writer.write(log_entry)


def main():
    app = Click2EndpointV2()
    app.run()


if __name__ == "__main__":
    main()