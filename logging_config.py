import logging
import logging.handlers
import os
import sys
from datetime import datetime

def is_test_environment():
    """Check if we're running in a test environment"""
    return 'unittest' in sys.modules or 'pytest' in sys.modules

class TestHandler(logging.FileHandler):
    """Custom handler for test environment that filters out expected test errors"""
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)
        self.expected_messages = {
            "File not found",
            "Error opening file",
            "Failed to remove file",
            "Attempted to set empty",
            "Invalid level",
            "Failed to add class"
        }

    def emit(self, record):
        # Only emit if it's an unexpected error
        if record.levelno >= logging.ERROR:
            for expected in self.expected_messages:
                if expected in record.getMessage():
                    return  # Skip logging for expected test errors
            super().emit(record)

def setup_logging():
    """Configure logging for the entire application"""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"toonmng_{timestamp}.log")
    
    # Test environment log file
    test_log_file = os.path.join(log_dir, "test.log")

    # Define log format
    log_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)

    # Clear any existing handlers
    root_logger.handlers.clear()

    if is_test_environment():
        # Test environment: Only log unexpected ERRORs to file, no console output
        file_handler = TestHandler(test_log_file, mode='w')
        file_handler.setFormatter(log_format)
        file_handler.setLevel(logging.ERROR)
        root_logger.addHandler(file_handler)
    else:
        # Normal environment: Full logging setup
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(log_format)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.INFO)
        
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Log startup information
        root_logger.info("Logging system initialized")
        root_logger.debug(f"Log file: {log_file}")

def get_logger(name):
    """Get a logger instance for a module"""
    return logging.getLogger(name) 