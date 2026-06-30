from __future__ import annotations
from typing import Any
from uuid import uuid4
from ..core.enums import DecisionState, MergeStrategy
from ..core.models.decision import Decision
from .context import DecisionContext
from .selection import SelectionResult
from ..config.configuration_models import ConfidenceConfig as ConfidenceConfiguration


class DecisionBuilder:
    """Builds Decision domain objects from selected values and confidence scores."""

    def __init__(self, config: ConfidenceConfiguration) -> None:
        """Initializes the DecisionBuilder.

        Args:
            config (ConfidenceConfiguration): Confidence configuration containing thresholds.
        """
        self._config = config

    def build(
        self,
        context: DecisionContext,
        selection: SelectionResult,
        confidence: float,
    ) -> Decision:
        """Constructs a validated field Decision object.

        Args:
            context (DecisionContext): Context of the field.
            selection (SelectionResult): Selected observations and reason.
            confidence (float): Confidence score for the field.

        Returns:
            Decision: The finalized Decision.
        """
        # Determine value based on MergeStrategy
        strategy = context.field_definition.merge_strategy
        selected_value: Any = None

        if selection.selected_observations:
            if strategy == MergeStrategy.SINGLE_VALUE:
                selected_value = selection.selected_observations[0].normalized_value
            elif strategy == MergeStrategy.UNION:
                unique_vals = set()
                for o in selection.selected_observations:
                    if isinstance(o.normalized_value, list):
                        unique_vals.update(o.normalized_value)
                    elif o.normalized_value is not None:
                        unique_vals.add(o.normalized_value)
                selected_value = sorted(list(unique_vals))
            elif strategy == MergeStrategy.TIMELINE:
                selected_value = [o.normalized_value for o in selection.selected_observations]

        # Determine decision state based on thresholds
        thresholds = self._config.thresholds
        if confidence >= thresholds.accepted:
            state = DecisionState.ACCEPTED
        elif confidence >= thresholds.uncertain:
            state = DecisionState.UNCERTAIN
        else:
            state = DecisionState.REJECTED

        obs_refs = [o.id for o in selection.selected_observations]

        return Decision(
            decision_id=uuid4(),
            field_name=context.field_definition.canonical_name,
            selected_value=selected_value,
            confidence=confidence,
            decision_state=state,
            reason=selection.reason,
            observation_references=obs_refs,
            policy_references=[strategy.name],
        )
