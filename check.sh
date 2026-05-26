#!/bin/bash
# Health check script for Astro Jyotish application

echo "🔍 Astro Jyotish - System Health Check"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

checks_passed=0
checks_failed=0

# Helper functions
check_command() {
    local cmd=$1
    local name=$2
    
    if command -v $cmd &> /dev/null; then
        echo -e "${GREEN}✓${NC} $name is installed"
        ((checks_passed++))
    else
        echo -e "${RED}✗${NC} $name is NOT installed"
        ((checks_failed++))
    fi
}

check_file() {
    local file=$1
    local name=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $name exists"
        ((checks_passed++))
    else
        echo -e "${RED}✗${NC} $name is MISSING"
        ((checks_failed++))
    fi
}

check_port() {
    local port=$1
    local name=$2
    
    if curl -s http://localhost:$port/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name is responding on port $port"
        ((checks_passed++))
    else
        echo -e "${YELLOW}⚠${NC} $name is not responding on port $port"
        ((checks_failed++))
    fi
}

check_python_module() {
    local module=$1
    local name=$2
    
    if python3 -c "import $module" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python module '$name' is installed"
        ((checks_passed++))
    else
        echo -e "${RED}✗${NC} Python module '$name' is MISSING"
        ((checks_failed++))
    fi
}

# System checks
echo "📋 System Requirements:"
check_command python3 "Python 3"
check_command pip "pip"
check_command git "Git"
echo ""

# Python modules
echo "🐍 Python Dependencies:"
check_python_module flask "Flask"
check_python_module swisseph "Swiss Ephemeris"
check_python_module timezonefinder "Timezonefinder"
check_python_module geopy "Geopy"
check_python_module ollama "Ollama"
check_python_module requests "Requests"
echo ""

# Project files
echo "📁 Project Files:"
check_file "requirements.txt" "requirements.txt"
check_file "README.md" "README.md"
check_file "INSTALLATION.md" "INSTALLATION.md"
check_file "STARTUP.md" "STARTUP.md"
check_file "app.py" "app.py"
check_file "init_db.py" "init_db.py"
check_file "seed_jyotish_data.py" "seed_jyotish_data.py"
echo ""

# Startup scripts
echo "🚀 Startup Scripts:"
for script in start.sh start-ollama.sh dev.sh stop.sh; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        echo -e "${GREEN}✓${NC} $script (executable)"
        ((checks_passed++))
    else
        echo -e "${RED}✗${NC} $script (missing or not executable)"
        ((checks_failed++))
    fi
done
echo ""

# Database
echo "🗄️ Database:"
if [ -f "jyotish_core.db" ]; then
    echo -e "${GREEN}✓${NC} Database exists"
    size=$(du -h jyotish_core.db | cut -f1)
    echo "  Size: $size"
    ((checks_passed++))
else
    echo -e "${YELLOW}⚠${NC} Database not initialized (will be created on first run)"
fi
echo ""

# Ollama check (only if running)
echo "🤖 Ollama & AI:"
check_command ollama "Ollama"
check_port 11434 "Ollama API"
echo ""

# Flask app check
echo "🌐 Flask Application:"
if timeout 2 python3 -c "from app import app; print('✓')" 2>/dev/null | grep -q "✓"; then
    echo -e "${GREEN}✓${NC} Flask app imports successfully"
    ((checks_passed++))
else
    echo -e "${RED}✗${NC} Flask app has import errors"
    ((checks_failed++))
fi
echo ""

# Summary
echo "======================================"
echo "Results:"
echo -e "${GREEN}Passed: $checks_passed${NC}"
echo -e "${RED}Failed: $checks_failed${NC}"
echo ""

if [ $checks_failed -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! You're ready to run the application.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start Ollama: ./start-ollama.sh"
    echo "2. In another terminal, run: python app.py"
    echo "3. Open: http://localhost:5001"
    exit 0
else
    echo -e "${YELLOW}⚠ Some checks failed. Please review the issues above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "1. Install dependencies: pip install -r requirements.txt"
    echo "2. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "3. Initialize database: python init_db.py && python seed_jyotish_data.py"
    exit 1
fi
