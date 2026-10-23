"""Reference solution — human-written, used ONLY to validate the oracle tests."""


def is_palindrome(s: str) -> bool:
    cleaned = s.replace(" ", "").lower()
    return cleaned == cleaned[::-1]
