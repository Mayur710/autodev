from solution import dedupe_chars


def test_dedupe_basic():
    assert dedupe_chars("abcabc") == "abc"


def test_dedupe_keeps_first_occurrence():
    assert dedupe_chars("cbacba") == "cba"


def test_dedupe_all_same_and_empty():
    assert dedupe_chars("aaaa") == "a"
    assert dedupe_chars("") == ""


def test_dedupe_preserves_order_and_spaces():
    assert dedupe_chars("aabbccd") == "abcd"
    assert dedupe_chars("a a") == "a "


def test_dedupe_output_is_subsequence():
    s = "stress test input"
    out = dedupe_chars(s)
    it = iter(s)
    assert all(ch in it for ch in out)  # out appears in s in order
