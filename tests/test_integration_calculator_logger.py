from src.calculator import Calculator
from src.logger import Logger
from unittest.mock import Mock

def test_calculator_logger():
    calculator = Calculator()
    logger = Logger()
    mock_notifier = Mock()

    result = calculator.add(4, 6)
    logger.log("4 + 6", result)
    
    assert logger.get_logs() == ["4 + 6 = 10"]