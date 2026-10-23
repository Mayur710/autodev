import pytest
from solution import is_palindrome


@pytest.mark.parametrize("s", [
    "A man a plan a canal Panama",
    "race car",
    "Was it a car or a cat I saw",
    "Abba",
    "level",
    "",
    " ",
])
def test_palindrome_true_cases(s):
    assert is_palindrome(s) is True


@pytest.mark.parametrize("s", ["hello", "abc", "Aab", "ab cba d"])
def test_palindrome_false_cases(s):
    assert is_palindrome(s) is False


def test_palindrome_ignores_spaces_only():
    # spec says ignore case AND spaces — nothing else
    assert is_palindrome("ab a") is True
