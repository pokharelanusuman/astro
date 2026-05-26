#!/bin/bash
# Astro App + Ollama Startup Script

set -e

echo "🚀 Starting Vedic Astrology Engine..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama is not installed. Visit https://ollama.ai to install.${NC}"
    exit 1
fi

# Start Ollama in the background
echo -e "${BLUE}📡 Starting Ollama server...${NC}"
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!
echo "   Ollama PID: $OLLAMA_PID"

# Wait for Ollama to be ready
echo -e "${BLUE}⏳ Waiting for Ollama to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠️  Ollama took too long to start. Check /tmp/ollama.log${NC}"
    fi
    sleep 1
done

# Ensure mistral model is available
echo -e "${BLUE}🤖 Checking Mistral model...${NC}"
if ! ollama list | grep -q "mistral"; then
    echo -e "${YELLOW}📥 Pulling Mistral model (first time, this may take a few minutes)...${NC}"
    ollama pull mistral
fi
echo -e "${GREEN}✓ Mistral model ready${NC}"
echo ""

# Start Flask app
echo -e "${BLUE}🌐 Starting Flask application...${NC}"
python app.py

# Cleanup on exit
trap "kill $OLLAMA_PID" EXIT
