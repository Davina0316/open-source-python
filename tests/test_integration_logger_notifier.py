from src.logger_component import Logger
from src.notifier_component import Notifier


def test_logger_notifier() -> None:
    logger = Logger()
    notifier = Notifier(threshold=10)

    logger.log("5 * 3", 15)
    notifier.notify(15)

    assert logger.get_logs() == ["5 * 3 = 15"]
    assert notifier.get_notifications() == ["Alert: Result 15 exceeds threshold 10"]
