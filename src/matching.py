from __future__ import annotations

import pandas as pd


def normalize_company_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    return (
        name.replace("株式会社", "")
        .replace("ホールディングス", "HD")
        .replace("　", " ")
        .strip()
        .lower()
    )


def merge_manual_matches(raw_df: pd.DataFrame, match_df: pd.DataFrame) -> pd.DataFrame:
    prepared = match_df.copy()
    prepared["source_company_name_normalized"] = prepared["source_company_name"].map(normalize_company_name)

    result = raw_df.copy()
    result["source_company_name_normalized"] = result["company_name"].map(normalize_company_name)
    result = result.merge(
        prepared[["source_company_name_normalized", "code", "match_status", "notes"]],
        on="source_company_name_normalized",
        how="left",
        suffixes=("", "_manual"),
    )
    result["match_status"] = result["match_status_manual"].fillna(result.get("match_status"))
    result["notes"] = result["notes_manual"].fillna(result.get("notes"))
    return result.drop(
        columns=[
            "source_company_name_normalized",
            "match_status_manual",
            "notes_manual",
        ],
        errors="ignore",
    )
