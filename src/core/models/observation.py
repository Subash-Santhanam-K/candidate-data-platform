from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Any


@dataclass
class Observation:
    """Represents a fact claimed by a data source regarding a candidate attribute.

    Attributes:
        id (UUID): Unique identifier of the observation.
        source_id (UUID): Identifier of the SourceInstance that claimed this attribute.
        field_name (str): The candidate attribute/field name (e.g., 'email', 'name').
        raw_value (Any): The original value extracted from the source.
        normalized_value (Any | None): The normalized representation of the raw value.
        status (str): The current status of the observation (e.g., 'raw', 'normalized', 'valid', 'invalid').
        provenance (dict[str, Any]): Source-specific details on how the value was extracted.
        validation_result (dict[str, Any] | None): Validation logs, checks passed, or errors found.
        timestamp (datetime): The timestamp when the observation was recorded or extracted.
    """
    id: UUID
    source_id: UUID
    field_name: str
    raw_value: Any
    normalized_value: Any | None
    status: str
    provenance: dict[str, Any]
    validation_result: dict[str, Any] | None
    timestamp: datetime
