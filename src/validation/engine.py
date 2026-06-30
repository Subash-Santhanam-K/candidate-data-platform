from __future__ import annotations
from ..core.enums import FieldType
from ..core.models.observation import Observation
from .base import BaseValidator
from .validators import DefaultValidator, EmailValidator, PhoneValidator


class ValidationEngine:
    """Orchestrator selecting and executing semantic validators on normalized observation values."""

    def __init__(self) -> None:
        """Initializes the validation engine."""
        self._default = DefaultValidator()
        self._validators: dict[FieldType, BaseValidator] = {
            FieldType.EMAIL: EmailValidator(),
            FieldType.PHONE: PhoneValidator(),
            # Fallbacks resolved dynamically to default validator
        }

    def validate(self, observations: list[Observation]) -> list[Observation]:
        """Validates the normalized value of each observation in place.

        Updates 'validation_result' on each observation, preserving all other fields.

        Args:
            observations (list[Observation]): Observations list to validate.

        Returns:
            list[Observation]: The same list of observations with validation results populated.
        """
        for obs in observations:
            validator = self._validators.get(obs.field_type, self._default)
            obs.validation_result = validator.validate(obs.normalized_value)
        return observations
