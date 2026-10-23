import pathlib
from solution import flag_ages

CSV = pathlib.Path(__file__).parent / "fixtures" / "sample_data.csv"


def test_flag_ages_removes_no_rows():
    """The exact case where the agent's own self-written tests once
    contradicted the prompt: the spec says FLAG, never REMOVE."""
    out = flag_ages(str(CSV))
    assert len(out) == 7


def test_flag_ages_column_is_boolean():
    out = flag_ages(str(CSV))
    assert out["age_valid"].dtype == bool


def test_flag_ages_flags_match_range():
    out = flag_ages(str(CSV))
    # fixture ages in row order: 30, 45, 30, 200, -5, 0, 120
    assert out["age_valid"].tolist() == [
        True, True, True, False, False, True, True,
    ]


def test_flag_ages_boundaries_inclusive():
    out = flag_ages(str(CSV))
    # "outside 0-120" means 0 and 120 are INSIDE the valid range
    assert out.loc[out["age"] == 0, "age_valid"].item() is True
    assert out.loc[out["age"] == 120, "age_valid"].item() is True


def test_flag_ages_prints_summary(capsys):
    flag_ages(str(CSV))
    assert capsys.readouterr().out.strip() != ""
