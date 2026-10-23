import pytest
from solution import fibonacci


@pytest.mark.parametrize("n,expected", [
    (0, 0), (1, 1), (2, 1), (3, 2), (10, 55), (30, 832040),
])
def test_fibonacci_nominal(n, expected):
    assert fibonacci(n) == expected


def test_fibonacci_is_memoized():
    # naive recursion is infeasible at n=100 — this doubles as a
    # memoization check, not just a value check
    assert fibonacci(100) == 354224848179261915075


def test_fibonacci_repeated_calls_are_consistent():
    assert [fibonacci(n) for n in [10, 10, 15]] == [55, 55, 610]
