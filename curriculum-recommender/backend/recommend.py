from __future__ import annotations
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional
from collections import OrderedDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "dataresults" / "uniskill_recommendations.json"
EXPANDED_PATH = PROJECT_ROOT / "dataresults" / "uniskill_recommendations_expanded.json"

# Optional imports for TF-IDF based ranking
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    _SKLEARN_AVAILABLE = True
except Exception:
    TfidfVectorizer = None  # type: ignore
    linear_kernel = None  # type: ignore
    _SKLEARN_AVAILABLE = False


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def _tokenize(value: str | None) -> set[str]:
    normalized = _normalize_text(value)
    return {token for token in normalized.split() if token}


TECH_SKILL_HINTS = {
    "python", "sql", "java", "javascript", "typescript", "csharp", "c", "cpp", "react", "node", "fastapi",
    "flask", "django", "docker", "kubernetes", "aws", "azure", "gcp", "postgres", "postgresql", "mysql",
    "mongodb", "redis", "pandas", "numpy", "pytorch", "tensorflow", "spark", "hadoop", "api", "rest",
    "graphql", "html", "css", "git", "linux", "bash", "pytest", "unittest", "devops", "cloud", "ai", "ml",
    "machine", "learning", "data", "science", "tableau", "powerbi", "excel", "terraform", "jenkins"
}
GENERIC_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "with", "to", "of", "in", "on", "at", "from", "into", "our",
    "you", "we", "be", "is", "are", "was", "were", "must", "should", "need", "needs", "seeking", "seek",
    "strong", "solid", "preferred", "preferably", "experience", "experienced", "team", "role", "developer",
    "engineer", "software", "backend", "frontend", "fullstack", "senior", "junior", "lead", "company",
    "product", "build", "building", "develop", "developing", "design", "working", "years", "year"
}


def _is_likely_skill_phrase(value: str | None) -> bool:
    if not value:
        return False
    tokens = [token for token in _normalize_text(value).split() if token]
    if not tokens:
        return False
    if len(tokens) > 3:
        return False
    if any(token in GENERIC_STOPWORDS for token in tokens):
        return False
    if len(tokens) == 2 and all(token in TECH_SKILL_HINTS for token in tokens):
        return True
    if len(tokens) == 1 and (tokens[0] in TECH_SKILL_HINTS or len(tokens[0]) >= 3):
        return True
    return any(token in TECH_SKILL_HINTS for token in tokens)


def extract_skills_from_job_text(text: str | None) -> list[str]:
    if not text:
        return []
    cleaned = re.sub(r"[^a-z0-9+.#/&]+", " ", str(text).lower()).strip()
    if not cleaned:
        return []
    words = [word for word in cleaned.split() if word]
    candidates: list[str] = []
    seen_phrases: set[str] = set()
    for size in range(1, min(3, len(words)) + 1):
        for index in range(0, len(words) - size + 1):
            phrase = " ".join(words[index:index + size])
            if phrase in seen_phrases:
                continue
            if _is_likely_skill_phrase(phrase):
                candidates.append(phrase)
                seen_phrases.add(phrase)
    unique: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate not in seen:
            unique.append(candidate)
            seen.add(candidate)
    return unique


def _normalize_skill_name(value: str | None) -> str:
    if not value:
        return ""
    tokens = [token for token in re.split(r"[^a-z0-9]+", str(value).lower()) if token]
    return " ".join(tokens).strip()


def _humanize_skill_name(value: str) -> str:
    parts = [part for part in re.split(r"[^a-z0-9]+", str(value).lower()) if part]
    if not parts:
        return ""
    return " ".join(part.capitalize() if part.isalpha() and len(part) > 1 else part.upper() if part.isalnum() and len(part) <= 3 else part for part in parts)


def _skills_match(curriculum_skill: str | None, job_skill: str | None) -> bool:
    if not curriculum_skill or not job_skill:
        return False
    normalized_curriculum = _normalize_skill_name(curriculum_skill)
    normalized_job = _normalize_skill_name(job_skill)
    if not normalized_curriculum or not normalized_job:
        return False
    if normalized_curriculum == normalized_job:
        return True
    if normalized_curriculum in normalized_job or normalized_job in normalized_curriculum:
        return True
    curriculum_tokens = set(normalized_curriculum.split())
    job_tokens = set(normalized_job.split())
    return bool(curriculum_tokens & job_tokens)


