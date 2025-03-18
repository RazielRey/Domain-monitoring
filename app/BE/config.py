import os
from dotenv import load_dotenv
import logging

load_dotenv()

class Config:
    # Flask Configuration
    FLASK_HOST = os.getenv('HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('PORT', 5001))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Database Configuration - These are not directly used for DB connections
    # but might be used elsewhere in the application, so keeping for compatibility
    DB_NAME = os.getenv('DB_NAME', 'moniDB')
    DB_USER = os.getenv('DB_USER', 'myuser')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'mypassword')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    
    # Domain Check Configuration
    HTTP_TIMEOUT = float(os.getenv('HTTP_CHECK_TIMEOUT', 1.5))
    SSL_TIMEOUT = float(os.getenv('SSL_CHECK_TIMEOUT', 2.0))
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 50))
    DOMAIN_CHECK_TIMEOUT = float(os.getenv('DOMAIN_CHECK_TIMEOUT', 30.0))

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    CallbackUrl = os.getenv('GOOGLE_CALLBACK_URL', 'http://localhost:3000/auth/google/callback')

        
    # CORS Configuration
    CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

    
    # Directory settings
    JSON_DIRECTORY = 'Jsons'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'backend.log')
    
    # Scheduler
    SCHEDULER_TIMEZONE = "UTC"
    
    @staticmethod
    def ensure_directories():
        directories = ['logs', Config.JSON_DIRECTORY]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)

def setup_logger():
    Config.ensure_directories()
    
    logger = logging.getLogger('domain_monitor')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Clear any existing handlers
    logger.handlers = []
    
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