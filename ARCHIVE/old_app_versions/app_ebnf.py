"""
C2M API V2 Click2Endpoint Navigator with EBNF Integration
Combines Level 1 hardcoded decision tree with Level 2 EBNF-based parameter collection
"""

import streamlit as st
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import time

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ebnf_qa_parser import generate_qa_tree_for_endpoint, walk_qa_tree
from endpoint_mapper import EndpointMapper

# Page configuration
st.set_page_config(
    page_title="C2M API V2 - Click2Endpoint Navigator",
    page_icon="📮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Main container styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Card styling */
    .endpoint-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        transition: transform 0.3s ease;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .endpoint-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
    }
    
    .option-card {
        background: #f7fafc;
        border: 2px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .option-card:hover {
        border-color: #667eea;
        background: #eef2ff;
        transform: translateY(-2px);
    }
    
    .option-card.selected {
        border-color: #667eea;
        background: #eef2ff;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.1);
    }
    
    /* Progress indicator */
    .progress-step {
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #e2e8f0;
        color: #a0aec0;
        text-align: center;
        line-height: 30px;
        margin: 0 0.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .progress-step.active {
        background: #667eea;
        color: white;
    }
    
    .progress-step.completed {
        background: #48bb78;
        color: white;
    }
    
    /* Parameter input styling */
    .param-section {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Success message styling */
    .success-box {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'stage' not in st.session_state:
    st.session_state.stage = 'level1'  # 'level1', 'level2', 'complete'
if 'level1_answers' not in st.session_state:
    st.session_state.level1_answers = {}
if 'current_question_id' not in st.session_state:
    st.session_state.current_question_id = 'initial'
if 'selected_endpoint' not in st.session_state:
    st.session_state.selected_endpoint = None
if 'selected_use_case' not in st.session_state:
    st.session_state.selected_use_case = None
if 'level2_answers' not in st.session_state:
    st.session_state.level2_answers = {}
if 'ebnf_path' not in st.session_state:
    st.session_state.ebnf_path = str(Path(__file__).parent.parent.parent / "c2mapiv2-dd-with-questions.ebnf")
if 'qa_tree' not in st.session_state:
    st.session_state.qa_tree = None

def reset_navigation():
    """Reset the navigation to start over"""
    st.session_state.stage = 'level1'
    st.session_state.level1_answers = {}
    st.session_state.current_question_id = 'initial'
    st.session_state.selected_endpoint = None
    st.session_state.selected_use_case = None
    st.session_state.level2_answers = {}
    st.session_state.qa_tree = None

def display_progress():
    """Display progress indicator"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; margin: 2rem 0;'>", unsafe_allow_html=True)
        
        # Progress steps
        steps = ['1', '2', '3']
        for i, step in enumerate(steps):
            if i == 0 and st.session_state.stage in ['level1', 'level2', 'complete']:
                class_name = 'completed' if st.session_state.stage in ['level2', 'complete'] else 'active'
            elif i == 1 and st.session_state.stage in ['level2', 'complete']:
                class_name = 'completed' if st.session_state.stage == 'complete' else 'active'
            elif i == 2 and st.session_state.stage == 'complete':
                class_name = 'active'
            else:
                class_name = ''
                
            st.markdown(f'<span class="progress-step {class_name}">{step}</span>', unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Progress labels
        if st.session_state.stage == 'level1':
            st.markdown("<p style='text-align: center; color: #667eea; font-weight: bold;'>Step 1: Find Your Endpoint</p>", unsafe_allow_html=True)
        elif st.session_state.stage == 'level2':
            st.markdown("<p style='text-align: center; color: #667eea; font-weight: bold;'>Step 2: Configure Parameters</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align: center; color: #48bb78; font-weight: bold;'>Step 3: Get Your Code!</p>", unsafe_allow_html=True)

def display_level1_question():
    """Display Level 1 questions for endpoint selection"""
    # Get current question
    if st.session_state.current_question_id == 'initial':
        question_data = EndpointMapper.get_initial_question()
    else:
        # Get question by ID
        question_data = EndpointMapper.get_question_by_id(st.session_state.current_question_id)
        if not question_data:
            # Reset to initial if question not found
            question_data = EndpointMapper.get_initial_question()
            st.session_state.current_question_id = 'initial'
    
    st.markdown(f"### {question_data['question']}")
    
    # Display options as cards
    cols = st.columns(len(question_data['options']))
    
    for idx, (col, option) in enumerate(zip(cols, question_data['options'])):
        with col:
            card_content = f"""
            <div class="option-card" onclick="this.querySelector('button').click()">
                <h4>{option['label']}</h4>
                <p>{option['description']}</p>
            </div>
            """
            st.markdown(card_content, unsafe_allow_html=True)
            
            if st.button(f"Select {option['label']}", key=f"opt_{option['value']}", use_container_width=True):
                # Process the answer
                st.session_state.level1_answers[st.session_state.current_question_id] = option['value']
                
                # Get next question or endpoint
                result = EndpointMapper.get_next_question(st.session_state.current_question_id, option['value'])
                
                if result:
                    if result['type'] == 'endpoint':
                        # We've reached an endpoint
                        st.session_state.selected_endpoint = result['endpoint']
                        st.session_state.selected_use_case = result['use_case']
                        st.session_state.stage = 'level2'
                    else:
                        # Move to next question
                        st.session_state.current_question_id = result['id']
                else:
                    st.error("Invalid selection. Please try again.")
                    
                st.rerun()

def display_level2_parameters():
    """Display Level 2 parameter collection using EBNF"""
    endpoint_info = EndpointMapper.get_endpoint_info(st.session_state.selected_endpoint)
    
    st.markdown(f"### Selected Endpoint: {endpoint_info['name']}")
    st.markdown(f"**Endpoint:** `{st.session_state.selected_endpoint}`")
    st.markdown(f"**Description:** {endpoint_info['description']}")
    
    # Generate Q&A tree from EBNF if not already done
    if not st.session_state.qa_tree:
        tree_data = generate_qa_tree_for_endpoint(
            st.session_state.ebnf_path,
            st.session_state.selected_use_case
        )
        if not tree_data or 'qa_tree' not in tree_data:
            st.error(f"Could not generate parameter questions for {st.session_state.selected_use_case}")
            return
        st.session_state.qa_tree = tree_data['qa_tree']
    
    st.markdown("---")
    st.markdown("### Configure Your Request Parameters")
    
    # Display the QA tree
    display_qa_node(st.session_state.qa_tree, "root")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.stage = 'level1'
            st.session_state.qa_tree = None
            st.rerun()
            
    with col2:
        # For now, allow proceeding if we have any answers
        has_answers = len(st.session_state.level2_answers) > 0
        
        if st.button("Generate Code →", use_container_width=True, disabled=not has_answers):
            st.session_state.stage = 'complete'
            st.rerun()
    
def display_qa_node(node, node_id, parent_key=""):
    """Recursively display QA tree nodes"""
    if not node:
        return
        
    node_type = node.get("type")
    question = node.get("question", "")
    is_optional = node.get("optional", False)
    is_repeatable = node.get("repeatable", False)
    
    # Create unique key for this node
    key = f"{parent_key}_{node_id}" if parent_key else node_id
    
    if node_type == "choice":
        # Multiple choice question
        options = node.get("options", [])
        option_labels = [opt.get("answer", "Option") for opt in options]
        
        label = question
        if is_optional:
            label += " (optional)"
            option_labels = ["None"] + option_labels
            
        selected = st.selectbox(
            label,
            options=option_labels,
            key=f"choice_{key}"
        )
        
        if selected and selected != "None":
            st.session_state.level2_answers[question] = selected
            
            # Check for follow-up questions
            selected_idx = option_labels.index(selected)
            if not is_optional or selected_idx > 0:
                actual_idx = selected_idx - 1 if is_optional else selected_idx
                if actual_idx < len(options) and "follow_up" in options[actual_idx]:
                    display_qa_node(options[actual_idx]["follow_up"], f"{node_id}_followup", key)
                    
    elif node_type == "sequence":
        # Sequence of questions
        if question:
            st.markdown(f"**{question}**")
            
        steps = node.get("steps", [])
        for i, step in enumerate(steps):
            display_qa_node(step, f"{node_id}_step{i}", key)
            
    elif node_type == "field":
        # Text input field
        label = question
        if is_optional:
            label += " (optional)"
            
        if is_repeatable:
            # Multiple values
            st.markdown(f"**{label}**")
            count_key = f"count_{key}"
            if count_key not in st.session_state:
                st.session_state[count_key] = 1
                
            values = []
            for i in range(st.session_state[count_key]):
                value = st.text_input(
                    f"Value {i+1}",
                    key=f"field_{key}_{i}"
                )
                if value:
                    values.append(value)
                    
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("➕ Add", key=f"add_{key}"):
                    st.session_state[count_key] += 1
                    st.rerun()
                    
            if values:
                st.session_state.level2_answers[question] = values
        else:
            # Single value
            value = st.text_input(
                label,
                key=f"field_{key}"
            )
            if value:
                st.session_state.level2_answers[question] = value

def generate_sdk_code():
    """Generate SDK code based on selections"""
    endpoint = st.session_state.selected_endpoint
    params = st.session_state.level2_answers
    
    # Python SDK code
    python_code = f'''import requests
import json

# C2M API Configuration
API_BASE_URL = "https://api-stage.click2mail.com"
API_KEY = "your_api_key_here"

# Prepare request payload
payload = {json.dumps(params, indent=4)}

# Make API request
headers = {{
    "Authorization": f"Bearer {{API_KEY}}",
    "Content-Type": "application/json"
}}

response = requests.post(
    f"{{API_BASE_URL}}{endpoint}",
    headers=headers,
    json=payload
)

# Handle response
if response.status_code == 200:
    result = response.json()
    print("Success:", result)
else:
    print("Error:", response.status_code, response.text)
'''

    # JavaScript SDK code
    js_code = f'''const axios = require('axios');

// C2M API Configuration
const API_BASE_URL = 'https://api-stage.click2mail.com';
const API_KEY = 'your_api_key_here';

// Prepare request payload
const payload = {json.dumps(params, indent=2)};

// Make API request
axios.post(
    `${{API_BASE_URL}}{endpoint}`,
    payload,
    {{
        headers: {{
            'Authorization': `Bearer ${{API_KEY}}`,
            'Content-Type': 'application/json'
        }}
    }}
)
.then(response => {{
    console.log('Success:', response.data);
}})
.catch(error => {{
    console.error('Error:', error.response?.status, error.response?.data);
}});
'''
    
    return python_code, js_code

def display_complete():
    """Display completion screen with generated code"""
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown("### ✅ Your API Request is Ready!")
    st.markdown(f"**Endpoint:** `{st.session_state.selected_endpoint}`")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate SDK code
    python_code, js_code = generate_sdk_code()
    
    # Display code in tabs
    tab1, tab2, tab3 = st.tabs(["Python SDK", "JavaScript SDK", "Request Summary"])
    
    with tab1:
        st.code(python_code, language="python")
        if st.button("📋 Copy Python Code", key="copy_python"):
            st.write("Code copied!")
            
    with tab2:
        st.code(js_code, language="javascript")
        if st.button("📋 Copy JavaScript Code", key="copy_js"):
            st.write("Code copied!")
            
    with tab3:
        st.json({
            "endpoint": st.session_state.selected_endpoint,
            "use_case": st.session_state.selected_use_case,
            "parameters": st.session_state.level2_answers,
            "level1_decisions": st.session_state.level1_answers
        })
    
    # Start over button
    st.markdown("---")
    if st.button("🔄 Start New Request", use_container_width=True):
        reset_navigation()
        st.rerun()

# Main app
def main():
    # Header
    st.markdown("# 📮 C2M API V2 - Click2Endpoint Navigator")
    st.markdown("Navigate to the right endpoint and generate SDK code with ease!")
    
    # Display progress indicator
    display_progress()
    
    # Main content area
    if st.session_state.stage == 'level1':
        display_level1_question()
    elif st.session_state.stage == 'level2':
        display_level2_parameters()
    else:
        display_complete()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🛠️ About This Tool")
        st.markdown("""
        This tool helps you:
        1. **Find the right endpoint** through simple questions
        2. **Configure parameters** based on EBNF specifications
        3. **Generate SDK code** ready for integration
        
        All parameters are dynamically generated from the C2M API V2 EBNF data dictionary.
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Session Info")
        st.json({
            "stage": st.session_state.stage,
            "endpoint": st.session_state.selected_endpoint,
            "parameters_collected": len(st.session_state.level2_answers)
        })
        
        if st.button("🔄 Reset", use_container_width=True):
            reset_navigation()
            st.rerun()

if __name__ == "__main__":
    main()