"""Reference solution — human-written, used ONLY to validate the oracle tests.

Uses .copy() + assignment (NOT inplace chained assignment) so it survives
pandas copy-on-write — the exact trap this project documented."""

import pandas as pd


def clean_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.drop_duplicates().copy()
    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")
    print(f"rows={len(df)}, missing salaries={df['salary'].isna().sum()}")
    return df
