#!/bin/bash
# Development mode: Start Ollama in one terminal, Flask in another

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Ollama...${NC}"
./start-ollama.sh

echo ""
echo -e "${GREEN}✓ Ollama is running${NC}"
echo -e "${BLUE}Now run in another terminal: python app.py${NC}"
echo ""
echo "To stop Ollama, run: ./stop.sh"
