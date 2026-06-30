from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID
from .observation import Observation


@dataclass
class DecisionTrace:
    """Stores explanation details and steps taken during a reasoning decision.

    Attributes:
        decision_id (UUID): Identifier of the decision this trace describes.
        observations_used (list[Observation]): The list of observations evaluated to make the decision.
        policies_used (list[str]): The list of policies referenced or applied.
        reasoning_steps (list[str]): Sequential log of steps taken by the reasoning engine.
    """
    decision_id: UUID
    observations_used: list[Observation]
    policies_used: list[str]
    reasoning_steps: list[str]
