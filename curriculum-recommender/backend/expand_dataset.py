from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "dataresults" / "uniskill_recommendations.json"
OUT = PROJECT_ROOT / "dataresults" / "uniskill_recommendations_expanded.json"


def expand(seed: int = 42, factor: int = 5) -> None:
    """Create an expanded dataset by duplicating and mutating existing records.

    - seed: random seed for reproducibility
    - factor: how many times to multiply the dataset size
    """
    random.seed(seed)
    if not SRC.exists():
        raise FileNotFoundError(f"Source dataset not found: {SRC}")
    with SRC.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    expanded: list[dict[str, Any]] = []
    base_count = len(data)
    for i in range(factor):
        for rec in data:
            new = dict(rec)
            # mutate curriculum title slightly every iteration
            if i > 0:
                new_title = f"{rec.get('curriculum_title', 'Curriculum')} (v{i})"
                new['curriculum_title'] = new_title
            # jitter popularity
            try:
                pop = float(rec.get('popularity') or 1.0)
            except Exception:
                pop = 1.0
            jitter = random.uniform(-0.2, 0.6)
            new['popularity'] = max(0.1, round(pop + jitter, 3))
            # add minor variations to descriptions
            desc = str(rec.get('skill_description') or '')
            if desc:
                new['skill_description'] = desc + (" " + random.choice(['Includes hands-on labs.', 'Project-based.', 'Updated content.']) if random.random() < 0.2 else '')
            expanded.append(new)

    # also add a few synthetic records by combining skills
    skills = [r.get('skill_name', '') for r in data if r.get('skill_name')]
    for i in range(min(100, len(skills))):
        a = random.choice(skills)
        b = random.choice(skills)
        if a == b:
            continue
        rec = {
            'skill_name': f'{a} & {b}',
            'skill_description': f'Integrated module covering {a} and {b}.',
            'curriculum_title': f'Integrated {a} & {b} Course',
            'curriculum_area': 'Integrated',
            'curriculum_level': random.choice(['Beginner', 'Intermediate', 'Advanced']),
            'popularity': round(random.uniform(0.5, 1.5), 3),
        }
        expanded.append(rec)

    # write out
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8') as fh:
        json.dump(expanded, fh, indent=2, ensure_ascii=False)

    print(f'Expanded dataset written to {OUT} (size={len(expanded)})')


if __name__ == '__main__':
    expand()
