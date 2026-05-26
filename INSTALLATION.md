# Local Installation & Deployment Guide

## Complete Setup for a Fresh System

### Step 1: System Prerequisites
```bash
# Update package manager
sudo apt update && sudo apt upgrade -y  # For Linux

# Install Python (if not present)
sudo apt install python3 python3-pip -y  # Linux
brew install python3  # macOS

# Verify Python version
python3 --version  # Should be 3.8+
```

### Step 2: Clone Repository
```bash
git clone <repository-url> astro
cd astro
```

### Step 3: Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 4: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Install Ollama
```bash
# Automatic (via script)
./start-ollama.sh

# OR Manual installation
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 6: Initialize Database
```bash
# This happens automatically on first run, but you can manually trigger:
python init_db.py
python seed_jyotish_data.py
```

### Step 7: Run Application

**For Production/Quick Start:**
```bash
./start.sh
```

**For Development:**
```bash
# Terminal 1
./start-ollama.sh

# Terminal 2
python app.py
```

## Automated Deployment

### Docker Setup (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Expose ports
EXPOSE 5001 11434

# Run startup script
CMD ["./start.sh"]
```

Build and run:
```bash
docker build -t astro-jyotish .
docker run -p 5001:5001 -p 11434:11434 astro-jyotish
```

### Systemd Service (Linux - Optional)

Create `/etc/systemd/system/astro-jyotish.service`:
```ini
[Unit]
Description=Vedic Astrology Engine
After=network.target

[Service]
Type=simple
User=<your-username>
WorkingDirectory=/path/to/astro
ExecStart=/path/to/astro/start.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable astro-jyotish
sudo systemctl start astro-jyotish
```

Check status:
```bash
sudo systemctl status astro-jyotish
```

## Verification Checklist

After installation, verify:

```bash
# 1. Python dependencies
python -c "import flask; import swisseph; print('✓ Dependencies OK')"

# 2. Database exists
ls -la jyotish_core.db

# 3. Ollama is installed
which ollama

# 4. Ollama is running
curl -s http://localhost:11434/api/tags | head -20

# 5. Mistral model is available
ollama list | grep mistral

# 6. Flask app starts
timeout 3 python app.py || echo "✓ App starts correctly"
```

## Deployment Environments

### Development
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Production
```bash
export FLASK_ENV=production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Testing
```bash
pip install pytest
pytest tests/
```

## Environment Variables (Optional)

Create `.env` file:
```bash
FLASK_ENV=production
FLASK_SECRET_KEY=your-secret-key
OLLAMA_HOST=localhost:11434
OLLAMA_MODEL=mistral
DATABASE_PATH=./jyotish_core.db
```

## Troubleshooting Deployment

### Issue: "Command not found: ollama"
```bash
# Reinstall or add to PATH
export PATH=$PATH:/usr/local/bin
ollama --version
```

### Issue: Port 5001 already in use
```bash
# Find and kill process
lsof -i :5001
kill -9 <PID>

# Or use different port
python app.py --port 5002
```

### Issue: Insufficient disk space
```bash
# Check space
df -h

# Clean up Ollama cache (if needed)
rm -rf ~/.ollama/models
```

### Issue: Out of memory
```bash
# Reduce Mistral model size or use smaller model
ollama pull mistral:7b-q4_0  # Quantized version
```

## Maintenance

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Update Mistral Model
```bash
ollama pull mistral
```

### Backup Database
```bash
cp jyotish_core.db jyotish_core.db.backup
```

### Reset Everything
```bash
./stop.sh
rm -f jyotish_core.db
python init_db.py
python seed_jyotish_data.py
./start-ollama.sh
```

## Next Steps

1. **Access the application**: http://localhost:5001
2. **Enter birth chart data** and calculate
3. **Get AI-powered analysis** from local Mistral
4. **Check logs**: `tail -f /tmp/ollama.log`

---

**Questions?** Check [README.md](README.md) and [STARTUP.md](STARTUP.md)
