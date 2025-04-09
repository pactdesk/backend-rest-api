import sys
from pathlib import Path

from loguru import logger


def setup_logging(log_level="INFO", log_file=None):
    """
    Configure loguru with the specified settings.
    
    Args:
        log_level: The minimum log level to display (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to a log file. If None, logs will only go to stderr.
    """
    # Remove default handler
    logger.remove()
    
    # Add stderr handler with the specified log level
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )
    
    # Add file handler if log_file is specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation="10 MB",
            retention="1 week",
        )
    
    logger.info(f"Logging configured with level {log_level}")
    if log_file:
        logger.info(f"Log file: {log_file}") 