# 🌟 Vedic Astrology Engine (Jyotish)

A powerful local-first Vedic astrology analysis platform powered by AI and SQLite. Combines traditional Jyotish knowledge with modern LLM interpretations.

## ✨ Features

- **Vedic Birth Chart Analysis** - Calculate planetary positions using Swiss Ephemeris
- **AI-Powered Interpretations** - Get deep astrological insights via local Mistral AI
- **27 Nakshatras Database** - Complete constellation mappings and meanings
- **House System** - Full 12-house Bhava analysis with Karaka planets
- **Planetary Dignities** - Exaltation, debilitation, and Moolatrikona tracking
- **Behavioral States** - Retrograde and planetary state analysis
- **Web Interface** - Beautiful Flask-based UI for chart calculation and analysis

## 📋 Requirements

### System
- Python 3.8+
- Linux/macOS/Windows
- ~10GB disk space (for Ollama + Mistral model)
- 4GB+ RAM recommended

### Software
- Ollama (installed automatically via script)
- Python dependencies (in `requirements.txt`)

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <repo-url> astro
cd astro
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Ollama
The startup scripts will handle this, but if you want to install manually:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 4. Start Services

**Option A: All-in-one (Recommended for first time)**
```bash
./start.sh
```
This automatically starts Ollama, downloads Mistral model, and launches the Flask app.

**Option B: Separate terminals (Better for development)**

Terminal 1:
```bash
./start-ollama.sh
```

Terminal 2:
```bash
python app.py
```

### 5. Access the App
Open browser to: **http://127.0.0.1:5001**

## 📖 Usage

1. **Enter Birth Details**
   - Date, Time, Location
   - App automatically calculates timezone

2. **Calculate Chart**
   - View planetary positions
   - See house placements
   - Check planetary dignities

3. **Get AI Analysis**
   - Click "Analyze" to get AI-powered interpretations
   - Powered by local Mistral model
   - Instant results (no API latency)

## 🛠️ Startup Scripts

| Script | Purpose |
|--------|---------|
| `./start.sh` | Start Ollama + Flask (all-in-one) |
| `./start-ollama.sh` | Start just Ollama server |
| `./dev.sh` | Start Ollama for development |
| `./stop.sh` | Stop all services |

## 🗄️ Project Structure

```
astro/
├── app.py                 # Flask application
├── ai_engine.py          # AI analysis engine
├── ai_interpreter.py     # Ollama integration
├── engine.py             # Astrological calculations
├── db.py                 # Database queries
├── knowledge_manager.py   # AI knowledge persistence
├── init_db.py            # Database initialization
├── seed_jyotish_data.py  # Load Vedic knowledge
├── jyotish_core.db       # SQLite database (created on first run)
├── requirements.txt      # Python dependencies
├── STARTUP.md            # Detailed startup guide
├── templates/            # HTML templates
├── api/                  # API endpoints
└── *.sh                  # Startup scripts
```

## 🗄️ Database Schema

### Tables
- **house_rules** - 12 Bhava (houses) with significations and Karaka planets
- **planetary_dignities** - Exaltation/debilitation/Moolatrikona positions
- **nakshatra_rules** - 27 Nakshatras with degree spans and rulers
- **behavioral_rules** - Retrograde and special states

Auto-populated on first run via `init_db.py` and `seed_jyotish_data.py`

## 🔧 Troubleshooting

### Ollama Connection Error
```
Error: HTTPConnectionPool(host='localhost', port=11434)
```
**Solution:** Ensure Ollama is running:
```bash
./start-ollama.sh
```

### Port Already in Use
```bash
# Find process using port 5001
lsof -i :5001

# Kill it
kill -9 <PID>
```

### Mistral Model Not Found
```bash
# Manually pull the model
ollama pull mistral
```

### Database Errors
```bash
# Reinitialize database
rm -f jyotish_core.db
python init_db.py
python seed_jyotish_data.py
```

### ImportError: No module named 'flask'
```bash
pip install -r requirements.txt
```

## 📚 Key Technologies

- **Flask** - Web framework
- **SQLite** - Database
- **Swiss Ephemeris (pyswisseph)** - Astronomical calculations
- **Ollama + Mistral** - Local AI model
- **Geopy + Timezonefinder** - Location & timezone handling

## 🤖 AI Integration

The app uses **Mistral** running locally via **Ollama**:
- No cloud dependency
- Private astrological interpretations
- Fast responses (local processing)
- Free & unlimited usage

### First Run Setup
- Ollama: ~500MB
- Mistral Model: ~4.4GB
- Total download: ~5GB (one-time)

## 🔄 Workflow

1. **User enters birth data** → Flask validates input
2. **Chart calculation** → Swiss Ephemeris computes positions
3. **Database query** → Fetch house/planet interactions from SQLite
4. **AI Analysis** → Send to local Mistral model
5. **Display results** → Return formatted interpretation to UI

## 📝 Development

### Add New Features
1. Update database schema in `seed_jyotish_data.py`
2. Add calculations in `engine.py`
3. Create new endpoints in `app.py`
4. Build UI in `templates/`

### Run in Debug Mode
```bash
export FLASK_ENV=development
python app.py
```

## 📄 License

[Add your license here]

## 🙏 Credits

Built with:
- Swiss Ephemeris for astronomical accuracy
- Vedic astrology principles
- Modern AI for interpretation
- Flask for the web interface

## 📞 Support

For issues:
1. Check [STARTUP.md](STARTUP.md) for common solutions
2. Review logs: `tail -f /tmp/ollama.log`
3. Restart services: `./stop.sh` then `./start.sh`

---

**Happy Astrological Analysis! 🌙✨**
