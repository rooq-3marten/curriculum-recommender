from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StudentProfile:
    id: str
    email: str
    display_name: str
    career_goal: str = "Aspiring Developer"
    target_level: str = "Intermediate"
    skills: list[str] = field(default_factory=list)
    interests: list[str] = field(default_factory=list)
    plan: list[str] = field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class CourseRecommendation:
    id: str
    title: str
    description: str
    skill: str
    weight: float
    level: str
    job_postings: list[str] = field(default_factory=list)
    importance: float = 0.0


@dataclass
class SkillsGapReport:
    profile: dict[str, Any]
    matched_skills: list[dict[str, Any]]
    gap_skills: list[dict[str, Any]]
    recommended_courses: list[dict[str, Any]]
    coverage_percent: float
    summary: str
