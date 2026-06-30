from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from typing import Any
from ..enums import ObservationStatus, FieldType


@dataclass(slots=True)
class Observation:
    """Represents a fact claimed by a data source regarding a candidate attribute.

    Attributes:
        id (UUID): Unique identifier of the observation.
        source_instance_id (UUID): Identifier of the SourceInstance that claimed this attribute.
        field_type (FieldType): The semantic category of the field.
        field_name (str): The candidate attribute/field name (e.g., 'primary_email').
        raw_value (Any): The original value extracted from the source.
        status (ObservationStatus): The current processing status of the observation.
        timestamp (datetime): The timestamp when the observation was recorded or extracted.
        normalized_value (Any | None): The normalized representation of the raw value.
        provenance (dict[str, Any]): Source-specific details on how the value was extracted.
        validation_result (dict[str, Any] | None): Validation logs, checks passed, or errors found.
    """
    id: UUID
    source_instance_id: UUID
    field_type: FieldType
    field_name: str
    raw_value: Any
    status: ObservationStatus
    timestamp: datetime
    normalized_value: Any | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    validation_result: dict[str, Any] | None = None

