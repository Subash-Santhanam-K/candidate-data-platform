from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID
from typing import Any


@dataclass
class Decision:
    """Represents a reasoning decision made for a specific field of the candidate profile.

    Attributes:
        field_name (str): The name of the field this decision applies to.
        selected_value (Any): The resolved value chosen for this field.
        confidence (float): The calculated confidence score for the selected value.
        decision_state (str): The status or state of this decision (e.g., 'resolved', 'conflict', 'manual').
        observation_references (list[UUID]): List of UUIDs of observations that support or contributed to this decision.
        policy_references (list[str]): List of identifiers of the policies applied to reach this decision.
        reason (str): Human-readable explanation of why this decision was made.
    """
    field_name: str
    selected_value: Any
    confidence: float
    decision_state: str
    observation_references: list[UUID]
    policy_references: list[str]
    reason: str
