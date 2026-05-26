#!/bin/bash
# Stop Ollama and Flask services

echo "🛑 Stopping services..."

# Kill Ollama
pkill -f "ollama serve" || true
echo "✓ Ollama stopped"

# Kill Flask
pkill -f "python app.py" || true
echo "✓ Flask app stopped"

echo "All services stopped"
