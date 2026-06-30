from __future__ import annotations
from dataclasses import dataclass
from ..core.models.candidate_cluster import CandidateCluster
from ..registries.field_definition import FieldDefinition
from ..core.models.observation import Observation


@dataclass(slots=True)
class DecisionContext:
    """Internal context for reasoning about a single canonical field.

    Attributes:
        candidate_cluster (CandidateCluster): The CandidateCluster being processed.
        field_definition (FieldDefinition): Metadata properties for the canonical field.
        observations (list[Observation]): The candidate observations for this specific field.
    """
    candidate_cluster: CandidateCluster
    field_definition: FieldDefinition
    observations: list[Observation]
