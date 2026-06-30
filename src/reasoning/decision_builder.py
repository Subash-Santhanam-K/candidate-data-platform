from __future__ import annotations
from typing import Any
from uuid import uuid4
from ..core.enums import DecisionState
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
            selected_value=selection.resolved_value,
            confidence=confidence,
            decision_state=state,
            reason=selection.reason,
            observation_references=obs_refs,
            policy_references=[context.field_definition.merge_strategy.name],
        )
