"""Evidence packet selection."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from job_search.models import CanonicalJob

from .discipline import classify_job
from .keywords import build_alias_map, extract_keyword_strings, normalize_text, tokenize
from .loader import EvidenceLoader
from .scorer import EvidenceScorer, ScoreContext
from .types import EvidenceItem, EvidencePacket, EvidenceScore


@dataclass(frozen=True)
class SelectionLimits:
    resume_bullets: int = 12
    cover_fragments: int = 5
    role_fragments: int = 5
    projects: int = 3
    coursework: int = 8
    skills_tools_methods_total: int = 15
    field_docs: int = 5


class EvidenceSelector:
    def __init__(self, loader: EvidenceLoader | None = None, scorer: EvidenceScorer | None = None):
        self.loader = loader or EvidenceLoader()
        self.scorer = scorer or EvidenceScorer()

    def select(
        self,
        profile: dict,
        job: CanonicalJob,
        jd: str,
        keywords=None,
        limits: SelectionLimits | None = None,
    ) -> EvidencePacket:
        limits = limits or SelectionLimits()
        keywords = keywords if keywords is not None else list(tokenize(jd))
        top_keywords = extract_keyword_strings(keywords)
        alias_map = build_alias_map(profile)
        classification = classify_job(job, jd)
        items = self.loader.load(profile)

        context = ScoreContext(
            job=job,
            jd=jd,
            keyword_terms=top_keywords + list(tokenize(jd)),
            alias_map=alias_map,
            classification=classification,
        )
        scored = self.scorer.score_all(items, context)
        omitted = Counter()

        resume = self._pick(scored, {"resume_bullet"}, limits.resume_bullets, omitted)
        cover = self._pick(scored, {"cover_fragment"}, limits.cover_fragments, omitted)
        role = self._pick(scored, {"role_fragment"}, limits.role_fragments, omitted)
        projects = self._pick_projects(scored, limits.projects, omitted)
        coursework = self._pick(scored, {"coursework"}, limits.coursework, omitted)

        stm = self._pick(scored, {"skill", "tool", "method"}, limits.skills_tools_methods_total, omitted)
        skills = [i for i in stm if i.evidence_type == "skill"]
        tools = [i for i in stm if i.evidence_type == "tool"]
        methods = [i for i in stm if i.evidence_type == "method"]

        if self._field_docs_relevant(jd, classification.role_family):
            field_docs = self._pick(scored, {"field_practice", "documentation"}, limits.field_docs, omitted)
            role.extend(field_docs)
        else:
            omitted["field_documentation_not_relevant"] += len([
                s for s in scored if s.item.evidence_type in {"field_practice", "documentation"}
            ])

        warnings = []
        if not items:
            warnings.append("No rich evidence sections were found in the profile.")
        if classification.role_family == "general_civil":
            warnings.append("Role-family confidence was low; using general_civil evidence mix.")
        if len(resume) < 4:
            warnings.append("Fewer than four resume bullets were selected; full-profile fallback may be safer.")

        return EvidencePacket(
            target_discipline=classification.discipline,
            target_role_family=classification.role_family,
            top_keywords=top_keywords,
            resume_bullets=resume,
            cover_fragments=cover,
            role_fragments=role,
            projects=projects,
            personal_projects=[i for i in projects if i.evidence_type == "personal_project"],
            coursework=coursework,
            skills=skills,
            tools=tools,
            methods=methods,
            warnings=warnings,
            omitted_reason_summary=dict(omitted),
        )

    def _pick(
        self,
        scored: list[EvidenceScore],
        evidence_types: set[str],
        limit: int,
        omitted: Counter,
    ) -> list[EvidenceItem]:
        selected: list[EvidenceItem] = []
        selected_signatures: set[str] = set()
        candidates = [s for s in scored if s.item.evidence_type in evidence_types]
        for score in candidates:
            if len(selected) >= limit:
                omitted["limit_reached"] += 1
                continue
            signature = self._signature(score.item.text)
            if signature in selected_signatures:
                omitted["redundant"] += 1
                continue
            if score.score <= 0.15 and selected:
                omitted["low_score"] += 1
                continue
            selected.append(score.item)
            selected_signatures.add(signature)
        return selected

    def _pick_projects(
        self,
        scored: list[EvidenceScore],
        limit: int,
        omitted: Counter,
    ) -> list[EvidenceItem]:
        selected: list[EvidenceItem] = []
        selected_signatures: set[str] = set()
        selected_topics: set[str] = set()
        selected_ids: set[str] = set()
        candidates = [s for s in scored if s.item.evidence_type in {"project", "personal_project"}]
        for score in candidates:
            if score.item.id in selected_ids:
                omitted["redundant"] += 1
                continue
            signature = self._signature(score.item.text)
            if signature in selected_signatures:
                omitted["redundant"] += 1
                continue
            topic = self._project_topic(score.item)
            if topic in selected_topics and score.item.evidence_type != "personal_project":
                if score.item.section == "capstone_project":
                    replaced = self._replace_project_topic(selected, topic, score.item)
                    if replaced:
                        selected_ids.discard(replaced.id)
                        selected_ids.add(score.item.id)
                        selected_signatures.add(signature)
                        omitted["replaced_redundant_project_with_capstone"] += 1
                        continue
                omitted["redundant_project_topic"] += 1
                continue
            if len(selected) >= limit:
                omitted["limit_reached"] += 1
                continue
            if score.score <= 0.15 and selected:
                omitted["low_score"] += 1
                continue
            selected.append(score.item)
            selected_signatures.add(signature)
            selected_topics.add(topic)
            selected_ids.add(score.item.id)
        return selected

    def _replace_project_topic(
        self,
        selected: list[EvidenceItem],
        topic: str,
        replacement: EvidenceItem,
    ) -> EvidenceItem | None:
        for index, item in enumerate(selected):
            if self._project_topic(item) == topic and item.section != "capstone_project":
                selected[index] = replacement
                return item
        return None

    @staticmethod
    def _signature(text: str) -> str:
        tokens = sorted(tokenize(text))
        return " ".join(tokens[:8]) or normalize_text(text)[:60]

    @staticmethod
    def _project_topic(item: EvidenceItem) -> str:
        text = normalize_text(" ".join([item.text, " ".join(item.tags), " ".join(item.disciplines)]))
        if any(term in text for term in ["python", "automation", "sqlite", "openai", "llm", "data ingestion", "google sheets"]):
            return "software_automation"
        if any(term in text for term in ["structural", "steel", "concrete", "ram", "framing", "load"]):
            return "structural_design"
        if any(term in text for term in ["construction", "traffic", "schedule", "safety", "field"]):
            return "construction"
        if any(term in text for term in ["stormwater", "water", "hydraulic", "cistern"]):
            return "water_resources"
        return normalize_text(item.text)[:40]

    @staticmethod
    def _field_docs_relevant(jd: str, role_family: str) -> bool:
        text = normalize_text(jd)
        if role_family in {"construction_management", "field_engineering", "public_sector"}:
            return True
        return any(term in text for term in ["field", "inspection", "rfi", "submittal", "documentation", "construction"])
