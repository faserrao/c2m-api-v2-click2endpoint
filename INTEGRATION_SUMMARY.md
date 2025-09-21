# C2M Endpoint Navigator - EBNF Integration Summary

## Overview

Successfully integrated the two C2M API V2 projects:

1. **c2m-api-v2-click2endpoint** - Streamlit web UI with visual cards
2. **chat-ebnf-to-qa-generator** - EBNF grammar parser for dynamic Q&A

The integrated solution uses EBNF as the single source of truth while maintaining the polished Streamlit UI.

## Architecture

### Two-Level Question System

1. **Level 1: Endpoint Selection** (Hardcoded)
   - Interactive decision tree to identify the correct API endpoint
   - Maps user choices to one of 9 endpoints
   - Implemented in `scripts/endpoint_mapper.py`

2. **Level 2: Parameter Collection** (EBNF-Driven)
   - Dynamically generates questions based on EBNF definitions
   - Special handling for template business logic
   - Implemented in `scripts/ebnf_template_parser.py`

## Key Components

### 1. EBNF Template Parser (`scripts/ebnf_template_parser.py`)

Parses the EBNF file to:
- Extract template logic from commented blocks
- Understand what comes from templates vs API calls
- Generate appropriate UI flows

Key features:
- Handles complex alternations for Use Case 1
- Supports optional template parameters for Use Case 3
- Extracts parameter questions from EBNF comments

### 2. Endpoint Mapper (`scripts/endpoint_mapper.py`)

Maps between:
- Level 1 decision paths → API endpoints
- API endpoints → EBNF use case names

### 3. Integrated Streamlit App (`streamlit_app/app_template_integrated.py`)

Combines:
- Level 1 hardcoded questions for endpoint selection
- Level 2 EBNF-driven parameter collection
- Template choice handling for Use Cases 1 and 3

## Template Business Logic

The parser correctly handles two use cases with template logic:

### Use Case 1: `/jobs/single-doc-job-template`
Three options:
1. Template provides document → User provides recipients
2. Template provides recipients → User provides document  
3. Template provides job options only → User provides both
   - **Special case**: This option requires an additional question asking whether the document comes from the template or API call
   - If document from template → User only provides recipients
   - If document from API → User provides both document and recipients

### Use Case 3: `/jobs/multi-doc-merge-job-template`
Two options:
1. Template provides recipient → User provides documents
2. Template provides job options only → User provides everything

## Testing

Run the integration test:
```bash
python test_integration.py
```

Run the template parser test:
```bash
python scripts/test_template_parser.py
```

Run the integrated Streamlit app:
```bash
streamlit run streamlit_app/app_template_integrated.py
```

## EBNF Format

The solution works with the modified EBNF format:
- Clean EBNF for OpenAPI generation (no TEMPLATE literal in syntax)
- Template logic preserved in comments using `(* ... *)` blocks
- Questions embedded as `(* Question: ... *)` comments

## Next Steps

1. Complete parameter collection UI for all endpoints
2. Add SDK code generation (Python/JavaScript)
3. Integrate with Postman mock servers
4. Add validation for collected parameters
5. Implement export functionality