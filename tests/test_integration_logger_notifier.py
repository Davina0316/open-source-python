from src.logger.logger import Logger
from src.notifier.notifier import Notifier
from unittest.mock import Mock

def test_logger_notifier():
    logger = Logger()
    notifier = Notifier(threshold=10)
    mock_calculator = Mock()

    logger.log("5 * 3", 15)
    notifier.notify(15)

    assert logger.get_logs() == ["5 * 3 = 15"]
    assert notifier.get_notifications() == ["Alert: Result 15 exceeds threshold 10"]