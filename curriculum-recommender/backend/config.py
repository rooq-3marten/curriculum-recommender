from __future__ import annotations

import os
from typing import Any


class Settings:
    app_name: str = "Curriculum Recommender"
    env: str = os.getenv("APP_ENV", "development")
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "demo-project")
    firebase_enabled: bool = os.getenv("FIREBASE_ENABLED", "false").lower() == "true"
    vercel_domain: str = os.getenv("VERCEL_DOMAIN", "")


settings = Settings()
