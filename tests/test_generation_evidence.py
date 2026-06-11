"""Tests for evidence packet integration in document generation."""

import json
from pathlib import Path

from job_search.generation.generator import DocumentGenerator
from job_search.llm.types import LLMResponse
from job_search.models import CanonicalJob

from tests.test_evidence_selection import sample_profile


class FakeLLMProvider:
    provider_name = "fake"

    def __init__(self):
        self.requests = []

    def generate_json(self, request):
        self.requests.append(request)
        if len(self.requests) == 1:
            return LLMResponse(content=json.dumps({
                "professional_summary": "Structural candidate.",
                "skills": ["RAM"],
                "education": [],
                "experience": [],
                "projects": [],
                "activities": [],
                "certifications": [],
                "keyword_notes": {"included": [], "rationale": ""},
            }))
        return LLMResponse(content=json.dumps({
            "salutation": "Dear Hiring Manager,",
            "body_paragraphs": ["I am interested in this structural role."],
            "closing": "Sincerely, James",
        }))

    def submit_json_batch(self, requests):
        raise NotImplementedError

    def retrieve_batch_status(self, batch_id):
        raise NotImplementedError

    def fetch_json_batch_results(self, batch_id):
        raise NotImplementedError


def make_job(description: str | None = None) -> CanonicalJob:
    return CanonicalJob(
        source="test",
        source_job_id="job1",
        company="Acme",
        title="Structural Engineer",
        description_normalized=description or "Structural design using RAM, steel, concrete, and AutoCAD.",
    )


def user_prompt(fake: FakeLLMProvider, index: int = 0) -> str:
    return fake.requests[index].messages[1].content


def test_generator_uses_selected_evidence_instead_of_full_profile():
    fake = FakeLLMProvider()
    generator = DocumentGenerator(llm_provider=fake)
    profile = sample_profile()
    profile["unrelated_private_note"] = "DO NOT SEND THIS IRRELEVANT FULL PROFILE NOTE"
    generator._profile = profile

    result = generator.generate(make_job())

    assert result["evidence_fallback_used"] is False
    prompt = user_prompt(fake)
    assert "selected_evidence_packet" in prompt
    assert "baseline_profile_facts" in prompt
    assert "rb_structural" in prompt
    assert "DO NOT SEND THIS IRRELEVANT FULL PROFILE NOTE" not in prompt


def test_generator_includes_work_history_in_baseline_profile_facts():
    fake = FakeLLMProvider()
    generator = DocumentGenerator(llm_provider=fake)
    profile = sample_profile()
    profile["experience"] = [{
        "employer": "Urban Air Adventure Park",
        "title": "Event Coordination Department Head",
        "start_date": "2021-09",
        "end_date": "present",
        "location": "Lake Grove, NY",
    }]
    generator._profile = profile

    generator.generate(make_job())

    prompt = user_prompt(fake)
    assert "baseline_profile_facts" in prompt
    assert "Urban Air Adventure Park" in prompt
    assert "Event Coordination Department Head" in prompt


def test_resume_style_guide_is_included_in_prompt():
    fake = FakeLLMProvider()
    generator = DocumentGenerator(llm_provider=fake)
    generator._profile = sample_profile()

    generator.generate(make_job())

    prompt = user_prompt(fake)
    assert "Resume Rendering Spec" in prompt
    assert "Resume Content Rules" in prompt
    assert "Target length: 1 page" in prompt
    assert "Relevant Coursework is conditional" in prompt


def test_cover_letter_style_guide_is_included_in_prompt():
    fake = FakeLLMProvider()
    generator = DocumentGenerator(llm_provider=fake)
    generator._profile = sample_profile()

    generator.generate(make_job())

    prompt = user_prompt(fake, index=1)
    assert "Cover Letter Style Guide" in prompt
    assert "1 page maximum" in prompt
    assert "Paragraph 1: name the role/company" in prompt
    assert "Do not repeat resume bullets mechanically" in prompt


def test_generator_falls_back_to_full_profile_when_evidence_is_sparse():
    fake = FakeLLMProvider()
    generator = DocumentGenerator(llm_provider=fake)
    generator._profile = {
        "identity": {"first_name": "James"},
        "legacy_fact": "Fallback profile fact",
    }

    result = generator.generate(make_job("General civil engineer role."))

    assert result["evidence_fallback_used"] is True
    assert "full_profile_fallback" in user_prompt(fake)
    assert "Fallback profile fact" in user_prompt(fake)


def test_resume_qa_limits_bullets_sections_and_skills():
    generator = DocumentGenerator(llm_provider=FakeLLMProvider())
    data = {
        "professional_summary": "Civil engineering candidate with project experience.",
        "skills": [f"Skill {i}" for i in range(30)],
        "education": [],
        "experience": [
            {"employer": f"Employer {i}", "title": "Lead", "bullets": [f"Work bullet {j}" for j in range(8)]}
            for i in range(4)
        ],
        "projects": [
            {"name": f"Project {i}", "role": "Student", "bullets": [f"Project bullet {j}" for j in range(8)]}
            for i in range(5)
        ],
        "activities": [],
        "certifications": [],
    }

    out = generator._qa_resume_json(data, "Structural engineering role with steel and concrete.")

    assert len(out["skills"]) == 14
    assert len(out["experience"]) == 1
    assert 1 <= len(out["experience"][0]["bullets"]) <= 3
    assert 1 <= len(out["projects"]) <= 3
    assert all(len(proj["bullets"]) <= 4 for proj in out["projects"])
    assert out["rendering_qa"]["length_risk"] in {"ok", "soft_cap_risk", "hard_cap_risk"}
    assert out["rendering_qa"]["estimated_words"] <= 950


