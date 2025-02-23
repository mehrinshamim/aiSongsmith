import logging
from pathlib import Path

def setup_logger(name: str, log_dir: Path):
    """Set up logger for training/inference"""
    logger = logging.getLogger(name)
    # Configure logger
    return logger