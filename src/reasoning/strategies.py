from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from .context import DecisionContext
from .selection import SelectionResult
from ..core.models.observation import Observation
from ..registries.source_registry import SourceRegistry


class BaseMergeStrategy(ABC):
    """Abstract base class for field merge/resolution strategies."""

    @abstractmethod
    def select(self, context: DecisionContext) -> SelectionResult:
        """Selects target observations for conflict resolution and constructs resolved values.

        Args:
            context (DecisionContext): Context of the field's observations.

        Returns:
            SelectionResult: The selected observations and reasoning.
        """
        pass


class SingleValueStrategy(BaseMergeStrategy):
    """Strategy resolving to a single value by validation, reliability, and age.

    EMAIL, PHONE, NAME, LOCATION.
    """

    def __init__(self, source_registry: SourceRegistry | None = None) -> None:
        """Initializes the SingleValueStrategy with an optional SourceRegistry.

        Args:
            source_registry (SourceRegistry | None): Source metadata registry.
        """
        self._source_registry = source_registry

    def select(self, context: DecisionContext) -> SelectionResult:
        # 1. Filter out observations that failed validation
        valid_obs = [obs for obs in context.observations if self._is_valid(obs)]

        if not valid_obs:
            return SelectionResult(
                selected_observations=[],
                resolved_value=None,
                reason="No valid observations found for this field.",
            )

        # 2. Sort by: reliability (descending), timestamp (descending)
        # Python's stable Timsort will group by reliability first, then newest timestamp
        sorted_obs = sorted(
            valid_obs,
            key=lambda o: (self._get_reliability(o), o.timestamp.timestamp() if o.timestamp else 0),
            reverse=True,
        )

        selected_obs = sorted_obs[0]

        return SelectionResult(
            selected_observations=[selected_obs],
            resolved_value=selected_obs.normalized_value,
            reason="Selected newest valid observation",
        )

    def _is_valid(self, obs: Observation) -> bool:
        """Determines if the observation passed validation."""
        res = obs.validation_result
        if res is None:
            return True
        if hasattr(res, "passed"):
            return res.passed
        if isinstance(res, dict):
            return res.get("passed", True)
        return True

    def _get_reliability(self, obs: Observation) -> float:
        """Retrieves reliability score for the observation source type."""
        if not self._source_registry or not isinstance(obs.provenance, dict):
            return 0.0
        source_type = obs.provenance.get("source")
        if not source_type:
            return 0.0
        try:
            return self._source_registry.get(source_type).reliability
        except Exception:
            return 0.0


class UnionStrategy(BaseMergeStrategy):
    """Strategy combining and deduplicating values.

    SKILLS, CERTIFICATIONS.
    """

    def select(self, context: DecisionContext) -> SelectionResult:
        # Select all observations that have a non-empty value
        contributing_obs = [o for o in context.observations if o.normalized_value is not None]

        unique_vals = set()
        for o in contributing_obs:
            if isinstance(o.normalized_value, list):
                unique_vals.update(o.normalized_value)
            elif o.normalized_value is not None:
                unique_vals.add(o.normalized_value)

        resolved_value = sorted(list(unique_vals))

        return SelectionResult(
            selected_observations=contributing_obs,
            resolved_value=resolved_value,
            reason="Selected union of unique normalized values",
        )


class TimelineStrategy(BaseMergeStrategy):
    """Strategy sorting values chronologically.

    EXPERIENCE, EDUCATION.
    """

    def select(self, context: DecisionContext) -> SelectionResult:
        # Sort chronologically based on date keys in normalized dictionary, falling back to timestamp
        def get_date_key(obs: Observation) -> str:
            val = obs.normalized_value
            if isinstance(val, dict):
                for key in ("start_date", "start", "from", "date"):
                    if key in val and val[key]:
                        return str(val[key])
            elif isinstance(val, str):
                return val
            return ""

        sorted_obs = sorted(
            context.observations,
            key=lambda o: (get_date_key(o), o.timestamp.timestamp() if o.timestamp else 0),
        )

        resolved_value = [o.normalized_value for o in sorted_obs]

        return SelectionResult(
            selected_observations=sorted_obs,
            resolved_value=resolved_value,
            reason="Selected chronological timeline",
        )
