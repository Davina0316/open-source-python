from .main import Logger
import pytest

def test_logger():
    logger = Logger()
    logger.log("5 + 3", 8)
    assert logger.get_logs() == ["5 + 3 = 8"]
