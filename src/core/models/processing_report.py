from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class ProcessingReport:
    """Represents stats, warnings, errors, and conflicts encountered during pipeline execution.

    Attributes:
        warnings (list[str]): List of warning messages.
        errors (list[str]): List of error messages.
        conflicts (list[dict[str, Any]]): List of data conflicts identified during processing.
        statistics (dict[str, Any]): Dictionary of execution statistics (e.g., execution time).
    """
    warnings: list[str]
    errors: list[str]
    conflicts: list[dict[str, Any]]
    statistics: dict[str, Any]
