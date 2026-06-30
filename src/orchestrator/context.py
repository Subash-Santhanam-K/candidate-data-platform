from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from ..adapters.models import RawCandidateDocument
from ..core.models.observation import Observation
from ..core.models.candidate_cluster import CandidateCluster
from ..core.models.golden_record import GoldenRecord


@dataclass(slots=True)
class PipelineContext:
    """Internal orchestrator workflow state capturing intermediate objects.

    Attributes:
        raw_documents (list[RawCandidateDocument]): Input raw candidate documents.
        observations (list[Observation]): Extracted and prepared candidate observations.
        candidate_clusters (list[CandidateCluster]): Resolved candidate identity groupings.
        golden_records (list[GoldenRecord]): Consolidated candidate profiles.
        projected_results (list[dict[str, Any]]): Resulting dictionary representations.
    """
    raw_documents: list[RawCandidateDocument] = field(default_factory=list)
    observations: list[Observation] = field(default_factory=list)
    candidate_clusters: list[CandidateCluster] = field(default_factory=list)
    golden_records: list[GoldenRecord] = field(default_factory=list)
    projected_results: list[dict[str, Any]] = field(default_factory=list)
