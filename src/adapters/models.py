from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID
from typing import Any
from ..core.enums import SourceType


@dataclass(slots=True, frozen=True)
class RawAttribute:
    """Represents a raw attribute extracted from a data source.

    Attributes:
        name (str): The raw key/name of the attribute from the source.
        value (Any): The raw extracted value.
        metadata (dict[str, Any]): Attribute-level extraction metadata.
        extraction_method (str | None): Method used to extract this attribute.
    """
    name: str
    value: Any
    metadata: dict[str, Any] = field(default_factory=dict)
    extraction_method: str | None = None


@dataclass(slots=True, frozen=True)
class RawCandidateDocument:
    """Represents a raw candidate document with extracted attributes.

    Attributes:
        source_instance_id (UUID): The physical source instance identifier.
        source (SourceType): The type of the source.
        attributes (list[RawAttribute]): The list of raw attributes extracted.
        document_metadata (dict[str, Any]): Document-level metadata.
    """
    source_instance_id: UUID
    source: SourceType
    attributes: list[RawAttribute] = field(default_factory=list)
    document_metadata: dict[str, Any] = field(default_factory=dict)
