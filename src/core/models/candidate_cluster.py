from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID
from .observation import Observation


@dataclass(slots=True)
class CandidateCluster:
    """Represents a grouping of observations resolved to a single candidate.

    Attributes:
        cluster_id (UUID): Unique identifier of the candidate cluster.
        observations (list[Observation]): The list of observations resolved to this candidate.
    """
    cluster_id: UUID
    observations: list[Observation] = field(default_factory=list)

