#!/bin/bash
# Launch script for C2M API V2 Click2Endpoint with EBNF integration

echo "Starting C2M API V2 Click2Endpoint Navigator (EBNF Version)..."
echo "============================================="
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Error: Streamlit is not installed."
    echo "Please install it with: pip install streamlit"
    exit 1
fi

# Check if EBNF file exists
EBNF_FILE="../c2mapiv2-dd-with-questions.ebnf"
if [ ! -f "$EBNF_FILE" ]; then
    echo "Error: EBNF file not found at $EBNF_FILE"
    echo "Please ensure c2mapiv2-dd-with-questions.ebnf exists in the parent directory."
    exit 1
fi

# Run the Streamlit app
echo "Launching Streamlit app..."
echo "The app will open in your default browser."
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

streamlit run streamlit_app/app_ebnf.py --server.port 8502