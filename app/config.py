# app/config.py
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Get the absolute path to the instance directory
base_dir = Path(__file__).resolve().parent.parent
instance_dir = base_dir / 'instance'
env_file = instance_dir / '.env'

logger.info(f"Looking for .env file at: {env_file}")

# Load environment variables from .env file
if env_file.exists():
    logger.info(f"Found .env file at {env_file}")
    load_dotenv(dotenv_path=env_file)
    
    # Check if API key is loaded
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    if anthropic_key:
        logger.info(f"Anthropic API key loaded successfully with length: {len(anthropic_key)}")
    else:
        logger.warning("Anthropic API key not found in environment variables after loading .env")
else:
    logger.warning(f"No .env file found at {env_file}")

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # MongoDB settings
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/compliance_auditor')
    
    # Elasticsearch settings
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')
    
    # Anthropic API settings
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
    
    # Log Anthropic API key length for debugging (don't log the actual key!)
    if ANTHROPIC_API_KEY:
        logger.info(f"Config loaded Anthropic API key with length: {len(ANTHROPIC_API_KEY)}")
    else:
        logger.warning("Config loaded with empty Anthropic API key")
    
    # Compliance settings
    DEFAULT_COMPLIANCE_TYPES = ['GDPR', 'HIPAA']