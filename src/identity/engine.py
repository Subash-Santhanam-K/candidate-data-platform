from __future__ import annotations
from ..core.models.candidate_cluster import CandidateCluster
from ..core.models.observation import Observation
from .index import IdentityIndex
from .cluster_builder import ClusterBuilder


class IdentityEngine:
    """Orchestrates candidate identity resolution and clustering."""

    def resolve(self, observations: list[Observation]) -> list[CandidateCluster]:
        """Resolves observations into candidate clusters in O(n) time.

        Args:
            observations (list[Observation]): Input observations to resolve.

        Returns:
            list[CandidateCluster]: Grouped candidate clusters.
        """
        index = IdentityIndex()
        for obs in observations:
            index.add(obs)

        builder = ClusterBuilder()
        return builder.build(index.groups())
