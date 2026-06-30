from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID
from ..core.enums import FieldType
from ..core.models.observation import Observation


@dataclass(slots=True)
class IdentityCandidate:
    """Internal candidate representation grouping observations by source instance.

    Attributes:
        source_instance_id (UUID): The original SourceInstance identifier.
        observations (list[Observation]): The complete list of observations from this source.
        identity_keys (dict[FieldType, str]): Mapped normalized identity keys (EMAIL, PHONE).
    """
    source_instance_id: UUID
    observations: list[Observation]
    identity_keys: dict[FieldType, str] = field(default_factory=dict)
