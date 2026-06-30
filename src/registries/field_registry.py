from __future__ import annotations
from ..core.exceptions import ConfigurationError
from ..config.configuration_models import PlatformConfiguration
from .field_definition import FieldDefinition


class FieldDefinitionRegistry:
    """Registry managing canonical candidate fields and alias lookups."""

    def __init__(self, config: PlatformConfiguration) -> None:
        """Initializes the registry and indexes canonical field definitions and aliases.

        Args:
            config (PlatformConfiguration): The platform configuration.

        Raises:
            ConfigurationError: If duplicate fields, duplicate aliases, name collisions,
                or multi-field alias pointers are detected.
        """
        self._canonical_index: dict[str, FieldDefinition] = {}
        self._alias_index: dict[str, str] = {}

        self._build_canonical_index(config)
        self._build_alias_index()

    def _build_canonical_index(self, config: PlatformConfiguration) -> None:
        """Helper to build and validate the canonical field definitions index."""
        for f_name, f_cfg in config.fields.items():
            definition = FieldDefinition(
                canonical_name=f_cfg.field_name,
                field_type=f_cfg.field_type,
                merge_strategy=f_cfg.merge_strategy,
                required=f_cfg.required,
                aliases=f_cfg.aliases,
                validator=f_cfg.validator,
                description=f_cfg.description,
            )

            # Lowercase for case-insensitive duplicate canonical checks
            normalized_name = definition.canonical_name.lower()
            if normalized_name in self._canonical_index:
                raise ConfigurationError(f"Duplicate canonical field name (case-insensitive): {definition.canonical_name}")

            # Store in index with normalized key
            self._canonical_index[normalized_name] = definition

    def _build_alias_index(self) -> None:
        """Helper to build and validate the alias mappings index."""
        for normalized_canonical, definition in self._canonical_index.items():
            for alias in definition.aliases:
                if not isinstance(alias, str) or not alias.strip():
                    raise ConfigurationError(
                        f"Empty or whitespace alias string found for field '{definition.canonical_name}'"
                    )

                # Lowercase for case-insensitive checks
                normalized_alias = alias.lower()

                # Validate alias colliding with canonical names
                if normalized_alias in self._canonical_index:
                    raise ConfigurationError(
                        f"Alias '{alias}' for field '{definition.canonical_name}' collides with an existing canonical field name"
                    )

                # Validate duplicate aliases / alias pointing to multiple canonical fields
                if normalized_alias in self._alias_index:
                    existing_canonical = self._alias_index[normalized_alias]
                    if existing_canonical != normalized_canonical:
                        orig_existing = self._canonical_index[existing_canonical].canonical_name
                        raise ConfigurationError(
                            f"Alias '{alias}' points to multiple canonical fields: '{orig_existing}' and '{definition.canonical_name}'"
                        )
                    else:
                        raise ConfigurationError(f"Duplicate alias '{alias}' defined for field '{definition.canonical_name}'")

                self._alias_index[normalized_alias] = normalized_canonical

    def resolve(self, name: str) -> FieldDefinition:
        """Resolves a field name or alias to its canonical FieldDefinition.

        Args:
            name (str): The canonical name or alias.

        Returns:
            FieldDefinition: The canonical field definition.

        Raises:
            KeyError: If the name or alias cannot be resolved.
        """
        normalized_name = name.lower()
        if normalized_name in self._canonical_index:
            return self._canonical_index[normalized_name]
        if normalized_name in self._alias_index:
            canonical_key = self._alias_index[normalized_name]
            return self._canonical_index[canonical_key]
        raise KeyError(f"Field name or alias '{name}' not found")

    def get(self, canonical_name: str) -> FieldDefinition:
        """Returns the canonical field definition without performing alias resolution.

        Args:
            canonical_name (str): The canonical field name.

        Returns:
            FieldDefinition: The canonical field definition.

        Raises:
            KeyError: If the canonical field name is not registered.
        """
        normalized_name = canonical_name.lower()
        if normalized_name in self._canonical_index:
            return self._canonical_index[normalized_name]
        raise KeyError(f"Canonical field '{canonical_name}' not found")

    def exists(self, name: str) -> bool:
        """Checks if a field name or alias is registered.

        Args:
            name (str): The canonical name or alias.

        Returns:
            bool: True if it exists as a canonical name or alias, otherwise False.
        """
        normalized_name = name.lower()
        return normalized_name in self._canonical_index or normalized_name in self._alias_index

    def all(self) -> list[FieldDefinition]:
        """Returns a list of all registered canonical field definitions.

        Returns:
            list[FieldDefinition]: List of all registered field definitions.
        """
        return list(self._canonical_index.values())
