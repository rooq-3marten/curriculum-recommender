from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILES_PATH = PROJECT_ROOT / "dataresults" / "profiles.json"


def _ensure_parent() -> None:
    PROFILES_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_profiles() -> List[Dict[str, Any]]:
    _ensure_parent()
    if not PROFILES_PATH.exists():
        return []
    try:
        with PROFILES_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return []


def save_profiles(profiles: List[Dict[str, Any]]) -> None:
    _ensure_parent()
    with PROFILES_PATH.open("w", encoding="utf-8") as fh:
        json.dump(profiles, fh, ensure_ascii=False, indent=2)


def add_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    profiles = load_profiles()
    new = dict(profile)
    new_id = datetime.utcnow().isoformat(timespec="seconds")
    new["id"] = new_id
    new.setdefault("prefs", {})
    new.setdefault("goals", [])
    new.setdefault("career_focus", "General")
    new.setdefault("last_skills", [])
    new.setdefault("learning_style", "guided")
    new["created_at"] = new_id
    new["updated_at"] = new_id
    profiles.append(new)
    save_profiles(profiles)
    return new


def update_profile(profile_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    profiles = load_profiles()
    for i, p in enumerate(profiles):
        if str(p.get("id")) == str(profile_id):
            updated = dict(p)
            if "name" in data:
                updated["name"] = data["name"]
            if "prefs" in data:
                updated["prefs"] = data["prefs"]
            if "goals" in data:
                updated["goals"] = data["goals"]
            if "career_focus" in data:
                updated["career_focus"] = data["career_focus"]
            if "last_skills" in data:
                updated["last_skills"] = data["last_skills"]
            if "learning_style" in data:
                updated["learning_style"] = data["learning_style"]
            updated.setdefault("prefs", {})
            updated.setdefault("goals", [])
            updated.setdefault("career_focus", "General")
            updated.setdefault("last_skills", [])
            updated.setdefault("learning_style", "guided")
            updated["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
            profiles[i] = updated
            save_profiles(profiles)
            return updated
    raise KeyError("profile not found")


def delete_profile(profile_id: str) -> bool:
    profiles = load_profiles()
    new = [p for p in profiles if str(p.get("id")) != str(profile_id)]
    if len(new) == len(profiles):
        return False
    save_profiles(new)
    return True
