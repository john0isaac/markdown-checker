"""
Utilities for logging config.
"""

import logging


def setup_logging(
    level: int = logging.INFO,
    format: str = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
) -> None:
    """
    Setup logging

    Args:
        level (int): The logging level
        format (str): The logging format
    """
    logging.basicConfig(level=level, format=format)
