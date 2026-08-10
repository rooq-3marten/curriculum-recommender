from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from backend.advanced_recommender import build_gap_report, build_progress_snapshot, optimize_course_selection
from backend.config import settings
from backend.firebase_service import FirebaseService
from backend.planner import build_learning_plan, build_career_paths, predict_progress
from backend.recommend import analyze_skill_gap, recommend_for_skills
from backend.storage import save_record, load_saved
from backend.profiles import load_profiles, add_profile, update_profile, delete_profile
from fastapi import HTTPException


app = FastAPI(title="Curriculum Recommender API", version="1.0.0")
firebase_service = FirebaseService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)
@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/ui/"
)

app.mount(
    "/ui",
    StaticFiles(directory=str(Path(__file__).resolve().parents[1] / "frontend"), html=True),
    name="frontend",
)


class RecommendationRequest(BaseModel):
    skills: list[str]


@app.get("/")
def health_root() -> dict[str, str]:
    return {"status": "ok", "message": "Curriculum recommender API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "message": "Curriculum recommender API is running"}


@app.post("/recommend")
def recommend(
    request: RecommendationRequest,
    method: str = Query("auto", description="Recommendation method: auto|tfidf|keyword"),
    top_n: int | None = Query(None, description="Limit number of returned items"),
) -> dict[str, Any]:
    results = recommend_for_skills(request.skills, method=method, top_n=top_n)
    return {"input_skills": request.skills, "recommendations": results}


@app.get("/recommend")
def recommend_query(
    skills: str = Query(..., description="Comma-separated skill names"),
    method: str = Query("auto", description="Recommendation method: auto|tfidf|keyword"),
    top_n: int | None = Query(None, description="Limit number of returned items"),
    aggregate_by: str | None = Query(None, description="Aggregate results by field, e.g. curriculum_title"),
    mmr: bool = Query(False, description="Enable MMR diversification"),
    diversity: float = Query(0.6, description="MMR diversity parameter (0-1)"),
) -> dict[str, Any]:
    parsed_skills = [skill.strip() for skill in skills.split(",") if skill.strip()]
    results = recommend_for_skills(parsed_skills, method=method, top_n=top_n, aggregate_by=aggregate_by, mmr=mmr, diversity=diversity)
    return {"input_skills": parsed_skills, "recommendations": results}


class GapAnalysisRequest(BaseModel):
    curriculum_skills: list[str] | None = None
    curriculum_options: list[dict[str, Any]] | None = None
    job_posting_text: str


class AuthRequest(BaseModel):
    email: str
    password: str


class StudentProfilePayload(BaseModel):
    email: str
    display_name: str
    skills: list[str] | None = None
    career_goal: str | None = None
    target_level: str | None = None
    interests: list[str] | None = None


class ProfileIn(BaseModel):
    name: str
    prefs: dict[str, str] | None = None
    goals: list[str] | None = None
    career_focus: str | None = None
    last_skills: list[str] | None = None
    learning_style: str | None = None


class LearningPlanRequest(BaseModel):
    email: str
    display_name: str
    skills: list[str] | None = None
    career_goal: str | None = None
    target_level: str | None = None
    interests: list[str] | None = None
    max_courses: int | None = None


class ProgressPredictionRequest(BaseModel):
    history: list[dict[str, Any]]
    targets: list[str]
    k: int | None = None


@app.get("/config")
def get_config() -> dict[str, Any]:
    return {
        "app_name": settings.app_name,
        "env": settings.env,
        "firebase_enabled": settings.firebase_enabled,
        "firebase_project_id": settings.firebase_project_id,
        "vercel_domain": settings.vercel_domain,
    }


@app.post("/auth/login")
def login(request: AuthRequest) -> dict[str, Any]:
    return {"status": "ok", "token": "demo-token", "user": {"email": request.email, "demo": True}}


@app.post("/auth/signup")
def signup(request: AuthRequest) -> dict[str, Any]:
    return {"status": "created", "token": "demo-token", "user": {"email": request.email, "demo": True}}


@app.post("/profile")
def save_student_profile(payload: StudentProfilePayload) -> dict[str, Any]:
    profile = {
        "email": payload.email,
        "display_name": payload.display_name,
        "skills": payload.skills or [],
        "career_goal": payload.career_goal or "Aspiring Developer",
        "target_level": payload.target_level or "Intermediate",
        "interests": payload.interests or [],
    }
    firebase_service.save_profile(profile)
    return {"status": "saved", "profile": profile}


@app.post("/gap-analysis")
def gap_analysis(request: GapAnalysisRequest) -> dict[str, Any]:
    result = analyze_skill_gap(
        curriculum_skills=request.curriculum_skills,
        curriculum_options=request.curriculum_options,
        job_posting_text=request.job_posting_text,
    )
    return result


@app.post("/planning/learning-plan")
def learning_plan(payload: LearningPlanRequest) -> dict[str, Any]:
    profile = {
        "email": payload.email,
        "display_name": payload.display_name,
        "skills": payload.skills or [],
        "career_goal": payload.career_goal or "Backend Engineer",
        "target_level": payload.target_level or "Intermediate",
        "interests": payload.interests or [],
    }
    plan = build_learning_plan(profile, max_courses=payload.max_courses or 3)
    firebase_service.save_gap_report(plan)
    return plan


@app.get("/planning/career-path")
def career_path(career_goal: str | None = Query(None)) -> dict[str, Any]:
    return build_career_paths(career_goal)


@app.post("/planning/predict")
def predict(payload: ProgressPredictionRequest) -> dict[str, Any]:
    return predict_progress(payload.history, payload.targets, k=payload.k or 3)


@app.post("/advanced-gap-analysis")
def advanced_gap_analysis(payload: StudentProfilePayload) -> dict[str, Any]:
    profile = {
        "email": payload.email,
        "display_name": payload.display_name,
        "skills": payload.skills or [],
        "career_goal": payload.career_goal or "Aspiring Developer",
        "target_level": payload.target_level or "Intermediate",
        "interests": payload.interests or [],
    }
    report = build_gap_report(profile)
    progress = build_progress_snapshot(profile)
    firebase_service.save_gap_report(report)
    return {"report": report, "progress": progress, "settings": {"firebase_enabled": settings.firebase_enabled}}


@app.get("/profiles")
def profiles_list() -> dict[str, Any]:
    items = load_profiles()
    return {"count": len(items), "profiles": items}


@app.post("/profiles")
def create_profile(profile: ProfileIn) -> dict[str, Any]:
    new = add_profile(profile.dict())
    return {"status": "created", "profile": new}


@app.put("/profiles/{profile_id}")
def modify_profile(profile_id: str, profile: ProfileIn) -> dict[str, Any]:
    try:
        updated = update_profile(profile_id, profile.dict())
    except KeyError:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"status": "updated", "profile": updated}


@app.delete("/profiles/{profile_id}")
def remove_profile(profile_id: str) -> dict[str, Any]:
    ok = delete_profile(profile_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"status": "deleted", "id": profile_id}


@app.post("/save")
def save_recommendation(record: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Save a recommendation result for later retrieval."""
    saved = save_record(record)
    return {"status": "saved", "saved": saved}


@app.get("/saved")
def list_saved() -> dict[str, Any]:
    items = load_saved()
    return {"count": len(items), "items": items}
