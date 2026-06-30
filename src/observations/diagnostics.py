from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from ..core.models.observation import Observation


@dataclass(slots=True, frozen=True)
class IgnoredAttribute:
    """Represents an attribute ignored due to structural or metadata mismatch.

    Attributes:
        raw_attribute (Any): The raw attribute object.
        reason (str): Reason for ignoring (e.g. UNKNOWN_FIELD, EMPTY_NAME).
    """
    raw_attribute: Any
    reason: str


@dataclass(slots=True, frozen=True)
class ObservationBuildResult:
    """Represents the results of translating raw document attributes to observations.

    Attributes:
        observations (list[Observation]): Successfully constructed observations.
        ignored_attributes (list[IgnoredAttribute]): Attributes that were ignored.
    """
    observations: list[Observation] = field(default_factory=list)
    ignored_attributes: list[IgnoredAttribute] = field(default_factory=list)
