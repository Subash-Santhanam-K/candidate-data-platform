from __future__ import annotations
from ..core.enums import FieldType
from ..core.models.observation import Observation
from ..registries.field_definition import FieldDefinition
from ..registries.field_registry import FieldDefinitionRegistry
from .base import BaseNormalizer
from .strategies import (
    DefaultNormalizer,
    EmailNormalizer,
    PhoneNormalizer,
    SkillNormalizer,
    DateNormalizer,
)


class NormalizationEngine:
    """Orchestrator selecting and executing field-specific normalizers on observations."""

    def __init__(self, field_registry: FieldDefinitionRegistry) -> None:
        """Initializes the normalization engine.

        Args:
            field_registry (FieldDefinitionRegistry): Metadata field catalog definition registry.
        """
        self._field_registry = field_registry
        self._default = DefaultNormalizer()
        self._strategies: dict[FieldType, BaseNormalizer] = {
            FieldType.EMAIL: EmailNormalizer(),
            FieldType.PHONE: PhoneNormalizer(),
            FieldType.SKILL: SkillNormalizer(),
            # Fallbacks are resolved dynamically to the default normalizer
        }

    def normalize(self, observations: list[Observation]) -> list[Observation]:
        """Runs the normalizer mapping logic on each observation's raw_value.

        Modifies the 'normalized_value' field on each observation in place.
        Preserves 'raw_value' unmodified.

        Args:
            observations (list[Observation]): The candidate observations to normalize.

        Returns:
            list[Observation]: The same list of observations with normalized_value updated.
        """
        for obs in observations:
            normalizer = self._strategies.get(obs.field_type, self._default)
            obs.normalized_value = normalizer.normalize(obs.raw_value)
        return observations
