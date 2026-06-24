"""Build 1 Package 2 — base resume library registry.

Metadata/reference-first registry of base-resume categories used as a
tailoring starting point (BUILD1-REQ-BASE-RESUME-LIBRARY). This module
defines *only* committed-safe category metadata: category id, intended role
family, selection cues, excluded/weak-fit cues, a rationale string, and a
`document_ref` placeholder. It never stores or returns real resume content,
real Drive URLs, or profile excerpts — `document_ref` is a provider-neutral
label pointing at where a human would find the real source document
locally; it is not a working link and is safe to commit.

Category set is grounded in the existing role-family/discipline
classification taxonomy in `job_search.evidence.discipline` (the same
`ROLE_FAMILIES` used by `classify_job()` and `EvidenceSelector`) rather than
invented from scratch. Capped at <= 10 categories per the accepted product
scope; currently 7. See `DEFERRED_BASE_RESUME_CATEGORIES` for the categories
intentionally not introduced in Build 1.

`general_strongest_overall` is a required, distinct category (not merely a
"fallback" label) representing the strongest broad-purpose resume package
for general applications when no specialized category is clearly superior.
Per accepted scope, this category's coursework section is optional — the
selector/recommender may omit coursework for this category specifically
when doing so produces the stronger overall resume (see
`general_strongest_overall_omits_coursework` below, enforced/testable, not
just a comment).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Role families recognized by job_search.evidence.discipline.classify_job().
# Re-stated here (not re-implemented) purely as a reference comment so the
# mapping below stays auditable against that module without re-importing
# constants that could drift silently:
#   structural, transportation, water_resources, civil_site_land_development,
#   construction_management, field_engineering, public_sector, environmental,
#   general_civil


@dataclass(frozen=True)
class BaseResumeCategory:
    """One approved base-resume category. Metadata/config only — never real
    resume content."""

    category_id: str
    label: str
    role_families: tuple[str, ...]
    """classify_job() role_family values this category is the natural match
    for. Used by the deterministic recommender to map a job's classification
    to a category."""
    selection_cues: tuple[str, ...]
    """Short, human-readable cues describing what makes this category a good
    fit for a posting (surfaced to the user as recommendation reasoning)."""
    excluded_cues: tuple[str, ...]
    """Short, human-readable cues describing what makes this category a poor
    fit (used to explain why a category was *not* recommended)."""
    rationale: str
    """One paragraph explaining why this category exists / when to use it."""
    document_ref: str
    """Provider-neutral placeholder reference to the real source document.
    Never a real Drive URL and never real resume content — just a stable,
    committed-safe label a human can use to locate the actual file locally."""
    coursework_optional: bool = False
    """When True, the selector/recommender may omit the coursework section
    for this category if doing so produces the stronger overall resume.
    True only for `general_strongest_overall` in the current set."""


# ── Approved categories (<= 10 total; currently 7) ───────────────────────────
#
# Each category maps to one or more `classify_job()` role families. The set
# below covers every role family discipline.py currently classifies *except*
# `transportation`, which is explicitly deferred (see
# DEFERRED_BASE_RESUME_CATEGORIES). `general_civil` (low-confidence/ambiguous
# postings) maps to `general_strongest_overall`, the required broad-purpose
# category, rather than being silently absorbed into one of the specialized
# categories.

APPROVED_BASE_RESUME_CATEGORIES: tuple[BaseResumeCategory, ...] = (
    BaseResumeCategory(
        category_id="structural_engineering",
        label="Structural Engineering",
        role_families=("structural",),
        selection_cues=(
            "Posting emphasizes structural design, steel, concrete, or bridge work",
            "Title contains \"Structural Engineer\" or similar",
        ),
        excluded_cues=(
            "Posting is primarily site/civil land-development or stormwater work",
            "No structural design responsibility mentioned",
        ),
        rationale=(
            "Structural design is a distinct, evidence-rich discipline with its own "
            "project/coursework emphasis (steel, concrete, loads, codes) — a generic "
            "civil resume under-represents this evidence."
        ),
        document_ref="base_resume_library/structural_engineering.reference",
    ),
    BaseResumeCategory(
        category_id="site_civil_land_development",
        label="Site Civil / Land Development",
        role_families=("civil_site_land_development",),
        selection_cues=(
            "Posting emphasizes grading, utilities, permitting, or Civil 3D",
            "Title references land development or site civil design",
        ),
        excluded_cues=(
            "Posting is primarily structural or water-resources focused",
        ),
        rationale=(
            "Site/civil land-development work has its own tool and evidence emphasis "
            "(Civil 3D, grading, utility coordination, permitting) distinct from "
            "structural or water-resources postings."
        ),
        document_ref="base_resume_library/site_civil_land_development.reference",
    ),
    BaseResumeCategory(
        category_id="water_resources_stormwater",
        label="Water Resources / Stormwater",
        role_families=("water_resources",),
        selection_cues=(
            "Posting emphasizes stormwater, hydrology, hydraulics, or drainage",
            "Title references water resources or drainage engineering",
        ),
        excluded_cues=(
            "Posting has no hydrology/hydraulics/drainage content",
        ),
        rationale=(
            "Water resources/stormwater work draws on a distinct evidence set "
            "(HEC-RAS, drainage design, hydraulic modeling) that a generic civil "
            "resume would dilute."
        ),
        document_ref="base_resume_library/water_resources_stormwater.reference",
    ),
    BaseResumeCategory(
        category_id="environmental_engineering",
        label="Environmental Engineering",
        role_families=("environmental",),
        selection_cues=(
            "Posting emphasizes environmental remediation, wetlands, or sustainability",
            "Title references environmental engineering or environmental compliance",
        ),
        excluded_cues=(
            "Posting has no environmental/remediation/permitting content",
        ),
        rationale=(
            "Environmental engineering postings reward evidence framed around "
            "remediation, wetlands, and environmental permitting rather than "
            "structural/site-civil design evidence."
        ),
        document_ref="base_resume_library/environmental_engineering.reference",
    ),
    BaseResumeCategory(
        category_id="construction_project_engineering",
        label="Construction / Project / Field Engineering",
        role_families=("construction_management", "field_engineering"),
        selection_cues=(
            "Posting emphasizes scheduling, estimating, constructability, or submittals",
            "Posting emphasizes field engineering, inspection, RFIs, or daily reports",
            "Title references project engineer, field engineer, or construction management",
        ),
        excluded_cues=(
            "Posting is purely design-office work with no field/construction-phase content",
        ),
        rationale=(
            "Construction-phase and field-engineering postings reward evidence framed "
            "around scheduling, field documentation, and constructability rather than "
            "pure design evidence; these two role families share enough evidence "
            "overlap (RFIs, submittals, field practice) to share one category rather "
            "than splitting into two near-duplicate categories."
        ),
        document_ref="base_resume_library/construction_project_engineering.reference",
    ),
    BaseResumeCategory(
        category_id="public_sector_civil",
        label="Public Sector / Municipal Civil",
        role_families=("public_sector",),
        selection_cues=(
            "Posting is a federal (USAJOBS), state, county, or municipal civil role",
            "Posting emphasizes public works or municipal infrastructure",
        ),
        excluded_cues=(
            "Posting is private-sector design/consulting with no public-agency framing",
        ),
        rationale=(
            "Public-sector postings (USAJOBS federal roles, municipal public works) "
            "have their own framing conventions and evidence emphasis distinct from "
            "private-sector consulting postings; discipline.py already tracks this as "
            "its own role family (`public_sector`), so it is evidence-grounded rather "
            "than invented."
        ),
        document_ref="base_resume_library/public_sector_civil.reference",
    ),
    BaseResumeCategory(
        category_id="general_strongest_overall",
        label="General / Strongest Overall",
        role_families=("general_civil",),
        selection_cues=(
            "Role-family classification confidence is low",
            "Posting data is sparse or the posting could not be reached",
            "No specialized category is a clearly stronger fit than the broad package",
        ),
        excluded_cues=(
            "A specialized category has high classification confidence and clear cue overlap",
        ),
        rationale=(
            "Required broad-purpose category for general/technical-analyst-style "
            "applications and any posting where a specialized category is not clearly "
            "superior. This is the manual-fallback category for unreachable postings. "
            "Coursework is optional here specifically: the strongest broad-purpose "
            "resume sometimes reads stronger with coursework trimmed in favor of "
            "project/work evidence, so the selector may omit it (see "
            "`coursework_optional=True`) rather than always including a generic "
            "coursework block."
        ),
        document_ref="base_resume_library/general_strongest_overall.reference",
        coursework_optional=True,
    ),
)


DEFERRED_BASE_RESUME_CATEGORIES: tuple[str, ...] = (
    "transportation_traffic",   # maps to discipline.py's "transportation" role family;
                                  # deferred per accepted Build 1 scope, not introduced here.
    "geotechnical",              # no discipline.py role-family signal exists yet; deferred.
    "operations_project_controls",  # no discipline.py role-family signal exists yet; deferred.
)


_BY_ID: dict[str, BaseResumeCategory] = {c.category_id: c for c in APPROVED_BASE_RESUME_CATEGORIES}

_BY_ROLE_FAMILY: dict[str, BaseResumeCategory] = {}
for _category in APPROVED_BASE_RESUME_CATEGORIES:
    for _role_family in _category.role_families:
        _BY_ROLE_FAMILY[_role_family] = _category


def list_categories() -> tuple[BaseResumeCategory, ...]:
    """Return all approved base resume categories, in stable declared order."""
    return APPROVED_BASE_RESUME_CATEGORIES


def get_category(category_id: str) -> BaseResumeCategory | None:
    return _BY_ID.get(category_id)


def category_for_role_family(role_family: str) -> BaseResumeCategory:
    """Map a `classify_job()` role_family to its approved base resume category.

    Falls back to `general_strongest_overall` for `general_civil` and for any
    role family without a direct mapping (e.g. a deferred family such as
    `transportation`) — this is the manual-fallback path, never an error.
    """
    return _BY_ROLE_FAMILY.get(role_family, _BY_ID["general_strongest_overall"])


def is_deferred_category(category_id: str) -> bool:
    return category_id in DEFERRED_BASE_RESUME_CATEGORIES


assert len(APPROVED_BASE_RESUME_CATEGORIES) <= 10, "Base resume category set must stay at or under 10 categories."
assert "general_strongest_overall" in _BY_ID, "general_strongest_overall is a required category."
