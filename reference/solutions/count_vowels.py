"""Reference solution — human-written, used ONLY to validate the oracle tests."""

VOWELS = set("aeiou")


def count_vowels(s: str) -> int:
    return sum(1 for ch in s.lower() if ch in VOWELS)
