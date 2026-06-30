from __future__ import annotations
from typing import Any
from ..core.enums import ProjectionProfile
from ..core.exceptions import PipelineError
from ..adapters.models import RawCandidateDocument
from ..core.models.golden_record import GoldenRecord
from ..core.models.candidate_cluster import CandidateCluster
from ..observations.builder import ObservationBuilder
from ..normalization.engine import NormalizationEngine
from ..validation.engine import ValidationEngine
from ..identity.engine import IdentityEngine
from ..reasoning.engine import ReasoningEngine
from ..projection.engine import ProjectionEngine
from .context import PipelineContext


class PipelineOrchestrator:
    """Coordinates execution of all pipeline stages from extraction to projection."""

    def __init__(
        self,
        observation_builder: ObservationBuilder,
        normalization_engine: NormalizationEngine,
        validation_engine: ValidationEngine,
        identity_engine: IdentityEngine,
        reasoning_engine: ReasoningEngine,
        projection_engine: ProjectionEngine,
    ) -> None:
        """Initializes the orchestrator with all injected dependency layers.

        Args:
            observation_builder (ObservationBuilder): Builder for candidate observations.
            normalization_engine (NormalizationEngine): Value normalization execution engine.
            validation_engine (ValidationEngine): Value validation execution engine.
            identity_engine (IdentityEngine): Identity resolution clustering engine.
            reasoning_engine (ReasoningEngine): GoldenRecord conflict resolution engine.
            projection_engine (ProjectionEngine): Target profile view projection engine.
        """
        self._observation_builder = observation_builder
        self._normalization_engine = normalization_engine
        self._validation_engine = validation_engine
        self._identity_engine = identity_engine
        self._reasoning_engine = reasoning_engine
        self._projection_engine = projection_engine

    def run(
        self,
        documents: list[RawCandidateDocument],
        profile: ProjectionProfile,
    ) -> list[dict[str, Any]]:
        """Coordinates pipeline stages and processes documents end-to-end.

        Args:
            documents (list[RawCandidateDocument]): Input raw candidate documents.
            profile (ProjectionProfile): Target visibility profile enum.

        Returns:
            list[dict[str, Any]]: Filtered and projected candidate record dicts.

        Raises:
            PipelineError: If any pipeline stage raises an unexpected exception.
        """
        try:
            context = PipelineContext(raw_documents=documents)

            self._build_observations(context)
            self._normalize(context)
            self._validate(context)
            self._resolve_identity(context)
            self._reason(context)
            self._project(context, profile)

            return context.projected_results
        except PipelineError:
            raise
        except Exception as exc:
            raise PipelineError(f"Pipeline execution failed: {str(exc)}") from exc

    def _build_observations(self, context: PipelineContext) -> None:
        """Step 1: Translates raw candidate transport documents into observations."""
        obs_list = []
        for doc in context.raw_documents:
            result = self._observation_builder.build(doc)
            obs_list.extend(result.observations)
        context.observations = obs_list

    def _normalize(self, context: PipelineContext) -> None:
        """Step 2: Normalizes raw attribute value representations."""
        context.observations = self._normalization_engine.normalize(context.observations)

    def _validate(self, context: PipelineContext) -> None:
        """Step 3: Performs semantic schema validation on normalized values."""
        context.observations = self._validation_engine.validate(context.observations)

    def _resolve_identity(self, context: PipelineContext) -> None:
        """Step 4: Merges candidate source entities based on matching identity keys."""
        context.candidate_clusters = self._identity_engine.resolve(context.observations)

    def _reason(self, context: PipelineContext) -> None:
        """Step 5: Selects best canonical values and resolves attribute conflicts."""
        context.golden_records = [
            self._reason_cluster(cluster)
            for cluster in context.candidate_clusters
        ]

    def _reason_cluster(self, cluster: CandidateCluster) -> GoldenRecord:
        """Delegates reasoning resolution for a single cluster of observations."""
        return self._reasoning_engine.reason(cluster)

    def _project(self, context: PipelineContext, profile: ProjectionProfile) -> None:
        """Step 6: Filters GoldenRecords to visible dictionary representations."""
        context.projected_results = [
            self._project_record(record, profile)
            for record in context.golden_records
        ]

    def _project_record(self, record: GoldenRecord, profile: ProjectionProfile) -> dict[str, Any]:
        """Delegates profile mapping view projection for a single GoldenRecord."""
        return self._projection_engine.project(record, profile)
