from __future__ import annotations
from typing import Any
from .base import BaseAdapter
from .models import RawCandidateDocument
from ..core.models.source_instance import SourceInstance


class ResumeAdapter(BaseAdapter):
    """Adapter translating resume JSON payloads into internal raw candidate documents."""

    def extract(
        self,
        source_instance: SourceInstance,
        payload: Any,
    ) -> RawCandidateDocument:
        return self._extract_mapping(source_instance, payload)
