from typing import Any
from .base import BaseValidator, BaseRule
from .result import ValidationResult
from .rules import RequiredRule, EmailFormatRule, PhoneFormatRule


class DefaultValidator(BaseValidator):
    """Fallback validator that performs no assertions and always passes."""

    def validate(self, value: Any) -> ValidationResult:
        return ValidationResult(
            passed=True,
            score=1.0,
            validator_name=self.__class__.__name__,
            rule_name="none",
            messages=[],
        )


class EmailValidator(BaseValidator):
    """Validator composing Required and Format validation checks for emails."""

    def __init__(self) -> None:
        self._rules: list[BaseRule] = [
            RequiredRule(),
            EmailFormatRule(),
        ]

    def validate(self, value: Any) -> ValidationResult:
        for rule in self._rules:
            passed, messages = rule.evaluate(value)
            if not passed:
                return ValidationResult(
                    passed=False,
                    score=0.0,
                    validator_name=self.__class__.__name__,
                    rule_name=rule.__class__.__name__,
                    messages=messages,
                )
        return ValidationResult(
            passed=True,
            score=1.0,
            validator_name=self.__class__.__name__,
            rule_name="all",
            messages=[],
        )


class PhoneValidator(BaseValidator):
    """Validator composing Required and Format validation checks for phone numbers."""

    def __init__(self) -> None:
        self._rules: list[BaseRule] = [
            RequiredRule(),
            PhoneFormatRule(),
        ]

    def validate(self, value: Any) -> ValidationResult:
        for rule in self._rules:
            passed, messages = rule.evaluate(value)
            if not passed:
                return ValidationResult(
                    passed=False,
                    score=0.0,
                    validator_name=self.__class__.__name__,
                    rule_name=rule.__class__.__name__,
                    messages=messages,
                )
        return ValidationResult(
            passed=True,
            score=1.0,
            validator_name=self.__class__.__name__,
            rule_name="all",
            messages=[],
        )
