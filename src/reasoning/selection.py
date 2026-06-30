from __future__ import annotations
from dataclasses import dataclass
from ..core.models.observation import Observation


@dataclass(slots=True)
class SelectionResult:
    """Internal representation of selected observations and conflict resolution reason.

    Attributes:
        selected_observations (list[Observation]): The winning observation(s).
        reason (str): Explanatory reason detailing the selection process.
    """
    selected_observations: list[Observation]
    reason: str