def analyze_skill_gap(curriculum_skills: list[str] | None = None, job_posting_text: str | None = None, curriculum_options: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    extracted_curriculum_skills: list[str] = []
    if curriculum_skills:
        extracted_curriculum_skills.extend([skill for skill in curriculum_skills if skill and str(skill).strip()])
    if curriculum_options:
        for option in curriculum_options:
            if not isinstance(option, dict):
                continue
            for key in ("skill_name", "curriculum_title", "title", "name", "skill"):
                value = option.get(key)
                if value and str(value).strip():
                    extracted_curriculum_skills.append(str(value))
    job_skills = extract_skills_from_job_text(job_posting_text)
    matched_skills: list[str] = []
    for job_skill in job_skills:
        for curriculum_skill in extracted_curriculum_skills:
            if _skills_match(curriculum_skill, job_skill):
                matched_skills.append(_humanize_skill_name(job_skill))
                break
    gap_skills = [_humanize_skill_name(skill) for skill in job_skills if _humanize_skill_name(skill) not in matched_skills]
    coverage_percent = round((len(matched_skills) / len(job_skills)) if job_skills else 1.0, 2)
    return {
        "curriculum_skills": extracted_curriculum_skills,
        "job_skills": [_humanize_skill_name(skill) for skill in job_skills],
        "matched_skills": matched_skills,
        "gap_skills": gap_skills,
        "coverage_percent": coverage_percent,
    }


def _build_corpus(records: list[dict[str, Any]]) -> list[str]:
    """Create a textual corpus for each record by joining fields likely to
    contain semantic information."""
    corpus: list[str] = []
    for rec in records:
        parts = [
            rec.get("skill_name", ""),
            rec.get("skill_description", ""),
            rec.get("curriculum_title", ""),
            rec.get("curriculum_area", ""),
        ]
        text = " ".join([str(p) for p in parts if p])
        corpus.append(_normalize_text(text))
    return corpus


def load_recommendations(path: str | Path | None = None) -> list[dict[str, Any]]:
    # prefer expanded dataset if present
    resolved_path = Path(path or (EXPANDED_PATH if EXPANDED_PATH.exists() else DATA_PATH))
    if not resolved_path.exists():
        raise FileNotFoundError(f"Recommendation data not found: {resolved_path}")
    with resolved_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class _RecommenderIndex:
    """Cacheable TF-IDF index for records. Builds on first use if sklearn is available."""

    def __init__(self, records: list[dict[str, Any]]):
        self.records = records
        self.corpus = _build_corpus(records)
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        if _SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer()
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)


# Simple module-level cache to avoid rebuilding TF-IDF on every request
_INDEX_CACHE: dict[str, Any] = {"count": 0, "index": None}


def _get_index(records: list[dict[str, Any]]) -> _RecommenderIndex:
    count = len(records)
    if _INDEX_CACHE.get("index") is None or _INDEX_CACHE.get("count") != count:
        _INDEX_CACHE["index"] = _RecommenderIndex(records)
        _INDEX_CACHE["count"] = count
    return _INDEX_CACHE["index"]


def _popularity_multiplier(record: dict[str, Any]) -> float:
    # If an explicit popularity field exists, use it (scaled). Otherwise,
    # use curriculum_level heuristic: Beginner > Intermediate > Advanced.
    try:
        val = record.get("popularity")
        if val is not None:
            return float(val)
    except Exception:
        pass
    level = str(record.get("curriculum_level", "")).lower()
    if "beginner" in level:
        return 1.2
    if "intermediate" in level:
        return 1.0
    if "advanced" in level:
        return 0.8
    return 1.0


# Simple LRU cache for recommendation results
_RESULT_CACHE: OrderedDict[tuple, list[dict[str, Any]]] = OrderedDict()
_RESULT_CACHE_MAX = 256


def _score_token_overlap(input_tokens: set[str], skill_tokens: set[str], normalized_skill: str, normalized_inputs: list[str]) -> int:
    score = 0
    if normalized_skill in normalized_inputs:
        score += 100
    for phrase in normalized_inputs:
        if phrase and phrase in normalized_skill:
            score += 35
    for token in input_tokens:
        if token in skill_tokens:
            score += 20
    return score


