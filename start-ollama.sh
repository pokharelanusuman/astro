#!/bin/bash
# Start Ollama server in the background (non-blocking)

set -e

echo "🚀 Starting Ollama server..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Visit https://ollama.ai to install."
    exit 1
fi

# Check if already running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama is already running"
    exit 0
fi

# Start Ollama in background
nohup ollama serve > /tmp/ollama.log 2>&1 &
echo "Ollama started (PID: $!)"

# Wait for it to be ready
echo "⏳ Waiting for Ollama to respond..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✓ Ollama is ready at http://localhost:11434"
        break
    fi
    sleep 1
done

# Ensure mistral is available
if ! ollama list | grep -q "mistral"; then
    echo "📥 Pulling Mistral model..."
    ollama pull mistral
fi

echo "✓ Setup complete! You can now start the Flask app: python app.py"
