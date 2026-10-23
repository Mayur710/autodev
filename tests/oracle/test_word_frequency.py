from solution import word_frequency


def test_word_frequency_basic():
    assert word_frequency("Hello, hello world!") == {"hello": 2, "world": 1}


def test_word_frequency_case_insensitive():
    assert word_frequency("the cat and THE dog") == {
        "the": 2, "cat": 1, "and": 1, "dog": 1,
    }


def test_word_frequency_single_word():
    assert word_frequency("a") == {"a": 1}


def test_word_frequency_empty_and_punctuation_only():
    assert word_frequency("") == {}
    assert word_frequency("!!! ??? ...") == {}


def test_word_frequency_deterministic():
    text = "Dogs chase cats. Dogs run!"
    assert word_frequency(text) == word_frequency(text)
