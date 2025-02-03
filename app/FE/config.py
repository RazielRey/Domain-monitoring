import os
from dotenv import load_dotenv
import logging

load_dotenv()

class Config:
    # Server settings
    HOST = '0.0.0.0'
    PORT = int(os.getenv('PORT', 8080))
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5001')
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    SESSION_PERMANENT = True
    SESSION_TYPE = "filesystem"
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    CallbackUrl = os.getenv('CallbackUrl')
    
    # Logging
    LOG_FILE = os.getenv('LOG_FILE', 'frontend.log')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

def setup_logger():
    logger = logging.getLogger('frontend_service')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Handlers
    file_handler = logging.FileHandler(f'logs/{Config.LOG_FILE}')
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()