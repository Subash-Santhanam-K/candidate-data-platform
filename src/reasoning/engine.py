from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID
from ..core.enums import MergeStrategy
from ..core.models.candidate_cluster import CandidateCluster
from ..core.models.golden_record import GoldenRecord
from ..core.models.decision import Decision
from ..core.models.observation import Observation
from ..registries.field_registry import FieldDefinitionRegistry
from ..registries.source_registry import SourceRegistry
from ..config.configuration_models import (
    ConfidenceConfig as ConfidenceConfiguration,
    MergeConfig as MergeConfiguration,
)
from .context import DecisionContext
from .selection import SelectionResult
from .strategies import (
    BaseMergeStrategy,
    SingleValueStrategy,
    UnionStrategy,
    TimelineStrategy,
)
from .confidence import ConfidenceCalculator
from .decision_builder import DecisionBuilder


class ReasoningEngine:
    """Orchestrates candidate attribute conflict resolution and profile assembly."""

    def __init__(
        self,
        field_registry: FieldDefinitionRegistry,
        source_registry: SourceRegistry,
        confidence_config: ConfidenceConfiguration,
        merge_config: MergeConfiguration,
    ) -> None:
        """Initializes the reasoning engine with config parameters and lookup catalogs.

        Args:
            field_registry (FieldDefinitionRegistry): Metadata field catalog definition registry.
            source_registry (SourceRegistry): Metadata input source catalog registry.
            confidence_config (ConfidenceConfiguration): Confidence configuration.
            merge_config (MergeConfiguration): Merge strategy configuration.
        """
        self._field_registry = field_registry
        self._source_registry = source_registry
        self._confidence_config = confidence_config
        self._merge_config = merge_config

        # Initialize strategies registry
        self._strategies: dict[MergeStrategy, BaseMergeStrategy] = {
            MergeStrategy.SINGLE_VALUE: SingleValueStrategy(self._source_registry),
            MergeStrategy.UNION: UnionStrategy(),
            MergeStrategy.TIMELINE: TimelineStrategy(),
        }

        # Initialize helper modules
        self._confidence_calculator = ConfidenceCalculator(
            self._confidence_config,
            self._source_registry,
        )
        self._decision_builder = DecisionBuilder(self._confidence_config)

    def reason(self, cluster: CandidateCluster) -> GoldenRecord:
        """Processes a CandidateCluster and returns its resolved GoldenRecord.

        Only reasons over fields that actually exist in the cluster observations.

        Args:
            cluster (CandidateCluster): The candidate cluster of observations.

        Returns:
            GoldenRecord: The resolved candidate profile.
        """
        # 1. Group observations by canonical field name
        obs_by_field: dict[str, list[Observation]] = {}
        for obs in cluster.observations:
            if obs.field_name not in obs_by_field:
                obs_by_field[obs.field_name] = []
            obs_by_field[obs.field_name].append(obs)

        decisions: list[Decision] = []

        # 2. Process only fields present in the CandidateCluster
        for field_name, field_obs in obs_by_field.items():
            try:
                field_defn = self._field_registry.resolve(field_name)
            except KeyError:
                continue

            context = DecisionContext(
                candidate_cluster=cluster,
                field_definition=field_defn,
                observations=field_obs,
            )

            strategy = self._strategies[field_defn.merge_strategy]
            selection = strategy.select(context)
            confidence = self._confidence_calculator.calculate(context, selection)
            decision = self._decision_builder.build(context, selection, confidence)

            decisions.append(decision)

        # 3. Construct and return GoldenRecord
        return GoldenRecord(
            candidate_id=cluster.cluster_id,
            version=1,
            decisions=decisions,
            metadata={"generated_at": datetime.now(timezone.utc).isoformat()},
        )
