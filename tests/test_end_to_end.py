from src.calculator_component.main import Calculator
from src.logger_component.main import Logger
from src.notifier_component.main import Notifier

def test_end_to_end():
    calculator = Calculator()
    logger = Logger()
    notifier = Notifier(threshold=10)

    result = calculator.multiply(5, 3)
    logger.log("5 * 3", result)
    notifier.notify(result)

    assert logger.get_logs() == ["5 * 3 = 15"]
    assert notifier.get_notifications() == ["Alert: Result 15 exceeds threshold 10"]
