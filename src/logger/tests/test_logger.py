import pytest
from src.logger.logger import Logger

def test_logger():
    logger = Logger()
    logger.log("5 + 3", 8)
    assert logger.get_logs() == ["5 + 3 = 8"]