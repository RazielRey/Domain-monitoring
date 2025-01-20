import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

class Config:
    # Define backend-specific configuration variables
    LOG_FILE = os.getenv("LOG_FILE", "backend.log")

def setup_logger():
    """Setup logger with daily files"""
    # Create logs directory
    if not os.path.exists('logs'):
        os.makedirs('logs')

     # Configure the logger
    logger = logging.getLogger('backend_service')
    logger.setLevel(logging.INFO)

    # Create a file handler
    log_filename = f'logs/{Config.LOG_FILE}'
    handler = logging.FileHandler(log_filename)
    handler.setLevel(logging.INFO)

    # Define the logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger

# Create logger instance
logger = setup_logger()