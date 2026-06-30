from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from ..core.enums import ProjectionProfile
from .context import ProjectionContext
from .result import ProjectionResult


class BaseProjectionStrategy(ABC):
    """Abstract base class for GoldenRecord projection strategies."""

    @abstractmethod
    def project(self, context: ProjectionContext) -> ProjectionResult:
        """Projects a GoldenRecord into a filtered dictionary structure.

        Args:
            context (ProjectionContext): The projection context configuration.

        Returns:
            ProjectionResult: The projected dictionary result.
        """
        pass


class MinimalProjectionStrategy(BaseProjectionStrategy):
    """Strategy filtering GoldenRecord down to minimal profile fields."""

    def project(self, context: ProjectionContext) -> ProjectionResult:
        include_fields = context.projection_configuration.include
        include_all = "*" in include_fields

        projected = {}
        for decision in context.golden_record.decisions:
            if include_all or decision.field_name in include_fields:
                projected[decision.field_name] = decision.selected_value

        return ProjectionResult(
            profile=ProjectionProfile.MINIMAL,
            projected_data=projected,
        )


class RecruiterProjectionStrategy(BaseProjectionStrategy):
    """Strategy filtering GoldenRecord down to recruiter profile fields + confidence scores."""

    def project(self, context: ProjectionContext) -> ProjectionResult:
        include_fields = context.projection_configuration.include
        include_all = "*" in include_fields

        projected = {}
        confidence = {}
        for decision in context.golden_record.decisions:
            if include_all or decision.field_name in include_fields:
                projected[decision.field_name] = decision.selected_value
                confidence[decision.field_name] = decision.confidence

        projected["confidence"] = confidence

        return ProjectionResult(
            profile=ProjectionProfile.RECRUITER,
            projected_data=projected,
        )


class AuditProjectionStrategy(BaseProjectionStrategy):
    """Strategy exposing all GoldenRecord fields, confidence, and full decision traces."""

    def project(self, context: ProjectionContext) -> ProjectionResult:
        include_fields = context.projection_configuration.include
        include_all = "*" in include_fields

        projected = {}
        confidence = {}
        trace = {}
        for decision in context.golden_record.decisions:
            if include_all or decision.field_name in include_fields:
                projected[decision.field_name] = decision.selected_value
                confidence[decision.field_name] = decision.confidence
                trace[decision.field_name] = {
                    "decision_id": str(decision.decision_id),
                    "decision_state": decision.decision_state.value,
                    "reason": decision.reason,
                    "observation_references": [str(r) for r in decision.observation_references],
                    "policy_references": decision.policy_references,
                }

        projected["confidence"] = confidence
        projected["decision_trace"] = trace

        return ProjectionResult(
            profile=ProjectionProfile.AUDIT,
            projected_data=projected,
        )
