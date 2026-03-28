"""
logger.py - 统一日志模块

Centralized logging for all modules.
"""

import logging
import sys
from pathlib import Path


# Default log format
DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str = "ai-video-editor", level: int = logging.INFO) -> logging.Logger:
    """Get or create a logger with the given name.
    
    Args:
        name: Logger name (usually module name).
        level: Logging level (default INFO).
    
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(level)
    
    return logger


def set_log_level(level: int | str) -> None:
    """Set log level for all ai-video-editor loggers.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    logger = logging.getLogger("ai-video-editor")
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


# Module-level logger for convenience
log = get_logger()