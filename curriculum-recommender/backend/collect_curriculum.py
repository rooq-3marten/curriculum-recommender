from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from backend.clean_data import prepare_recommendation_dataset


def build_recommendation_dataset() -> list[dict[str, str]]:
    raw_path = PROJECT_ROOT / "data" / "uniskill.csv"
    csv_output = PROJECT_ROOT / "dataprocessed" / "uniskill_recommendations.csv"
    json_output = PROJECT_ROOT / "dataresults" / "uniskill_recommendations.json"

    records = prepare_recommendation_dataset(
        path=raw_path,
        output_path=csv_output,
        output_format="csv",
    )
    prepare_recommendation_dataset(
        path=raw_path,
        output_path=json_output,
        output_format="json",
    )
    return records


if __name__ == "__main__":
    records = build_recommendation_dataset()
    print(f"Built {len(records)} curriculum recommendation rows")
