from pathlib import Path

import pandas as pd
import streamlit as st

from src.loaders import load_monthly_data, load_raw_monthly_data
from src.metrics import (
    build_audit_queue,
    build_rankings,
    prepare_monthly_metrics,
    summarize_dashboard,
    summarize_segments,
)


st.set_page_config(page_title="Insured Growth App", layout="wide")

DATA_PATH = Path("data/monthly_insured.csv")
SAMPLE_PATH = Path("data/monthly_insured_sample.csv")


@st.cache_data
def get_data() -> pd.DataFrame:
    if DATA_PATH.exists():
        return load_monthly_data(DATA_PATH)
    return prepare_monthly_metrics(load_raw_monthly_data(SAMPLE_PATH))


def render_dashboard(df: pd.DataFrame) -> None:
    summary = summarize_dashboard(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("最新月", summary["latest_month"])
    col2.metric("観測企業数", int(summary["observed_companies"]))
    col3.metric("要確認件数", int(summary["audit_count"]))
    col4.metric("平均観測率", f'{summary["average_observation_rate"]:.1%}')

    st.subheader("セグメント別観測率")
    seg_df = summarize_segments(df, "market")
    st.dataframe(seg_df, use_container_width=True, hide_index=True)


def render_rankings(df: pd.DataFrame) -> None:
    rankings = build_rankings(df)
    for title, table in rankings.items():
        st.subheader(title)
        st.dataframe(table, use_container_width=True, hide_index=True)


def render_segments(df: pd.DataFrame) -> None:
    segment_type = st.selectbox("セグメント軸", ["market", "sector17", "sector33", "theme"])
    seg_df = summarize_segments(df, segment_type)
    st.dataframe(seg_df, use_container_width=True, hide_index=True)


def render_company_detail(df: pd.DataFrame) -> None:
    companies = df[["code", "company_name"]].drop_duplicates().sort_values(["code", "company_name"])
    labels = {f'{row.code} | {row.company_name}': row.code for row in companies.itertuples()}
    selected_label = st.selectbox("企業を選択", list(labels.keys()))
    selected_code = labels[selected_label]

    company_df = df[df["code"] == selected_code].sort_values("month").copy()
    latest = company_df.iloc[-1]

    top1, top2, top3, top4 = st.columns(4)
    top1.metric("最新被保険者数", int(latest["insured_count"]))
    top2.metric("前月差", int(latest["mom_delta"]) if pd.notna(latest["mom_delta"]) else 0)
    top3.metric("3か月純増", int(latest["delta_3m"]) if pd.notna(latest["delta_3m"]) else 0)
    top4.metric("加速度", int(latest["accel_1m"]) if pd.notna(latest["accel_1m"]) else 0)

    st.line_chart(company_df.set_index("month")["insured_count"])

    detail_cols = [
        "month",
        "insured_count",
        "mom_delta",
        "mom_ratio",
        "delta_3m",
        "accel_1m",
        "up_streak",
        "quality_flag",
        "source",
        "match_status",
        "notes",
    ]
    st.dataframe(company_df[detail_cols], use_container_width=True, hide_index=True)


def render_audit_queue(df: pd.DataFrame) -> None:
    audit_df = build_audit_queue(df)
    st.dataframe(audit_df, use_container_width=True, hide_index=True)


def main() -> None:
    st.title("日本株 被保険者数バックフィル可視化")
    st.caption("2025-01 以降のバックフィル版。将来の日本年金機構 collector は未実装です。")

    try:
        df = get_data()
    except FileNotFoundError:
        st.error("data/monthly_insured.csv または data/monthly_insured_sample.csv が見つかりません。README の手順で生成してください。")
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["ダッシュボード", "企業ランキング", "セグメント", "企業詳細", "監査キュー"]
    )

    with tab1:
        render_dashboard(df)
    with tab2:
        render_rankings(df)
    with tab3:
        render_segments(df)
    with tab4:
        render_company_detail(df)
    with tab5:
        render_audit_queue(df)


if __name__ == "__main__":
    main()
