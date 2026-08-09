from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.recommend import recommend_for_skills


def build_frontend_payload(skills: list[str]) -> dict[str, Any]:
    recommendations = recommend_for_skills(skills)
    return {
        "input_skills": skills,
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    payload = build_frontend_payload(["Python", "Data Science"])
    print(json.dumps(payload, indent=2))
