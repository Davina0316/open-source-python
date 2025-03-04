from src.calculator.calculator import Calculator

@pytest.fixture
def calculator():
    return Calculator()

def test_add(calculator):
    assert calculator.add(2, 3) == 5

def test_subtract(calculator):
    assert calculator.subtract(10, 4) == 6

def test_multiply(calculator):
    assert calculator.multiply(3, 5) == 15