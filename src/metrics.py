from __future__ import annotations

import pandas as pd

from src.quality import compute_quality_flag


OUTPUT_COLUMNS = [
    "code",
    "company_name",
    "month",
    "insured_count",
    "mom_delta",
    "mom_ratio",
    "delta_3m",
    "accel_1m",
    "up_streak",
    "market",
    "sector17",
    "sector33",
    "theme",
    "source",
    "quality_flag",
    "match_status",
    "notes",
]


def _compute_up_streak(series: pd.Series) -> pd.Series:
    streak = []
    current = 0
    for value in series.fillna(0):
        if value > 0:
            current += 1
        else:
            current = 0
        streak.append(current)
    return pd.Series(streak, index=series.index)


def prepare_monthly_metrics(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["month"] = pd.to_datetime(data["month"], format="%Y-%m")
    data = data.sort_values(["code", "month"]).reset_index(drop=True)

    grouped = data.groupby("code", group_keys=False)["insured_count"]
    data["mom_delta"] = grouped.diff()
    prev = grouped.shift(1)
    data["mom_ratio"] = (data["mom_delta"] / prev).round(4)
    data["delta_3m"] = grouped.diff(3)
    data["accel_1m"] = data.groupby("code", group_keys=False)["mom_delta"].diff()
    data["up_streak"] = data.groupby("code", group_keys=False)["mom_delta"].apply(_compute_up_streak)
    data["quality_flag"] = compute_quality_flag(data)
    data["month"] = data["month"].dt.strftime("%Y-%m")

    return data[OUTPUT_COLUMNS]


def summarize_dashboard(df: pd.DataFrame) -> dict[str, object]:
    latest_month = df["month"].max()
    latest_df = df[df["month"] == latest_month].copy()
    seg = summarize_segments(df, "market")
    average_rate = seg["observation_rate"].mean() if not seg.empty else 0.0
    return {
        "latest_month": latest_month,
        "observed_companies": latest_df["code"].nunique(),
        "audit_count": (latest_df["quality_flag"] != "ok").sum(),
        "average_observation_rate": average_rate,
    }


def build_rankings(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    latest_month = df["month"].max()
    latest_df = df[df["month"] == latest_month].copy()
    columns = ["code", "company_name", "insured_count", "mom_delta", "mom_ratio", "delta_3m", "accel_1m", "up_streak", "quality_flag"]

    return {
        "前月比増加人数ランキング": latest_df.sort_values("mom_delta", ascending=False)[columns].head(10),
        "前月比増加率ランキング": latest_df.sort_values("mom_ratio", ascending=False)[columns].head(10),
        "3か月純増ランキング": latest_df.sort_values("delta_3m", ascending=False)[columns].head(10),
        "加速度ランキング": latest_df.sort_values("accel_1m", ascending=False)[columns].head(10),
        "連続増加月数ランキング": latest_df.sort_values("up_streak", ascending=False)[columns].head(10),
    }


def summarize_segments(df: pd.DataFrame, segment_col: str) -> pd.DataFrame:
    latest_month = df["month"].max()
    latest_df = df[df["month"] == latest_month].copy()
    grouped = latest_df.groupby(segment_col, dropna=False)

    seg_df = grouped.agg(
        observed_companies=("code", "nunique"),
        total_net_increase=("mom_delta", "sum"),
        median_growth_ratio=("mom_ratio", "median"),
    ).reset_index()

    denominators = df[["code", segment_col]].drop_duplicates().groupby(segment_col, dropna=False)["code"].nunique().reset_index(name="universe")
    seg_df = seg_df.merge(denominators, on=segment_col, how="left")
    seg_df["observation_rate"] = (seg_df["observed_companies"] / seg_df["universe"]).fillna(0)
    return seg_df[[segment_col, "observed_companies", "universe", "observation_rate", "total_net_increase", "median_growth_ratio"]]


def build_audit_queue(df: pd.DataFrame) -> pd.DataFrame:
    latest_month = df["month"].max()
    audit_df = df[df["month"] == latest_month].copy()
    audit_df["audit_reason"] = audit_df["quality_flag"]
    return audit_df[audit_df["quality_flag"] != "ok"][
        ["code", "company_name", "month", "insured_count", "match_status", "quality_flag", "source", "notes", "audit_reason"]
    ].sort_values(["quality_flag", "company_name"])
