from __future__ import annotations
from dataclasses import asdict
from typing import Any

from ..core.enums import ObservationStatus, FieldType
from ..core.models.observation import Observation
from ..core.models.raw_candidate import RawCandidateDocument, RawAttribute
from ..registries.field_definition import FieldDefinition
from ..registries.field_registry import FieldDefinitionRegistry
from ..registries.source_registry import SourceRegistry
from .identifier_provider import IdentifierProvider
from .time_provider import TimeProvider
from .provenance import ObservationProvenance
from .diagnostics import IgnoredAttribute, SkippedAttribute, ObservationBuildResult


class ObservationBuilder:
    """Builder that constructs canonical observations from raw candidate extraction documents."""

    def __init__(
        self,
        field_registry: FieldDefinitionRegistry,
        source_registry: SourceRegistry,
        identifier_provider: IdentifierProvider,
        time_provider: TimeProvider,
    ) -> None:
        """Initializes the builder with registries and utilities providers.

        Args:
            field_registry (FieldDefinitionRegistry): Catalog lookup for candidate fields.
            source_registry (SourceRegistry): Catalog lookup for candidate sources.
            identifier_provider (IdentifierProvider): UUID identifier generator service.
            time_provider (TimeProvider): Datetime generator service.
        """
        self._field_registry = field_registry
        self._source_registry = source_registry
        self._identifier_provider = identifier_provider
        self._time_provider = time_provider

    def build(self, document: RawCandidateDocument) -> ObservationBuildResult:
        """Translates a RawCandidateDocument into an ObservationBuildResult.

        Args:
            document (RawCandidateDocument): The raw extracted candidate document.

        Returns:
            ObservationBuildResult: The constructed observations and warnings/diagnostics.
        """
        self._validate_document(document)

        observations: list[Observation] = []
        ignored_attributes: list[IgnoredAttribute] = []
        skipped_attributes: list[SkippedAttribute] = []
        warnings: list[str] = []

        for attribute in document.attributes:
            result = self._process_attribute(document, attribute)
            if isinstance(result, Observation):
                observations.append(result)
            elif isinstance(result, IgnoredAttribute):
                ignored_attributes.append(result)
            elif isinstance(result, SkippedAttribute):
                skipped_attributes.append(result)

        return self._collect_result(observations, warnings, ignored_attributes, skipped_attributes)

    def _validate_document(self, document: RawCandidateDocument) -> None:
        """Validates core document properties.

        Raises:
            ValueError: If document or its provenance sources are invalid.
        """
        if not document:
            raise ValueError("RawCandidateDocument cannot be None")
        if not document.source_instance_id:
            raise ValueError("RawCandidateDocument must have a valid source_instance_id")
        if not document.source:
            raise ValueError("RawCandidateDocument must have a valid source")
        
        # Validate that the source is registered in the Source Registry
        if not self._source_registry.exists(document.source):
            raise ValueError(f"Source '{document.source}' is not registered in the Source Registry")

    def _process_attribute(
        self,
        document: RawCandidateDocument,
        attribute: RawAttribute,
    ) -> Observation | IgnoredAttribute | SkippedAttribute:
        """Processes a single RawAttribute into an Observation or diagnostic warning."""
        # 1. Validate raw attribute naming structure
        if not attribute.name or not attribute.name.strip():
            return IgnoredAttribute(raw_attribute=attribute, reason="EMPTY_NAME")

        # 2. Resolve the field using the registry lookup
        try:
            field_defn = self._resolve_field(attribute.name)
        except KeyError:
            return IgnoredAttribute(raw_attribute=attribute, reason="UNKNOWN_FIELD")

        # 3. Check value usability constraints
        skipped_reason = self._check_value_usability(attribute)
        if skipped_reason:
            return SkippedAttribute(raw_attribute=attribute, reason=skipped_reason)

        # 4. Create ObservationProvenance
        provenance = self._create_provenance(document, attribute)

        # 5. Build and return Observation
        return self._create_observation(document, attribute, field_defn, provenance)

    def _resolve_field(self, name: str) -> FieldDefinition:
        """Resolves field name or alias using FieldDefinitionRegistry.

        Raises:
            KeyError: If field name is unregistered/unknown.
        """
        return self._field_registry.resolve(name)

    def _check_value_usability(self, attribute: RawAttribute) -> str | None:
        """Determines if the raw attribute value is usable.

        Returns:
            str | None: Skipped reason string, or None if the value is usable.
        """
        val = attribute.value
        if val is None:
            return "NULL_VALUE"

        if isinstance(val, str):
            if not val:
                return "EMPTY_VALUE"
            if not val.strip():
                return "ONLY_WHITESPACE"
        elif hasattr(val, "__len__") and len(val) == 0:
            return "EMPTY_VALUE"

        return None

    def _create_provenance(self, document: RawCandidateDocument, attribute: RawAttribute) -> ObservationProvenance:
        """Constructs ObservationProvenance tracking original meta fields."""
        return ObservationProvenance(
            source=document.source,
            original_field=attribute.name,
            attribute_metadata=attribute.metadata,
            document_metadata=document.document_metadata,
            extraction_method=attribute.extraction_method,
        )

    def _create_observation(
        self,
        document: RawCandidateDocument,
        attribute: RawAttribute,
        field_defn: FieldDefinition,
        provenance: ObservationProvenance,
    ) -> Observation:
        """Instantiates the domain Observation object using provider inputs."""
        obs_id = self._identifier_provider.next_observation_id()
        ts = self._time_provider.now()

        return Observation(
            id=obs_id,
            source_instance_id=document.source_instance_id,
            field_type=field_defn.field_type,
            field_name=field_defn.canonical_name,
            raw_value=attribute.value,
            status=ObservationStatus.RAW,
            timestamp=ts,
            provenance=asdict(provenance),
        )

    def _collect_result(
        self,
        observations: list[Observation],
        warnings: list[str],
        ignored_attributes: list[IgnoredAttribute],
        skipped_attributes: list[SkippedAttribute],
    ) -> ObservationBuildResult:
        """Collates observations and diagnostics into the build result wrapper."""
        return ObservationBuildResult(
            observations=observations,
            warnings=warnings,
            ignored_attributes=ignored_attributes,
            skipped_attributes=skipped_attributes,
        )
