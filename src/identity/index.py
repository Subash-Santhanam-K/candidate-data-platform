from __future__ import annotations
from ..core.enums import FieldType
from .candidate import IdentityCandidate


class IdentityIndex:
    """Indexes IdentityCandidate objects by normalized identity values for EMAIL and PHONE."""

    def __init__(self) -> None:
        """Initializes the IdentityIndex."""
        self._groups: dict[str, list[IdentityCandidate]] = {}
        self._supported_fields = {FieldType.EMAIL, FieldType.PHONE}

    def add(self, candidate: IdentityCandidate) -> None:
        """Indexes a candidate's identity keys.

        Args:
            candidate (IdentityCandidate): The candidate to index.
        """
        for field_type, val in candidate.identity_keys.items():
            if field_type not in self._supported_fields:
                continue
            if val is None:
                continue

            val_str = str(val).strip()
            if not val_str:
                continue

            # Index candidate under this key
            if val_str not in self._groups:
                self._groups[val_str] = []

            # Prevent duplicate candidate registration under the same key
            if candidate not in self._groups[val_str]:
                self._groups[val_str].append(candidate)

    def groups(self) -> dict[str, list[IdentityCandidate]]:
        """Returns the dictionary mapping identity keys to lists of candidates.

        Returns:
            dict[str, list[IdentityCandidate]]: The identity groups dictionary.
        """
        return self._groups
