from .main import Logger


def test_logger() -> None:
    logger = Logger()
    logger.log("5 + 3", 8)
    assert logger.get_logs() == ["5 + 3 = 8"]
