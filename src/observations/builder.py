from __future__ import annotations
from dataclasses import asdict

from ..core.enums import ObservationStatus, FieldType
from ..core.models.observation import Observation
from ..adapters.models import RawCandidateDocument, RawAttribute
from ..registries.field_definition import FieldDefinition
from ..registries.field_registry import FieldDefinitionRegistry
from .identifier_provider import IdentifierProvider
from .time_provider import TimeProvider
from .provenance import ObservationProvenance
from .diagnostics import IgnoredAttribute, ObservationBuildResult


class ObservationBuilder:
    """Builder that constructs canonical observations from raw candidate extraction documents."""

    def __init__(
        self,
        field_registry: FieldDefinitionRegistry,
        identifier_provider: IdentifierProvider,
        time_provider: TimeProvider,
    ) -> None:
        """Initializes the builder with registries and utilities providers.

        Args:
            field_registry (FieldDefinitionRegistry): Catalog lookup for candidate fields.
            identifier_provider (IdentifierProvider): UUID identifier generator service.
            time_provider (TimeProvider): Datetime generator service.
        """
        self._field_registry = field_registry
        self._identifier_provider = identifier_provider
        self._time_provider = time_provider

    def build(self, document: RawCandidateDocument) -> ObservationBuildResult:
        """Translates a RawCandidateDocument into an ObservationBuildResult.

        Args:
            document (RawCandidateDocument): The raw extracted candidate document.

        Returns:
            ObservationBuildResult: The constructed observations and diagnostics.
        """
        observations: list[Observation] = []
        ignored_attributes: list[IgnoredAttribute] = []

        for attribute in document.attributes:
            result = self._process_attribute(document, attribute)
            if isinstance(result, Observation):
                observations.append(result)
            elif isinstance(result, IgnoredAttribute):
                ignored_attributes.append(result)

        return self._collect_result(observations, ignored_attributes)

    def _process_attribute(
        self,
        document: RawCandidateDocument,
        attribute: RawAttribute,
    ) -> Observation | IgnoredAttribute:
        """Processes a single RawAttribute into an Observation or IgnoredAttribute."""
        if not attribute.name or not attribute.name.strip():
            return IgnoredAttribute(raw_attribute=attribute, reason="EMPTY_NAME")

        try:
            field_defn = self._resolve_field(attribute.name)
        except KeyError:
            return IgnoredAttribute(raw_attribute=attribute, reason="UNKNOWN_FIELD")

        provenance = self._create_provenance(document, attribute)
        return self._create_observation(document, attribute, field_defn, provenance)

    def _resolve_field(self, name: str) -> FieldDefinition:
        """Resolves field name or alias using FieldDefinitionRegistry.

        Raises:
            KeyError: If field name is unregistered/unknown.
        """
        return self._field_registry.resolve(name)

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
        ignored_attributes: list[IgnoredAttribute],
    ) -> ObservationBuildResult:
        """Collates observations and diagnostics into the build result wrapper."""
        return ObservationBuildResult(
            observations=observations,
            ignored_attributes=ignored_attributes,
        )
