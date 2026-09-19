"""Shared, safe logging configuration for the News Brief services."""

import logging
import os
import sys


LOGGER_NAME = "src.news_brief_workflow"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging() -> None:
    """Send application logs to the console without writing log files."""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    service_logger = logging.getLogger(LOGGER_NAME)
    service_logger.setLevel(level)
    service_logger.propagate = False

    if any(getattr(handler, "_agentsway_console", False) for handler in service_logger.handlers):
        return

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler._agentsway_console = True  # type: ignore[attr-defined]
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    service_logger.addHandler(console_handler)
