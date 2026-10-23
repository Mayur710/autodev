"""MUTATION — known-bad implementation. The oracle suite MUST FAIL on this.

This is the exact pandas copy-on-write bug from the project writeup:
`df["salary"].fillna(...)` on a column selection is chained assignment and
silently does nothing under copy-on-write — the script runs, exits 0, prints
a summary, and the data is unchanged. Only data-state assertions catch it."""

import pandas as pd


def clean_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path).drop_duplicates()
    df["salary"].fillna(0, inplace=True)   # silent no-op under CoW
    print("done")
    return df
