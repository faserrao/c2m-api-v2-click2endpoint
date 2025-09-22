#!/bin/bash
# Quick start script for C2M Endpoint Navigator

echo "🧭 C2M Endpoint Navigator - Quick Start"
echo "======================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Use setup.py to handle virtual environment
echo "Setting up environment..."
python3 setup.py

# Determine venv location and activate it
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "streamlit_app/.venv" ]; then
    source streamlit_app/.venv/bin/activate
else
    echo "Error: Virtual environment not found!"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Create logs directory
mkdir -p logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "Choose how to run the navigator:"
echo "1) CLI Interface"
echo "2) Web Interface (Streamlit)"
echo "3) Docker"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "Starting CLI interface..."
        python scripts/qa_recommender.py
        ;;
    2)
        echo "Starting web interface..."
        echo "Opening http://localhost:8502"
        cd streamlit_app && streamlit run app_hardcoded_v1.py --server.port 8502 --server.address localhost
        ;;
    3)
        echo "Starting with Docker..."
        docker-compose up -d
        echo "Web interface available at http://localhost:8502"
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        ;;
esac