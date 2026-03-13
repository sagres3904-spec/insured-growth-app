from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.loaders import load_raw_monthly_data
from src.metrics import prepare_monthly_metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="月次被保険者数データから指標列を生成します。")
    parser.add_argument("--input", default="data/monthly_insured_sample.csv", help="入力CSVパス")
    parser.add_argument("--output", default="data/monthly_insured.csv", help="出力CSVパス")
    args = parser.parse_args()

    raw_df = load_raw_monthly_data(Path(args.input))
    metrics_df = prepare_monthly_metrics(raw_df)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"saved: {output_path}")


if __name__ == "__main__":
    main()
