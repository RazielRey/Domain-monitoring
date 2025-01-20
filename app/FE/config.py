import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

class Config:
    # Google OAuth configs only needed in frontend
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    CallbackUrl = os.getenv('CallbackUrl')

def setup_logger():
    """Setup logger with daily files"""
    # Create logs directory
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create logger
    logger = logging.getLogger('frontend_service')  # Changed from 'domain_monitor'
    # Rest of your logger setup remains the same
    ...

# Create logger instance
logger = setup_logger()