from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def build_sample_backfill() -> pd.DataFrame:
    sample_path = Path(__file__).resolve().parents[1] / "data" / "monthly_insured_sample.csv"
    return pd.read_csv(sample_path, dtype={"code": str})


def main() -> None:
    parser = argparse.ArgumentParser(
        description="hokendb バックフィル取得の雛形。現時点ではサンプルCSVを標準化出力します。"
    )
    parser.add_argument("--output", default="data/monthly_insured_sample.csv", help="出力CSVパス")
    args = parser.parse_args()

    df = build_sample_backfill()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"saved: {output_path}")


if __name__ == "__main__":
    main()
