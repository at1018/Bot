#!/bin/bash

# Chatbot API Startup Script

echo "🤖 Starting Chatbot API..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found! Creating from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your OpenAI API key"
    echo ""
fi

# Start the application
echo ""
echo "🚀 Starting FastAPI server..."
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/api/health"
echo ""

python main.py
