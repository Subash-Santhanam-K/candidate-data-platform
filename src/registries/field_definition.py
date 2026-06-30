from __future__ import annotations
from dataclasses import dataclass, field
from ..core.enums import FieldType, MergeStrategy


@dataclass(slots=True)
class FieldDefinition:
    """Represents the runtime definition and metadata of a canonical candidate field.

    Attributes:
        canonical_name (str): The platform-wide field identifier.
        field_type (FieldType): The semantic data type of the field.
        merge_strategy (MergeStrategy): Resolution logic for observation conflicts.
        required (bool): Flag determining if the field is mandatory.
        aliases (list[str]): Alternative field names mapped to this definition.
        validator (str | None): Optional validator identifier.
        description (str | None): Optional descriptive text of the field.
    """
    canonical_name: str
    field_type: FieldType
    merge_strategy: MergeStrategy
    required: bool = False
    aliases: list[str] = field(default_factory=list)
    validator: str | None = None
    description: str | None = None
