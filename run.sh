#!/bin/bash

# Simple script to run C2M Endpoint Navigator

echo "🧭 C2M Endpoint Navigator"
echo "========================="
echo ""
echo "Choose how to run:"
echo "1) Web Interface (Recommended)"
echo "2) Command Line Interface"
echo "3) View Demo"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "Starting web interface..."
        echo "Opening http://localhost:8501 in your browser..."
        
        # Try to open browser on different platforms
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open http://localhost:8501 &
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            xdg-open http://localhost:8501 &
        fi
        
        # Start Streamlit
        streamlit run streamlit_app/app.py
        ;;
    2)
        echo "Starting CLI interface..."
        python scripts/qa_recommender.py
        ;;
    3)
        echo "Running demo..."
        python demo.py
        ;;
    *)
        echo "Invalid choice. Please run ./run.sh again"
        exit 1
        ;;
esac