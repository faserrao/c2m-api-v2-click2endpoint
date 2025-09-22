# Click2Endpoint Test Suite Guide

## Overview

This comprehensive test suite ensures the Click2Endpoint application works correctly across all 27 QA paths, validates business logic, and verifies code generation. The tests are designed to run automatically whenever code changes are made, preventing regressions and ensuring quality.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_endpoint_mapping.py # Tests all 27 QA paths → endpoint mapping
├── test_document_specification.py # Tests 5 document specification methods
├── test_template_logic.py   # Tests template business rules
├── test_code_generation.py  # Tests Python/JS/cURL generation
└── test_integration.py      # End-to-end integration tests
```

## Running Tests

### Quick Start
```bash
# Run all tests with coverage
./run_tests.sh

# Run specific test file
pytest tests/test_endpoint_mapping.py -v

# Run with coverage report
pytest --cov=streamlit_app --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Manual Test Execution
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_endpoint_mapping.py::TestEndpointMapping::test_single_no_template_explicit
```

## Test Categories

### 1. Endpoint Mapping Tests (`test_endpoint_mapping.py`)
Tests all 27 possible paths through the QA decision tree:
- **Single Document (8 paths)**: With/without template, 3 recipient styles
- **Multi Document (8 paths)**: With/without template, personalization options
- **Merge Document (8 paths)**: Similar to multi with merge functionality
- **PDF Split (3 paths)**: 3 recipient styles only

**Example Test**:
```python
def test_single_template_explicit(self):
    """Path: single -> template -> explicit addresses"""
    answers = {
        "docType": "single",
        "templateUsage": "true",
        "recipientStyle": "explicit"
    }
    assert get_endpoint(answers) == "/jobs/single-doc-job-template"
```

### 2. Document Specification Tests (`test_document_specification.py`)
Tests all 5 EBNF-defined document specification methods:
1. `documentId` only
2. `externalUrl` only
3. `uploadRequestId` + `documentName`
4. `zipId` + `documentName`
5. `uploadRequestId` + `zipId` + `documentName`

**Coverage**: Validates each method works correctly and handles validation errors.

### 3. Template Logic Tests (`test_template_logic.py`)
Validates critical business rules:
- Templates ALWAYS provide job options
- Templates MAY provide either document OR recipients (NEVER both)
- Correct parameter collection based on what template provides

**Key Scenarios**:
- Template provides recipients → API needs document
- Template provides document → API needs recipients
- Template provides neither → API needs both

### 4. Code Generation Tests (`test_code_generation.py`)
Validates generated code for all formats:
- **Python**: Full authentication flow (revoke → long-term → short-term)
- **JavaScript**: Async/await with proper error handling
- **cURL**: Correct headers and JSON formatting

**Features Tested**:
- Authentication token flow
- Request body serialization
- Error handling
- Pretty printing
- All 6 payment types

### 5. Integration Tests (`test_integration.py`)
End-to-end testing:
- Complete flow from QA answers to generated code
- Postman mock server integration
- Validation across components
- Error scenarios

## Test Fixtures

### `conftest.py` Provides:
1. **`mock_streamlit`**: Automatically mocks Streamlit for all tests
2. **`sample_request_bodies`**: Pre-built request bodies for testing
3. **`mock_postman_response`**: Simulated Postman API responses
4. **`all_endpoints`**: List of valid EBNF endpoints
5. **`qa_paths`**: All 27 possible QA decision paths

## Coverage Requirements

Current coverage target: **80%**

To view coverage report:
```bash
# Generate HTML report
pytest --cov=streamlit_app --cov-report=html

# Open in browser
open htmlcov/index.html
```

## CI/CD Integration

### GitHub Actions Workflow
The `.github/workflows/tests.yml` runs on:
- Every push to `main` or `develop`
- Every pull request to `main`

**Actions performed**:
1. Run tests on Python 3.8-3.11
2. Generate coverage reports
3. Run linting (flake8, black, isort)
4. Security checks (bandit, safety)

### Pre-commit Testing
Before committing:
```bash
# Run quick test suite
pytest tests/ -x --tb=short

# Check specific functionality
pytest -k "template" -v
```

## Test Patterns

### Testing QA Paths
```python
# Pattern for testing endpoint selection
def test_[docType]_[templateUsage]_[recipientStyle]_[personalization](self):
    answers = {
        "docType": "...",
        "templateUsage": "true/false",
        "recipientStyle": "explicit/template/addressCapture",
        "personalization": "true/false"  # if applicable
    }
    assert get_endpoint(answers) == "/expected/endpoint"
```

### Testing Validation
```python
# Pattern for testing validation
def test_invalid_[field]_rejected(self):
    with pytest.raises(ValueError, match="expected error"):
        validate_function({"field": "invalid_value"})
```

## Adding New Tests

When adding features:
1. Add unit tests for new functions
2. Update integration tests for end-to-end flows
3. Add edge case tests for error handling
4. Update fixtures if new test data needed

**Example**: Adding a new endpoint
```python
# In test_endpoint_mapping.py
def test_new_endpoint_mapping(self):
    answers = {"docType": "new", ...}
    assert get_endpoint(answers) == "/jobs/new-endpoint"

# In test_integration.py
def test_new_endpoint_complete_flow(self):
    # Test full flow from QA to code generation
```

## Debugging Failed Tests

### Common Issues:
1. **Import Errors**: Check if Streamlit is properly mocked
2. **Assertion Failures**: Verify expected values match EBNF spec
3. **Mock Failures**: Ensure all external dependencies are mocked

### Debug Commands:
```bash
# Run with full traceback
pytest -vv --tb=long

# Run with pdb on failure
pytest --pdb

# Show print statements
pytest -s
```

## Best Practices

1. **Keep tests isolated**: Each test should be independent
2. **Use fixtures**: Reuse common test data via fixtures
3. **Mock external calls**: Never make real API calls in tests
4. **Test edge cases**: Include validation and error scenarios
5. **Descriptive names**: Test names should explain what they test

## Maintenance

### Regular Tasks:
- Update tests when EBNF changes
- Add tests for new features
- Remove tests for deprecated features
- Keep coverage above 80%

### Quarterly Review:
- Check test performance
- Update dependencies
- Review and refactor complex tests
- Update this guide

---

With this test suite, you can confidently make changes knowing that all 27 QA paths and critical business logic are automatically validated! 🎯