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

        # 1. Build canonical definitions
        for f_name, f_cfg in config.fields.items():
            aliases: list[str] = getattr(f_cfg, "aliases", [])
            description: str | None = getattr(f_cfg, "description", None)

            definition = FieldDefinition(
                canonical_name=f_cfg.field_name,
                field_type=f_cfg.field_type,
                merge_strategy=f_cfg.merge_strategy,
                required=f_cfg.required,
                aliases=aliases,
                validator=f_cfg.validator,
                description=description,
            )

            if definition.canonical_name in self._canonical_index:
                raise ConfigurationError(f"Duplicate canonical field name: {definition.canonical_name}")

            self._canonical_index[definition.canonical_name] = definition

        # 2. Build alias indexes and validate constraints
        for canonical_name, definition in self._canonical_index.items():
            for alias in definition.aliases:
                if not isinstance(alias, str) or not alias.strip():
                    raise ConfigurationError(f"Empty or whitespace alias string found for field '{canonical_name}'")

                # Validate alias colliding with canonical names
                if alias in self._canonical_index:
                    raise ConfigurationError(
                        f"Alias '{alias}' for field '{canonical_name}' collides with an existing canonical field name"
                    )

                # Validate duplicate aliases / alias pointing to multiple canonical fields
                if alias in self._alias_index:
                    existing_canonical = self._alias_index[alias]
                    if existing_canonical != canonical_name:
                        raise ConfigurationError(
                            f"Alias '{alias}' points to multiple canonical fields: '{existing_canonical}' and '{canonical_name}'"
                        )
                    else:
                        raise ConfigurationError(f"Duplicate alias '{alias}' defined for field '{canonical_name}'")

                self._alias_index[alias] = canonical_name

    def resolve(self, name: str) -> FieldDefinition:
        """Resolves a field name or alias to its canonical FieldDefinition.

        Args:
            name (str): The canonical name or alias.

        Returns:
            FieldDefinition: The canonical field definition.

        Raises:
            KeyError: If the name or alias cannot be resolved.
        """
        if name in self._canonical_index:
            return self._canonical_index[name]
        if name in self._alias_index:
            canonical_name = self._alias_index[name]
            return self._canonical_index[canonical_name]
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
        if canonical_name in self._canonical_index:
            return self._canonical_index[canonical_name]
        raise KeyError(f"Canonical field '{canonical_name}' not found")

    def exists(self, name: str) -> bool:
        """Checks if a field name or alias is registered.

        Args:
            name (str): The canonical name or alias.

        Returns:
            bool: True if it exists as a canonical name or alias, otherwise False.
        """
        return name in self._canonical_index or name in self._alias_index

    def all(self) -> list[FieldDefinition]:
        """Returns a list of all registered canonical field definitions.

        Returns:
            list[FieldDefinition]: List of all registered field definitions.
        """
        return list(self._canonical_index.values())
