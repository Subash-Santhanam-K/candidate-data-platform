from abc import ABC, abstractmethod
from typing import Any
from .result import ValidationResult


class BaseRule(ABC):
    """Abstract base class for validation rule conditions."""

    @abstractmethod
    def evaluate(self, value: Any) -> tuple[bool, list[str]]:
        """Evaluates a normalized value against a single rule condition.

        Args:
            value (Any): The normalized value to check.

        Returns:
            tuple[bool, list[str]]: A tuple of (passed, messages).
        """
        pass


class BaseValidator(ABC):
    """Abstract base class for validation execution composed of rules."""

    @abstractmethod
    def validate(self, value: Any) -> ValidationResult:
        """Validates a normalized value against composed rules.

        Args:
            value (Any): The normalized value to validate.

        Returns:
            ValidationResult: The resulting validation score and metadata.
        """
        pass
