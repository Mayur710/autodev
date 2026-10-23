import pytest
from solution import count_vowels


@pytest.mark.parametrize("s,expected", [
    ("hello", 2),
    ("HELLO", 2),
    ("banana", 3),
    ("xyz", 0),
    ("", 0),
    ("rhythm", 0),
    ("aeiouAEIOU", 10),
    ("The Quick Brown Fox", 5),
])
def test_count_vowels(s, expected):
    assert count_vowels(s) == expected
