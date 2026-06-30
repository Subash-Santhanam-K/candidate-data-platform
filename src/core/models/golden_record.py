from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID
from typing import Any
from .decision import Decision


@dataclass(slots=True)
class GoldenRecord:
    """Represents the canonical candidate profile generated from all decisions.

    Attributes:
        candidate_id (UUID): Unique identifier of the candidate.
        version (int): The version of the golden record.
        decisions (list[Decision]): Decisions made for each attribute of the candidate.
        metadata (dict[str, Any]): Metadata about the golden record.
    """
    candidate_id: UUID
    version: int
    decisions: list[Decision] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

