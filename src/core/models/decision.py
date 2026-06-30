from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID
from typing import Any
from ..enums import DecisionState


@dataclass(slots=True)
class Decision:
    """Represents a reasoning decision made for a specific field of the candidate profile.

    Attributes:
        decision_id (UUID): Unique identifier of the decision.
        field_name (str): The name of the field this decision applies to.
        selected_value (Any): The resolved value chosen for this field.
        confidence (float): The calculated confidence score for the selected value.
        decision_state (DecisionState): The status or state of this decision.
        reason (str): Human-readable explanation of why this decision was made.
        observation_references (list[UUID]): List of UUIDs of observations that support or contributed to this decision.
        policy_references (list[str]): List of identifiers of the policies applied to reach this decision.
    """
    decision_id: UUID
    field_name: str
    selected_value: Any
    confidence: float
    decision_state: DecisionState
    reason: str
    observation_references: list[UUID] = field(default_factory=list)
    policy_references: list[str] = field(default_factory=list)

