from solution import reverse_string


def test_reverse_basic():
    assert reverse_string("abc") == "cba"


def test_reverse_empty_and_single():
    assert reverse_string("") == ""
    assert reverse_string("a") == "a"


def test_reverse_preserves_case():
    # reversal moves characters, it does not change their case
    assert reverse_string("AbC") == "CbA"


def test_reverse_unicode():
    assert reverse_string("abcé") == "écba"


def test_reverse_is_involution():
    # reverse(reverse(s)) == s for every input
    for s in ["level", "A man a plan", "xyz123", ""]:
        assert reverse_string(reverse_string(s)) == s
