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


def test_generation_and_grading_do_not_import_openai_directly():
    generator_source = Path("job_search/generation/generator.py").read_text(encoding="utf-8")
    grader_source = Path("job_search/grading/grader.py").read_text(encoding="utf-8")

    assert "from openai import OpenAI" not in generator_source
    assert "from openai import OpenAI" not in grader_source
