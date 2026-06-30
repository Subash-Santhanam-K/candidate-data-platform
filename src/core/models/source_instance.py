from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from typing import Any
from ..enums import SourceType


@dataclass(slots=True)
class SourceInstance:
    """Represents a physical input source of candidate data.

    Attributes:
        id (UUID): Unique identifier of the source instance.
        source_type (SourceType): The type of the source.
        version (int): The version of the schema/format of the source file/data.
        path (str): The storage path or URI where the source file can be accessed.
        created_at (datetime): The timestamp when the source instance was created/recorded.
        metadata (dict[str, Any]): Source-specific metadata fields.
    """
    id: UUID
    source_type: SourceType
    version: int
    path: str
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

