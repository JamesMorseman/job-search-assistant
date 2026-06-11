"""Profile evidence normalization helpers."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from typing import Any

from .keywords import normalize_text, tokenize

TEXT_KEYS = ("text", "bullet", "fragment", "summary", "description", "name", "title", "course", "course_title")
TAG_KEYS = ("tags", "keywords", "discipline_tags", "role_tags", "categories")
DISCIPLINE_KEYS = ("disciplines", "discipline_tags", "discipline")
ROLE_KEYS = ("role_families", "roles", "role_tags")
SKILL_KEYS = ("skills", "skill_tags")
TOOL_KEYS = ("tools", "software", "software_used", "software_tools")
METHOD_KEYS = ("methods", "engineering_methods", "method_tags")
SOURCE_KEYS = ("source_refs", "sources", "source_traceability", "source")


def stable_id(section: str, text: str, index: int) -> str:
    digest = hashlib.sha1(f"{section}:{index}:{text}".encode("utf-8")).hexdigest()[:10]
    return f"{section}.{digest}"


def as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple | set):
        return list(value)
    return [value]


def string_list(value: Any) -> list[str]:
    out: list[str] = []
    for item in as_list(value):
        if isinstance(item, dict):
            text = item.get("name") or item.get("text") or item.get("id")
        else:
            text = item
        if text is not None and str(text).strip():
            out.append(str(text).strip())
    return out


def first_text(data: Any) -> str:
    if isinstance(data, str):
        return data.strip()
    if not isinstance(data, dict):
        return str(data).strip() if data is not None else ""
    for key in TEXT_KEYS:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    parts = []
    for key in ("degree", "major", "institution", "graduation", "status", "proficiency"):
        if data.get(key):
            parts.append(str(data[key]))
    return " - ".join(parts).strip()


def collect_fields(data: Any, keys: Iterable[str]) -> list[str]:
    if not isinstance(data, dict):
        return []
    out: list[str] = []
    for key in keys:
        out.extend(string_list(data.get(key)))
    return out


def infer_tags(text: str) -> list[str]:
    return sorted(tokenize(text))


def confidence_from(data: Any) -> float:
    if isinstance(data, dict):
        value = data.get("confidence")
        if isinstance(value, int | float):
            return max(0.0, min(1.0, float(value)))
    return 1.0