def _mmr_select(candidates: list[dict[str, Any]], scores: list[float], sim_matrix: list[list[float]] | None, top_k: int, diversity: float = 0.7) -> list[dict[str, Any]]:
    """Select `top_k` candidates using Maximal Marginal Relevance (MMR).

    - candidates: list of records
    - scores: relevance scores (higher better)
    - sim_matrix: pairwise similarity matrix (or None to approximate using scores)
    - diversity: float in [0,1], higher encourages diversity
    """
    if top_k <= 0 or not candidates:
        return []
    selected_indices: list[int] = []
    remaining = set(range(len(candidates)))
    # pick highest score first
    first = max(range(len(scores)), key=lambda i: scores[i])
    selected_indices.append(first)
    remaining.remove(first)

    while len(selected_indices) < min(top_k, len(candidates)) and remaining:
        best_idx = None
        best_val = None
        for idx in list(remaining):
            rel = scores[idx]
            # compute diversity penalty as max similarity to any selected
            if sim_matrix:
                max_sim = max(sim_matrix[idx][j] for j in selected_indices)
            else:
                # if no sim matrix, approximate using normalized scores
                max_sim = max((scores[j] / (max(scores) or 1)) for j in selected_indices)
            mmr_val = diversity * rel - (1 - diversity) * max_sim
            if best_val is None or mmr_val > best_val:
                best_val = mmr_val
                best_idx = idx
        if best_idx is None:
            break
        selected_indices.append(best_idx)
        remaining.remove(best_idx)

    return [candidates[i] for i in selected_indices]


def _aggregate_recommendations(recs: list[dict[str, Any]], by: str = "curriculum_title", top_n: Optional[int] = None) -> list[dict[str, Any]]:
    """Aggregate skill-level recommendations into curriculum-level buckets.

    Aggregation sums the match_score for skills sharing the same `by` field,
    then applies average popularity multiplier and returns sorted results.
    """
    buckets: dict[str, dict[str, Any]] = {}
    for r in recs:
        key = str(r.get(by) or r.get("curriculum_title") or "Unknown")
        bucket = buckets.setdefault(key, {"curriculum_title": key, "curriculum_area": r.get("curriculum_area"), "score": 0.0, "count": 0, "examples": []})
        bucket["score"] += float(r.get("match_score", 0.0)) * _popularity_multiplier(r)
        bucket["count"] += 1
        bucket["examples"].append(r.get("skill_name"))

    results = [
        {
            "curriculum_title": v["curriculum_title"],
            "curriculum_area": v.get("curriculum_area"),
            "aggregate_score": v["score"],
            "skill_count": v["count"],
            "examples": v["examples"],
        }
        for v in buckets.values()
    ]
    results.sort(key=lambda x: x["aggregate_score"], reverse=True)
    if top_n is not None:
        return results[:top_n]
    return results


