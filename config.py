import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask Settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    PORT = int(os.getenv('PORT', 5001))
    HOST = os.getenv('HOST', '127.0.0.1')
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', './jyotish_core.db')
    DATABASE_URL = f'sqlite:///{DATABASE_PATH}'
    
    # Ollama AI Configuration
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
    OLLAMA_PORT = int(os.getenv('OLLAMA_PORT', 11434))
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
    OLLAMA_URL = f'http://{OLLAMA_HOST}:{OLLAMA_PORT}'
    OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', 120))
    
    # API Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:5001')
    
    # Geolocation
    NOMINATIM_USER_AGENT = os.getenv('NOMINATIM_USER_AGENT', 'jyotish_engine_core_v2')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/tmp/astro_jyotish.log')
    
    # Feature Flags
    ENABLE_AI_ANALYSIS = os.getenv('ENABLE_AI_ANALYSIS', 'True').lower() == 'true'
    ENABLE_KNOWLEDGE_UPDATE = os.getenv('ENABLE_KNOWLEDGE_UPDATE', 'True').lower() == 'true'
    
    # Astrology Calculation Settings
    ZODIAC_MODE = os.getenv('ZODIAC_MODE', 'tropical').lower()  # 'tropical' or 'sidereal'
    if ZODIAC_MODE not in ('tropical', 'sidereal'):
        raise ValueError(f"ZODIAC_MODE must be 'tropical' or 'sidereal', got '{ZODIAC_MODE}'")
    
    # Cache Settings
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 3600))


class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_ENV = 'development'
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY', None)  # Must be set in production
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production!")


class TestingConfig(Config):
    """Testing configuration"""
    FLASK_ENV = 'testing'
    DEBUG = True
    DATABASE_PATH = ':memory:'


def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
