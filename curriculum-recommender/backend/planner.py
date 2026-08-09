from __future__ import annotations

import math
from typing import Any


ROLE_REQUIREMENTS: dict[str, list[dict[str, Any]]] = {
    "backend engineer": [
        {"skill": "Python", "importance": 1.0, "level": "Intermediate"},
        {"skill": "SQL", "importance": 0.9, "level": "Intermediate"},
        {"skill": "FastAPI", "importance": 0.95, "level": "Intermediate"},
        {"skill": "Docker", "importance": 0.85, "level": "Intermediate"},
    ],
    "data scientist": [
        {"skill": "Python", "importance": 1.0, "level": "Intermediate"},
        {"skill": "SQL", "importance": 0.9, "level": "Intermediate"},
        {"skill": "Machine Learning", "importance": 0.9, "level": "Intermediate"},
        {"skill": "Data Visualization", "importance": 0.8, "level": "Beginner"},
    ],
    "ai engineer": [
        {"skill": "Python", "importance": 1.0, "level": "Intermediate"},
        {"skill": "Machine Learning", "importance": 0.95, "level": "Intermediate"},
        {"skill": "TensorFlow", "importance": 0.9, "level": "Intermediate"},
        {"skill": "Cloud", "importance": 0.85, "level": "Beginner"},
    ],
    "full stack engineer": [
        {"skill": "JavaScript", "importance": 0.95, "level": "Intermediate"},
        {"skill": "React", "importance": 0.9, "level": "Intermediate"},
        {"skill": "Node.js", "importance": 0.9, "level": "Intermediate"},
        {"skill": "SQL", "importance": 0.85, "level": "Beginner"},
    ],
}

COURSE_LIBRARY: list[dict[str, Any]] = [
    {
        "id": "python-foundations",
        "title": "Python Foundations",
        "skill": "Python",
        "importance": 1.0,
        "career_alignment": 0.95,
        "level": "Beginner",
        "weight": 0.95,
        "prerequisites": [],
        "reason": "Builds the core coding fluency required for backend and data roles.",
        "duration_weeks": 4,
    },
    {
        "id": "fastapi-production",
        "title": "FastAPI in Production",
        "skill": "FastAPI",
        "importance": 0.95,
        "career_alignment": 0.96,
        "level": "Intermediate",
        "weight": 0.97,
        "prerequisites": ["Python"],
        "reason": "Pairs directly with backend engineering requirements and API delivery.",
        "duration_weeks": 6,
    },
    {
        "id": "sql-analytics",
        "title": "SQL for Analytics",
        "skill": "SQL",
        "importance": 0.9,
        "career_alignment": 0.92,
        "level": "Beginner",
        "weight": 0.9,
        "prerequisites": [],
        "reason": "Improves data access, reporting, and product analytics readiness.",
        "duration_weeks": 3,
    },
    {
        "id": "docker-ops",
        "title": "Docker and Deployment Workflows",
        "skill": "Docker",
        "importance": 0.85,
        "career_alignment": 0.9,
        "level": "Intermediate",
        "weight": 0.88,
        "prerequisites": ["Python"],
        "reason": "Adds operational confidence and deployment readiness for modern software teams.",
        "duration_weeks": 5,
    },
    {
        "id": "ml-core",
        "title": "Machine Learning Foundations",
        "skill": "Machine Learning",
        "importance": 0.9,
        "career_alignment": 0.94,
        "level": "Intermediate",
        "weight": 0.92,
        "prerequisites": ["Python"],
        "reason": "Covers the statistical and modeling foundations expected in data science roles.",
        "duration_weeks": 6,
    },
    {
        "id": "react-ui",
        "title": "React for Modern Interfaces",
        "skill": "React",
        "importance": 0.9,
        "career_alignment": 0.9,
        "level": "Intermediate",
        "weight": 0.91,
        "prerequisites": ["JavaScript"],
        "reason": "Strengthens end-to-end product delivery and full-stack credibility.",
        "duration_weeks": 5,
    },
]


