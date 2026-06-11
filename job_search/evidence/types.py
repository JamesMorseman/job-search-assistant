"""Types for evidence-grounded generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

EvidenceType = Literal[
    "resume_bullet",
    "cover_fragment",
    "role_fragment",
    "keyword",
    "project",
    "coursework",
    "skill",
    "tool",
    "method",
    "field_practice",
    "documentation",
    "certification",
    "education",
]


@dataclass(frozen=True)
class EvidenceItem:
    id: str
    section: str
    text: str
    evidence_type: EvidenceType
    tags: list[str] = field(default_factory=list)
    disciplines: list[str] = field(default_factory=list)
    role_families: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    confidence: float = 1.0

    def to_prompt_dict(self) -> dict:
        data = asdict(self)
        return {k: v for k, v in data.items() if v not in (None, [], "")}


@dataclass(frozen=True)
class EvidenceScore:
    item: EvidenceItem
    score: float
    reasons: list[str] = field(default_factory=list)


@dataclass
class EvidencePacket:
    target_discipline: str
    target_role_family: str
    top_keywords: list[str] = field(default_factory=list)
    resume_bullets: list[EvidenceItem] = field(default_factory=list)
    cover_fragments: list[EvidenceItem] = field(default_factory=list)
    role_fragments: list[EvidenceItem] = field(default_factory=list)
    projects: list[EvidenceItem] = field(default_factory=list)
    coursework: list[EvidenceItem] = field(default_factory=list)
    skills: list[EvidenceItem] = field(default_factory=list)
    tools: list[EvidenceItem] = field(default_factory=list)
    methods: list[EvidenceItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    omitted_reason_summary: dict[str, int] = field(default_factory=dict)

    @property
    def item_count(self) -> int:
        return sum(len(items) for items in self._groups().values())

    def has_rich_evidence(self) -> bool:
        return self.item_count >= 8

    def to_prompt_dict(self) -> dict:
        return {
            "target_discipline": self.target_discipline,
            "target_role_family": self.target_role_family,
            "top_keywords": self.top_keywords,
            "resume_bullets": [i.to_prompt_dict() for i in self.resume_bullets],
            "cover_fragments": [i.to_prompt_dict() for i in self.cover_fragments],
            "role_fragments": [i.to_prompt_dict() for i in self.role_fragments],
            "projects": [i.to_prompt_dict() for i in self.projects],
            "coursework": [i.to_prompt_dict() for i in self.coursework],
            "skills": [i.to_prompt_dict() for i in self.skills],
            "tools": [i.to_prompt_dict() for i in self.tools],
            "methods": [i.to_prompt_dict() for i in self.methods],
            "warnings": self.warnings,
            "omitted_reason_summary": self.omitted_reason_summary,
        }

    def _groups(self) -> dict[str, list[EvidenceItem]]:
        return {
            "resume_bullets": self.resume_bullets,
            "cover_fragments": self.cover_fragments,
            "role_fragments": self.role_fragments,
            "projects": self.projects,
            "coursework": self.coursework,
            "skills": self.skills,
            "tools": self.tools,
            "methods": self.methods,
        }
