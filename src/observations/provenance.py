from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from ..core.enums import SourceType


@dataclass(slots=True, frozen=True)
class ObservationProvenance:
    """Tracks the provenance/origin of a constructed observation.

    Attributes:
        source (SourceType): The source data type.
        original_field (str): The original attribute field name.
        attribute_metadata (dict[str, Any]): Extraction metadata for the attribute.
        document_metadata (dict[str, Any]): Metadata for the parent document.
        extraction_method (str | None): Extraction method descriptor.
    """
    source: SourceType
    original_field: str
    attribute_metadata: dict[str, Any] = field(default_factory=dict)
    document_metadata: dict[str, Any] = field(default_factory=dict)
    extraction_method: str | None = None
