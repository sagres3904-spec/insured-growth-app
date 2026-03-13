import pandas as pd

from src.metrics import prepare_monthly_metrics


def test_prepare_monthly_metrics_computes_deltas_and_quality():
    df = pd.DataFrame(
        [
            {
                "code": "1001",
                "company_name": "テスト社",
                "month": "2025-01",
                "insured_count": 1000,
                "market": "プライム",
                "sector17": "情報通信・サービスその他",
                "sector33": "情報・通信業",
                "theme": "テスト",
                "source": "hokendb",
                "match_status": "matched",
                "notes": "",
            },
            {
                "code": "1001",
                "company_name": "テスト社",
                "month": "2025-02",
                "insured_count": 1200,
                "market": "プライム",
                "sector17": "情報通信・サービスその他",
                "sector33": "情報・通信業",
                "theme": "テスト",
                "source": "hokendb",
                "match_status": "matched",
                "notes": "",
            },
            {
                "code": "1001",
                "company_name": "テスト社",
                "month": "2025-03",
                "insured_count": 1180,
                "market": "プライム",
                "sector17": "情報通信・サービスその他",
                "sector33": "情報・通信業",
                "theme": "テスト",
                "source": "hokendb",
                "match_status": "matched",
                "notes": "",
            },
        ]
    )

    result = prepare_monthly_metrics(df)

    feb = result.iloc[1]
    mar = result.iloc[2]

    assert feb["mom_delta"] == 200
    assert round(feb["mom_ratio"], 4) == 0.2
    assert feb["quality_flag"] == "low_count|extreme_change"
    assert mar["mom_delta"] == -20
    assert mar["up_streak"] == 0
