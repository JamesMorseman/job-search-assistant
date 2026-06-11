"""Deterministic evidence selection for grounded document generation."""

from .selector import EvidenceSelector
from .types import EvidenceItem, EvidencePacket, EvidenceScore

__all__ = ["EvidenceItem", "EvidencePacket", "EvidenceScore", "EvidenceSelector"]
