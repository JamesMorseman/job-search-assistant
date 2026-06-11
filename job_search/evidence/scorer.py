"""Deterministic evidence scoring."""

from __future__ import annotations

import re
from dataclasses import dataclass

from job_search.models import CanonicalJob

from .discipline import RoleClassification
from .keywords import expand_with_aliases, normalize_text, phrase_hits, tokenize
from .types import EvidenceItem, EvidenceScore


@dataclass(frozen=True)
class ScoreContext:
    job: CanonicalJob
    jd: str
    keyword_terms: list[str]
    alias_map: dict[str, set[str]]
    classification: RoleClassification


class EvidenceScorer:
    def score_all(self, items: list[EvidenceItem], context: ScoreContext) -> list[EvidenceScore]:
        scored = [self.score(item, context) for item in items]
        return sorted(scored, key=lambda s: s.score, reverse=True)

    def score(self, item: EvidenceItem, context: ScoreContext) -> EvidenceScore:
        reasons: list[str] = []
        item_text = " ".join([
            item.text,
            " ".join(item.tags),
            " ".join(item.disciplines),
            " ".join(item.role_families),
            " ".join(item.skills),
            " ".join(item.tools),
            " ".join(item.methods),
        ])
        item_tokens = tokenize(item_text)
        jd_terms = expand_with_aliases(context.keyword_terms, context.alias_map)

        score = 0.0
        overlaps = item_tokens & jd_terms
        if overlaps:
            score += min(3.0, 0.45 * len(overlaps))
            reasons.append("keyword_overlap")

        alias_hits = self._alias_hits(item_text, jd_terms)
        if alias_hits:
            score += min(2.0, 0.35 * len(alias_hits))
            reasons.append("alias_match")

        family = context.classification.role_family
        if family != "general_civil":
            if family in {normalize_text(v) for v in item.role_families + item.disciplines + item.tags}:
                score += 2.5
                reasons.append("role_family_match")
            elif family.replace("_", " ") in normalize_text(item_text):
                score += 1.7
                reasons.append("discipline_text_match")
        else:
            score += 0.4

        jd_text = normalize_text(context.jd)
        tool_hits = phrase_hits(item.tools + [t for t in item.tags if self._looks_like_tool(t)], jd_text)
        if tool_hits:
            score += min(1.5, 0.5 * len(tool_hits))
            reasons.append("tool_match")

        method_hits = phrase_hits(item.methods + [m for m in item.tags if self._looks_like_method(m)], jd_text)
        if method_hits:
            score += min(1.2, 0.4 * len(method_hits))
            reasons.append("method_match")

        if item.evidence_type in {"project", "coursework"} and (overlaps or family in normalize_text(item_text)):
            score += 1.0
            reasons.append("project_or_coursework_relevance")

        if item.evidence_type in {"resume_bullet", "cover_fragment", "role_fragment"}:
            score += 0.5
            reasons.append("strong_fragment_type")

        score += max(0.0, min(1.0, item.confidence)) * 0.5

        mismatch = self._mismatch_penalty(item, context)
        if mismatch:
            score -= mismatch
            reasons.append("mismatch_penalty")

        return EvidenceScore(item=item, score=round(max(score, 0.0), 4), reasons=reasons)

    @staticmethod
    def _alias_hits(item_text: str, expanded_terms: set[str]) -> set[str]:
        normalized = normalize_text(item_text)
        return {term for term in expanded_terms if len(term) > 2 and term in normalized}

    @staticmethod
    def _looks_like_tool(value: str) -> bool:
        text = normalize_text(value)
        return any(hint in text for hint in ["autocad", "civil 3d", "revit", "ram", "gis", "excel", "project", "bluebeam", "hec"])

    @staticmethod
    def _looks_like_method(value: str) -> bool:
        text = normalize_text(value)
        return any(hint in text for hint in ["analysis", "design", "scheduling", "estimating", "inspection", "documentation", "coordination"])

    @staticmethod
    def _mismatch_penalty(item: EvidenceItem, context: ScoreContext) -> float:
        jd = normalize_text(context.jd)
        text = normalize_text(item.text)
        penalty = 0.0
        if re.search(r"\b(pe|professional engineer)\b", jd) and "not eligible" in text:
            penalty += 1.5
        if re.search(r"\b(5|6|7|8|9|10)\+?\s+years?\b", jd) and "entry" in text:
            penalty += 1.0
        return penalty
