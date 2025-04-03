import pytest

from .main import Calculator


@pytest.fixture
def calculator() -> Calculator:
    return Calculator()


def test_add(calculator: Calculator) -> None:
    assert calculator.add(2, 3) == 5


def test_subtract(calculator: Calculator) -> None:
    assert calculator.subtract(10, 4) == 6


def test_multiply(calculator: Calculator) -> None:
    assert calculator.multiply(3, 5) == 15


def test_add_2(calculator: Calculator) -> None:
    assert calculator.add(2, 5) == 9
