from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Optional

try:
    import pandas as pd  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - depends on environment
    pd = None


def find_dataset_path(data_dir: Optional[Path] = None, filename: Optional[str] = None) -> Path:
    """Locate the UniSkill dataset in the project data folder."""
    base_dir = data_dir or Path(__file__).resolve().parents[1] / "data"
    base_dir = base_dir.resolve()

    if filename:
        candidate = base_dir / filename
        if candidate.exists():
            return candidate

    possible_names = [
        "uniskill.csv",
        "uniskill.json",
        "uniskill.xlsx",
        "uniskill.xls",
        "uniskill.parquet",
    ]

    for name in possible_names:
        candidate = base_dir / name
        if candidate.exists():
            return candidate

    for path in sorted(base_dir.rglob("*")):
        if not path.is_file():
            continue
        if "uniskill" in path.name.lower():
            return path

    raise FileNotFoundError(
        f"No UniSkill dataset found in {base_dir}. Expected one of: {', '.join(possible_names)}"
    )


def _load_csv_rows(path: Path):
    """Read CSV rows using a few common encodings."""
    encodings = ["utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "latin-1"]
    last_error = None
    for encoding in encodings:
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                content = handle.read()
            if not content:
                return []
            content = content.replace("\\n", "\n")
            normalized_lines = [line for line in content.splitlines() if line.strip()]
            if not normalized_lines:
                return []
            reader = csv.DictReader(normalized_lines)
            return list(reader)
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    raise UnicodeDecodeError("utf-8", b"", 0, 1, "Unable to decode CSV")


def load_uniskill_dataset(path: Optional[str | Path] = None, data_dir: Optional[str | Path] = None):
    """Load the UniSkill dataset from a file path or the project data folder."""
    resolved_path = None
    if path is not None:
        resolved_path = Path(path).expanduser().resolve()
    else:
        resolved_path = find_dataset_path(
            data_dir=Path(data_dir).expanduser().resolve() if data_dir is not None else None
        )

    if not resolved_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {resolved_path}")

    suffix = resolved_path.suffix.lower()
    if suffix == ".csv":
        if pd is not None:
            return pd.read_csv(resolved_path, encoding="utf-8-sig")
        return _load_csv_rows(resolved_path)
    if suffix == ".json":
        if pd is not None:
            return pd.read_json(resolved_path)
        with resolved_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    if suffix in {".xlsx", ".xls"}:
        if pd is not None:
            return pd.read_excel(resolved_path)
        raise ImportError("pandas is required to read Excel files.")
    if suffix == ".parquet":
        if pd is not None:
            return pd.read_parquet(resolved_path)
        raise ImportError("pandas is required to read Parquet files.")

    raise ValueError(f"Unsupported dataset format: {resolved_path.suffix}")


def _clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _infer_curriculum(skill_name: str) -> dict[str, str]:
    normalized = skill_name.lower()
    if "data" in normalized and "science" in normalized:
        return {
            "curriculum_title": "Data Science Foundations",
            "curriculum_area": "Data Science",
            "curriculum_level": "Beginner",
            "recommendation_reason": "Build a strong base in analysis, statistics, visualization, experimentation, and stakeholder communication.",
        }
    if "python" in normalized:
        return {
            "curriculum_title": "Python Programming Fundamentals",
            "curriculum_area": "Programming",
            "curriculum_level": "Beginner",
            "recommendation_reason": "Develop core programming concepts with practical coding exercises, automation tasks, and API-driven projects.",
        }
    if "sql" in normalized:
        return {
            "curriculum_title": "SQL for Data Workflows",
            "curriculum_area": "Databases",
            "curriculum_level": "Beginner",
            "recommendation_reason": "Learn query design, joins, optimization, reporting patterns, and analytics-ready warehouse workflows.",
        }
    if "ai" in normalized or "machine learning" in normalized:
        return {
            "curriculum_title": "Applied AI and Machine Learning",
            "curriculum_area": "Artificial Intelligence",
            "curriculum_level": "Intermediate",
            "recommendation_reason": "Explore predictive modeling, training pipelines, model evaluation, and deployment-ready workflows.",
        }
    if "cloud" in normalized or "devops" in normalized:
        return {
            "curriculum_title": "Cloud and DevOps Foundations",
            "curriculum_area": "Cloud & DevOps",
            "curriculum_level": "Intermediate",
            "recommendation_reason": "Understand automation, deployment pipelines, monitoring, reliability, and operational resilience.",
        }
    if "web" in normalized or "frontend" in normalized or "backend" in normalized:
        return {
            "curriculum_title": "Modern Web Development Path",
            "curriculum_area": "Web Development",
            "curriculum_level": "Intermediate",
            "recommendation_reason": "Create responsive interfaces and robust application services using modern tooling, testing, and deployment practices.",
        }
    if "cyber" in normalized or "security" in normalized:
        return {
            "curriculum_title": "Cybersecurity Essentials",
            "curriculum_area": "Cybersecurity",
            "curriculum_level": "Intermediate",
            "recommendation_reason": "Learn secure design, risk assessment, incident response, and defense strategies for digital systems.",
        }
    if "analytics" in normalized or "tableau" in normalized or "power bi" in normalized:
        return {
            "curriculum_title": "Analytics and Dashboard Design",
            "curriculum_area": "Business Intelligence",
            "curriculum_level": "Beginner",
            "recommendation_reason": "Translate raw data into insightful dashboards, executive summaries, and decision-ready reports.",
        }
    return {
        "curriculum_title": f"{skill_name.title()} Learning Path",
        "curriculum_area": "General Skills",
        "curriculum_level": "Intermediate",
        "recommendation_reason": "Create a structured roadmap around the requested skill with practical milestones.",
    }


def _build_course_variants(skill_name: str, curriculum: dict[str, str], index: int) -> list[dict[str, str]]:
    base_title = curriculum["curriculum_title"]
    area = curriculum["curriculum_area"]
    base_level = curriculum["curriculum_level"]
    variants: list[dict[str, str]] = []
    if index % 3 == 0:
        variants.append({
            "curriculum_title": f"{base_title} Essentials",
            "curriculum_area": area,
            "curriculum_level": base_level,
            "recommendation_reason": curriculum["recommendation_reason"],
            "course_variant": "foundation",
            "learning_mode": "guided",
            "duration_weeks": "4",
            "certificate_available": "yes",
        })
    if index % 3 == 1 or index % 3 == 0:
        variants.append({
            "curriculum_title": f"{base_title} Practicum",
            "curriculum_area": area,
            "curriculum_level": "Intermediate" if base_level != "Advanced" else "Advanced",
            "recommendation_reason": f"Apply {skill_name} in a practical project-driven experience.",
            "course_variant": "project",
            "learning_mode": "project-based",
            "duration_weeks": "6",
            "certificate_available": "yes",
        })
    variants.append({
        "curriculum_title": f"{base_title} Capstone",
        "curriculum_area": area,
        "curriculum_level": "Advanced" if base_level != "Advanced" else "Advanced",
        "recommendation_reason": f"Advance your {skill_name} expertise with portfolio-ready challenges.",
        "course_variant": "capstone",
        "learning_mode": "portfolio",
        "duration_weeks": "8",
        "certificate_available": "yes",
    })
    return variants


def prepare_recommendation_dataset(
    path: Optional[str | Path] = None,
    data_dir: Optional[str | Path] = None,
    output_path: Optional[str | Path] = None,
    output_format: str = "csv",
) -> list[dict[str, str]]:
    """Clean the UniSkill rows and map them into a curriculum-recommendation friendly dataset."""
    resolved_path = Path(path).expanduser().resolve() if path is not None else find_dataset_path(
        data_dir=Path(data_dir).expanduser().resolve() if data_dir is not None else None
    )

    dataset = load_uniskill_dataset(path=resolved_path)
    if pd is not None and hasattr(dataset, "columns"):
        rows = dataset.to_dict(orient="records")
    elif isinstance(dataset, list):
        rows = dataset
    else:
        rows = [dataset]

    records: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        skill_id = _clean_text(row.get("skill") or row.get("id") or row.get("skill_id") or "")
        skill_name = _clean_text(row.get("description") or row.get("skill_name") or row.get("name") or row.get("skill") or "")
        if not skill_name and not skill_id:
            continue
        if not skill_name and skill_id:
            skill_name = skill_id
        curriculum = _infer_curriculum(skill_name)
        course_variants = _build_course_variants(skill_name, curriculum, len(records))
        for variant in course_variants:
            record = {
                "skill_id": f"{skill_id or str(len(records) + 1)}-{len(records) + 1}",
                "skill_name": skill_name,
                "skill_category": curriculum["curriculum_area"],
                "skill_description": skill_name,
                "curriculum_title": variant["curriculum_title"],
                "curriculum_area": variant["curriculum_area"],
                "curriculum_level": variant["curriculum_level"],
                "recommendation_reason": variant["recommendation_reason"],
                "source_file": resolved_path.name,
                "course_variant": variant["course_variant"],
                "learning_mode": variant["learning_mode"],
                "duration_weeks": variant["duration_weeks"],
                "certificate_available": variant["certificate_available"],
            }
            records.append(record)

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_format.lower() == "json":
            output_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        else:
            with output_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "skill_id",
                        "skill_name",
                        "skill_category",
                        "skill_description",
                        "curriculum_title",
                        "curriculum_area",
                        "curriculum_level",
                        "recommendation_reason",
                        "source_file",
                        "course_variant",
                        "learning_mode",
                        "duration_weeks",
                        "certificate_available",
                    ],
                )
                writer.writeheader()
                writer.writerows(records)

    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Load and clean the UniSkill dataset")
    parser.add_argument("--path", help="Optional path to the dataset file")
    parser.add_argument("--data-dir", help="Optional directory to search for the dataset")
    parser.add_argument("--output", help="Optional destination for the cleaned dataset")
    parser.add_argument("--format", choices=["csv", "json"], default="csv")
    args = parser.parse_args()

    try:
        records = prepare_recommendation_dataset(
            path=args.path,
            data_dir=args.data_dir,
            output_path=args.output,
            output_format=args.format,
        )
    except (FileNotFoundError, ValueError, ImportError) as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Prepared {len(records)} recommendation-ready records")
    for record in records[:5]:
        print(record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
