from __future__ import annotations
from ..core.exceptions import ConfigurationError
from ..core.enums import SourceType
from ..config.configuration_models import PlatformConfiguration
from .source_definition import SourceDefinition


class SourceRegistry:
    """Registry managing input source definitions."""

    def __init__(self, config: PlatformConfiguration) -> None:
        """Initializes the registry and indexes candidate sources.

        Args:
            config (PlatformConfiguration): The platform configuration.

        Raises:
            ConfigurationError: If duplicate source types, enabled source without adapter,
                empty adapter name, reliability outside [0.0, 1.0], or invalid source types
                are encountered.
        """
        self._index: dict[SourceType, SourceDefinition] = {}

        for src_name, src_cfg in config.sources.items():
            # Validate source type validity
            try:
                source_type = SourceType(src_name.upper())
            except ValueError as e:
                raise ConfigurationError(f"Invalid SourceType name '{src_name}' in sources config.") from e

            # Validate duplicate source types
            if source_type in self._index:
                raise ConfigurationError(f"Duplicate source type registered: {source_type.name}")

            # Validate reliability range
            if not (0.0 <= src_cfg.reliability <= 1.0):
                raise ConfigurationError(
                    f"Source '{src_name}' reliability must be between 0.0 and 1.0 (got {src_cfg.reliability})"
                )

            # Validate adapter presence if enabled
            if src_cfg.enabled:
                if not src_cfg.adapter or not src_cfg.adapter.strip():
                    raise ConfigurationError(f"Enabled source '{src_name}' must have a non-empty adapter name")

            # Validate empty adapter name even if not enabled
            if src_cfg.adapter is not None and not isinstance(src_cfg.adapter, str):
                raise ConfigurationError(f"Source '{src_name}' adapter must be a string")

            # Create SourceDefinition
            description: str | None = getattr(src_cfg, "description", None)
            definition = SourceDefinition(
                source_type=source_type,
                reliability=src_cfg.reliability,
                adapter=src_cfg.adapter,
                enabled=src_cfg.enabled,
                description=description,
            )

            self._index[source_type] = definition

    def get(self, source_type: SourceType | str) -> SourceDefinition:
        """Returns the definition for the specified SourceType.

        Args:
            source_type (SourceType | str): The SourceType to look up.

        Returns:
            SourceDefinition: The source definition.

        Raises:
            ConfigurationError: If the source type is not registered or invalid.
        """
        resolved_type = source_type
        if isinstance(source_type, str):
            try:
                resolved_type = SourceType(source_type.upper())
            except ValueError as e:
                raise ConfigurationError(f"Invalid SourceType value: {source_type}") from e

        if resolved_type in self._index:
            return self._index[resolved_type]
        raise ConfigurationError(f"Source type '{resolved_type}' not found in registry.")

    def exists(self, source_type: SourceType | str) -> bool:
        """Checks if a SourceType is registered.

        Args:
            source_type (SourceType | str): The source type to check.

        Returns:
            bool: True if registered, otherwise False.
        """
        resolved_type = source_type
        if isinstance(source_type, str):
            try:
                resolved_type = SourceType(source_type.upper())
            except ValueError:
                return False
        return resolved_type in self._index

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