def test_resume_qa_preserves_work_and_prefers_job_search_assistant_breadth():
    generator = DocumentGenerator(llm_provider=FakeLLMProvider())
    data = {
        "professional_summary": "Structural candidate.",
        "skills": ["RAM Structural System", "Python", "SQLite"],
        "education": [],
        "experience": [{
            "employer": "Urban Air Adventure Park",
            "title": "Event Coordination Department Head",
            "dates": "September 2021 - Present",
            "location": "Lake Grove, New York",
            "bullets": ["Coordinated staffing.", "Trained employees.", "Managed operations."],
        }],
        "projects": [
            {
                "name": "Senior Capstone Project",
                "role": "Structural Design Lead",
                "bullets": ["Capstone bullet 1", "Capstone bullet 2", "Capstone bullet 3", "Capstone bullet 4"],
            },
            {
                "name": "Steel Design Project",
                "role": "Student designer",
                "bullets": ["Duplicate steel structural design evidence."],
            },
            {
                "name": "Job Search Assistant",
                "role": "Personal software / automation project",
                "bullets": ["Built Python automation with SQLite, OpenAI, Google Sheets, and CLI workflow."],
            },
        ],
        "activities": [],
        "certifications": [],
    }

    out = generator._qa_resume_json(data, "Entry level structural engineer using RAM and steel design.")
    project_names = [project["name"] for project in out["projects"]]

    assert "Senior Capstone Project" in project_names
    assert "Job Search Assistant" in project_names
    assert "Steel Design Project" not in project_names
    assert out["experience"][0]["employer"] == "Urban Air Adventure Park"
    assert out["experience"][0]["title"] == "Event Coordination Department Head"
    assert 2 <= len(out["experience"][0]["bullets"]) <= 3
    assert len(out["projects"][0]["bullets"]) == 4
    assert out["rendering_qa"]["expansion_order"][0] == "capstone_bullets"
    if "work_experience_bullets" in out["rendering_qa"]["expansion_order"]:
        assert out["rendering_qa"]["expansion_order"].index("work_experience_bullets") > out["rendering_qa"]["expansion_order"].index("capstone_bullets")


def test_resume_qa_expands_project_evidence_before_extra_work_depth():
    generator = DocumentGenerator(llm_provider=FakeLLMProvider())
    data = {
        "professional_summary": "Civil engineering candidate.",
        "skills": ["RAM Structural System", "AutoCAD", "Steel Design"],
        "education": [],
        "experience": [{
            "employer": "Urban Air Adventure Park",
            "title": "Event Coordination Department Head",
            "dates": "September 2021 - Present",
            "location": "Lake Grove, New York",
            "bullets": ["Coordinated staffing.", "Trained employees.", "Managed operations."],
        }],
        "projects": [
            {
                "name": "Senior Capstone Project",
                "role": "Structural Design Lead",
                "bullets": ["Capstone bullet 1", "Capstone bullet 2", "Capstone bullet 3", "Capstone bullet 4"],
            },
            {
                "name": "Stormwater Cistern Project",
                "role": "Student designer",
                "bullets": ["Calculated runoff.", "Evaluated storage and overflow options."],
            },
        ],
        "activities": [],
        "certifications": [],
    }

    out = generator._qa_resume_json(data, "Entry level civil engineer focused on structural and water resources projects.")
    order = out["rendering_qa"]["expansion_order"]

    assert out["experience"]
    assert len(out["experience"][0]["bullets"]) >= 2
    assert len(out["projects"][0]["bullets"]) == 4
    assert len(out["projects"][1]["bullets"]) == 2
    assert order.index("capstone_bullets") < order.index("academic_project_bullets")
    if "work_experience_bullets" in order:
        assert order.index("academic_project_bullets") < order.index("work_experience_bullets")


def test_resume_qa_prioritizes_job_search_assistant_before_other_academic_projects():
    generator = DocumentGenerator(llm_provider=FakeLLMProvider())
    data = {
        "professional_summary": "Civil engineering candidate.",
        "skills": ["RAM Structural System", "Python", "SQLite"],
        "education": [],
        "experience": [{
            "employer": "Urban Air Adventure Park",
            "title": "Event Coordination Department Head",
            "bullets": ["Coordinated staffing.", "Trained employees."],
        }],
        "projects": [
            {"name": "Senior Capstone Project", "role": "Structural Design Lead", "bullets": ["Capstone 1", "Capstone 2"]},
            {"name": "Bridge Replacement Project", "role": "Student designer", "bullets": ["Bridge 1"]},
            {"name": "Job Search Assistant", "role": "Software Automation Project", "bullets": ["JSA 1"]},
        ],
        "activities": [],
        "certifications": [],
    }

    out = generator._qa_resume_json(data, "Entry level structural engineer using RAM and Python automation.")
    project_names = [project["name"] for project in out["projects"]]

    assert project_names[:2] == ["Senior Capstone Project", "Job Search Assistant"]
    assert project_names.index("Job Search Assistant") < project_names.index("Bridge Replacement Project")
    assert out["experience"]


