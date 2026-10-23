"""Reference solution — human-written, used ONLY to validate the oracle tests.

FLAG, never remove — the exact spec the agent's self-written tests once
contradicted."""

import pandas as pd


def flag_ages(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["age_valid"] = (df["age"] >= 0) & (df["age"] <= 120)
    print(f"rows={len(df)}, invalid ages={int((~df['age_valid']).sum())}")
    return df
