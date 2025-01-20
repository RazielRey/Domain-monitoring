import logging
import os
from datetime import datetime

def setup_test_logger():
    """Setup logger for tests"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('test_logs'):
        os.makedirs('test_logs')

    # Create logger
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Create file handler
    current_date = datetime.now().strftime("%Y%m%d")
    file_handler = logging.FileHandler(f'test_logs/test_{current_date}.log')
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create logger instance
test_logger = setup_test_logger()