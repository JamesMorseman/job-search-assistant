"""Role-family classification for civil engineering jobs."""

from __future__ import annotations

from dataclasses import dataclass

from job_search.models import CanonicalJob

from .keywords import normalize_text

ROLE_FAMILIES = [
    "structural",
    "transportation",
    "water_resources",
    "civil_site_land_development",
    "construction_management",
    "field_engineering",
    "public_sector",
    "environmental",
    "general_civil",
]

ROLE_PATTERNS: dict[str, list[tuple[str, float]]] = {
    "structural": [
        ("structural", 4), ("steel", 2), ("concrete", 2), ("bridge", 2),
        ("ram", 1.5), ("foundation", 1.5), ("load", 1),
    ],
    "transportation": [
        ("transportation", 4), ("traffic", 2), ("roadway", 2), ("highway", 2),
        ("dot", 2), ("transit", 1.5), ("signal", 1),
    ],
    "water_resources": [
        ("water resources", 4), ("stormwater", 3), ("hydrology", 2),
        ("hydraulic", 2), ("drainage", 2), ("hec-ras", 1.5),
    ],
    "civil_site_land_development": [
        ("land development", 4), ("site civil", 3), ("grading", 2),
        ("utility", 2), ("civil 3d", 1.5), ("permitting", 1.5),
    ],
    "construction_management": [
        ("construction management", 4), ("scheduler", 2), ("scheduling", 2),
        ("estimating", 2), ("constructability", 2), ("submittal", 1.5),
    ],
    "field_engineering": [
        ("field engineer", 4), ("inspection", 2.5), ("site visit", 2),
        ("field", 1.5), ("rfi", 1.5), ("daily report", 1.5),
    ],
    "public_sector": [
        ("usajobs", 4), ("municipal", 2.5), ("public works", 2.5),
        ("federal", 2), ("state agency", 2), ("county", 1.5),
    ],
    "environmental": [
        ("environmental", 4), ("remediation", 2), ("wetland", 2),
        ("permitting", 1.5), ("sustainability", 1.5),
    ],
}


@dataclass(frozen=True)
class RoleClassification:
    role_family: str
    discipline: str
    confidence: float
    scores: dict[str, float]


def classify_job(job: CanonicalJob, jd: str) -> RoleClassification:
    text = normalize_text(
        " ".join([
            job.title or "",
            job.company or "",
            jd or "",
            " ".join(job.discipline_tags or []),
            job.source or "",
        ])
    )
    scores: dict[str, float] = {family: 0.0 for family in ROLE_FAMILIES}
    for family, patterns in ROLE_PATTERNS.items():
        for pattern, weight in patterns:
            if pattern in text:
                scores[family] += weight

    best_family = max(scores, key=scores.get)
    best_score = scores[best_family]
    total = sum(scores.values())
    confidence = best_score / total if total else 0.0
    if best_score < 2.0 or confidence < 0.35:
        best_family = "general_civil"
        confidence = max(confidence, 0.25 if total else 0.0)
    scores["general_civil"] = max(scores["general_civil"], 0.5)
    return RoleClassification(
        role_family=best_family,
        discipline=best_family,
        confidence=round(confidence, 3),
        scores=scores,
    )
