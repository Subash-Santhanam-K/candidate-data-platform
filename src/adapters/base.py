from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from ..core.models.source_instance import SourceInstance
from .models import RawCandidateDocument, RawAttribute


class BaseAdapter(ABC):
    """Abstract base class for payload data source adapters translating to runtime models."""

    @abstractmethod
    def extract(
        self,
        source_instance: SourceInstance,
        payload: Any,
    ) -> RawCandidateDocument:
        """Extracts candidate data from external source payload.

        Args:
            source_instance (SourceInstance): Physical metadata of the source.
            payload (Any): The payload to adapt.

        Returns:
            RawCandidateDocument: Adapted raw candidate transport document.
        """
        pass

    def _extract_mapping(
        self,
        source_instance: SourceInstance,
        payload: Any,
    ) -> RawCandidateDocument:
        """Helper to translate a payload dictionary structure into a RawCandidateDocument.

        Args:
            source_instance (SourceInstance): Physical metadata of the source.
            payload (Any): The payload dictionary mapping fields to values.

        Returns:
            RawCandidateDocument: Adapted raw candidate transport document.
        """
        attributes = []
        if isinstance(payload, dict):
            for k, v in payload.items():
                attributes.append(self._create_attribute(name=k, value=v))

        return RawCandidateDocument(
            source_instance_id=source_instance.id,
            source=source_instance.source_type,
            attributes=attributes,
            document_metadata=source_instance.metadata,
        )

    def _create_attribute(
        self,
        name: str,
        value: Any,
        metadata: dict[str, Any] | None = None,
        extraction_method: str | None = None,
    ) -> RawAttribute:
        """Helper to cleanly build a RawAttribute object.

        Every adapter should reuse this helper instead of manual instantiation.

        Args:
            name (str): Original field name.
            value (Any): Extracted raw field value.
            metadata (dict[str, Any] | None): Extraction metadata.
            extraction_method (str | None): Method of extraction.

        Returns:
            RawAttribute: Constructed attribute transport object.
        """
        return RawAttribute(
            name=name,
            value=value,
            metadata=metadata if metadata is not None else {},
            extraction_method=extraction_method,
        )
