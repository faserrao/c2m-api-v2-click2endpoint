# 🎯 Click2Endpoint - C2M API v2

An interactive tool that helps developers find the perfect C2M API endpoint for their document submission needs through a guided Q&A process.

## 🎯 Purpose

The C2M API offers multiple endpoints for document submission, each optimized for specific use cases. Click2Endpoint simplifies endpoint selection by:

- Asking targeted questions about your use case
- Analyzing your requirements
- Recommending the optimal endpoint
- Providing documentation and examples
- Logging sessions for continuous improvement

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/faserrao/c2m-api-v2-click2endpoint.git
cd c2m-api-v2-click2endpoint

# Run setup (creates virtual environment and installs dependencies)
python setup.py

# Or use the quickstart script
./quickstart.sh
```

### CLI Usage

```bash
# Run the command-line interface
python scripts/qa_recommender.py
```

### Web Interface

```bash
# Navigate to the streamlit app directory and run
cd streamlit_app
streamlit run app_hardcoded_v1.py --server.port 8502 --server.address localhost
```

The web interface will open at `http://localhost:8502`

## 📁 Project Structure

```
c2m-api-v2-click2endpoint/
├── data/
│   ├── endpoints.json      # Endpoint metadata registry
│   └── qa_tree.yaml       # Decision tree configuration
├── scripts/
│   ├── qa_recommender.py  # CLI implementation
│   └── build_training_file.py  # LLM training data exporter
├── streamlit_app/
│   └── app.py            # Web interface
├── logs/                 # Session logs (auto-created)
│   ├── sessions.jsonl    # Detailed session data
│   └── recommendations.csv # Summary data
├── tests/
│   └── test_click2endpoint.py # Unit tests
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-container setup
└── requirements.txt     # Python dependencies
```

## 🔧 Configuration

### Documentation Server (`config.yaml`)

Configure where documentation links point to:

```yaml
documentation:
  # Set to 'local' or 'remote'
  default_server: local
  
  # Local documentation server URL
  local_url: http://localhost:4000
  
  # Remote documentation server URL (GitHub Pages)
  remote_url: https://c2m.github.io/api-docs
  
  # Allow users to toggle between servers in the UI
  allow_toggle: true
```

To use remote documentation by default:
1. Edit `config.yaml`
2. Change `default_server: remote`
3. Set `allow_toggle: false` to hide the toggle

### Endpoint Metadata (`data/endpoints.json`)

Defines all available C2M API endpoints with their characteristics:

```json
{
  "id": "submitSingleDocTemplate",
  "path": "/jobs/submit/single/doc/template",
  "method": "POST",
  "description": "Submit a single document using a saved job template",
  "docType": "single",
  "templateUsage": "yes",
  "useCases": ["Legal letters", "Real estate postcards"],
  "linkToDocs": "https://docs.api.c2m.com/...",
  "examples": ["postman/examples/..."]
}
```

### Decision Tree (`data/qa_tree.yaml`)

Configures the Q&A flow:

```yaml
decision_tree:
  - tier: 1
    question: "What type of document submission do you need?"
    field: docType
    options:
      - value: single
        label: "Single document"
      - value: multi
        label: "Multiple separate documents"
```

## 💡 Common Use Cases

### Legal Firm Letters
- **Scenario**: Daily certified mail letters with copies to legal representatives
- **Recommended**: `/jobs/submit/single/doc/template`
- **Features**: Template support, certified mail options

### Monthly Invoices
- **Scenario**: Batch invoice processing with address extraction
- **Recommended**: `/jobs/submit/multi/doc` with address capture
- **Features**: Batch processing, automatic address detection

### Medical Reports
- **Scenario**: Custom reports with standard information pages
- **Recommended**: `/jobs/submit/multi/doc/merge`
- **Features**: Document merging, template support

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the web interface
open http://localhost:8501

# View logs
docker-compose logs -f
```

## 📊 Session Logging

All recommendation sessions are logged for:
- Analytics and improvement
- LLM training data generation
- Usage pattern analysis

### Log Formats

**JSONL** (`logs/sessions.jsonl`):
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "session_log": [...],
  "answers": {...},
  "recommended_endpoint": "/jobs/submit/single/doc"
}
```

**CSV** (`logs/recommendations.csv`):
```csv
timestamp,docType,templateUsage,endpoint,endpoint_id
2024-01-15T10:30:00,single,yes,/jobs/submit/single/doc/template,submitSingleDocTemplate
```

## 🤖 LLM Training Data

Generate training data for fine-tuning language models:

```bash
python scripts/build_training_file.py \
  --input logs/sessions.jsonl \
  --output training_data.jsonl \
  --format openai
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

## 🔌 API Integration

Click2Endpoint can be integrated into your applications:

```python
from click2endpoint import Click2Endpoint

click2endpoint = Click2Endpoint()
answers = {
    "docType": "single",
    "templateUsage": "yes"
}
endpoint = click2endpoint.find_endpoint(answers)
print(f"Use: {endpoint['path']}")
```

## 📚 Endpoint Reference

| Endpoint | Use Case |
|----------|----------|
| `/jobs/submit/single/doc` | Simple one-off mailings |
| `/jobs/submit/single/doc/template` | Recurring single documents |
| `/jobs/submit/multi/doc` | Batch processing |
| `/jobs/submit/multi/doc/template` | Batch with templates |
| `/jobs/submit/multi/doc/merge` | Merge multiple documents |
| `/jobs/submit/pdf/split` | Split combined PDFs |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Documentation: https://docs.api.c2m.com
- Issues: https://github.com/[your-username]/c2m-api-v2-click2endpoint/issues
- Email: support@c2m.com