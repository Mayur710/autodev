import pytest
from solution import lcs


@pytest.mark.parametrize("s1,s2,expected", [
    ("abc", "abc", 3),
    ("abc", "def", 0),
    ("AGGTAB", "GXTXAYB", 4),   # classic: "GTAB"
    ("longest", "lo", 2),
    ("", "abc", 0),
    ("abc", "", 0),
    ("ABC", "abc", 0),          # case-sensitive
])
def test_lcs_nominal(s1, s2, expected):
    assert lcs(s1, s2) == expected


def test_lcs_symmetry():
    for a, b in [("abcde", "ace"), ("AGGTAB", "GXTXAYB"), ("xyz", "xyz")]:
        assert lcs(a, b) == lcs(b, a)


def test_lcs_against_itself():
    for s in ["", "a", "abcdef"]:
        assert lcs(s, s) == len(s)
