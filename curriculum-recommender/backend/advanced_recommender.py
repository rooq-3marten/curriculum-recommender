from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "dataresults" / "uniskill_recommendations.json"
CACHE_PATH = PROJECT_ROOT / "dataresults" / "skill_cache.json"


def _load_data() -> list[dict[str, Any]]:
    if DATA_PATH.exists():
        with DATA_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return []


def _load_cache() -> dict[str, Any]:
    if CACHE_PATH.exists():
        with CACHE_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return {"skills": {}, "courses": []}


def _save_cache(cache: dict[str, Any]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_PATH.open("w", encoding="utf-8") as handle:
        json.dump(cache, handle, indent=2)


SKILL_IMPORTANCE = {
    "python": 1.0,
    "sql": 0.9,
    "fastapi": 0.95,
    "docker": 0.85,
    "kubernetes": 0.8,
    "aws": 0.8,
    "react": 0.75,
    "javascript": 0.75,
    "typescript": 0.75,
    "data science": 0.85,
    "machine learning": 0.8,
    "ai": 0.8,
    "cloud": 0.75,
}


def _normalize(value: str | None) -> str:
    return " ".join([token for token in value.lower().replace("-", " ").split() if token]) if value else ""


def _score_skill(skill: str, level: str | None = None) -> float:
    normalized = _normalize(skill)
    base = SKILL_IMPORTANCE.get(normalized, 0.5)
    if level and "advanced" in level.lower():
        return round(base * 1.1, 2)
    if level and "beginner" in level.lower():
        return round(base * 0.95, 2)
    return round(base, 2)


def _get_job_requirements(target_role: str | None = None) -> list[dict[str, Any]]:
    role = (target_role or "backend engineer").lower()
    if "data" in role and "scient" in role:
        return [
            {"skill": "Python", "importance": 1.0},
            {"skill": "SQL", "importance": 0.9},
            {"skill": "Machine Learning", "importance": 0.85},
        ]
    if "backend" in role or "engineer" in role:
        return [
            {"skill": "Python", "importance": 1.0},
            {"skill": "SQL", "importance": 0.9},
            {"skill": "FastAPI", "importance": 0.95},
            {"skill": "Docker", "importance": 0.85},
            {"skill": "Kubernetes", "importance": 0.8},
        ]
    return [{"skill": "Python", "importance": 0.9}]


def build_gap_report(profile: dict[str, Any]) -> dict[str, Any]:
    candidate_skills = [skill for skill in profile.get("skills", []) if skill]
    target_role = profile.get("career_goal")
    requirements = _get_job_requirements(target_role)
    matched: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    for requirement in requirements:
        skill_name = requirement["skill"]
        normalized_skill = _normalize(skill_name)
        has_skill = any(_normalize(item) == normalized_skill for item in candidate_skills)
        if has_skill:
            matched.append({"skill": skill_name, "importance": requirement["importance"]})
        else:
            gaps.append({"skill": skill_name, "importance": requirement["importance"], "priority": round(requirement["importance"] * 1.2, 2)})

    courses = [
        {"id": "course-python", "title": "Python for Modern Development", "skill": "Python", "weight": 0.95, "level": "Beginner"},
        {"id": "course-fastapi", "title": "FastAPI Masterclass", "skill": "FastAPI", "weight": 0.95, "level": "Intermediate"},
        {"id": "course-sql", "title": "SQL for Analysts and Engineers", "skill": "SQL", "weight": 0.9, "level": "Beginner"},
        {"id": "course-docker", "title": "Containerization with Docker", "skill": "Docker", "weight": 0.85, "level": "Intermediate"},
    ]
    filtered = [course for course in courses if any(_normalize(course["skill"]) == _normalize(gap["skill"]) for gap in gaps)]
    cache = _load_cache()
    cache.setdefault("skills", {})
    cache.setdefault("courses", filtered)
    for skill in gaps:
        cache["skills"][skill["skill"]] = {"importance": skill["importance"], "priority": skill["priority"]}
    _save_cache(cache)
    return {
        "profile": profile,
        "matched_skills": matched,
        "gap_skills": gaps,
        "recommended_courses": filtered,
        "coverage_percent": round((len(matched) / max(len(requirements), 1)) * 100, 1),
        "summary": f"{profile.get('display_name', 'Student')} is missing {len(gaps)} priority skills for {target_role or 'target role'}.",
    }


def optimize_course_selection(courses: list[dict[str, Any]], max_courses: int = 3) -> list[dict[str, Any]]:
    ranked = sorted(courses, key=lambda item: item.get("weight", 0.0), reverse=True)
    return ranked[:max_courses]


def build_progress_snapshot(profile: dict[str, Any]) -> dict[str, Any]:
    report = build_gap_report(profile)
    acquired = len(report["matched_skills"])
    total = max(len(report["gap_skills"]) + acquired, 1)
    return {
        "progress_percent": round((acquired / total) * 100, 1),
        "acquired_skills": acquired,
        "remaining_skills": len(report["gap_skills"]),
    }
