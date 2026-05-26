# 🔐 Environment Configuration Guide

## Overview

This project uses environment variables for configuration management. All sensitive data and configuration is stored in `.env` files, keeping your codebase clean and secure.

## Files

- **`.env.example`** - Template showing all available variables (safe to commit)
- **`.env`** - Your local configuration (⚠️ NEVER commit - contains secrets)
- **`config.py`** - Configuration loader that reads from `.env`

## 🚀 Setup

### 1. Copy the example file
```bash
cp .env.example .env
```

### 2. Edit `.env` with your values
```bash
# Development defaults (already set)
FLASK_ENV=development
DEBUG=True
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
```

### 3. For Production, generate a secure SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_hex(16))"
```

Then update `.env`:
```bash
SECRET_KEY=<generated-key-here>
FLASK_ENV=production
DEBUG=False
```

## 📋 Configuration Variables

### Flask Application
```env
FLASK_ENV=development              # development, production, testing
DEBUG=True                          # Enable debug mode
SECRET_KEY=<secure-random-string>   # Flask session secret
HOST=127.0.0.1                      # Server host
PORT=5001                           # Server port
```

### Database
```env
DATABASE_PATH=./jyotish_core.db    # SQLite database location
```

### Ollama & AI
```env
OLLAMA_HOST=localhost               # Ollama server hostname
OLLAMA_PORT=11434                   # Ollama server port
OLLAMA_MODEL=mistral                # Model to use
OLLAMA_TIMEOUT=120                  # Request timeout (seconds)
```

### API Configuration
```env
API_BASE_URL=http://127.0.0.1:5001  # API base URL
NOMINATIM_USER_AGENT=jyotish_...    # Geolocation user agent
```

### Logging
```env
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=/tmp/astro_jyotish.log     # Log file location
```

### Features
```env
ENABLE_AI_ANALYSIS=True             # Enable AI analysis
ENABLE_KNOWLEDGE_UPDATE=True        # Enable knowledge updates
CACHE_TIMEOUT=3600                  # Cache timeout (seconds)
```

## 🔄 Using Configuration in Code

### In Python files:
```python
from config import get_config

config = get_config()

# Access variables
print(config.OLLAMA_HOST)
print(config.DEBUG)
print(config.PORT)
```

### In Flask app:
```python
from config import get_config

config = get_config()
app = Flask(__name__)
app.config.from_object(config)

# Use in routes
if app.config['DEBUG']:
    print("Debug mode enabled")
```

## 🔒 Security Best Practices

### ✅ DO:
- Store all secrets in `.env`
- Use strong, random SECRET_KEY in production
- Commit `.env.example` (without secrets)
- Never commit `.env` (it's in .gitignore)
- Use environment variables for all configuration

### ❌ DON'T:
- Hardcode API keys or passwords in code
- Commit `.env` files to git
- Share `.env` files via email/chat
- Use weak SECRET_KEY values
- Store production credentials in development

## 🚀 Deployment

### Development
```bash
# Just use the local .env file
./start.sh
```

### Production on Server
```bash
# Create secure .env on server
nano .env

# Set production values
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<strong-random-key>
OLLAMA_HOST=<production-ollama-host>
```

### Docker Deployment
Pass environment variables:
```bash
docker run -e FLASK_ENV=production \
           -e SECRET_KEY=<key> \
           -e OLLAMA_HOST=ollama \
           -p 5001:5001 \
           astro-jyotish
```

### Environment Variables from Secrets
For Kubernetes or similar:
```bash
# Secrets stored in cluster, mapped to Pod environment
kubectl create secret generic astro-secrets \
  --from-literal=SECRET_KEY=<key> \
  --from-literal=OLLAMA_HOST=ollama-service
```

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"
```bash
pip install python-dotenv
```

### Variables not loading
```bash
# Check if .env file exists
ls -la .env

# Check format (no spaces around =)
cat .env | grep -E "^[A-Z_]+="
```

### Configuration not applying
```bash
# Restart Flask app
./stop.sh
./start.sh
```

### Connection refused errors
Check `.env` values match actual services:
```bash
# Test Ollama connection
curl -s http://${OLLAMA_HOST}:${OLLAMA_PORT}/api/tags

# Test Flask port
lsof -i :${PORT}
```

## 📚 Environment File Examples

### Development
```env
FLASK_ENV=development
DEBUG=True
SECRET_KEY=dev-key-insecure
HOST=127.0.0.1
PORT=5001
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
```

### Production
```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<very-long-random-secure-key>
HOST=0.0.0.0
PORT=5001
OLLAMA_HOST=ai.internal.company.com
OLLAMA_PORT=11434
LOG_LEVEL=WARNING
CACHE_TIMEOUT=86400
```

### Testing
```env
FLASK_ENV=testing
DEBUG=True
DATABASE_PATH=:memory:
ENABLE_AI_ANALYSIS=False
```

## 🔄 Rotating Secrets

### Change SECRET_KEY
```bash
# Generate new key
python -c "import secrets; print(secrets.token_hex(16))"

# Update .env
SECRET_KEY=new-key-here

# Restart app
./stop.sh && ./start.sh
```

### Update Ollama Host
```bash
# Edit .env
OLLAMA_HOST=new-ollama-server.com

# Restart app
./stop.sh && ./start.sh
```

## 📞 Support

- Check [README.md](README.md) for general info
- Check [INSTALLATION.md](INSTALLATION.md) for setup
- Check [STARTUP.md](STARTUP.md) for startup issues

---

**Keep your `.env` file secure! 🔐**