def _normalize_skill_name(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(token for token in str(value).lower().replace("-", " ").split() if token)


def _skill_matches(candidate: str | None, target: str | None) -> bool:
    candidate_norm = _normalize_skill_name(candidate)
    target_norm = _normalize_skill_name(target)
    if not candidate_norm or not target_norm:
        return False
    if candidate_norm == target_norm:
        return True
    if candidate_norm in target_norm or target_norm in candidate_norm:
        return True
    candidate_tokens = set(candidate_norm.split())
    target_tokens = set(target_norm.split())
    return bool(candidate_tokens & target_tokens)


def compute_skill_value(skill: str, level: str | None = None, importance: float = 0.8, alignment: float = 0.8) -> float:
    level_multiplier = 1.0
    if level and "advanced" in level.lower():
        level_multiplier = 1.12
    elif level and "beginner" in level.lower():
        level_multiplier = 0.9
    base = max(0.0, min(1.0, float(importance) * float(alignment) * level_multiplier))
    return round(base, 2)


def _get_role_requirements(career_goal: str | None) -> list[dict[str, Any]]:
    if not career_goal:
        return ROLE_REQUIREMENTS["backend engineer"]
    normalized = career_goal.lower()
    for role, requirements in ROLE_REQUIREMENTS.items():
        if role in normalized or normalized in role:
            return requirements
    if "data" in normalized and "scient" in normalized:
        return ROLE_REQUIREMENTS["data scientist"]
    if "ai" in normalized:
        return ROLE_REQUIREMENTS["ai engineer"]
    if "full stack" in normalized or "fullstack" in normalized:
        return ROLE_REQUIREMENTS["full stack engineer"]
    return ROLE_REQUIREMENTS["backend engineer"]


def _course_candidates(requirements: list[dict[str, Any]], user_skills: list[str]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for requirement in requirements:
        skill_name = requirement["skill"]
        for course in COURSE_LIBRARY:
            if _skill_matches(course["skill"], skill_name):
                course_value = compute_skill_value(
                    course["skill"],
                    course.get("level"),
                    float(course.get("importance", 0.8)),
                    float(course.get("career_alignment", 0.8)),
                )
                candidates.append(
                    {
                        **course,
                        "requirement_skill": skill_name,
                        "value_score": course_value,
                        "user_has_skill": any(_skill_matches(skill, skill_name) for skill in user_skills),
                    }
                )
    unique: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for candidate in candidates:
        if candidate["id"] in seen_ids:
            continue
        seen_ids.add(candidate["id"])
        unique.append(candidate)
    return unique


def _course_priority(candidate: dict[str, Any], requirements: list[dict[str, Any]], user_skills: list[str]) -> float:
    priority = float(candidate.get("value_score", 0.0))
    normalized_skill = _normalize_skill_name(candidate.get("skill"))
    missing_requirements = {
        _normalize_skill_name(requirement["skill"])
        for requirement in requirements
        if not any(_skill_matches(skill, requirement["skill"]) for skill in user_skills)
    }
    if normalized_skill in missing_requirements:
        priority += 0.08
    for prerequisite in candidate.get("prerequisites", []) or []:
        if _normalize_skill_name(prerequisite) in missing_requirements:
            priority += 0.05
    for other_course in COURSE_LIBRARY:
        if normalized_skill in {_normalize_skill_name(prerequisite) for prerequisite in (other_course.get("prerequisites", []) or [])}:
            if _normalize_skill_name(other_course.get("skill")) in missing_requirements:
                priority += 0.05
    if not candidate.get("prerequisites"):
        priority += 0.03
    return priority


def _feasible_course(course: dict[str, Any], available_skills: set[str], selected_ids: set[str]) -> bool:
    prerequisites = course.get("prerequisites", []) or []
    if not prerequisites:
        return True
    for prerequisite in prerequisites:
        if prerequisite in available_skills:
            continue
        if prerequisite in selected_ids:
            continue
        return False
    return True


def build_learning_plan(profile: dict[str, Any], max_courses: int = 3) -> dict[str, Any]:
    career_goal = profile.get("career_goal") or "Backend Engineer"
    user_skills = [skill for skill in profile.get("skills", []) if skill]
    requirements = _get_role_requirements(career_goal)

    missing_skills: list[dict[str, Any]] = []
    matched_skills: list[dict[str, Any]] = []
    for requirement in requirements:
        if any(_skill_matches(skill, requirement["skill"]) for skill in user_skills):
            matched_skills.append(requirement)
        else:
            missing_skills.append(requirement)

    candidates = _course_candidates(requirements, user_skills)
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    available_skills = {_normalize_skill_name(skill) for skill in user_skills}

    while len(selected) < max_courses:
        feasible_candidates = [
            candidate
            for candidate in candidates
            if candidate["id"] not in selected_ids and _feasible_course(candidate, available_skills, selected_ids)
        ]
        if not feasible_candidates:
            break
        best = max(
            feasible_candidates,
            key=lambda item: _course_priority(item, requirements, user_skills),
        )
        selected.append(best)
        selected_ids.add(best["id"])
        available_skills.add(_normalize_skill_name(best["skill"]))

    plan = []
    for course in selected:
        plan.append(
            {
                "id": course["id"],
                "title": course["title"],
                "skill": course["skill"],
                "value": course.get("value_score", 0.0),
                "level": course.get("level", "Beginner"),
                "reason": course.get("reason", "Recommended for your target role."),
            }
        )

    total_value = round(sum(item["value"] for item in plan), 2)
    reasoning = [
        f"Targeted {career_goal} readiness with {len(missing_skills)} missing skill priorities.",
        f"Selected {len(plan)} courses that respect prerequisite constraints and maximize skill value.",
    ]

    return {
        "profile": profile,
        "career_goal": career_goal,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommended_courses": plan,
        "plan": plan,
        "value_score": total_value,
        "reasoning": reasoning,
    }


def build_career_paths(career_goal: str | None = None) -> dict[str, Any]:
    requirements = _get_role_requirements(career_goal)
    milestones = [
        {"step": 1, "title": "Foundation", "skills": [item["skill"] for item in requirements[:2]]},
        {"step": 2, "title": "Application", "skills": [item["skill"] for item in requirements[2:]]},
    ]
    return {
        "career_goal": career_goal or "Backend Engineer",
        "requirements": requirements,
        "milestones": milestones,
    }


def predict_progress(history: list[dict[str, Any]], targets: list[str], k: int = 3) -> dict[str, Any]:
    if not history:
        return {"targets": targets, "predictions": []}

    def similarity(left: dict[str, Any], right: dict[str, Any]) -> float:
        left_skills = {str(item).lower() for item in left.get("skills", [])}
        right_skills = {str(item).lower() for item in right.get("skills", [])}
        overlap = len(left_skills & right_skills)
        score = float(left.get("score", 0.0) - right.get("score", 0.0))
        return overlap + max(0.0, score / 100.0)

    predictions: list[dict[str, Any]] = []
    for target in targets:
        neighbors = sorted(history, key=lambda item: similarity(item, {"skills": [target]}), reverse=True)[:max(1, k)]
        neighbor_scores = [float(item.get("score", 0.0)) for item in neighbors]
        if not neighbor_scores:
            predicted = 0.0
            confidence = 0.0
        else:
            predicted = round(sum(neighbor_scores) / len(neighbor_scores), 1)
            variance = round(math.sqrt(sum((value - predicted) ** 2 for value in neighbor_scores) / max(len(neighbor_scores), 1)), 2)
            confidence = round(max(0.0, 1.0 - min(variance / 100.0, 0.95)), 2)
        predictions.append(
            {
                "target": target,
                "predicted_score": predicted,
                "confidence": confidence,
                "interval": [round(max(0.0, predicted - variance), 1), round(min(100.0, predicted + variance), 1)],
            }
        )
    return {"targets": targets, "predictions": predictions}
