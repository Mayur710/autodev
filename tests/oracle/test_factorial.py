import pytest
from solution import factorial


@pytest.mark.parametrize("n,expected", [
    (0, 1), (1, 1), (2, 2), (5, 120), (10, 3628800),
    (20, 2432902008176640000),
])
def test_factorial_nominal(n, expected):
    assert factorial(n) == expected


def test_factorial_negative_raises():
    with pytest.raises(ValueError):
        factorial(-1)
    with pytest.raises(ValueError):
        factorial(-100)


def test_factorial_repeatable():
    # guards against stray module-level caching
    assert [factorial(n) for n in [3, 3, 4]] == [6, 6, 24]
