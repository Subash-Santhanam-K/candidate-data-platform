from __future__ import annotations
from uuid import uuid4
from ..core.models.candidate_cluster import CandidateCluster
from .candidate import IdentityCandidate


class ClusterBuilder:
    """Builds CandidateCluster domain objects from merged IdentityCandidates."""

    def build(self, candidates: list[IdentityCandidate]) -> CandidateCluster:
        """Converts grouped candidates into a single CandidateCluster.

        Collates observations across all candidates and ensures uniqueness.

        Args:
            candidates (list[IdentityCandidate]): The merged candidates.

        Returns:
            CandidateCluster: The constructed domain cluster.
        """
        obs_by_id = {}
        for cand in candidates:
            for obs in cand.observations:
                obs_by_id[obs.id] = obs

        return CandidateCluster(
            cluster_id=uuid4(),
            observations=list(obs_by_id.values()),
        )
