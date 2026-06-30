from __future__ import annotations
from uuid import UUID
from ..core.enums import FieldType
from ..core.models.candidate_cluster import CandidateCluster
from ..core.models.observation import Observation
from .candidate import IdentityCandidate
from .index import IdentityIndex
from .cluster_builder import ClusterBuilder


class DSU:
    """Disjoint Set Union (DSU) for tracking and merging candidate source components."""

    def __init__(self, candidates: list[IdentityCandidate]) -> None:
        """Initializes the DSU with each candidate as its own representative parent."""
        self.parent = {c.source_instance_id: c.source_instance_id for c in candidates}

    def find(self, item: UUID) -> UUID:
        """Finds the representative parent root for the given item."""
        if self.parent[item] == item:
            return item
        self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, item1: UUID, item2: UUID) -> None:
        """Unions the disjoint sets containing item1 and item2."""
        root1 = self.find(item1)
        root2 = self.find(item2)
        if root1 != root2:
            self.parent[root1] = root2


class IdentityEngine:
    """Orchestrates candidate identity resolution and clustering."""

    def resolve(self, observations: list[Observation]) -> list[CandidateCluster]:
        """Resolves observations into candidate clusters using transitive identity linkage.

        Groups observations by source_instance_id, indexes identity keys, merges
        connected candidates sharing keys in O(n) time, and builds clusters.

        Args:
            observations (list[Observation]): Input observations to resolve.

        Returns:
            list[CandidateCluster]: Grouped candidate clusters.
        """
        if not observations:
            return []

        # 1. Group observations by source_instance_id
        obs_by_source: dict[UUID, list[Observation]] = {}
        for obs in observations:
            if obs.source_instance_id not in obs_by_source:
                obs_by_source[obs.source_instance_id] = []
            obs_by_source[obs.source_instance_id].append(obs)

        # 2. Instantiate IdentityCandidates
        candidates: list[IdentityCandidate] = []
        for source_id, obs_list in obs_by_source.items():
            identity_keys: dict[FieldType, str] = {}
            for obs in obs_list:
                if obs.field_type in (FieldType.EMAIL, FieldType.PHONE):
                    if obs.normalized_value:
                        val_str = str(obs.normalized_value).strip()
                        if val_str:
                            identity_keys[obs.field_type] = val_str

            candidates.append(
                IdentityCandidate(
                    source_instance_id=source_id,
                    observations=obs_list,
                    identity_keys=identity_keys,
                )
            )

        # 3. Build IdentityIndex
        index = IdentityIndex()
        for candidate in candidates:
            index.add(candidate)

        # 4. Merge IdentityCandidates sharing any identity key (transitive DSU)
        dsu = DSU(candidates)
        for cand_list in index.groups().values():
            if len(cand_list) > 1:
                first_cand = cand_list[0]
                for next_cand in cand_list[1:]:
                    dsu.union(first_cand.source_instance_id, next_cand.source_instance_id)

        # Group candidates by their representative DSU roots
        merged_groups: dict[UUID, list[IdentityCandidate]] = {}
        for cand in candidates:
            root_id = dsu.find(cand.source_instance_id)
            if root_id not in merged_groups:
                merged_groups[root_id] = []
            merged_groups[root_id].append(cand)

        # 5. Build CandidateClusters
        builder = ClusterBuilder()
        clusters: list[CandidateCluster] = []
        for merged_candidates in merged_groups.values():
            cluster = builder.build(merged_candidates)
            clusters.append(cluster)

        return clusters
