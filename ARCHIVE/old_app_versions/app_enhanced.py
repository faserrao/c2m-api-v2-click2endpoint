"""
Click2Endpoint - C2M API v2 Endpoint Finder
Interactive web interface for finding the right C2M API endpoint
Enhanced with EBNF-based structure while keeping the beautiful UI
"""

import streamlit as st
import json
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
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

# Keep ALL the original beautiful CSS styling
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
    
    .stRadio > div > label:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
    }
    
    .stRadio > div > label > div {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .stRadio > div > label > div > p {
        margin: 0 !important;
        font-size: 1rem !important;
        line-height: 1.4 !important;
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
    
    .endpoint-path {
        font-family: 'Monaco', 'Consolas', monospace;
        font-size: 1.6rem;
        font-weight: bold;
        color: #1565c0;
        background: rgba(255, 255, 255, 0.8);
        padding: 1rem 2rem;
        border-radius: 10px;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 4.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.02em;
        line-height: 1.1;
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
    
    /* Title container for compass and subtitle on same line */
    .title-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Compass emoji styling */
    .compass-emoji {
        font-size: 4rem;
        line-height: 1;
    }
    
    /* Subtitle styling - darker color */
    .subtitle {
        font-size: 2.8rem !important;
        color: #0f172a;
        font-weight: 400;
        margin: 0 !important;
        line-height: 1.2;
    }
    
    /* Question headers */
    h3 {
        color: #1f2937;
        font-size: 1.8rem !important;
        text-align: center;
        margin: 2rem 0 1rem 0 !important;
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
    
    /* Feature cards */
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 30px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Checkbox styling - minimal to avoid conflicts */
    .stCheckbox > label {
        font-size: 1rem !important;
        color: #4b5563 !important;
    }
    
    /* Code block styling */
    .stCodeBlock {
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f3f4f6 0%, #e5e7eb 100%);
    }
    
    /* Option descriptions */
    .option-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
        color: white;
    }
    
    .option-desc {
        font-size: 0.9rem;
        opacity: 0.9;
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Emoji styling */
    .big-emoji {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    /* Controls bar styling */
    .controls-bar {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 0.5rem 0;
        margin-bottom: 1rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Question container with scroll */
    .question-container {
        max-height: calc(100vh - 400px);
        overflow-y: auto;
        padding-right: 1rem;
    }
    
    .question-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .question-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    
    .question-container::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 3px;
    }
    
    .question-container::-webkit-scrollbar-thumb:hover {
        background: #555;
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
    
    /* Force equal height columns and button alignment */
    div[data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
    
    div[data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
    }
    
    div[data-testid="column"] > div:last-child {
        margin-top: auto !important;
    }
    
    /* Ensure consistent spacing */
    .choice-button-wrapper {
        margin-top: auto;
        padding-top: 1rem;
    }
    
    /* Sleek button style */
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
    
    /* NEW: Job options card styling */
    .job-option-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .job-option-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .job-option-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.75rem;
    }
    
    .job-option-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    /* Job option button styling */
    .job-option-btn {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        background: white;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .job-option-btn:hover {
        border-color: #667eea;
        background: #f3f4ff;
    }
    
    .job-option-btn.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitNavigator:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.config = self._load_config()
        self.endpoints = self._load_endpoints()
        self.qa_tree = self._load_qa_tree()
        
        # Initialize session state
        if "answers" not in st.session_state:
            st.session_state.answers = {}
        if "job_options" not in st.session_state:
            st.session_state.job_options = {}
        if "qa_log" not in st.session_state:
            st.session_state.qa_log = []
        if "recommendation" not in st.session_state:
            st.session_state.recommendation = None
        if "doc_base_url" not in st.session_state:
            # Set default documentation server based on config
            default_server = self.config["documentation"]["default_server"]
            
            # Use new structure if available
            if "servers" in self.config["documentation"]:
                if default_server in self.config["documentation"]["servers"]:
                    st.session_state.doc_base_url = self.config["documentation"]["servers"][default_server]["url"]
                else:
                    # Fallback to first server
                    first_server = list(self.config["documentation"]["servers"].values())[0]
                    st.session_state.doc_base_url = first_server["url"]
            else:
                # Legacy support
                if default_server == "local":
                    st.session_state.doc_base_url = self.config["documentation"]["local_url"]
                else:
                    st.session_state.doc_base_url = self.config["documentation"]["remote_url"]
    
    def _load_config(self):
        config_file = Path(__file__).parent.parent / "config.yaml"
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        
        # Try to load mock server URL from c2m-api-repo if available
        mock_url_file = Path(__file__).parent.parent.parent.parent.parent / "c2m-api-repo" / "postman" / "postman_mock_url.txt"
        if mock_url_file.exists():
            try:
                mock_url = mock_url_file.read_text().strip()
                if mock_url and mock_url.startswith("https://"):
                    config["api"]["mock_server_url"] = mock_url
            except Exception:
                pass  # Fall back to config.yaml value
        
        return config
    
    def _load_endpoints(self):
        # Use EBNF-based endpoints if available, otherwise fallback to original
        ebnf_endpoints_path = self.data_dir / "endpoints_ebnf.json"
        original_endpoints_path = self.data_dir / "endpoints.json"
        
        if ebnf_endpoints_path.exists():
            with open(ebnf_endpoints_path, "r") as f:
                data = json.load(f)
        else:
            with open(original_endpoints_path, "r") as f:
                data = json.load(f)
        return {ep["id"]: ep for ep in data["endpoints"]}
    
    def _load_qa_tree(self):
        # Use EBNF-based qa_tree if available, otherwise fallback to original
        ebnf_qa_path = self.data_dir / "qa_tree_ebnf.yaml"
        original_qa_path = self.data_dir / "qa_tree.yaml"
        
        if ebnf_qa_path.exists():
            with open(ebnf_qa_path, "r") as f:
                return yaml.safe_load(f)
        else:
            with open(original_qa_path, "r") as f:
                return yaml.safe_load(f)
    
    def render_header(self):
        """Render the app header"""
        # Main title and subtitle at the very top
        st.markdown('<div style="text-align: center; padding-top: 1rem;">', unsafe_allow_html=True)
        st.markdown('<h1 class="main-title">Click2Endpoint</h1>', unsafe_allow_html=True)
        st.markdown('<div class="title-container">', unsafe_allow_html=True)
        st.markdown('<span class="compass-emoji">🎯</span>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Find the perfect API endpoint for your mail scenario</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Controls bar with checkbox and reset button
        st.markdown('<div class="controls-bar">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 3, 2])
        with col1:
            # Documentation server selection dropdown
            if self.config["documentation"]["allow_toggle"]:
                # Get documentation servers from config
                doc_servers = {}
                
                # Use new structure if available, otherwise fall back to legacy
                if "servers" in self.config["documentation"]:
                    for server_id, server_config in self.config["documentation"]["servers"].items():
                        doc_servers[server_config["name"]] = server_config["url"]
                else:
                    # Legacy fallback
                    doc_servers = {
                        "Local (localhost:8080)": self.config["documentation"]["local_url"],
                        "GitHub Pages": self.config["documentation"]["remote_url"]
                    }
                
                # Find current selection
                current_server = list(doc_servers.keys())[0]  # Default to first server
                for name, url in doc_servers.items():
                    if st.session_state.doc_base_url == url:
                        current_server = name
                        break
                
                # Documentation server dropdown
                selected_server = st.selectbox(
                    "📚 Documentation Server",
                    options=list(doc_servers.keys()),
                    index=list(doc_servers.keys()).index(current_server),
                    help="Select which documentation server to use for API reference links",
                    key="doc_server_select"
                )
                
                # Update the session state with selected server URL
                st.session_state.doc_base_url = doc_servers[selected_server]
        with col3:
            # Reset button on the right with proper alignment
            st.markdown('<div style="text-align: right;">', unsafe_allow_html=True)
            if st.button("🔄 Reset", type="secondary", use_container_width=True):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    if key not in ['doc_base_url']:  # Keep doc server preference
                        del st.session_state[key]
                # Reinitialize required states
                st.session_state.answers = {}
                st.session_state.job_options = {}
                st.session_state.qa_log = []
                st.session_state.recommendation = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_scenario_flow(self):
        """Render visual flow of selected scenario"""
        icons = {
            "single": "📄",
            "multi": "📚", 
            "merge": "🔗",
            "split": "✂️",
            "pdfSplit": "✂️",
            "true": "✅",
            "false": "❌",
            "yes": "✅",
            "no": "❌",
            "explicit": "📝",
            "template": "📋",
            "addressCapture": "🔍",
            "addressList": "📑",
            "savedAddress": "💾"
        }
        
        # Build flow visualization
        flow_parts = []
        answers = st.session_state.answers
        
        if "docType" in answers:
            icon = icons.get(answers["docType"], "📌")
            flow_parts.append(f"{icon}")
        
        if "useTemplate" in answers:
            icon = icons.get(str(answers["useTemplate"]).lower(), "")
            if icon:
                flow_parts.append(f"{icon}")
        
        if "addressSource" in answers:
            icon = icons.get(answers["addressSource"], "📮")
            flow_parts.append(f"{icon}")
        
        if flow_parts:
            flow_html = " → ".join(flow_parts)
            st.markdown(f"""
            <div style="text-align: center; background: rgba(102, 126, 234, 0.1); 
                        border-radius: 20px; padding: 20px; margin: 20px 0;">
                <div style="font-size: 48px; margin-bottom: 10px;">{flow_html}</div>
                <div style="font-size: 16px; color: #666;">Your Current Scenario</div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_visual_choice(self, field, options, current_value=None):
        """Render visual icon-based choice buttons"""
        # Icon mapping for different options
        icons = {
            "single": "📄",
            "multi": "📚", 
            "merge": "🔗",
            "split": "✂️",
            "pdfSplit": "✂️",
            "true": "✅",
            "false": "❌",
            "yes": "✅",
            "no": "❌",
            "explicit": "📝",
            "template": "📋",
            "addressCapture": "🔍",
            "listId": "📑",
            "addressList": "📑",
            "savedAddress": "💾"
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
                    key=f"{field}_{opt['value']}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    selected = opt["value"]
        
        return selected
    
    def render_job_options(self):
        """Render job options selection for non-template endpoints"""
        st.markdown("### ⚙️ Select Print and Mail Options")
        st.info("💡 These options control how your documents will be printed and mailed. Some options allow multiple selections.")
        
        # Job options structure from EBNF - updated to match actual EBNF values
        job_options = {
            "documentClass": {
                "title": "Document Class",
                "options": ["uspsFirstClass", "uspsMarketing", "uspsNonProfit"],
                "multiselect": False,  # Single select
                "required": True
            },
            "layout": {
                "title": "Layout",
                "options": ["address_on_separate_page", "address_on_first_page"],
                "multiselect": False,  # Single select
                "required": True
            },
            "mailclass": {
                "title": "Mail Class", 
                "options": ["certified", "certified_return_receipt", "registered", "priority", "standard"],
                "multiselect": True,  # Can select multiple mail services
                "required": True
            },
            "paperType": {
                "title": "Paper Type",
                "options": ["standard", "perfed", "letterhead"],
                "multiselect": False,  # Single select
                "required": True
            },
            "printOption": {
                "title": "Print Option",
                "options": ["none", "color", "grayscale"],
                "multiselect": False,  # Single select
                "required": True
            },
            "envelope": {
                "title": "Envelope Type",
                "options": ["flat", "windowedFlat", "letter", "legal", "postcard"],
                "multiselect": False,  # Single select
                "required": True
            }
        }
        
        # Render each job option with the beautiful UI
        for field, config in job_options.items():
            st.markdown(f"""
            <div class="job-option-card">
                <div class="job-option-title">{config['title']}{"" if not config.get('multiselect') else " (select multiple)"}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if config.get('multiselect', False):
                # Multi-select using styled checkboxes
                current_values = st.session_state.job_options.get(field, [])
                if not isinstance(current_values, list):
                    current_values = []
                
                cols = st.columns(len(config['options']))
                for col, option in zip(cols, config['options']):
                    with col:
                        # Use a custom checkbox implementation with buttons
                        is_selected = option in current_values
                        if st.button(
                            f"{'☑' if is_selected else '☐'} {option}",
                            key=f"job_{field}_{option}",
                            use_container_width=True,
                            type="primary" if is_selected else "secondary"
                        ):
                            if is_selected:
                                # Remove from selection
                                current_values.remove(option)
                            else:
                                # Add to selection
                                current_values.append(option)
                            st.session_state.job_options[field] = current_values
                            st.rerun()
            else:
                # Single select using buttons (original behavior)
                cols = st.columns(len(config['options']))
                current_value = st.session_state.job_options.get(field)
                
                for col, option in zip(cols, config['options']):
                    with col:
                        is_selected = current_value == option
                        if st.button(
                            option if not is_selected else f"✓ {option}",
                            key=f"job_{field}_{option}",
                            use_container_width=True,
                            type="primary" if is_selected else "secondary"
                        ):
                            st.session_state.job_options[field] = option
                            st.rerun()
    
    def check_if_template_endpoint(self, answers):
        """Check if current answers lead to a template endpoint"""
        return answers.get("useTemplate", False) or answers.get("templateUsage", False)
    
    def render_questionnaire(self):
        """Render the interactive questionnaire with enhanced logic"""
        st.markdown("<h2 style='text-align: center; font-size: 2.5rem; margin-bottom: 2rem;'>🎯 Build Your Scenario</h2>", unsafe_allow_html=True)
        
        # Container for questions with scrolling
        st.markdown('<div class="question-container">', unsafe_allow_html=True)
        
        # Add auto-scroll JavaScript with better timing and scrolling
        components.html("""
        <script>
        // Auto-scroll to the last unanswered question
        function scrollToLastQuestion() {
            // Find all question sections
            const questions = document.querySelectorAll('.question-section');
            if (questions.length > 0) {
                // Scroll to the last visible question
                const lastQuestion = questions[questions.length - 1];
                if (lastQuestion) {
                    // Get the position of the element
                    const rect = lastQuestion.getBoundingClientRect();
                    const absoluteTop = window.pageYOffset + rect.top;
                    
                    // Scroll to position with offset for better visibility
                    window.scrollTo({
                        top: absoluteTop - 100,
                        behavior: 'smooth'
                    });
                }
            }
        }
        
        // Run after DOM is loaded and Streamlit has rendered
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(scrollToLastQuestion, 500);
            });
        } else {
            setTimeout(scrollToLastQuestion, 500);
        }
        
        // Also run on mutation to catch Streamlit updates
        const observer = new MutationObserver(function(mutations) {
            if (mutations.some(m => m.addedNodes.length > 0)) {
                setTimeout(scrollToLastQuestion, 100);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        </script>
        """, height=0)
        
        # Track which tier we're on
        current_tier = 0
        question_count = 0
        all_questions_answered = True
        
        # First pass: render initial questions
        for tier_config in self.qa_tree["decision_tree"]:
            # Skip job options question for template endpoints
            if tier_config.get("field") == "extraFeatures" and self.check_if_template_endpoint(st.session_state.answers):
                continue
            
            # Check conditions
            if "conditions" in tier_config:
                should_show = all(
                    st.session_state.answers.get(field) in values
                    for field, values in tier_config["conditions"].items()
                )
                if not should_show:
                    continue
            
            # Skip optional questions based on toggle
            if tier_config.get("optional", False):
                if not st.checkbox(
                    f"Configure {tier_config['question'].lower()}?",
                    key=f"optional_{tier_config['field']}"
                ):
                    continue
            
            current_tier += 1
            question_count += 1
            
            # Check if this question is answered
            if tier_config["field"] not in st.session_state.answers:
                all_questions_answered = False
            
            # Create question section with smooth styling and unique ID
            with st.container():
                st.markdown(f'<div class="question-section" id="q{question_count}">', unsafe_allow_html=True)
                st.markdown(f"#### Step {current_tier}: {tier_config['question']}")
                
                # Get current value for this field
                current_value = st.session_state.answers.get(tier_config["field"])
                
                # Use visual buttons for selection
                selected = self.render_visual_choice(
                    tier_config["field"],
                    tier_config["options"],
                    current_value
                )
                
                # Update answers if selection made
                if selected:
                    st.session_state.answers[tier_config["field"]] = selected
                    # Add some space before rerun to show next question will appear
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)  # Close question-section div
        
        # After initial questions, check if we need job options
        if (all_questions_answered and 
            not self.check_if_template_endpoint(st.session_state.answers) and
            len(st.session_state.job_options) == 0):
            
            current_tier += 1
            with st.container():
                st.markdown(f'<div class="question-section" id="q{current_tier}">', unsafe_allow_html=True)
                st.markdown(f"#### Step {current_tier}: Configure Job Options")
                self.render_job_options()
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Check if all job options are selected
            required_options = ["documentClass", "layout", "mailclass", "paperType", "printOption", "envelope"]
            all_options_selected = all(
                opt in st.session_state.job_options and 
                (st.session_state.job_options[opt] if not isinstance(st.session_state.job_options.get(opt), list) 
                 else len(st.session_state.job_options[opt]) > 0)
                for opt in required_options
            )
            if not all_options_selected:
                all_questions_answered = False
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close question container
        
        # Show recommendation button when questions are answered
        if all_questions_answered and len(st.session_state.answers) >= 2:  # At least docType and templateUsage
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🎯 Get My Perfect Endpoint", type="primary", use_container_width=True):
                    self.find_recommendation()
            
            # Show error if no match found
            if st.session_state.get('show_error', False):
                st.error("❌ No matching endpoint found for your criteria.")
                with st.expander("View your selections"):
                    for field, value in st.session_state.answers.items():
                        st.write(f"**{field}**: {value}")
                st.session_state.show_error = False
    
    def find_recommendation(self):
        """Find and display the recommended endpoint"""
        # Update the mapping to handle "useTemplate" field
        answers = st.session_state.answers.copy()
        if "useTemplate" in answers:
            answers["templateUsage"] = answers["useTemplate"]
        
        # Also handle "split" as "pdfSplit"
        if answers.get("docType") == "split":
            answers["docType"] = "pdfSplit"
        
        # Find matching endpoint
        endpoint_id = None
        for rule in self.qa_tree["endpoint_rules"]:
            matches = all(
                answers.get(field) == value
                for field, value in rule["conditions"].items()
            )
            if matches:
                endpoint_id = rule["endpoint"]
                break
        
        if endpoint_id:
            st.session_state.recommendation = self.endpoints[endpoint_id]
            self.log_session(endpoint_id)
            st.rerun()  # Force refresh to show recommendation
        else:
            # Store error state to show after rerun
            st.session_state.show_error = True
            st.session_state.recommendation = None
            st.rerun()
    
    def render_recommendation(self):
        """Display the recommendation with job options if selected"""
        if not st.session_state.recommendation:
            return
        
        endpoint = st.session_state.recommendation
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### ✨ Your Perfect Endpoint Match")
        
        # Main recommendation box with enhanced styling
        st.markdown(f"""
        <div class="recommendation-box" style="text-align: center; max-width: 800px; margin: 0 auto;">
            <span class="big-emoji">🎉</span>
            <div class="endpoint-path">{endpoint['method']} {endpoint['path']}</div>
            <p style="font-size: 1.2rem; color: #1565c0; margin-top: 1rem;">{endpoint['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show job options if selected
        if st.session_state.job_options:
            st.markdown("#### 📋 Your Selected Job Options")
            cols = st.columns(3)
            for idx, (field, value) in enumerate(st.session_state.job_options.items()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="feature-card" style="background: white; border-radius: 10px; padding: 1rem; margin-bottom: 0.5rem; border-left: 3px solid #667eea;">
                        <strong style="color: #374151;">{field}:</strong> <span style="color: #667eea;">{value}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Add spacing before resources section
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Center the Resources column
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.markdown("#### 📚 Resources")
            
            # Documentation link with correct Redocly anchor format
            if endpoint.get("docPath"):
                # For Redocly, we need to ensure the anchor is properly formatted
                # The docPath already contains the # prefix
                base_url = st.session_state.get('doc_base_url', 'http://localhost:8080')
                
                # Construct the full URL with the anchor
                # Some browsers handle anchors better with a slight delay
                doc_url = f"{base_url}{endpoint['docPath']}"
                
                # Use HTML link - removing target="_blank" might help with anchor navigation
                # but we'll add it back with a note
                st.markdown(f'📖 <a href="{doc_url}" target="_blank" style="color: #667eea; font-weight: 600; text-decoration: none;">**View Full Documentation**</a>', unsafe_allow_html=True)
                st.caption(f"Opens documentation for: {endpoint['method']} {endpoint['path']}")
                
                # Provide the direct anchor for manual navigation
                with st.expander("🔧 Having trouble navigating to the endpoint?"):
                    st.markdown("**Option 1:** Copy and paste this URL into your browser:")
                    st.code(doc_url, language="text")
                    st.markdown("**Option 2:** After the page loads, search for:")
                    st.code(endpoint['path'], language="text")
                    st.markdown("**Option 3:** Look for the operation ID:")
                    st.code(endpoint['docPath'].replace('#operation/', ''), language="text")
            
            # Example code checkbox
            if endpoint.get("example"):
                if st.checkbox("Show Example Code", key="show_example_checkbox"):
                    # Show example code when checkbox is checked
                    st.markdown("#### Example Code")
                    st.markdown(f"**{endpoint['example']['description']}**")
                    st.code(endpoint['example']['code'], language="bash")
                    st.info("💡 Remember to replace YOUR_CLIENT_ID and YOUR_SECRET with your actual credentials")
            
            # Export options
            st.markdown("#### 💾 Export Recommendation")
            # Language selector for SDK code
            selected_language = st.selectbox(
                "Select SDK language:",
                ["Python", "JavaScript"],
                key="sdk_language"
            )
            
            # Generate the code based on selection
            endpoint = st.session_state.recommendation
            if selected_language == "Python":
                code = self.generate_python_sdk_code(endpoint)
                filename = f"c2m_{self._generate_function_name(endpoint['id'])}.py"
                mime = "text/x-python"
            else:  # JavaScript
                code = self.generate_javascript_sdk_code(endpoint)
                filename = f"c2m_{self._generate_function_name(endpoint['id'], 'js')}.js"
                mime = "text/javascript"
            
            # Direct download button
            st.download_button(
                label="📥 Download Sample Code",
                data=code,
                file_name=filename,
                mime=mime,
                type="primary"
            )
            
            # Show mock server notice if enabled
            if self.config["api"].get("use_mock_server", False):
                mock_url = self.config["api"].get("mock_server_url", "")
                if "xxxxxxxx" in mock_url:
                    st.warning("⚠️ **Action Required**: Update `config.yaml` with your personal Postman mock server URL. Check your Postman workspace → Mock Servers to find your URL.")
                else:
                    st.success(f"✅ Using Postman mock server: `{mock_url}`")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar with additional options"""
        with st.sidebar:
            st.markdown("### 🛠️ Click2Endpoint Tools")
            st.markdown("---")
            
            # Show current answers in a nice format
            if st.session_state.answers:
                st.markdown("#### 📋 Your Selections")
                for field, value in st.session_state.answers.items():
                    field_name = field.replace("_", " ").title()
                    st.markdown(f"""
                    <div class="feature-card" style="background: white; border-radius: 10px; padding: 1rem; margin-bottom: 0.5rem; border-left: 3px solid #667eea;">
                        <strong style="color: #374151;">{field_name}:</strong> <span style="color: #667eea;">{value}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Show job options if selected
            if st.session_state.job_options:
                st.markdown("#### ⚙️ Job Options")
                for field, value in st.session_state.job_options.items():
                    st.markdown(f"""
                    <div class="feature-card" style="background: white; border-radius: 10px; padding: 0.5rem 1rem; margin-bottom: 0.5rem; border-left: 3px solid #764ba2;">
                        <strong style="color: #374151;">{field}:</strong> <span style="color: #764ba2;">{value}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Use case examples with cleaner styling
            st.markdown("#### 💡 Quick Examples")
            use_cases = {
                "⚖️ Legal Letters": "Single doc + Template",
                "💰 Monthly Invoices": "Multi doc + Address capture",
                "📰 Newsletters": "Single doc + Template + Mailing list",
                "🏥 Medical Reports": "Multi doc merge + Template"
            }
            
            for name, desc in use_cases.items():
                with st.expander(name, expanded=False):
                    st.markdown(f"**Scenario:** {desc}")
                    st.caption("Click to see how to configure this")
            
            # Postman Integration
            if self.config.get("postman", {}).get("enabled", False):
                st.markdown("#### 🔗 Postman Integration")
                with st.expander("Select Mock Server", expanded=False):
                    postman = PostmanAPI(self.config["postman"].get("api_key"))
                    selected_mock_url = postman.select_mock_server_ui()
                    
                    if selected_mock_url and st.button("Use This Mock Server"):
                        self.config["api"]["mock_server_url"] = selected_mock_url
                        st.success(f"✅ Updated to use: {selected_mock_url}")
                        st.rerun()
            
            # Session history with cleaner metrics
            st.markdown("#### 📊 Session Stats")
            log_dir = Path(__file__).parent.parent / "logs"
            if log_dir.exists():
                csv_file = log_dir / "recommendations.csv"
                if csv_file.exists():
                    df = pd.read_csv(csv_file)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total", len(df))
                    with col2:
                        if not df.empty:
                            top_endpoint = df['endpoint'].mode().iloc[0]
                            st.metric("Popular", top_endpoint.split('/')[-1][:10] + "...")
    
    def log_session(self, endpoint_id: str):
        """Log the session for analytics"""
        timestamp = datetime.now().isoformat()
        endpoint = self.endpoints[endpoint_id]
        
        # Prepare log entry
        log_entry = {
            "timestamp": timestamp,
            "answers": st.session_state.answers,
            "job_options": st.session_state.job_options,
            "recommended_endpoint": endpoint["path"],
            "endpoint_id": endpoint_id
        }
        
        # Create logs directory
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Append to JSONL
        with jsonlines.open(log_dir / "sessions.jsonl", mode="a") as writer:
            writer.write(log_entry)
        
        # Append to CSV
        csv_file = log_dir / "recommendations.csv"
        csv_exists = csv_file.exists()
        
        import csv
        with open(csv_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "timestamp", "docType", "templateUsage", "endpoint", "endpoint_id"
            ])
            if not csv_exists:
                writer.writeheader()
            writer.writerow({
                "timestamp": timestamp,
                "docType": st.session_state.answers.get("docType", ""),
                "templateUsage": st.session_state.answers.get("templateUsage", st.session_state.answers.get("useTemplate", "")),
                "endpoint": endpoint["path"],
                "endpoint_id": endpoint_id
            })
    
    def generate_python_sdk_code(self, endpoint: Dict[str, Any]) -> str:
        """Generate Python SDK code for the endpoint"""
        # Extract example code if available
        example = endpoint.get("example", {})
        
        # Determine API URL based on configuration
        if self.config["api"].get("use_mock_server", False):
            api_url = self.config["api"].get("mock_server_url", "https://YOUR-MOCK-SERVER-ID.mock.pstmn.io")
            auth_note = "# Note: Using test credentials for the mock server"
            client_id = "test-client-123"
            client_secret = "super-secret-password-123"
        else:
            api_url = self.config["api"].get("base_url", "https://api.c2m.com")
            auth_note = ""
            client_id = "YOUR_CLIENT_ID"
            client_secret = "YOUR_CLIENT_SECRET"
        
        # Include job options in the generated code if applicable
        job_options_code = ""
        if st.session_state.job_options and not self.check_if_template_endpoint(st.session_state.answers):
            job_options_code = f"""
    # Job options from your configuration
    "jobOptions": {{
        "documentClass": "{st.session_state.job_options.get('documentClass', 'businessLetter')}",
        "layout": "{st.session_state.job_options.get('layout', 'portrait')}",
        "mailclass": "{st.session_state.job_options.get('mailclass', 'firstClassMail')}",
        "paperType": "{st.session_state.job_options.get('paperType', 'letter')}",
        "printOption": "{st.session_state.job_options.get('printOption', 'color')}",
        "envelope": "{st.session_state.job_options.get('envelope', 'flat')}"
    }},"""
        
        code = f'''#!/usr/bin/env python3
"""
C2M API - {endpoint['description']}
Endpoint: {endpoint['method']} {endpoint['path']}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import requests
import json
from typing import Dict, Any

# Configuration
API_BASE_URL = "{api_url}"  # Mock server or production API endpoint
AUTH_BASE_URL = "https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev"  # C2M Auth service (always use this)
{auth_note}
CLIENT_ID = "{client_id}"  # Replace with your client ID if using production
CLIENT_SECRET = "{client_secret}"  # Replace with your client secret if using production


def print_request(method: str, url: str, headers: Dict, body: Any = None):
    """Pretty print HTTP request"""
    print("\\n" + "="*60)
    print("📤 REQUEST")
    print("="*60)
    print(f"{{method}} {{url}}")
    print("\\nHEADERS:")
    for key, value in headers.items():
        if key.lower() == 'authorization' and len(value) > 50:
            print(f"  {{key}}: Bearer {{value[7:27]}}...")
        else:
            print(f"  {{key}}: {{value}}")
    if body:
        print("\\nBODY:")
        print(json.dumps(body, indent=2))
    print("="*60)

def print_response(response: requests.Response):
    """Pretty print HTTP response"""
    print("\\n" + "-"*60)
    print("📥 RESPONSE")
    print("-"*60)
    print(f"Status: {{response.status_code}} {{response.reason}}")
    print("\\nHEADERS:")
    for key, value in response.headers.items():
        print(f"  {{key}}: {{value}}")
    print("\\nBODY:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("-"*60 + "\\n")

def revoke_existing_tokens(client_id: str, client_secret: str):
    """Revoke any existing tokens to ensure fresh authentication"""
    revoke_url = f"{{AUTH_BASE_URL}}/auth/tokens/revoke"
    
    print("\\n🔄 Attempting to revoke any existing tokens...")
    
    headers = {{
        "Content-Type": "application/json"
    }}
    
    # Try to revoke using client credentials
    payload = {{
        "client_id": client_id,
        "client_secret": client_secret
    }}
    
    print_request("POST", revoke_url, headers, payload)
    
    try:
        response = requests.post(revoke_url, json=payload, headers=headers)
        print_response(response)
        if response.status_code == 200:
            print("✅ Existing tokens revoked successfully")
        elif response.status_code == 403:
            print("⚠️  No existing tokens to revoke (403: Missing Authentication Token)")
        else:
            print("⚠️  Token revocation returned status:", response.status_code)
    except Exception as e:
        print(f"⚠️  Could not revoke tokens: {{e}}")

def get_access_token(client_id: str, client_secret: str) -> str:
    """Get an access token using client credentials"""
    # First, revoke any existing tokens
    revoke_existing_tokens(client_id, client_secret)
    
    # Step 1: Get long-term token
    print("\\n🔐 Getting long-term token...")
    auth_url = f"{{AUTH_BASE_URL}}/auth/tokens/long"
    
    if "mock.pstmn.io" in API_BASE_URL:
        print("📍 Using mock server for API calls")
        print("🔐 Getting fresh tokens from C2M Auth service...")
    
    headers = {{
        "Content-Type": "application/json"
    }}
    
    payload = {{
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }}
    
    print_request("POST", auth_url, headers, payload)
    
    try:
        response = requests.post(auth_url, json=payload, headers=headers)
        print_response(response)
        response.raise_for_status()
        
        long_token_data = response.json()
        long_token = long_token_data.get("access_token", "")
        
        print("\\n✅ Long-term token obtained!")
        print(f"🔑 Long token (30-90 days): {{long_token[:30]}}...")
        print(f"⏱️  Expires in: {{long_token_data.get('expires_in', 'unknown')}} seconds")
        
        # Step 2: Exchange for short-term token
        print("\\n🔄 Exchanging for short-term token...")
        short_url = f"{{AUTH_BASE_URL}}/auth/tokens/short"
        
        short_headers = {{
            "Authorization": f"Bearer {{long_token}}",
            "Content-Type": "application/json"
        }}
        
        short_payload = {{}}  # Can optionally narrow scopes here
        
        print_request("POST", short_url, short_headers, short_payload)
        
        response = requests.post(short_url, json=short_payload, headers=short_headers)
        print_response(response)
        response.raise_for_status()
        
        short_token_data = response.json()
        short_token = short_token_data.get("access_token", "")
        
        print("\\n✅ Short-term token obtained!")
        print(f"🔑 Short token (15 min): {{short_token[:30]}}...")
        print(f"⏱️  Expires in: {{short_token_data.get('expires_in', 'unknown')}} seconds")
        
        return short_token
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("\\n❌ Authentication failed. Check your client_id and client_secret.")
        else:
            print(f"\\n❌ Auth error: {{e}}")
        raise


def {self._generate_function_name(endpoint['id'])}(token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """{endpoint['description']}
    
    Args:
        token: Bearer token for authentication
        payload: Request payload
        
    Returns:
        API response as dictionary
    """
    url = f"{{API_BASE_URL}}{endpoint['path']}"
    
    headers = {{
        "Authorization": f"Bearer {{token}}",
        "Content-Type": "application/json"
    }}
    
    print_request("POST", url, headers, payload)
    
    response = requests.post(url, json=payload, headers=headers)
    print_response(response)
    response.raise_for_status()
    
    return response.json()


if __name__ == "__main__":
    # Get access token
    print("\\n🔐 Getting access token...")
    token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    print(f"✅ Access token obtained: {{token[:20]}}..." if len(token) > 20 else f"✅ Access token: {{token}}")
    
    # Example payload
    payload = {self._generate_example_payload(endpoint)}
    {job_options_code}
    
    # Submit request
    print(f"\\n📤 Sending request to: {{API_BASE_URL}}{endpoint['path']}")
    
    try:
        result = {self._generate_function_name(endpoint['id'])}(token, payload)
        print("\\n✅ Success! Job submitted")
    except requests.exceptions.RequestException as e:
        print(f"\\n❌ Error: {{e}}")
'''
        return code
    
    def generate_javascript_sdk_code(self, endpoint: Dict[str, Any]) -> str:
        """Generate JavaScript SDK code for the endpoint with job options"""
        # Determine API URL based on configuration
        if self.config["api"].get("use_mock_server", False):
            api_url = self.config["api"].get("mock_server_url", "https://YOUR-MOCK-SERVER-ID.mock.pstmn.io")
            auth_note = "// Note: Using test credentials for the mock server\n"
            client_id = "test-client-123"
            client_secret = "super-secret-password-123"
        else:
            api_url = self.config["api"].get("base_url", "https://api.c2m.com")
            auth_note = ""
            client_id = "YOUR_CLIENT_ID"
            client_secret = "YOUR_CLIENT_SECRET"
        
        # Include job options in the generated code if applicable
        job_options_code = ""
        if st.session_state.job_options and not self.check_if_template_endpoint(st.session_state.answers):
            job_options_code = f"""
    // Job options from your configuration
    jobOptions: {{
      documentClass: "{st.session_state.job_options.get('documentClass', 'businessLetter')}",
      layout: "{st.session_state.job_options.get('layout', 'portrait')}",
      mailclass: "{st.session_state.job_options.get('mailclass', 'firstClassMail')}",
      paperType: "{st.session_state.job_options.get('paperType', 'letter')}",
      printOption: "{st.session_state.job_options.get('printOption', 'color')}",
      envelope: "{st.session_state.job_options.get('envelope', 'flat')}"
    }},"""
        
        code = f'''/**
 * C2M API - {endpoint['description']}
 * Endpoint: {endpoint['method']} {endpoint['path']}
 * Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */

const axios = require('axios');

// Configuration
const API_BASE_URL = '{api_url}'; // Mock server or production API endpoint
const AUTH_BASE_URL = 'https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev'; // C2M Auth service (always use this)
{auth_note}const CLIENT_ID = '{client_id}'; // Replace with your client ID if using production
const CLIENT_SECRET = '{client_secret}'; // Replace with your client secret if using production

/**
 * Pretty print HTTP request
 */
function printRequest(method, url, headers, body = null) {{
  console.log("\\n" + "=".repeat(60));
  console.log("📤 REQUEST");
  console.log("=".repeat(60));
  console.log(`${{method}} ${{url}}`);
  console.log("\\nHEADERS:");
  for (const [key, value] of Object.entries(headers)) {{
    if (key.toLowerCase() === 'authorization' && value.length > 50) {{
      console.log(`  ${{key}}: Bearer ${{value.substring(7, 27)}}...`);
    }} else {{
      console.log(`  ${{key}}: ${{value}}`);
    }}
  }}
  if (body) {{
    console.log("\\nBODY:");
    console.log(JSON.stringify(body, null, 2));
  }}
  console.log("=".repeat(60));
}}

/**
 * Pretty print HTTP response
 */
function printResponse(response) {{
  console.log("\\n" + "-".repeat(60));
  console.log("📥 RESPONSE");
  console.log("-".repeat(60));
  console.log(`Status: ${{response.status}} ${{response.statusText}}`);
  console.log("\\nHEADERS:");
  for (const [key, value] of Object.entries(response.headers)) {{
    console.log(`  ${{key}}: ${{value}}`);
  }}
  console.log("\\nBODY:");
  console.log(JSON.stringify(response.data, null, 2));
  console.log("-".repeat(60) + "\\n");
}}

/**
 * Revoke existing tokens before authentication
 */
async function revokeExistingTokens(clientId, clientSecret) {{
  console.log("\\n🔒 Revoking any existing tokens...");
  const url = `${{AUTH_BASE_URL}}/auth/tokens/revoke`;
  const data = {{
    grant_type: 'client_credentials',
    client_id: clientId,
    client_secret: clientSecret
  }};
  const headers = {{
    'Content-Type': 'application/json'
  }};
  
  printRequest('POST', url, headers, data);
  
  try {{
    const response = await axios.post(url, data, {{ headers }});
    printResponse(response);
    console.log("✅ Tokens revoked successfully");
  }} catch (error) {{
    if (error.response) {{
      printResponse(error.response);
      if (error.response.status === 403) {{
        console.log("⚠️  No existing tokens to revoke (403: Missing Authentication Token)");
      }} else {{
        console.log("⚠️  Token revocation returned status:", error.response.status);
      }}
    }} else {{
      console.log("⚠️  Could not revoke tokens:", error.message);
    }}
  }}
}}

/**
 * Get an access token using client credentials
 * @param {{string}} clientId - Your client ID
 * @param {{string}} clientSecret - Your client secret
 * @returns {{Promise<string>}} Access token
 */
async function getAccessToken(clientId, clientSecret) {{
  // First revoke any existing tokens
  await revokeExistingTokens(clientId, clientSecret);
  
  // Step 1: Get long-term token
  console.log("\\n🔐 Getting long-term token...");
  const authUrl = `${{AUTH_BASE_URL}}/auth/tokens/long`;
  
  if (API_BASE_URL.includes('mock.pstmn.io')) {{
    console.log('📍 Using mock server for API calls');
    console.log('🔐 Getting fresh tokens from C2M Auth service...');
  }}
  
  const payload = {{
    grant_type: 'client_credentials',
    client_id: clientId,
    client_secret: clientSecret
  }};
  const headers = {{
    'Content-Type': 'application/json'
  }};
  
  printRequest('POST', authUrl, headers, payload);
  
  try {{
    const response = await axios.post(authUrl, payload, {{ headers }});
    printResponse(response);
    
    const longTokenData = response.data;
    const longToken = longTokenData.access_token;
    
    console.log("\\n✅ Long-term token obtained!");
    console.log(`🔑 Long token (30-90 days): ${{longToken.substring(0, 30)}}...`);
    console.log(`⏱️  Expires in: ${{longTokenData.expires_in || 'unknown'}} seconds`);
    
    // Step 2: Exchange for short-term token
    console.log("\\n🔄 Exchanging for short-term token...");
    const shortUrl = `${{AUTH_BASE_URL}}/auth/tokens/short`;
    
    const shortHeaders = {{
      'Authorization': `Bearer ${{longToken}}`,
      'Content-Type': 'application/json'
    }};
    
    const shortPayload = {{}}; // Can optionally narrow scopes here
    
    printRequest('POST', shortUrl, shortHeaders, shortPayload);
    
    const shortResponse = await axios.post(shortUrl, shortPayload, {{ headers: shortHeaders }});
    printResponse(shortResponse);
    
    const shortTokenData = shortResponse.data;
    const shortToken = shortTokenData.access_token;
    
    console.log("\\n✅ Short-term token obtained!");
    console.log(`🔑 Short token (15 min): ${{shortToken.substring(0, 30)}}...`);
    console.log(`⏱️  Expires in: ${{shortTokenData.expires_in || 'unknown'}} seconds`);
    
    return shortToken;
  }} catch (error) {{
    if (error.response) {{
      printResponse(error.response);
    }}
    throw error;
  }}
}}

/**
 * {endpoint['description']}
 * @param {{string}} token - Bearer token for authentication
 * @param {{Object}} payload - Request payload
 * @returns {{Promise<Object>}} API response
 */
async function {self._generate_function_name(endpoint['id'], 'js')}(token, payload) {{
  console.log("\\n📤 Sending request to C2M API...");
  const url = `${{API_BASE_URL}}{endpoint['path']}`;
  
  const headers = {{
    'Authorization': `Bearer ${{token}}`,
    'Content-Type': 'application/json'
  }};
  
  printRequest('POST', url, headers, payload);
  
  try {{
    const response = await axios.post(url, payload, {{ headers }});
    printResponse(response);
    console.log('✅ Request successful!');
    return response.data;
  }} catch (error) {{
    if (error.response) {{
      printResponse(error.response);
    }}
    throw error;
  }}
}}

// Main execution
(async () => {{
  try {{
    // Get access token
    const token = await getAccessToken(CLIENT_ID, CLIENT_SECRET);
    
    // Example payload
    const payload = {self._generate_example_payload(endpoint, 'js')};
    {job_options_code}
    
    // Submit request
    const result = await {self._generate_function_name(endpoint['id'], 'js')}(token, payload);
    
    console.log('\\n🎉 Job completed successfully!');
  }} catch (error) {{
    console.error('\\n❌ Error:', error.message);
    process.exit(1);
  }}
}})();
'''
        return code
    
    def _generate_function_name(self, endpoint_id: str, language: str = 'python') -> str:
        """Generate a function name from endpoint ID"""
        # Convert camelCase to snake_case for Python
        if language == 'python':
            # Insert underscore before capital letters and convert to lowercase
            import re
            name = re.sub('([A-Z])', r'_\1', endpoint_id).lower()
            return name.lstrip('_')
        else:
            # Keep camelCase for JavaScript
            return endpoint_id

    def _generate_example_payload(self, endpoint: Dict[str, Any], language: str = 'python') -> str:
        """Generate example payload based on endpoint with job options if needed"""
        # Create example payload based on endpoint type
        if endpoint['id'] == 'submitSingleDoc':
            payload = {
                "document": {
                    "url": "https://example.com/letter.pdf"
                },
                "recipient": {
                    "name": "John Doe",
                    "address1": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip": "12345"
                }
            }
            # Add job options for non-template endpoints
            if st.session_state.job_options:
                payload["jobOptions"] = {}
                for field, value in st.session_state.job_options.items():
                    payload["jobOptions"][field] = value
        elif endpoint['id'] in ['submitSingleDocTemplate', 'submitSingleDocWithTemplate']:
            payload = {
                "templateId": "your-template-id",
                "document": {
                    "url": "https://example.com/document.pdf"
                },
                "recipientOverride": {
                    "name": "Jane Smith",
                    "address1": "456 Oak Ave"
                }
            }
        elif endpoint['id'] == 'submitMultiDoc':
            payload = {
                "documents": [
                    {
                        "url": "https://example.com/doc1.pdf",
                        "addressCapture": True
                    },
                    {
                        "url": "https://example.com/doc2.pdf",
                        "addressCapture": True
                    }
                ]
            }
            # Add job options for non-template endpoints
            if st.session_state.job_options:
                payload["jobOptions"] = {}
                for field, value in st.session_state.job_options.items():
                    payload["jobOptions"][field] = value
        elif endpoint['id'] in ['submitMultiDocTemplate', 'submitMultiDocWithTemplate']:
            payload = {
                "templateId": "your-template-id",
                "documents": [
                    {
                        "url": "https://example.com/doc1.pdf",
                        "recipientOverride": {
                            "name": "John Doe",
                            "address1": "123 Main St"
                        }
                    },
                    {
                        "url": "https://example.com/doc2.pdf",
                        "recipientOverride": {
                            "name": "Jane Smith",
                            "address1": "456 Oak Ave"
                        }
                    }
                ]
            }
        elif endpoint['id'] in ['submitPdfSplit', 'splitPdf', 'splitPdfWithCapture']:
            payload = {
                "document": {
                    "url": "https://example.com/combined.pdf"
                },
                "splitOptions": {
                    "delimiter": "pageBreak",
                    "addressCapture": True,
                    "addressLocation": "topRight"
                }
            }
            # Add job options for non-template endpoints
            if st.session_state.job_options:
                payload["jobOptions"] = {}
                for field, value in st.session_state.job_options.items():
                    payload["jobOptions"][field] = value
        elif endpoint['id'] == 'singleDocJob':
            # Use Case 4: Single doc to multiple recipients
            payload = {
                "document": {
                    "url": "https://example.com/document.pdf"
                },
                "recipients": [
                    {
                        "name": "John Doe",
                        "address1": "123 Main St",
                        "city": "Anytown",
                        "state": "CA",
                        "zip": "12345"
                    },
                    {
                        "name": "Jane Smith",
                        "address1": "456 Oak Ave",
                        "city": "Another City",
                        "state": "NY",
                        "zip": "10001"
                    }
                ]
            }
            # Add job options
            if st.session_state.job_options:
                payload["jobOptions"] = {}
                for field, value in st.session_state.job_options.items():
                    payload["jobOptions"][field] = value
        elif endpoint['id'] in ['mergeMultiDoc', 'mergeMultiDocWithTemplate']:
            # Merge multiple documents
            payload = {
                "documentsToMerge": [
                    {"url": "https://example.com/page1.pdf"},
                    {"url": "https://example.com/page2.pdf"},
                    {"url": "https://example.com/page3.pdf"}
                ],
                "recipient": {
                    "name": "John Doe",
                    "address1": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip": "12345"
                }
            }
            if 'Template' in endpoint['id']:
                payload["templateId"] = "your-template-id"
                payload.pop("recipient", None)  # Template provides recipient
            elif st.session_state.job_options:
                payload["jobOptions"] = {}
                for field, value in st.session_state.job_options.items():
                    payload["jobOptions"][field] = value
        elif endpoint['id'] == 'multiPdfWithCapture':
            # Use Case 9: Multiple PDFs with address capture
            payload = {
                "addressCapturePdfs": [
                    {
                        "url": "https://example.com/invoice1.pdf",
                        "addressRegion": {
                            "x": 100,
                            "y": 100,
                            "width": 300,
                            "height": 150
                        }
                    },
                    {
                        "url": "https://example.com/invoice2.pdf",
                        "addressRegion": {
                            "x": 100,
                            "y": 100,
                            "width": 300,
                            "height": 150
                        }
                    }
                ]
            }
            # Add job options
            if st.session_state.job_options:
                payload["jobOptions"] = {}
                for field, value in st.session_state.job_options.items():
                    payload["jobOptions"][field] = value
        else:
            # Generic payload
            payload = {
                "document": {
                    "url": "https://example.com/document.pdf"
                },
                "options": {
                    "color": True
                }
            }
        
        # Add job options if they exist and this is not a template endpoint
        if st.session_state.job_options and not self.check_if_template_endpoint(st.session_state.answers):
            payload["jobOptions"] = {}
            for field, value in st.session_state.job_options.items():
                # Handle multi-select fields (currently only mailclass)
                if isinstance(value, list):
                    payload["jobOptions"][field] = value
                else:
                    payload["jobOptions"][field] = value
        
        if language == 'python':
            return json.dumps(payload, indent=4)
        else:
            return json.dumps(payload, indent=2)

    
    def run(self):
        """Main app runner"""
        self.render_header()
        self.render_sidebar()
        
        # Main content area
        if st.session_state.recommendation:
            self.render_recommendation()
            st.markdown("---")
            with st.expander("Start a new recommendation"):
                self.render_questionnaire()
        else:
            self.render_questionnaire()
        
        # Footer with cleaner styling
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            f"""<div style='text-align: center; padding: 2rem 0; color: #9ca3af; font-size: 0.875rem;'>
            <p>🚀 Powered by C2M API | 
            <a href='{st.session_state.get("doc_base_url", "http://localhost:8080")}' target='_blank' style='color: #667eea; text-decoration: none;'>Documentation</a> | 
            <a href='https://github.com/c2m/api' target='_blank' style='color: #667eea; text-decoration: none;'>GitHub</a></p>
            </div>""",
            unsafe_allow_html=True
        )

def main():
    navigator = StreamlitNavigator()
    navigator.run()

if __name__ == "__main__":
    main()