def test_coursework_trims_by_full_table_rows():
    generator = DocumentGenerator(llm_provider=FakeLLMProvider())
    data = {
        "education": [{
            "institution": "Farmingdale State College",
            "degree": "B.S.",
            "relevant_coursework": [f"Course {idx}" for idx in range(1, 8)],
        }]
    }

    assert generator._trim_coursework_row(data) is True

    remaining = data["education"][0]["relevant_coursework"]
    assert remaining == [f"Course {idx}" for idx in range(1, 7)]


def test_length_trim_preserves_work_and_removes_third_project_before_work():
    generator = DocumentGenerator(llm_provider=FakeLLMProvider())
    data = {
        "professional_summary": " ".join(["summary"] * 900),
        "skills": [f"Skill {idx}" for idx in range(14)],
        "education": [{
            "institution": "Farmingdale State College",
            "degree": "B.S.",
            "relevant_coursework": [f"Course {idx}" for idx in range(1, 10)],
        }],
        "experience": [{
            "employer": "Urban Air Adventure Park",
            "title": "Event Coordination Department Head",
            "bullets": ["Coordinated staffing.", "Trained employees."],
        }],
        "projects": [
            {"name": "Senior Capstone Project", "role": "Structural Design Lead", "bullets": ["Capstone"] * 5},
            {"name": "Job Search Assistant", "role": "Software Automation Project", "bullets": ["JSA"] * 3},
            {"name": "Bridge Replacement Project", "role": "Student designer", "bullets": ["Bridge"] * 4},
        ],
        "activities": [],
        "certifications": [],
    }
    warnings = []

    generator._trim_resume_to_length(data, warnings)

    assert data["experience"]
    assert all(project["name"] != "Bridge Replacement Project" for project in data["projects"])
    assert [project["name"] for project in data["projects"]] == ["Senior Capstone Project", "Job Search Assistant"]


def test_resume_qa_removes_question_mark_replacement_characters():
    generator = DocumentGenerator(llm_provider=FakeLLMProvider())
    data = {
        "professional_summary": "Candidate ? structural.",
        "skills": ["RAM Structural System ? Project coordination"],
        "education": [],
        "experience": [],
        "projects": [],
        "activities": [],
        "certifications": [],
    }

    out = generator._qa_resume_json(data, "Structural engineer.")

    assert "?" not in out["professional_summary"]
    assert "?" not in " ".join(out["skills"])


def test_relevant_coursework_is_conditional():
    generator = DocumentGenerator(llm_provider=FakeLLMProvider())
    data = {
        "professional_summary": "Candidate.",
        "skills": [],
        "education": [{
            "degree": "B.S.",
            "major": "Civil Engineering Technology",
            "institution": "Farmingdale State College",
            "graduation": "May 2026",
            "relevant_coursework": ["Structural Design", "Reinforced Concrete Design"],
        }],
        "experience": [],
        "projects": [],
        "activities": [],
        "certifications": [],
    }

    relevant = generator._qa_resume_json(data, "Entry level structural engineer working with concrete.")
    irrelevant = generator._qa_resume_json(data, "Customer success role focused on sales outreach.")

    assert relevant["education"][0]["relevant_coursework"]
    assert "relevant_coursework" not in irrelevant["education"][0]
    assert "coursework omitted" in " ".join(irrelevant["rendering_qa"]["warnings"])


def test_resume_qa_removes_blank_sections_and_items():
    generator = DocumentGenerator(llm_provider=FakeLLMProvider())
    data = {
        "professional_summary": "  ",
        "skills": ["", "RAM"],
        "education": [{"degree": "", "institution": ""}],
        "experience": [{"employer": "", "title": "", "bullets": [""]}],
        "projects": [{"name": "", "role": "", "bullets": [""]}],
        "activities": [{"organization": "", "role": ""}],
        "certifications": ["", "FE Civil Exam Candidate"],
    }

    out = generator._qa_resume_json(data, "Structural engineer.")

    assert out["professional_summary"] == ""
    assert out["skills"] == ["RAM"]
    assert out["education"] == []
    assert out["experience"] == []
    assert out["projects"] == []
    assert out["activities"] == []
    assert out["certifications"] == ["FE Civil Exam Candidate"]


def test_generation_and_grading_do_not_import_openai_directly():
    generator_source = Path("job_search/generation/generator.py").read_text(encoding="utf-8")
    grader_source = Path("job_search/grading/grader.py").read_text(encoding="utf-8")

    assert "from openai import OpenAI" not in generator_source
    assert "from openai import OpenAI" not in grader_source
