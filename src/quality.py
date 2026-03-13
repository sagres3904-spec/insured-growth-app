from __future__ import annotations

import pandas as pd


def compute_quality_flag(df: pd.DataFrame) -> pd.Series:
    flags = []
    for row in df.itertuples():
        row_flags = []
        if getattr(row, "insured_count", 0) < 1500:
            row_flags.append("low_count")
        if pd.notna(getattr(row, "mom_ratio", None)) and abs(row.mom_ratio) >= 0.15:
            row_flags.append("extreme_change")
        if getattr(row, "match_status", "") in {"uncertain", "manual_review"}:
            row_flags.append("match_review")
        if pd.isna(getattr(row, "insured_count", None)):
            row_flags.append("missing")
        flags.append("|".join(row_flags) if row_flags else "ok")
    return pd.Series(flags, index=df.index)
