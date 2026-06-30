from __future__ import annotations
from typing import Any
from .base import BaseAdapter
from .models import RawCandidateDocument
from ..core.models.source_instance import SourceInstance


class LinkedInAdapter(BaseAdapter):
    """Adapter translating LinkedIn profile JSON payloads into internal raw candidate documents."""

    def extract(
        self,
        source_instance: SourceInstance,
        payload: Any,
    ) -> RawCandidateDocument:
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
