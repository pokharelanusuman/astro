# 🚀 Startup Guide

## Quick Start (One Command)

```bash
./start.sh
```

This starts both Ollama and the Flask app together.

---

## Development Mode (Recommended)

**Terminal 1 - Start Ollama:**
```bash
./dev.sh
# or directly:
./start-ollama.sh
```

**Terminal 2 - Start Flask App:**
```bash
python app.py
```

This gives you control over each service and makes debugging easier.

---

## Manual Control

**Start Ollama only:**
```bash
./start-ollama.sh
```

**Stop all services:**
```bash
./stop.sh
```

---

## Troubleshooting

### Ollama not starting?
- Ensure Ollama is installed: https://ollama.ai
- Check logs: `tail -f /tmp/ollama.log`

### "Connection refused" error in Flask app?
- Make sure Ollama is running in another terminal
- Test connection: `curl http://localhost:11434/api/tags`

### Mistral model not found?
- The scripts auto-pull it, but you can manually pull:
  ```bash
  ollama pull mistral
  ```

### Port already in use?
- Flask (5001) or Ollama (11434) might be in use
- Find process: `lsof -i :5001` or `lsof -i :11434`
- Kill it: `kill -9 <PID>`

---

## What Each Script Does

| Script | Purpose |
|--------|---------|
| `start.sh` | Start both Ollama & Flask (all-in-one) |
| `start-ollama.sh` | Start just Ollama server |
| `dev.sh` | Start Ollama for development |
| `stop.sh` | Stop all running services |

Choose the method that works best for your workflow!
