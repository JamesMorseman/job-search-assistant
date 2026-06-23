"""Keyword and alias helpers for deterministic evidence scoring."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

STOPWORDS = {
    "and", "the", "for", "with", "from", "that", "this", "will", "you", "your",
    "our", "are", "all", "job", "role", "work", "team", "civil", "engineer",
    "engineering", "project", "projects", "including", "related",
}

# Unicode punctuation that should collapse to a canonical ASCII equivalent
# *before* the strip regex runs, so terms typed with "smart" punctuation
# (common in job descriptions copy-pasted from Word/PDF) still line up with
# resume/profile text typed with plain ASCII punctuation. Hyphen-like dashes
# map to "-" so compound terms (e.g. "co-ordinate") stay joined instead of
# being split into separate tokens; quote-like marks map to "'" so
# contractions/possessives don't lose trailing characters; space-like
# separators map to a plain space.
_UNICODE_PUNCT_MAP = {
    "‐": "-",  # hyphen
    "‑": "-",  # non-breaking hyphen
    "‒": "-",  # figure dash
    "–": "-",  # en dash
    "—": "-",  # em dash
    "―": "-",  # horizontal bar
    "‘": "'",  # left single quote
    "’": "'",  # right single quote / apostrophe
    "‚": "'",  # single low-9 quote
    "‛": "'",  # single high-reversed-9 quote
    "“": '"',  # left double quote
    "”": '"',  # right double quote
    " ": " ",  # non-breaking space
    " ": " ",  # figure space
    " ": " ",  # narrow no-break space
    "­": "",   # soft hyphen (invisible; drop rather than split words)
}
_UNICODE_PUNCT_RE = re.compile("|".join(re.escape(ch) for ch in _UNICODE_PUNCT_MAP))


def _fold_unicode_punctuation(text: str) -> str:
    return _UNICODE_PUNCT_RE.sub(lambda m: _UNICODE_PUNCT_MAP[m.group(0)], text)


def normalize_text(value: Any) -> str:
    text = str(value or "").lower()
    text = _fold_unicode_punctuation(text)
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(value: Any) -> set[str]:
    text = normalize_text(value)
    return {
        token
        for token in re.findall(r"[a-z0-9+#.][a-z0-9+#.-]{1,}", text)
        if token not in STOPWORDS and not token.isdigit()
    }


def phrase_hits(needles: Iterable[str], haystack: str) -> set[str]:
    normalized = normalize_text(haystack)
    return {n for n in needles if n and normalize_text(n) in normalized}


def extract_keyword_strings(keywords: Iterable[Any], *, max_count: int = 24) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for kw in keywords:
        value = getattr(kw, "keyword", kw)
        text = str(value or "").strip()
        key = normalize_text(text)
        if text and key not in seen:
            seen.add(key)
            out.append(text)
        if len(out) >= max_count:
            break
    return out


def build_alias_map(profile: dict) -> dict[str, set[str]]:
    aliases: dict[str, set[str]] = {}
    raw = profile.get("job_matching_keywords") or {}

    def add(term: Any, alias_values: Iterable[Any] = ()) -> None:
        key = normalize_text(term)
        if not key:
            return
        bucket = aliases.setdefault(key, set())
        bucket.add(key)
        for alias in alias_values:
            alias_key = normalize_text(alias)
            if alias_key:
                bucket.add(alias_key)

    if isinstance(raw, dict):
        for key, value in raw.items():
            if isinstance(value, dict):
                values = []
                for field in ("aliases", "keywords", "terms", "synonyms"):
                    field_value = value.get(field)
                    if isinstance(field_value, list):
                        values.extend(field_value)
                    elif field_value:
                        values.append(field_value)
                add(key, values)
            elif isinstance(value, list):
                add(key, value)
            else:
                add(key, [value])
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                term = item.get("keyword") or item.get("term") or item.get("name") or item.get("text")
                aliases_raw = item.get("aliases") or item.get("synonyms") or []
                aliases_list = aliases_raw if isinstance(aliases_raw, list) else [aliases_raw]
                add(term, aliases_list)
            else:
                add(item)
    return aliases


def expand_with_aliases(terms: Iterable[str], alias_map: dict[str, set[str]]) -> set[str]:
    expanded = {normalize_text(term) for term in terms if normalize_text(term)}
    for term in list(expanded):
        for canonical, aliases in alias_map.items():
            if term == canonical or term in aliases:
                expanded.update(aliases)
                expanded.add(canonical)
    return expanded
