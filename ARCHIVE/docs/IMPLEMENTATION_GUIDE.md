# Click2Endpoint Implementation Guide

## Table of Contents
1. [Overview](#overview)
2. [Current Implementation](#current-implementation)
3. [Key Code Components](#key-code-components)
4. [Features Implemented](#features-implemented)
5. [Deferred Features](#deferred-features)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Unused Code Analysis](#unused-code-analysis)
8. [Architecture Decisions](#architecture-decisions)

## Overview

Click2Endpoint is an interactive web application that helps developers select the correct C2M API v2 endpoint for their document submission needs. It uses a 4-question decision tree to identify the appropriate endpoint, collects required parameters based on the EBNF specification, and generates complete, runnable code with authentication.

### Core Workflow
1. **Level 1 Questions** (Endpoint Selection)
   - Q1: Document type (single/multi/merge/pdfSplit)
   - Q2: Template usage (yes/no)
   - Q3: Recipient style (explicit/template/addressCapture)
   - Q4: Personalization (yes/no) - only for multi/merge

2. **Level 2 Parameters** (EBNF-based collection)
   - Document specification (5 methods from EBNF)
   - Recipient addresses (3 methods)
   - Job template (ID and/or name)
   - Payment details (6 types)
   - Tags

3. **Code Generation**
   - Complete Python scripts with authentication flow
   - JSON request bodies
   - JavaScript previews
   - cURL commands

## Current Implementation

### File Structure
```
streamlit_app/app_hardcoded_v1.py  # Main application (Phase 1 hardcoded)
scripts/ebnf_template_parser.py     # EBNF comment parser for template logic
config.yaml                         # Configuration (Postman, mock servers)
c2mapiv2-dd.ebnf                   # EBNF specification (source of truth)
```

### Technology Stack
- **Frontend**: Streamlit with custom CSS for beautiful UI
- **Backend**: Python 3.x
- **Authentication**: C2M Auth Service (2-token system)
- **API Testing**: Postman Mock Servers
- **Configuration**: YAML + Environment variables

## Key Code Components

### 1. Endpoint Mapping (app_hardcoded_v1.py:304-330)
```python
def get_endpoint(answers):
    """Determine endpoint based on answers - from EBNF file"""
    doc_type = answers.get("docType")
    template_usage = answers.get("templateUsage")
    recipient_style = answers.get("recipientStyle")
    
    if doc_type == "single":
        if template_usage == "true":
            return "/jobs/single-doc-job-template"  # Use Case 1
        else:
            return "/jobs/single-doc"  # Use Case 4
    # ... additional mappings
```

This hardcoded function maps the 27 possible paths through the decision tree to 8 unique endpoints defined in the EBNF.

### 2. Document Specification Helper (app_hardcoded_v1.py:373-419)
```python
def render_document_specification(key_suffix=""):
    """Helper to render document specification with all 5 EBNF options"""
    # Shows expandable info with all 5 methods
    # Renders appropriate input fields based on selection
    # Handles: documentId, externalUrl, uploadRequestId+documentName, 
    #          zipId+documentName, uploadRequestId+zipId+documentName
```

Implements the EBNF-defined documentSourceIdentifier with all 5 specification methods.

### 3. Template Logic Implementation (app_hardcoded_v1.py:582-611)
```python
# For endpoints with templates (Use Cases 1 & 3)
if recipient_style == "template":
    # Recipients from template - only ask about document
    doc_option = st.selectbox(
        "How will the document be provided?",
        ["Document from template", "Document from API call"]
    )
elif recipient_style == "explicit":
    # Recipients in API call - ask about both document and addresses
```

Implements the business logic where templates ALWAYS provide job options and MAY provide either document OR recipients (never both).

### 4. Authentication Code Generation (app_hardcoded_v1.py:742-945)
```python
def generate_full_python_code(endpoint: str, body: dict) -> str:
    """Generate complete Python code with authentication flow"""
    # Includes:
    # - Token revocation
    # - Long-term token acquisition
    # - Short-term token exchange
    # - Request/response pretty printing
    # - Error handling
```

Generates production-ready Python scripts matching the examples provided.

### 5. Postman Integration (app_hardcoded_v1.py:37-87)
```python
def get_postman_mock_servers():
    """Fetch mock servers from Postman API"""
    # Currently hardcoded with personal API key
    # Returns all mock servers from account
    # Falls back to config default if API fails
```

## Features Implemented

### ✅ Complete Features
1. **Beautiful UI** - Card-based selection with icons and gradients
2. **All 8 EBNF endpoints** - Correct paths from Use Cases 1-8
3. **5 document specification methods** - Per EBNF documentSourceIdentifier
4. **6 payment types** - CREDIT_CARD, INVOICE, ACH, USER_CREDIT, APPLE_PAY, GOOGLE_PAY
5. **Template logic** - Job options always + document OR recipients (never both)
6. **Complete auth flow** - Revoke → Long-term → Short-term tokens
7. **Code generation** - Python (full), JavaScript (preview), cURL, JSON
8. **File operations** - Save generated code with timestamps
9. **Download buttons** - For generated scripts
10. **Session state** - Maintains selections through navigation
11. **Code execution** - Run generated Python code directly in UI with results display

### 🔧 Partial Features
1. **Postman Integration** - API key hardcoded, fetches mocks but doesn't filter
2. **Mock server selection** - Dropdown works but correct URL is hardcoded
3. **EBNF parsing** - Template parser extracts comments but not used for questions

## Deferred Features

### 1. Dynamic Postman Mock Server Fetching
**Current State**: 
- API key is hardcoded in the code
- Fetches all mock servers but doesn't properly filter for C2M
- Falls back to hardcoded URL

**Implementation Plan**:
```python
# Step 1: Properly load API keys from environment
def load_postman_config():
    return {
        'personal_key': os.getenv('POSTMAN_API_KEY_PERSONAL'),
        'team_key': os.getenv('POSTMAN_API_KEY_TEAM'),
        'workspace': os.getenv('POSTMAN_WORKSPACE', 'personal')
    }

# Step 2: Enhanced mock server fetching with filtering
def get_c2m_mock_servers(workspace='personal'):
    # Fetch collections first
    collections = fetch_postman_collections(workspace)
    # Find C2M collection
    c2m_collection = find_collection_by_name(collections, "C2M API v2")
    # Get associated mock servers
    return fetch_collection_mocks(c2m_collection['id'])

# Step 3: Cache results to avoid repeated API calls
@st.cache_data(ttl=300)  # 5-minute cache
def get_cached_mock_servers(workspace):
    return get_c2m_mock_servers(workspace)
```

### 2. Personal vs Team Workspace Selection
**Current State**: 
- UI shows radio buttons if both keys exist
- But selection doesn't actually switch between workspaces

**Implementation Plan**:
```python
# Step 1: Create workspace manager
class PostmanWorkspaceManager:
    def __init__(self):
        self.personal_api = PostmanAPI(os.getenv('POSTMAN_API_KEY_PERSONAL'))
        self.team_api = PostmanAPI(os.getenv('POSTMAN_API_KEY_TEAM'))
    
    def get_workspace_mocks(self, workspace_type):
        api = self.personal_api if workspace_type == 'personal' else self.team_api
        return api.get_mock_servers()

# Step 2: Update UI to use workspace manager
if 'workspace_manager' not in st.session_state:
    st.session_state.workspace_manager = PostmanWorkspaceManager()

workspace = st.radio("Select Workspace", ["personal", "team"])
mocks = st.session_state.workspace_manager.get_workspace_mocks(workspace)
```

### 3. Dynamic Question Generation from EBNF
**Current State**: 
- Questions are hardcoded in render_level1_questions()
- EBNF parser exists but only used for template logic extraction

**Implementation Plan**:

#### Phase 1: Extract Question Metadata from EBNF
```python
# Add question metadata to EBNF comments
"""
(* 
  Q1: What type of document submission do you need?
  Options: single|multi|merge|pdfSplit
  Next: Q2 if single|multi|merge, Q3 if pdfSplit
*)
"""

# Enhanced parser to extract questions
class EBNFQuestionParser(EBNFTemplateParser):
    def parse_question_metadata(self):
        # Extract Q1, Q2, etc. from comments
        # Build decision tree structure
        return {
            'q1': {
                'text': 'What type of document submission?',
                'options': ['single', 'multi', 'merge', 'pdfSplit'],
                'next': {'single': 'q2', 'multi': 'q2', ...}
            }
        }
```

#### Phase 2: Dynamic Question Renderer
```python
class DynamicQuestionRenderer:
    def __init__(self, question_tree):
        self.tree = question_tree
    
    def render_question(self, question_id):
        q = self.tree[question_id]
        
        # Create options with descriptions from EBNF
        options = []
        for opt in q['options']:
            options.append({
                'value': opt,
                'label': self.get_label_from_ebnf(opt),
                'description': self.get_description_from_ebnf(opt)
            })
        
        # Render using existing visual_choice component
        selected = render_visual_choice(question_id, options)
        
        if selected:
            next_q = q['next'].get(selected)
            st.session_state.current_step = next_q
```

#### Phase 3: Level 2 Dynamic Parameters
```python
# Use existing EBNF parser to get parameter requirements
def get_endpoint_parameters(endpoint):
    # Parse EBNF to find endpoint definition
    ebnf_tree = parse_ebnf_file('c2mapiv2-dd.ebnf')
    
    # Extract parameters for endpoint
    params = ebnf_tree.get_endpoint_params(endpoint)
    
    # Generate form fields dynamically
    for param in params:
        if param.type == 'documentSourceIdentifier':
            render_document_specification()
        elif param.type == 'recipientAddressSource':
            render_address_inputs()
        # etc.
```

## Unused Code Analysis

### From chat-ebnf-to-qa-generator:

1. **ebnf_qa_parser.py** - Full EBNF parser that could generate questions
   - Currently only using template parser for comments
   - Could use for full dynamic generation

2. **scripts/qa_recommender.py** - CLI interface with rich output
   - Has session logging we could integrate
   - Export functionality we partially reimplemented

3. **data/qa_tree.yaml** - YAML-based question tree
   - Could be generated from EBNF instead of hardcoded
   - Has more detailed option descriptions

4. **build_training_file.py** - Converts logs to training data
   - Not used but could help improve question flow

5. **endpoint_mapper.py** - Maps questions to endpoints
   - We reimplemented this as get_endpoint()
   - Original has more sophisticated mapping logic

### Opportunities:
1. **Session Logging**: Original has comprehensive logging we should add
2. **Export Formats**: Original supports multiple export formats
3. **Training Data**: Could use interaction logs to improve questions
4. **CLI Interface**: Could offer CLI version using questionary

## Architecture Decisions

### Why Phase 1 Hardcoded?
1. **Faster iteration** - Could test UI/UX without parser complexity
2. **Known working state** - Ensures all 27 paths work correctly
3. **Clear requirements** - Hardcoding revealed exact needs for parser
4. **Risk mitigation** - Can always fall back to hardcoded if parser fails

### Why Streamlit?
1. **Rapid prototyping** - Built beautiful UI in hours
2. **Component reuse** - Visual choice cards, forms, etc.
3. **Session state** - Built-in state management
4. **Deployment ready** - Easy to containerize and deploy

### Why Two-Level System?
1. **Separation of concerns** - Navigation vs data collection
2. **EBNF alignment** - Level 1 finds use case, Level 2 gets params
3. **User experience** - Progressive disclosure of complexity
4. **Maintainability** - Can update levels independently

## Next Steps

### Immediate (Phase 1.5)
1. ~~Create comprehensive test suite~~ ✅ COMPLETED
2. ~~Add code execution feature~~ ✅ COMPLETED
3. Fix Postman integration to properly use environment variables
4. Add session logging for analytics
5. Add input validation for all fields

### Short-term (Phase 2)
1. Implement dynamic Level 2 from EBNF
2. Add workspace switching functionality  
3. Cache Postman API responses
4. Add more endpoints (Use Cases 9+)

### Long-term (Phase 3)
1. Full dynamic question generation
2. Natural language endpoint finder
3. Integration with actual C2M API
4. Multi-language code generation

## Conclusion

The current implementation successfully delivers a working Phase 1 with:
- Beautiful, intuitive UI
- Correct endpoint selection for all 27 paths
- Complete code generation with auth
- All EBNF-specified parameters

The deferred features are well-understood with clear implementation paths. The modular architecture makes it straightforward to evolve from hardcoded to fully dynamic while maintaining the polished user experience.