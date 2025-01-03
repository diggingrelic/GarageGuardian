import logging
from config import LogConfig

# Map string levels to logging constants
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# Get log level from config
LOG_LEVEL = LOG_LEVELS.get(LogConfig.LOG_LEVEL, logging.INFO)

def setup_logging():
    # Create logger
    logger = logging.getLogger('GarageOS')
    logger.setLevel(LOG_LEVEL)
    
    # Create console handler
    console = logging.StreamHandler()
    console.setLevel(LOG_LEVEL)
    
    # Create formatter
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console)
    
    return logger

# Create global logger instance
logger = setup_logging()

# Convenience methods
def debug(msg, *args):
    logger.debug(msg, *args)

def info(msg, *args):
    logger.info(msg, *args)

def warning(msg, *args):
    logger.warning(msg, *args)

def error(msg, *args):
    logger.error(msg, *args)

def critical(msg, *args):
    logger.critical(msg, *args)

# For backward compatibility
def log(msg, *args):
    logger.info(msg, *args)