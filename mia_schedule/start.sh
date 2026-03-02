#!/usr/bin/env bash

# MIA Schedule App - Start Script

echo "🚀 Starting MIA Schedule App..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "Starting Flask server..."
python app.py

