from __future__ import annotations
from dataclasses import dataclass
from ..core.enums import SourceType


@dataclass(slots=True)
class SourceDefinition:
    """Represents the runtime definition and metadata of an input source.

    Attributes:
        source_type (SourceType): The type of the data source.
        reliability (float): The configured reliability score of the source.
        adapter (str): The identifier of the adapter to process this source.
        enabled (bool): Flag determining if this source is active.
        description (str | None): Optional descriptive text of the source.
    """
    source_type: SourceType
    reliability: float
    adapter: str
    enabled: bool
    description: str | None = None
