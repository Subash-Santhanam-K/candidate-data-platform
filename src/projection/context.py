from __future__ import annotations
from dataclasses import dataclass
from ..core.models.golden_record import GoldenRecord
from ..config.configuration_models import ProjectionProfileConfig


@dataclass(slots=True)
class ProjectionContext:
    """Internal context for executing a projection strategy on a GoldenRecord.

    Attributes:
        golden_record (GoldenRecord): The GoldenRecord profile to project.
        projection_configuration (ProjectionProfileConfig): The configuration settings
            associated with the target projection profile.
    """
    golden_record: GoldenRecord
    projection_configuration: ProjectionProfileConfig
