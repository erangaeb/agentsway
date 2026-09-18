"""Shared, safe logging configuration for the News Brief services."""

import logging
import os


def configure_logging() -> None:
    """Configure application logs without including request bodies or credentials."""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level_name, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
