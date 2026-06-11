"""Tests for deterministic evidence selection."""

from job_search.evidence.discipline import classify_job
from job_search.evidence.keywords import build_alias_map, expand_with_aliases
from job_search.evidence.loader import EvidenceLoader
from job_search.evidence.scorer import EvidenceScorer, ScoreContext
from job_search.evidence.selector import EvidenceSelector
from job_search.models import CanonicalJob


def make_job(**kwargs) -> CanonicalJob:
    defaults = dict(
        source="test",
        source_job_id="job1",
        company="Acme",
        title="Entry Level Structural Engineer",
        description_normalized=(
            "Structural design role using RAM, steel design, reinforced concrete, "
            "AutoCAD, construction documentation, and coordination."
        ),
        location_city="New York",
        location_state="NY",
    )
    defaults.update(kwargs)
    return CanonicalJob(**defaults)


def sample_profile() -> dict:
    return {
        "identity": {"first_name": "James"},
        "resume_bullet_bank": [
            {
                "id": "rb_structural",
                "text": "Performed structural analysis for steel and reinforced concrete systems using RAM.",
                "discipline_tags": ["structural"],
                "tools": ["RAM"],
                "keywords": ["steel design", "reinforced concrete"],
            },
            {
                "id": "rb_duplicate",
                "text": "Performed structural analysis for steel and reinforced concrete systems using RAM.",
                "discipline_tags": ["structural"],
            },
            {
                "id": "rb_retail",
                "text": "Coordinated weekend retail staffing schedules.",
                "discipline_tags": ["operations"],
            },
        ],
        "cover_letter_fragment_bank": [
            {"id": "cf_fit", "text": "I am drawn to roles that combine structural coursework with practical documentation."}
        ],
        "role_specific_fragments": {
            "structural": [
                {"id": "rf_structural", "text": "Structural focus with steel, concrete, load paths, and RAM modeling."}
            ],
            "construction": [
                {"id": "rf_field", "text": "Construction coordination and field documentation experience."}
            ],
        },
        "job_matching_keywords": {
            "ram": ["ram structural system"],
            "construction documentation": ["submittals", "rfi", "field reports"],
        },
        "capstone_project": {
            "id": "capstone",
            "name": "Bridge redesign capstone",
            "description": "Analyzed bridge members and reactions for structural redesign.",
            "discipline_tags": ["structural"],
        },
        "academic_projects": [
            {"id": "proj_docs", "name": "Construction plan report", "description": "Prepared safety and traffic documentation."}
        ],
        "relevant_coursework_by_category": {
            "structural": ["Steel Design", "Reinforced Concrete Design", "Structural Analysis"],
            "construction": ["Construction Management"],
        },
        "transcript_coursework": ["Transportation Engineering"],
        "technical_skills": ["Structural analysis", "Load tracing"],
        "software_tools": ["RAM Structural System", "AutoCAD"],
        "engineering_methods": ["Load analysis", "Construction documentation"],
        "field_practices": ["Field observation and site safety awareness"],
        "construction_documentation": ["Prepared RFIs and submittal logs in coursework"],
        "writing_and_communication": ["Prepared technical reports and presentations"],
        "certifications": {"fe_exam": {"status": "PENDING", "discipline": "CIVIL"}},
        "education_detail": {"degree": "Bachelor of Science", "major": "Civil Engineering Technology"},
    }


def test_alias_matching_expands_job_matching_keywords():
    aliases = build_alias_map(sample_profile())

    expanded = expand_with_aliases(["ram structural system"], aliases)

    assert "ram" in expanded
    assert "ram structural system" in expanded


def test_role_family_classification_detects_structural():
    job = make_job()

    classification = classify_job(job, job.description_normalized or "")

    assert classification.role_family == "structural"
    assert classification.confidence > 0


def test_profile_flattening_covers_rich_sections():
    items = EvidenceLoader().load(sample_profile())
    sections = {item.section for item in items}

    assert "resume_bullet_bank" in sections
    assert "cover_letter_fragment_bank" in sections
    assert "capstone_project" in sections
    assert "software_tools" in sections
    assert "education_detail" in sections


def test_scoring_rewards_keyword_and_discipline_overlap():
    profile = sample_profile()
    job = make_job()
    items = EvidenceLoader().load(profile)
    classification = classify_job(job, job.description_normalized or "")
    context = ScoreContext(
        job=job,
        jd=job.description_normalized or "",
        keyword_terms=["structural", "ram", "steel", "concrete"],
        alias_map=build_alias_map(profile),
        classification=classification,
    )

    scored = EvidenceScorer().score_all(items, context)

    assert scored[0].item.id in {"rb_structural", "rf_structural", "capstone"}
    assert scored[0].score > 0


def test_selector_deduplicates_and_groups_by_evidence_type():
    packet = EvidenceSelector().select(
        sample_profile(),
        make_job(),
        make_job().description_normalized or "",
    )

    resume_ids = [item.id for item in packet.resume_bullets]
    assert "rb_structural" in resume_ids
    assert len(resume_ids) == len(set(resume_ids))
    assert "rb_duplicate" not in resume_ids
    assert packet.cover_fragments
    assert packet.role_fragments
    assert packet.projects
    assert packet.coursework
    assert packet.skills or packet.tools or packet.methods
    assert packet.target_role_family == "structural"
