import os
from dotenv import load_dotenv
import logging

load_dotenv()

class Config:
    # Server settings
    HOST = '0.0.0.0'
    PORT = int(os.getenv('PORT', 5001))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Domain checking
    SSL_CHECK_TIMEOUT = int(os.getenv('SSL_CHECK_TIMEOUT', 2))
    HTTP_CHECK_TIMEOUT = float(os.getenv('HTTP_CHECK_TIMEOUT', 1.5))
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 500))
    DOMAIN_CHECK_TIMEOUT = int(os.getenv('DOMAIN_CHECK_TIMEOUT', 30))
    
    # Directory settings
    JSON_DIRECTORY = 'Jsons'
    
    # Logging
    LOG_FILE = os.getenv('LOG_FILE', 'backend.log')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
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
    
    logger = logging.getLogger('backend_service')
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