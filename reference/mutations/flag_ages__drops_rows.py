"""MUTATION — known-bad implementation. The oracle suite MUST FAIL on this.

The prompt says "remove NO rows", but this implementation filters the
frame instead of flagging it. This is the failure mode where the agent's
own self-written test once AGREED with the wrong behavior (self-grading
blind spot) — an external oracle catches it."""

import pandas as pd


def flag_ages(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[df["age"].between(0, 120)].copy()   # WRONG: removes rows
    df["age_valid"] = True
    print(f"rows={len(df)}")
    return df
