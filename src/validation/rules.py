import re
from typing import Any
from .base import BaseRule


class RequiredRule(BaseRule):
    """Rule verifying that a value is populated, non-null, and non-empty."""

    def evaluate(self, value: Any) -> tuple[bool, list[str]]:
        if value is None:
            return False, ["Value is required and cannot be null"]

        if isinstance(value, str):
            if not value.strip():
                return False, ["Value is required and cannot be empty or whitespace only"]
        elif hasattr(value, "__len__") and len(value) == 0:
            return False, ["Value is required and cannot be an empty collection"]

        return True, []


class EmailFormatRule(BaseRule):
    """Rule validating the string email format using regex."""

    _EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

    def evaluate(self, value: Any) -> tuple[bool, list[str]]:
        if not isinstance(value, str):
            return False, ["Email value must be a string"]

        if not self._EMAIL_REGEX.match(value):
            return False, [f"Invalid email format: '{value}'"]

        return True, []


class PhoneFormatRule(BaseRule):
    """Rule validating phone number structure using digits and optional plus prefix."""

    _PHONE_REGEX = re.compile(r"^\+?[0-9]{7,15}$")

    def evaluate(self, value: Any) -> tuple[bool, list[str]]:
        if not isinstance(value, str):
            return False, ["Phone value must be a string"]

        cleaned = value.strip()
        if not self._PHONE_REGEX.match(cleaned):
            return False, [f"Invalid phone format: '{value}'"]

        return True, []
