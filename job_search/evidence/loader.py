"""Flatten master profile sections into evidence items."""

from __future__ import annotations

from typing import Any

from .normalizer import (
    DISCIPLINE_KEYS,
    METHOD_KEYS,
    ROLE_KEYS,
    SKILL_KEYS,
    SOURCE_KEYS,
    TAG_KEYS,
    TOOL_KEYS,
    collect_fields,
    confidence_from,
    first_text,
    infer_tags,
    stable_id,
    string_list,
)
from .types import EvidenceItem, EvidenceType

SECTION_TYPES: dict[str, EvidenceType] = {
    "resume_bullet_bank": "resume_bullet",
    "cover_letter_fragment_bank": "cover_fragment",
    "role_specific_fragments": "role_fragment",
    "job_matching_keywords": "keyword",
    "capstone_project": "project",
    "academic_projects": "project",
    "personal_projects": "personal_project",
    "relevant_coursework_by_category": "coursework",
    "transcript_coursework": "coursework",
    "technical_skills": "skill",
    "software_tools": "tool",
    "software": "tool",
    "engineering_methods": "method",
    "field_practices": "field_practice",
    "construction_documentation": "documentation",
    "writing_and_communication": "documentation",
    "certifications": "certification",
    "education_detail": "education",
    "education": "education",
}


class EvidenceLoader:
    def load(self, profile: dict) -> list[EvidenceItem]:
        items: list[EvidenceItem] = []
        for section, evidence_type in SECTION_TYPES.items():
            if section in profile:
                items.extend(self._flatten_section(section, profile[section], evidence_type))
        return items

    def _flatten_section(self, section: str, value: Any, evidence_type: EvidenceType) -> list[EvidenceItem]:
        raw_items = list(self._iter_leaf_records(value))
        out: list[EvidenceItem] = []
        for index, raw in enumerate(raw_items):
            text = first_text(raw)
            if not text:
                continue
            context_tags = self._context_tags(raw)
            item = EvidenceItem(
                id=self._item_id(section, raw, text, index),
                section=section,
                text=text,
                evidence_type=evidence_type,
                tags=sorted(set(context_tags + infer_tags(text))),
                disciplines=sorted(set(collect_fields(raw, DISCIPLINE_KEYS))),
                role_families=sorted(set(collect_fields(raw, ROLE_KEYS))),
                skills=sorted(set(collect_fields(raw, SKILL_KEYS))),
                tools=sorted(set(collect_fields(raw, TOOL_KEYS))),
                methods=sorted(set(collect_fields(raw, METHOD_KEYS))),
                source_refs=sorted(set(collect_fields(raw, SOURCE_KEYS))),
                confidence=confidence_from(raw),
            )
            out.append(item)
        return out

    def _iter_leaf_records(self, value: Any):
        if isinstance(value, str):
            yield value
            return
        if isinstance(value, list):
            for item in value:
                yield from self._iter_leaf_records(item)
            return
        if isinstance(value, dict):
            if self._has_direct_text(value):
                yield value
            for key, child in value.items():
                if self._has_direct_text(value) and key in {"evidence", "technologies", "bullets"}:
                    for record in self._iter_leaf_records(child):
                        if not isinstance(record, dict):
                            record = {"text": str(record)}
                        if isinstance(record, dict):
                            parent_tags = string_list(value.get("tags")) + string_list(value.get("discipline_tags"))
                            record = {
                                **record,
                                "id": value.get("id") or record.get("id"),
                                "name": value.get("name") or record.get("name"),
                                "description": f"{value.get('name', '')}: {record.get('text') or record.get('description') or record.get('name') or ''}",
                                "tags": parent_tags + string_list(record.get("tags")) + [key],
                                "tools": string_list(value.get("technologies")) + string_list(record.get("tools")),
                                "source_refs": string_list(value.get("source_refs")) + string_list(record.get("source_refs")),
                            }
                        yield record
                elif key in {
                    "bullets", "items", "fragments", "keywords", "courses",
                    "coursework", "projects", "tools", "skills", "methods",
                    "other", "relevant_coursework", "evidence", "technologies",
                }:
                    yield from self._iter_leaf_records(child)
                elif not self._has_direct_text(value) and isinstance(child, str):
                    yield {"text": child, "tags": [key]}
                elif not self._has_direct_text(value) and isinstance(child, list | dict):
                    for record in self._iter_leaf_records(child):
                        if isinstance(record, dict):
                            record = {**record, "tags": string_list(record.get("tags")) + [key]}
                        yield record
            return
        if value is not None:
            yield str(value)

    @staticmethod
    def _has_direct_text(value: dict) -> bool:
        return any(value.get(key) for key in ("text", "bullet", "fragment", "summary", "description", "name", "title", "course", "course_title", "degree"))

    @staticmethod
    def _context_tags(raw: Any) -> list[str]:
        return collect_fields(raw, TAG_KEYS) if isinstance(raw, dict) else []

    @staticmethod
    def _item_id(section: str, raw: Any, text: str, index: int) -> str:
        if isinstance(raw, dict) and raw.get("id"):
            return str(raw["id"])
        return stable_id(section, text, index)
