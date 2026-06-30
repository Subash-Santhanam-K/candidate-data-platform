from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from ..core.enums import ProjectionProfile


@dataclass(slots=True)
class ProjectionResult:
    """Represents the dictionary outcome of projecting a GoldenRecord.

    Attributes:
        profile (ProjectionProfile): The profile type projected.
        projected_data (dict[str, Any]): The structured projected view payload.
    """
    profile: ProjectionProfile
    projected_data: dict[str, Any]
