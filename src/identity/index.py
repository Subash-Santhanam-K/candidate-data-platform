from __future__ import annotations
from typing import Any
from ..core.enums import FieldType
from ..core.models.observation import Observation


class IdentityIndex:
    """Indexes observations by normalized identity values for EMAIL and PHONE."""

    def __init__(self) -> None:
        """Initializes the IdentityIndex."""
        self._groups: dict[str, list[Observation]] = {}
        self._supported_fields = {FieldType.EMAIL, FieldType.PHONE}

    def add(self, observation: Observation) -> None:
        """Adds an observation to the index if it is a supported identity field.

        Args:
            observation (Observation): The observation to add.
        """
        if observation.field_type not in self._supported_fields:
            return

        val = observation.normalized_value
        if val is None:
            return

        if isinstance(val, str):
            val_str = val.strip()
            if not val_str:
                return
        elif hasattr(val, "__len__") and len(val) == 0:
            return
        else:
            val_str = str(val).strip()
            if not val_str:
                return

        # Use the normalized string representation as the key
        if val_str not in self._groups:
            self._groups[val_str] = []
        self._groups[val_str].append(observation)

    def groups(self) -> dict[str, list[Observation]]:
        """Returns the dictionary mapping identity keys to lists of observations.

        Returns:
            dict[str, list[Observation]]: The identity groups dictionary.
        """
        return self._groups
