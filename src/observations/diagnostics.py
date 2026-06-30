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
class SkippedAttribute:
    """Represents an attribute skipped due to unusable value content.

    Attributes:
        raw_attribute (Any): The raw attribute object.
        reason (str): Reason for skipping (e.g. EMPTY_VALUE, NULL_VALUE).
    """
    raw_attribute: Any
    reason: str


@dataclass(slots=True, frozen=True)
class ObservationBuildResult:
    """Represents the results of translating raw document attributes to observations.

    Attributes:
        observations (list[Observation]): Successfully constructed observations.
        warnings (list[str]): Build execution warnings.
        ignored_attributes (list[IgnoredAttribute]): Attributes that were ignored.
        skipped_attributes (list[SkippedAttribute]): Attributes that were skipped.
    """
    observations: list[Observation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    ignored_attributes: list[IgnoredAttribute] = field(default_factory=list)
    skipped_attributes: list[SkippedAttribute] = field(default_factory=list)
