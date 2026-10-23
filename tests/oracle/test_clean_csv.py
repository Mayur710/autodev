import pathlib
import pandas as pd
from solution import clean_csv

CSV = pathlib.Path(__file__).parent / "fixtures" / "sample_data.csv"


def test_clean_csv_removes_duplicate_rows():
    out = clean_csv(str(CSV))
    assert len(out) == 6          # 7 rows - 1 exact duplicate


def test_clean_csv_bad_salaries_are_nan():
    out = clean_csv(str(CSV))
    # "abc" and the empty cell are the invalid entries
    assert out["salary"].isna().sum() == 2


def test_clean_csv_salary_is_numeric():
    out = clean_csv(str(CSV))
    assert pd.api.types.is_numeric_dtype(out["salary"])


def test_clean_csv_valid_salaries_preserved():
    out = clean_csv(str(CSV))
    assert out.loc[out["name"] == "Dave", "salary"].item() == 70000
    assert out.loc[out["name"] == "Alice", "salary"].item() == 50000


def test_clean_csv_cow_trap():
    """The pandas copy-on-write bug this project is about: an inplace
    fillna on a column selection silently does nothing under CoW, the run
    exits cleanly, and the data is unchanged. Only an assertion on the
    actual data state catches it."""
    out = clean_csv(str(CSV))
    assert out.loc[out["name"] == "Bob", "salary"].isna().all()
    assert out.loc[out["name"] == "Carol", "salary"].isna().all()


def test_clean_csv_prints_summary(capsys):
    clean_csv(str(CSV))
    assert capsys.readouterr().out.strip() != ""
