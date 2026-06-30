from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID
from typing import Any
from .decision import Decision


@dataclass
class GoldenRecord:
    """Represents the canonical candidate profile generated from all decisions.

    Attributes:
        candidate_id (UUID): Unique identifier of the candidate.
        decisions (list[Decision]): Decisions made for each attribute of the candidate.
        metadata (dict[str, Any]): Metadata about the golden record (e.g., creation timestamp, model version).
    """
    candidate_id: UUID
    decisions: list[Decision]
    metadata: dict[str, Any]
