from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAVED_PATH = PROJECT_ROOT / "dataresults" / "saved_recommendations.json"


def _ensure_parent() -> None:
    SAVED_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_saved() -> list[dict[str, Any]]:
    _ensure_parent()
    if not SAVED_PATH.exists():
        return []
    with SAVED_PATH.open("r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except Exception:
            return []


def save_record(record: dict[str, Any]) -> dict[str, Any]:
    """Append a recommendation record to the saved file with a timestamped id."""
    items = load_saved()
    new = dict(record)
    new_id = datetime.utcnow().isoformat(timespec="seconds")
    new["saved_id"] = new_id
    new["saved_at"] = new["saved_id"]
    items.append(new)
    with SAVED_PATH.open("w", encoding="utf-8") as fh:
        json.dump(items, fh, indent=2, ensure_ascii=False)
    return new
