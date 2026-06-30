from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProcessingReport:
    """Represents stats, warnings, errors, and conflicts encountered during pipeline execution.

    Attributes:
        warnings (list[str]): List of warning messages.
        errors (list[str]): List of error messages.
        conflicts (list[dict[str, Any]]): List of data conflicts identified during processing.
        statistics (dict[str, Any]): Dictionary of execution statistics (e.g., execution time).
    """
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)

