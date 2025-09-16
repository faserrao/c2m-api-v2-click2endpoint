#!/bin/bash
# Quick start script for C2M Endpoint Navigator

echo "🧭 C2M Endpoint Navigator - Quick Start"
echo "======================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

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
        echo "Opening http://localhost:8501"
        streamlit run streamlit_app/app.py
        ;;
    3)
        echo "Starting with Docker..."
        docker-compose up -d
        echo "Web interface available at http://localhost:8501"
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        ;;
esac