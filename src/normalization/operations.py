import unicodedata
from typing import Any


class TrimOperation:
    """Removes leading and trailing whitespace from string values."""

    def apply(self, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value


class LowercaseOperation:
    """Converts string values to lowercase."""

    def apply(self, value: Any) -> Any:
        if isinstance(value, str):
            return value.lower()
        return value


class RemoveWhitespaceOperation:
    """Removes all whitespace characters from string values."""

    def apply(self, value: Any) -> Any:
        if isinstance(value, str):
            return "".join(value.split())
        return value


class RemoveSeparatorOperation:
    """Removes common delimiters and punctuation from string values."""

    def apply(self, value: Any) -> Any:
        if isinstance(value, str):
            separators = "-.()/\\, "
            translation_table = str.maketrans("", "", separators)
            return value.translate(translation_table)
        return value


class UnicodeNormalizationOperation:
    """Applies standard Unicode NFKC normalization to string values."""

    def apply(self, value: Any) -> Any:
        if isinstance(value, str):
            return unicodedata.normalize("NFKC", value)
        return value
