# C2M API V2 Click2Endpoint - EBNF Integration

## Overview

This is an enhanced version of the C2M Click2Endpoint Navigator that integrates EBNF-based parameter generation. The system combines:

1. **Level 1 Questions**: Hardcoded decision tree to identify the correct API endpoint
2. **Level 2 Questions**: Dynamic parameter collection based on EBNF data dictionary

## Key Components

### 1. EBNF Parser (`scripts/ebnf_parser.py`)
- Parses `c2mapiv2-dd-with-questions.ebnf` file
- Extracts use cases, endpoints, and parameter questions
- Generates dynamic Q&A trees for parameter collection

### 2. Endpoint Mapper (`scripts/endpoint_mapper.py`)
- Contains hardcoded Level 1 decision tree
- Maps user decisions to EBNF use cases
- Supports all 9 C2M API endpoints

### 3. Streamlit App (`streamlit_app/app_ebnf.py`)
- Visual interface with cards and animations
- Two-stage question flow
- SDK code generation (Python & JavaScript)

## Supported Endpoints

1. `/jobs/single-doc` - Single document to multiple recipients
2. `/jobs/single-doc-job-template` - Single document with template
3. `/jobs/multi-doc` - Multiple documents to different recipients
4. `/jobs/multi-docs-job-template` - Multiple documents with template
5. `/jobs/multi-doc-merge` - Merge documents before sending
6. `/jobs/multi-doc-merge-job-template` - Merge with template
7. `/jobs/single-pdf-split` - Split PDF into sections
8. `/jobs/single-pdf-split-addressCapture` - Split PDF with address extraction
9. `/jobs/multi-pdf-address-capture` - Multiple PDFs with address capture

## Running the Application

```bash
# Make sure you're in the c2m-api-v2-click2endpoint directory
cd c2m-api-v2-click2endpoint

# Run the EBNF-integrated version
./run_ebnf.sh

# Or run directly with Streamlit
streamlit run streamlit_app/app_ebnf.py --server.port 8502
```

## Architecture

```
Level 1: Endpoint Selection (Hardcoded)
├── How many documents?
│   ├── Single → Template? → Endpoint
│   ├── Multiple → Separate/Merge → Template? → Endpoint
│   └── PDF Split → Address capture? → Endpoint

Level 2: Parameter Collection (EBNF-based)
├── Parse EBNF use case definition
├── Extract parameter questions
├── Display dynamic form
└── Generate SDK code
```

## EBNF File Format

The system expects questions embedded in EBNF comments:

```ebnf
(* 
  Use Case 1: Description
  Endpoint: POST /jobs/endpoint
  Question: Top-level question for this use case
*)
useCaseName = 
    parameterOne        (* Question: What is parameter one? *)
  + parameterTwo        (* Question: What is parameter two? *)
  + [ optionalParam ] ; (* Question (optional): Optional parameter? *)
```

## Testing

```bash
# Test EBNF parser
python scripts/test_ebnf_parser.py

# This will show:
# - All parsed use cases
# - Extracted parameters and questions
# - Generated Q&A tree for a sample use case
```

## Benefits of EBNF Integration

1. **Single Source of Truth**: EBNF file drives parameter definitions
2. **Dynamic Questions**: Automatically generates parameter forms
3. **Maintainable**: Changes to EBNF automatically reflect in UI
4. **Type-Safe**: EBNF grammar ensures correct parameter structure
5. **Documentation**: EBNF serves as both spec and implementation

## Future Enhancements

- Natural language endpoint selection using use case descriptions
- Validation based on EBNF grammar rules
- Auto-complete for parameter values
- Export to Postman collections
- Integration with API testing framework