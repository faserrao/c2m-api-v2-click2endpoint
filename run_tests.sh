#!/bin/bash
# Run all Click2Endpoint tests

echo "🧪 Running Click2Endpoint Test Suite..."
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt
pip install -q -r requirements-test.txt

# Run tests with coverage
echo -e "\n${YELLOW}Running tests...${NC}"
pytest tests/ \
    --cov=streamlit_app \
    --cov=scripts \
    --cov-report=term-missing \
    --cov-report=html \
    -v

# Capture exit code
TEST_EXIT_CODE=$?

# Generate coverage report
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
    echo -e "${YELLOW}Coverage report generated in htmlcov/index.html${NC}"
else
    echo -e "\n${RED}❌ Some tests failed!${NC}"
fi

# Run specific test categories
echo -e "\n${YELLOW}Test Summary by Category:${NC}"
echo "========================="

# Unit tests
echo -n "Unit tests: "
pytest tests/ -m unit -q --tb=no 2>/dev/null && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}"

# Integration tests
echo -n "Integration tests: "
pytest tests/ -m integration -q --tb=no 2>/dev/null && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}"

# Run individual test files
echo -e "\n${YELLOW}Individual Test Files:${NC}"
echo "====================="

for test_file in tests/test_*.py; do
    if [ -f "$test_file" ]; then
        filename=$(basename "$test_file")
        echo -n "$filename: "
        pytest "$test_file" -q --tb=no 2>/dev/null && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}"
    fi
done

# Quick smoke test
echo -e "\n${YELLOW}Running quick smoke test...${NC}"
python -c "
import sys
sys.path.insert(0, '.')
try:
    from streamlit_app.app_hardcoded_v1 import get_endpoint
    # Test a simple case
    result = get_endpoint({'docType': 'single', 'templateUsage': 'false', 'recipientStyle': 'explicit'})
    assert result == '/jobs/single-doc', f'Expected /jobs/single-doc, got {result}'
    print('✅ Smoke test passed!')
except Exception as e:
    print(f'❌ Smoke test failed: {e}')
    sys.exit(1)
"

# Deactivate virtual environment
deactivate

exit $TEST_EXIT_CODE