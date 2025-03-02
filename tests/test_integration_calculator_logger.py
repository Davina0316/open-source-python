from src.calculator.calculator import Calculator
from src.logger.logger import Logger
from unittest.mock import Mock

def test_calculator_logger():
    calculator = Calculator()
    logger = Logger()
    mock_notifier = Mock()

    result = calculator.add(4, 6)
    logger.log("4 + 6", result)
    mock_notifier.notify(result)
    
    assert logger.get_logs() == ["4 + 6 = 10"]
    mock_notifier.notify.assert_called_once_with(10)