def recommend_for_skills(skills: list[str], method: str = "auto", top_n: Optional[int] = None, aggregate_by: Optional[str] = None, mmr: bool = False, diversity: float = 0.6) -> list[dict[str, Any]]:
    """Return ranked recommendations for the provided skills.

    method: 'auto' (prefer TF-IDF if available), 'tfidf', or 'keyword'.
    """
    records = load_recommendations()
    normalized_inputs = [_normalize_text(skill) for skill in skills if skill and skill.strip()]
    if not normalized_inputs:
        return []

    input_query = " ".join(normalized_inputs)
    input_tokens = {token for skill in normalized_inputs for token in skill.split() if token}

    use_tfidf = (method == "tfidf") or (method == "auto" and _SKLEARN_AVAILABLE)

    ranked: list[dict[str, Any]] = []

    # Build cache key using normalized inputs, method, top_n and dataset version
    dataset_version = _INDEX_CACHE.get("count", len(records))
    cache_key = (method, top_n, tuple(normalized_inputs), dataset_version)
    if cache_key in _RESULT_CACHE:
        # Move to the end to mark as recently used
        _RESULT_CACHE.move_to_end(cache_key)
        # Return a shallow copy to avoid external mutation
        return [dict(r) for r in _RESULT_CACHE[cache_key]]

    # We'll compute multiple signals and combine them with configurable weights.
    # Signals: tfidf similarity (if available), token overlap, popularity multiplier.
    if use_tfidf:
        index = _get_index(records)
        if index.vectorizer is not None and index.tfidf_matrix is not None:
            query_vec = index.vectorizer.transform([input_query])
            # compute cosine similarity quickly
            sims = linear_kernel(query_vec, index.tfidf_matrix).flatten().tolist()
            # normalize sims to [0,1]
            max_sim = max(sims) if sims else 1.0
            sim_norms = [(s / max_sim) if max_sim else 0.0 for s in sims]
            # compute overlap scores and popularity
            overlaps = []
            pops = []
            for rec in records:
                skill_name = str(rec.get("skill_name", ""))
                normalized_skill = _normalize_text(skill_name)
                skill_tokens = _tokenize(skill_name)
                overlap_score = _score_token_overlap(input_tokens, skill_tokens, normalized_skill, normalized_inputs)
                overlaps.append(overlap_score)
                pops.append(_popularity_multiplier(rec))

            max_overlap = max(overlaps) if overlaps else 1.0
            min_pop, max_pop = (min(pops) if pops else 1.0, max(pops) if pops else 1.0)
            # weights
            w_tfidf = 0.6
            w_overlap = 0.25
            w_pop = 0.15

            for rec, sim, sim_norm, overlap, pop in zip(records, sims, sim_norms, overlaps, pops):
                overlap_norm = (overlap / max_overlap) if max_overlap else 0.0
                pop_norm = (pop - min_pop) / (max_pop - min_pop) if max_pop - min_pop else 0.0
                combined = (w_tfidf * sim_norm + w_overlap * overlap_norm + w_pop * pop_norm)
                # scale to comparable match_score
                score = float(combined * 100.0)
                ranked.append({**rec, "match_score": score, "_tfidf_sim": float(sim)})
        else:
            # fallback to keyword if vectorizer failed
            use_tfidf = False

    if not use_tfidf:
        # keyword-only scoring: use overlap and popularity
        overlaps = []
        pops = []
        for record in records:
            skill_name = str(record.get("skill_name", ""))
            normalized_skill = _normalize_text(skill_name)
            skill_tokens = _tokenize(skill_name)
            rank = _score_token_overlap(input_tokens, skill_tokens, normalized_skill, normalized_inputs)
            overlaps.append(rank)
            pops.append(_popularity_multiplier(record))
        max_overlap = max(overlaps) if overlaps else 1.0
        min_pop, max_pop = (min(pops) if pops else 1.0, max(pops) if pops else 1.0)
        w_overlap = 0.75
        w_pop = 0.25
        for record, overlap, pop in zip(records, overlaps, pops):
            overlap_norm = (overlap / max_overlap) if max_overlap else 0.0
            pop_norm = (pop - min_pop) / (max_pop - min_pop) if max_pop - min_pop else 0.0
            score = float((w_overlap * overlap_norm + w_pop * pop_norm) * 100.0)
            ranked.append({**record, "match_score": score})

    ranked.sort(key=lambda item: item["match_score"], reverse=True)
    if mmr and top_n and len(ranked) > 0:
        # build sim matrix if available
        sim_matrix = None
        if _SKLEARN_AVAILABLE:
            index = _get_index(records)
            try:
                import numpy as _np
                from sklearn.metrics.pairwise import linear_kernel as _lk
                corpus_vecs = index.tfidf_matrix
                if corpus_vecs is not None:
                    sims = _lk(corpus_vecs, corpus_vecs)
                    sim_matrix = sims.tolist()
            except Exception:
                sim_matrix = None
        scores = [r.get('match_score', 0.0) for r in ranked]
        result = _mmr_select(ranked, scores, sim_matrix, top_n, diversity=diversity)
    else:
        if top_n is not None:
            result = ranked[:top_n]
        else:
            result = ranked

    # insert into LRU cache
    try:
        _RESULT_CACHE[cache_key] = [dict(r) for r in result]
        _RESULT_CACHE.move_to_end(cache_key)
        if len(_RESULT_CACHE) > _RESULT_CACHE_MAX:
            _RESULT_CACHE.popitem(last=False)
    except Exception:
        # Cache best-effort: ignore failures
        pass

    if aggregate_by:
        return _aggregate_recommendations(result, by=aggregate_by, top_n=top_n)

    return result


if __name__ == "__main__":
    sample = recommend_for_skills(["Python"])
    print(json.dumps(sample[:5], indent=2))
