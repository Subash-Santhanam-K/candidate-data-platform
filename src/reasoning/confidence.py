from __future__ import annotations
from typing import Any
from .context import DecisionContext
from .selection import SelectionResult
from ..core.models.observation import Observation
from ..registries.source_registry import SourceRegistry
from ..config.configuration_models import ConfidenceConfig as ConfidenceConfiguration


class ConfidenceCalculator:
    """Estimates the confidence score of a resolved decision value."""

    def __init__(
        self,
        config: ConfidenceConfiguration,
        source_registry: SourceRegistry | None = None,
    ) -> None:
        """Initializes the confidence calculator with weights configurations.

        Args:
            config (ConfidenceConfiguration): Injected weights/thresholds config.
            source_registry (SourceRegistry | None): Injected source metadata registry.
        """
        self._config = config
        self._source_registry = source_registry

    def calculate(self, context: DecisionContext, selection: SelectionResult) -> float:
        """Calculates a weighted average confidence score from 0.0 to 1.0.

        Args:
            context (DecisionContext): Context of the field.
            selection (SelectionResult): Selected observations.

        Returns:
            float: Combined confidence score.
        """
        if not selection.selected_observations:
            return 0.0

        weights = self._config.weights

        score_agreement = self._compute_agreement_score(context, selection)
        score_val = self._compute_validation_score(selection)
        score_rel = self._compute_source_reliability_score(selection)
        score_fresh = self._compute_freshness_score(selection)

        # Weighted Average Calculation
        num = (
            weights.agreement * score_agreement
            + weights.validation * score_val
            + weights.source_reliability * score_rel
            + weights.freshness * score_fresh
        )
        den = (
            weights.agreement
            + weights.validation
            + weights.source_reliability
            + weights.freshness
        )

        return num / den if den > 0 else 0.0

    def _compute_agreement_score(self, context: DecisionContext, selection: SelectionResult) -> float:
        """Computes the agreement consensus ratio among observations."""
        selected_obs = selection.selected_observations
        if len(selected_obs) == 1:
            sel_val = selected_obs[0].normalized_value
            matches = sum(1 for o in context.observations if o.normalized_value == sel_val)
            return matches / len(context.observations) if context.observations else 1.0
        return 1.0

    def _compute_validation_score(self, selection: SelectionResult) -> float:
        """Computes the average validation score of selected observations."""
        val_scores = []
        for obs in selection.selected_observations:
            res = obs.validation_result
            if res is None:
                val_scores.append(1.0)
            elif hasattr(res, "score"):
                val_scores.append(res.score)
            elif isinstance(res, dict):
                val_scores.append(res.get("score", 1.0))
            else:
                val_scores.append(1.0)
        return sum(val_scores) / len(val_scores) if val_scores else 1.0

    def _compute_source_reliability_score(self, selection: SelectionResult) -> float:
        """Computes the average source reliability score of selected observations."""
        rel_scores = []
        for obs in selection.selected_observations:
            rel_scores.append(self._get_reliability(obs))
        return sum(rel_scores) / len(rel_scores) if rel_scores else 1.0

    def _compute_freshness_score(self, selection: SelectionResult) -> float:
        """Computes the freshness score of selected observations (placeholder constant)."""
        return 1.0

    def _get_reliability(self, obs: Observation) -> float:
        """Lookup reliability score for the observation source type."""
        if not self._source_registry or not isinstance(obs.provenance, dict):
            return 0.0
        source_type = obs.provenance.get("source")
        if not source_type:
            return 0.0
        try:
            return self._source_registry.get(source_type).reliability
        except Exception:
            return 0.0
