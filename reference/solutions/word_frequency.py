"""Reference solution — human-written, used ONLY to validate the oracle tests."""

import string


def word_frequency(text: str) -> dict:
    cleaned = text.translate(str.maketrans("", "", string.punctuation)).lower()
    freq = {}
    for word in cleaned.split():
        freq[word] = freq.get(word, 0) + 1
    return freq
