"""
Vedic Astrology Engine - Main Application
A professional astrological analysis platform combining Vedic principles with AI
"""

import os
import sys
import signal
import psutil
import warnings
import logging
from flask import Flask

# Import configuration
from config import get_config

# Import blueprints
from blueprints.api import api_bp
from blueprints.web import web_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
config = get_config()

# Create Flask app
app = Flask(__name__)
app.config.from_object(config)

# Register blueprints
app.register_blueprint(api_bp)
app.register_blueprint(web_bp)


# ==============================================================================
# Graceful Shutdown Handler
# ==============================================================================
def graceful_shutdown_handler(signum, frame):
    """Clean shutdown handler for process management"""
    warnings.filterwarnings("ignore", category=UserWarning, module="multiprocessing.resource_tracker")
    try:
        current_pid = os.getpid()
        parent = psutil.Process(current_pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                if "resource_tracker" in child.name():
                    continue
                child.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        psutil.wait_procs(children, timeout=0.1)
    except Exception:
        pass

    try:
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            os.killpg(os.getpgrp(), signal.SIGTERM)
    except Exception:
        pass
    sys.exit(0)


signal.signal(signal.SIGINT, graceful_shutdown_handler)
signal.signal(signal.SIGTERM, graceful_shutdown_handler)


# ==============================================================================
# Error Handlers
# ==============================================================================
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    from utils import APIResponse
    return APIResponse.not_found("Resource not found")


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    from utils import APIResponse
    logger.error(f"Internal server error: {error}")
    return APIResponse.server_error()


# ==============================================================================
# Application Entry Point
# ==============================================================================
if __name__ == '__main__':
    logger.info(f"Starting Vedic Astrology Engine in {config.FLASK_ENV} mode")
    logger.info(f"Server: {config.HOST}:{config.PORT}")
    logger.info(f"Ollama: {config.OLLAMA_URL}")
    logger.info(f"Database: {config.DATABASE_PATH}")
    
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT,
        use_reloader=False
    )
