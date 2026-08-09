from __future__ import annotations

import os
from typing import Any


class FirebaseService:
    def __init__(self) -> None:
        self.project_id = os.getenv("FIREBASE_PROJECT_ID", "demo-project")
        self.enabled = os.getenv("FIREBASE_ENABLED", "false").lower() == "true"

    def save_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {"status": "demo", "profile": profile}
        return {"status": "not-implemented", "profile": profile}

    def save_gap_report(self, report: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {"status": "demo", "report": report}
        return {"status": "not-implemented", "report": report}
