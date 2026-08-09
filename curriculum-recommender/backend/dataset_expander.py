from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = PROJECT_ROOT / "dataresults" / "uniskill_recommendations.json"
OUTPUT_PATH = PROJECT_ROOT / "dataresults" / "expanded_course_catalog.json"
JOB_POSTINGS_PATH = PROJECT_ROOT / "dataresults" / "job_postings.json"


def build_expanded_catalog(seed: int = 42, factor: int = 8) -> dict[str, Any]:
    random.seed(seed)
    with SOURCE_PATH.open("r", encoding="utf-8") as handle:
        base_records = json.load(handle)

    expanded: list[dict[str, Any]] = []
    for index in range(factor):
        for record in base_records:
            new_record = dict(record)
            new_record["id"] = f"{new_record.get('curriculum_title','course').lower().replace(' ','-')}-{index}-{len(expanded)}"
            new_record["curriculum_title"] = f"{new_record.get('curriculum_title', 'Course')} • Variant {index + 1}"
            new_record["popularity"] = round(max(0.2, float(new_record.get("popularity", 1.0)) + random.uniform(0.05, 0.45)), 3)
            new_record["skill_description"] = f"{new_record.get('skill_description', '')} Hands-on labs, practical exercises, and project-based assessment.".strip()
            new_record["curriculum_level"] = new_record.get("curriculum_level") or random.choice(["Beginner", "Intermediate", "Advanced"])
            expanded.append(new_record)

    for i in range(120):
        skill_a = random.choice([record.get("skill_name") for record in base_records if record.get("skill_name")])
        skill_b = random.choice([record.get("skill_name") for record in base_records if record.get("skill_name")])
        if not skill_a or not skill_b or skill_a == skill_b:
            continue
        expanded.append({
            "id": f"integrated-{i}",
            "skill_name": f"{skill_a} + {skill_b}",
            "skill_description": f"A blended module for {skill_a} and {skill_b} in modern product delivery workflows.",
            "curriculum_title": f"{skill_a} + {skill_b} Studio",
            "curriculum_area": random.choice(["Data Science", "Programming", "Artificial Intelligence", "Web Development", "Cloud"]),
            "curriculum_level": random.choice(["Beginner", "Intermediate", "Advanced"]),
            "popularity": round(random.uniform(0.6, 1.7), 3),
        })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(expanded, handle, indent=2, ensure_ascii=False)

    job_postings = [
        {
            "id": f"job-{i}",
            "title": title,
            "summary": summary,
            "required_skills": skills,
        }
        for i, (title, summary, skills) in enumerate([
            ("Senior Backend Engineer", "Build reliable APIs and data services using Python, FastAPI, SQL, Docker, and cloud-native tooling.", ["Python", "FastAPI", "SQL", "Docker", "Cloud"]),
            ("Data Scientist", "Analyze product and customer data with Python, machine learning, SQL, and visualization tools.", ["Python", "Machine Learning", "SQL", "Data Visualization"]),
            ("AI Platform Engineer", "Design and operationalize machine learning systems with Python, MLOps, cloud, and deployment automation.", ["Python", "Machine Learning", "Cloud", "Docker"]),
            ("Full Stack Product Engineer", "Build delightful user experiences with React, JavaScript, Node.js, SQL, and testing practices.", ["JavaScript", "React", "Node.js", "SQL"]),
        ])
    ]
    with JOB_POSTINGS_PATH.open("w", encoding="utf-8") as handle:
        json.dump(job_postings, handle, indent=2, ensure_ascii=False)

    return {
        "courses": len(expanded),
        "job_postings": len(job_postings),
        "catalog_path": str(OUTPUT_PATH),
        "job_postings_path": str(JOB_POSTINGS_PATH),
    }


if __name__ == "__main__":
    print(json.dumps(build_expanded_catalog(), indent=2))
