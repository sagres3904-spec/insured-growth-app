from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_raw_monthly_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path, dtype={"code": str})
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m").dt.strftime("%Y-%m")
    return df


def load_monthly_data(path: Path) -> pd.DataFrame:
    df = load_raw_monthly_data(path)
    if "quality_flag" not in df.columns:
        raise ValueError("quality_flag 列がありません。scripts/build_metrics.py を先に実行してください。")
    return df
