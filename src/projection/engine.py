from __future__ import annotations
from typing import Any
from ..core.enums import ProjectionProfile
from ..core.models.golden_record import GoldenRecord
from ..config.configuration_models import ProjectionConfig as ProjectionConfiguration
from .context import ProjectionContext
from .result import ProjectionResult
from .strategies import (
    BaseProjectionStrategy,
    MinimalProjectionStrategy,
    RecruiterProjectionStrategy,
    AuditProjectionStrategy,
)


class ProjectionEngine:
    """Orchestrates candidate GoldenRecord projections into customized views."""

    def __init__(self, config: ProjectionConfiguration) -> None:
        """Initializes the ProjectionEngine.

        Args:
            config (ProjectionConfiguration): Injected profiles config parameters.
        """
        self._config = config
        self._strategies: dict[ProjectionProfile, BaseProjectionStrategy] = {
            ProjectionProfile.MINIMAL: MinimalProjectionStrategy(),
            ProjectionProfile.RECRUITER: RecruiterProjectionStrategy(),
            ProjectionProfile.AUDIT: AuditProjectionStrategy(),
        }

    def project(
        self,
        golden_record: GoldenRecord,
        profile: ProjectionProfile,
    ) -> dict[str, Any]:
        """Resolves target profile config, selects the strategy, and executes projection.

        Args:
            golden_record (GoldenRecord): Canonical candidate profile.
            profile (ProjectionProfile): View visibility profile enum.

        Returns:
            dict[str, Any]: Mapped candidate view properties.
        """
        profile_config = self._config.profiles.get(profile.value)
        if not profile_config:
            raise KeyError(f"Profile configuration for '{profile}' not found.")

        context = ProjectionContext(
            golden_record=golden_record,
            projection_configuration=profile_config,
        )

        strategy = self._strategies[profile]
        result = strategy.project(context)

        return result.projected_data
