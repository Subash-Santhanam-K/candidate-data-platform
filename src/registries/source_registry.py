from __future__ import annotations
from ..core.exceptions import ConfigurationError
from ..core.enums import SourceType
from ..config.configuration_models import PlatformConfiguration, SourceConfig
from .source_definition import SourceDefinition


class SourceRegistry:
    """Registry managing input source definitions."""

    def __init__(self, config: PlatformConfiguration) -> None:
        """Initializes the registry and indexes candidate sources.

        Args:
            config (PlatformConfiguration): The platform configuration.

        Raises:
            ConfigurationError: If duplicate source types, enabled source without adapter,
                empty adapter name, or reliability outside [0.0, 1.0] are encountered.
        """
        self._index: dict[SourceType, SourceDefinition] = {}

        for src_cfg in config.sources.values():
            self._validate_source(src_cfg)
            definition = self._create_definition(src_cfg)
            self._register_source(definition)

    def _validate_source(self, src_cfg: SourceConfig) -> None:
        """Validates runtime constraints for a single source config.

        Raises:
            ConfigurationError: If validation rules are violated.
        """
        # Validate duplicate source types
        if src_cfg.source_type in self._index:
            raise ConfigurationError(f"Duplicate source type registered: {src_cfg.source_type.name}")

        # Validate reliability range
        if not (0.0 <= src_cfg.reliability <= 1.0):
            raise ConfigurationError(
                f"Source '{src_cfg.name}' reliability must be between 0.0 and 1.0 (got {src_cfg.reliability})"
            )

        # Validate adapter presence if enabled
        if src_cfg.enabled:
            if not src_cfg.adapter or not src_cfg.adapter.strip():
                raise ConfigurationError(f"Enabled source '{src_cfg.name}' must have a non-empty adapter name")

    def _create_definition(self, src_cfg: SourceConfig) -> SourceDefinition:
        """Creates a runtime SourceDefinition from typed configuration."""
        return SourceDefinition(
            source_type=src_cfg.source_type,
            reliability=src_cfg.reliability,
            adapter=src_cfg.adapter,
            enabled=src_cfg.enabled,
            description=src_cfg.description,
        )

    def _register_source(self, definition: SourceDefinition) -> None:
        """Indexes the validated definition."""
        self._index[definition.source_type] = definition

    def get(self, source_type: SourceType) -> SourceDefinition:
        """Returns the definition for the specified SourceType.

        Args:
            source_type (SourceType): The SourceType to look up.

        Returns:
            SourceDefinition: The source definition.

        Raises:
            ConfigurationError: If the source type is not registered.
            TypeError: If the source_type is not an instance of SourceType.
        """
        if not isinstance(source_type, SourceType):
            raise TypeError("source_type must be an instance of SourceType")
        if source_type in self._index:
            return self._index[source_type]
        raise ConfigurationError(f"Source type '{source_type}' not found in registry.")

    def exists(self, source_type: SourceType) -> bool:
        """Checks if a SourceType is registered.

        Args:
            source_type (SourceType): The source type to check.

        Returns:
            bool: True if registered, otherwise False.
        """
        if not isinstance(source_type, SourceType):
            return False
        return source_type in self._index

    def enabled_sources(self) -> list[SourceDefinition]:
        """Returns a list of all active (enabled) source definitions.

        Returns:
            list[SourceDefinition]: Active source definitions.
        """
        return [defn for defn in self._index.values() if defn.enabled]

    def all(self) -> list[SourceDefinition]:
        """Returns a list of all registered source definitions.

        Returns:
            list[SourceDefinition]: All registered source definitions.
        """
        return list(self._index.values())
