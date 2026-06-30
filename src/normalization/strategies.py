from typing import Any
from datetime import datetime
from .base import BaseNormalizer
from .operations import (
    TrimOperation,
    LowercaseOperation,
    RemoveSeparatorOperation,
    UnicodeNormalizationOperation,
)


class DefaultNormalizer(BaseNormalizer):
    """Fallback normalizer applying standard trimming and Unicode normalization."""

    def __init__(self) -> None:
        self._ops = [
            TrimOperation(),
            UnicodeNormalizationOperation(),
        ]

    def normalize(self, value: Any) -> Any:
        val = value
        for op in self._ops:
            val = op.apply(val)
        return val


class EmailNormalizer(BaseNormalizer):
    """Strategy for email normalization: lowercase, trim, and unicode normalization."""

    def __init__(self) -> None:
        self._ops = [
            TrimOperation(),
            UnicodeNormalizationOperation(),
            LowercaseOperation(),
        ]

    def normalize(self, value: Any) -> Any:
        val = value
        for op in self._ops:
            val = op.apply(val)
        return val


class PhoneNormalizer(BaseNormalizer):
    """Strategy for phone normalization: trim, unicode normalization, and separator removal."""

    def __init__(self) -> None:
        self._ops = [
            TrimOperation(),
            UnicodeNormalizationOperation(),
            RemoveSeparatorOperation(),
        ]

    def normalize(self, value: Any) -> Any:
        val = value
        for op in self._ops:
            val = op.apply(val)
        return val


class SkillNormalizer(BaseNormalizer):
    """Strategy for skills lists and individual strings normalization."""

    def __init__(self) -> None:
        self._trim = TrimOperation()
        self._unicode = UnicodeNormalizationOperation()
        self._lowercase = LowercaseOperation()

    def normalize(self, value: Any) -> Any:
        if isinstance(value, list):
            return [self._normalize_single(item) for item in value]
        return self._normalize_single(value)

    def _normalize_single(self, val: Any) -> Any:
        if isinstance(val, str):
            val = self._trim.apply(val)
            val = self._unicode.apply(val)
            val = self._lowercase.apply(val)
        return val


class DateNormalizer(BaseNormalizer):
    """Strategy for parsing and standardizing date values to ISO YYYY-MM-DD format."""

    def __init__(self) -> None:
        self._trim = TrimOperation()

    def normalize(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        cleaned = self._trim.apply(value)
        # Attempt standard formatting conversions
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m", "%B %Y"):
            try:
                dt = datetime.strptime(cleaned, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
        return cleaned
