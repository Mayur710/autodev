import pytest
from solution import is_valid_email


@pytest.mark.parametrize("s", [
    "abc@example.com",
    "user@domain.co.uk",   # more than one dot after @ is fine
    "a@b.io",
    "x1@y2.z3",
])
def test_valid_emails(s):
    assert is_valid_email(s) is True


@pytest.mark.parametrize("s", [
    "",                      # no @ at all
    "abcexample.com",        # no @
    "abc@@example.com",      # two @
    "ab@c@example.com",      # two @
    "abc example@mail.com",  # space inside
    "abc@example.com ",      # trailing space
    "abc@example",           # no dot after @
])
def test_invalid_emails(s):
    assert is_valid_email(s) is False
