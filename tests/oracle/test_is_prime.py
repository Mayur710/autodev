import pytest
from solution import is_prime


@pytest.mark.parametrize("n,expected", [
    (2, True), (3, True), (7, True), (97, True),
    (0, False), (1, False), (-7, False),
    (4, False), (9, False), (100, False),
])
def test_is_prime(n, expected):
    assert is_prime(n) is expected


def test_large_prime():
    assert is_prime(1_000_000_007) is True


def test_large_composite():
    assert is_prime(1_000_000_007 * 3) is False
