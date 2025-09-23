# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **C2M Endpoint Navigator** - an interactive Q&A-based tool that helps developers select the correct C2M API endpoint for submitting job requests. It's designed to work with the c2m-api-repo project's endpoints.

## Architecture

The system now has a complete implementation in `/c2m-endpoint-navigator/`:

### Core Components

- **Endpoint Registry** (`data/endpoints.json`): Metadata for all C2M API endpoints
- **Decision Tree** (`data/qa_tree.yaml`): Configurable Q&A flow with conditional logic
- **CLI Tool** (`scripts/qa_recommender.py`): Interactive command-line interface using questionary
- **Web App** (`streamlit_app/app.py`): Full-featured Streamlit web interface
- **Training Builder** (`scripts/build_training_file.py`): Converts logs to LLM training data
- **Docker Support**: Complete containerization with docker-compose

### Legacy Implementations
- **Chat Version** (`/chat-version/`): Original prototype implementations
- **Claude Version** (`/claude-version/`): Original specification document

## Key Functionality

The navigator uses a tiered decision tree to recommend endpoints:
1. Document type (single/multi/merge/split)
2. Template usage (yes/no)
3. Recipient addressing method
4. Personalization requirements
5. Special features needed

Supported endpoints:
- `/jobs/submit/single/doc` - Simple single document
- `/jobs/submit/single/doc/template` - Single doc with template
- `/jobs/submit/multi/doc` - Multiple separate documents
- `/jobs/submit/multi/doc/template` - Multiple docs with template
- `/jobs/submit/multi/doc/merge` - Merge multiple documents
- `/jobs/submit/pdf/split` - Split combined PDF

## Development Commands

### Quick Start
```bash
cd c2m-endpoint-navigator
./quickstart.sh
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run CLI
python scripts/qa_recommender.py

# Run web interface
streamlit run streamlit_app/app.py

# Run with Docker
docker-compose up -d
```

### Building Training Data
```bash
python scripts/build_training_file.py \
  --input logs/sessions.jsonl \
  --output training_data.jsonl \
  --format openai
```

## Project Structure

```
c2m-endpoint-navigator/
├── data/                    # Configuration files
│   ├── endpoints.json      # Endpoint metadata
│   └── qa_tree.yaml       # Decision tree
├── scripts/                # CLI tools
├── streamlit_app/         # Web interface
├── logs/                  # Session logs (auto-created)
├── Dockerfile            # Container config
├── docker-compose.yml    # Multi-container setup
└── requirements.txt      # Dependencies
```

## Implementation Notes

- Uses questionary for rich CLI interactions
- Streamlit provides responsive web UI
- Logs all sessions in JSONL and CSV formats
- Supports OpenAI, Claude, and generic training data formats
- Docker setup includes web, CLI, and training services
- Rich console output with colored formatting
- Export recommendations in JSON/YAML formats

## Testing & Running

```bash
# Test CLI locally
python scripts/qa_recommender.py

# Test web app
streamlit run streamlit_app/app.py

# Run all tests
pytest tests/

# Generate training data from logs
python scripts/build_training_file.py --stats
```

## C2M API Context

This navigator is specifically designed for the C2M API V2 project's document submission endpoints. It helps developers choose between various submission methods based on their specific use cases (legal letters, invoices, newsletters, etc.).