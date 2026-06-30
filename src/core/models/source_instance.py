from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Any


@dataclass
class SourceInstance:
    """Represents a physical input source of candidate data.

    Attributes:
        id (UUID): Unique identifier of the source instance.
        source_type (str): The type of the source (e.g., 'resume', 'linkedin', 'github', 'csv').
        version (int): The version of the schema/format of the source file/data.
        path (str): The storage path or URI where the source file can be accessed.
        metadata (dict[str, Any]): Source-specific metadata fields.
        created_at (datetime): The timestamp when the source instance was created/recorded.
    """
    id: UUID
    source_type: str
    version: int
    path: str
    metadata: dict[str, Any]
    created_at: datetime
