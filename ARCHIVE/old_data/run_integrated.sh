#!/bin/bash
# Launch script for C2M API V2 Click2Endpoint with integrated parameter questions

echo "Starting C2M API V2 Click2Endpoint Navigator (Integrated Version)..."
echo "============================================="
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Error: Streamlit is not installed."
    echo "Please install it with: pip install streamlit"
    exit 1
fi

# Run the Streamlit app
echo "Launching Streamlit app..."
echo "The app will open in your default browser."
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

streamlit run streamlit_app/app_integrated.py --server.port 8502