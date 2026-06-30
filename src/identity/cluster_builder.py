from __future__ import annotations
from uuid import uuid4
from ..core.models.candidate_cluster import CandidateCluster
from ..core.models.observation import Observation


class ClusterBuilder:
    """Builds CandidateCluster domain objects from indexed identity groups."""

    def build(self, groups: dict[str, list[Observation]]) -> list[CandidateCluster]:
        """Converts grouped observations into CandidateCluster objects.

        Args:
            groups (dict[str, list[Observation]]): Grouped observations dictionary.

        Returns:
            list[CandidateCluster]: Constructed candidate clusters.
        """
        clusters: list[CandidateCluster] = []
        for obs_list in groups.values():
            if not obs_list:
                continue
            cluster = CandidateCluster(
                cluster_id=uuid4(),
                observations=list(obs_list),
            )
            clusters.append(cluster)
        return clusters
