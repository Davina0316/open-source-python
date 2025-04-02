"""The `logger_component` package provides a Logger class for logging operations performed by the calculator.

It supports logging the operation
details and retrieving all the logs.

Usage:
    from logger_component import Logger

    logger = Logger()
    logger.log("3 * 4", 12)
    all_logs = logger.get_logs()
"""

from .main import Logger

__all__ = ["Logger"]
