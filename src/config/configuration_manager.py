from __future__ import annotations
import math
from pathlib import Path
from typing import Any
import yaml
from yaml.loader import SafeLoader

from ..core.exceptions import ConfigurationError
from ..core.enums import FieldType, MergeStrategy
from .configuration_models import (
    PlatformConfiguration,
    PlatformConfig,
    PipelineConfig,
    FeaturesConfig,
    SourceConfig,
    FieldConfig,
    MergeConfig,
    SingleValueStrategyConfig,
    UnionStrategyConfig,
    TimelineStrategyConfig,
    WeightsConfig,
    ThresholdsConfig,
    ConfidenceConfig,
    ValidationConfig,
    ValidationRuleConfig,
    ProjectionConfig,
    ProjectionProfileConfig,
)


class UniqueKeyLoader(SafeLoader):
    """YAML SafeLoader that detects duplicate keys in mappings and raises a ConstructorError."""

    def construct_mapping(self, node, deep=False):
        mapping = []
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    f"found duplicate key ({key})", key_node.start_mark
                )
            mapping.append(key)
        return super().construct_mapping(node, deep=deep)


class ConfigurationManager:
    """Manager to load and validate YAML configurations for Candidate Data Platform."""

    _CONFIGURATION_FILES: dict[str, str] = {
        "platform": "platform.yaml",
        "sources": "sources.yaml",
        "fields": "fields.yaml",
        "merge": "merge.yaml",
        "confidence": "confidence.yaml",
        "validation": "validation.yaml",
        "projection": "projection.yaml",
    }

    def __init__(self, config_directory: Path | str | None = None) -> None:
        """Initializes the ConfigurationManager with a config directory.

        Args:
            config_directory (Path | str | None): Path to the configs directory.
                Defaults to the standard root configs/ folder.
        """
        if config_directory is None:
            self._config_dir = Path(__file__).resolve().parent.parent.parent / "configs"
        else:
            self._config_dir = Path(config_directory)

    def load(self) -> PlatformConfiguration:
        """Loads and validates all configurations from the config directory.

        Returns:
            PlatformConfiguration: The strongly typed root configuration object.

        Raises:
            ConfigurationError: If configurations are invalid, malformed, or missing.
        """
        # 1. Load YAML files
        raw_configs: dict[str, dict[str, Any]] = {}
        for key, filename in self._CONFIGURATION_FILES.items():
            raw_configs[key] = self._load_yaml(self._config_dir / filename)

        # 2. Validate all raw configurations
        self._validate_configuration(raw_configs)

        # 3. Build configuration models
        return self._build_configuration_models(raw_configs)

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        """Loads a single YAML file using the UniqueKeyLoader.

        Args:
            path (Path): Path to the YAML file.

        Returns:
            dict[str, Any]: Parsed dictionary content.

        Raises:
            ConfigurationError: If reading or parsing fails.
        """
        if not path.is_file():
            raise ConfigurationError(f"Configuration file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = yaml.load(f, Loader=UniqueKeyLoader)
                if content is None:
                    return {}
                if not isinstance(content, dict):
                    raise ConfigurationError(f"Configuration file {path.name} must be a dictionary mapping.")
                return content
        except yaml.constructor.ConstructorError as e:
            raise ConfigurationError(f"Duplicate key found in YAML file {path.name}: {e}") from e
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Malformed YAML in file {path.name}: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to read file {path.name}: {e}") from e

    def _validate_configuration(self, raw_configs: dict[str, dict[str, Any]]) -> None:
        """Orchestrates validation of all configuration models.

        Args:
            raw_configs (dict[str, dict[str, Any]]): Map of config key to parsed dictionary.
        """
        self._validate_versions(raw_configs)
        self._validate_platform(raw_configs["platform"])
        self._validate_sources(raw_configs["sources"])
        self._validate_fields(raw_configs["fields"], raw_configs["merge"])
        self._validate_merge(raw_configs["merge"])
        self._validate_confidence(raw_configs["confidence"])
        self._validate_validation_rules(raw_configs["validation"])
        self._validate_projection(raw_configs["projection"])

    def _validate_versions(self, raw_configs: dict[str, dict[str, Any]]) -> None:
        """Validates versions exist and are positive integers across all configs."""
        for name, cfg in raw_configs.items():
            filename = self._CONFIGURATION_FILES[name]
            if "version" not in cfg:
                raise ConfigurationError(f"Missing required section 'version' in {filename}")
            version = cfg["version"]
            if not isinstance(version, int) or version <= 0:
                raise ConfigurationError(f"Invalid 'version' value in {filename}: must be a positive integer.")

    def _validate_platform(self, platform: dict[str, Any]) -> None:
        """Validates platform config fields and features."""
        for section in ("pipeline", "features"):
            if section not in platform:
                raise ConfigurationError(f"Missing required section '{section}' in platform.yaml")
            if not isinstance(platform[section], dict):
                raise ConfigurationError(f"'{section}' section in platform.yaml must be a dictionary")

        pipeline_sec = platform["pipeline"]
        for key in ("fail_fast", "keep_observation_history", "generate_decision_trace"):
            if key not in pipeline_sec:
                raise ConfigurationError(f"Missing required pipeline field '{key}' in platform.yaml")
            if not isinstance(pipeline_sec[key], bool):
                raise ConfigurationError(f"Field '{key}' in platform.yaml must be a boolean")

        features_sec = platform["features"]
        for key in ("confidence_scoring", "projection"):
            if key not in features_sec:
                raise ConfigurationError(f"Missing required features field '{key}' in platform.yaml")
            if not isinstance(features_sec[key], bool):
                raise ConfigurationError(f"Field '{key}' in platform.yaml must be a boolean")

    def _validate_sources(self, sources: dict[str, Any]) -> None:
        """Validates source reliability, adapters, and enable state."""
        if "sources" not in sources:
            raise ConfigurationError("Missing required section 'sources' in sources.yaml")
        sources_sec = sources["sources"]
        if not isinstance(sources_sec, dict):
            raise ConfigurationError("'sources' section in sources.yaml must be a dictionary")

        for src_name, src_cfg in sources_sec.items():
            if not isinstance(src_cfg, dict):
                raise ConfigurationError(f"Source configuration for '{src_name}' must be a dictionary")
            for field_key in ("reliability", "adapter", "enabled"):
                if field_key not in src_cfg:
                    raise ConfigurationError(f"Missing field '{field_key}' in source config for '{src_name}'")

            reliability = src_cfg["reliability"]
            if not isinstance(reliability, (int, float)) or not (0.0 <= reliability <= 1.0):
                raise ConfigurationError(f"Source '{src_name}' reliability must be a float between 0.0 and 1.0")

            if not isinstance(src_cfg["adapter"], str) or not src_cfg["adapter"].strip():
                raise ConfigurationError(f"Source '{src_name}' adapter must be a non-empty string")

            if not isinstance(src_cfg["enabled"], bool):
                raise ConfigurationError(f"Source '{src_name}' enabled must be a boolean")

    def _validate_fields(self, fields: dict[str, Any], merge: dict[str, Any]) -> None:
        """Validates field enums, strategies, and references."""
        if "fields" not in fields:
            raise ConfigurationError("Missing required section 'fields' in fields.yaml")
        fields_sec = fields["fields"]
        if not isinstance(fields_sec, dict):
            raise ConfigurationError("'fields' section in fields.yaml must be a dictionary")

        for f_name, f_cfg in fields_sec.items():
            if not isinstance(f_cfg, dict):
                raise ConfigurationError(f"Field configuration for '{f_name}' must be a dictionary")
            if "type" not in f_cfg:
                raise ConfigurationError(f"Missing 'type' for field '{f_name}'")
            if "strategy" not in f_cfg:
                raise ConfigurationError(f"Missing 'strategy' for field '{f_name}'")

            # Validate Enum names (FieldType)
            f_type_str = f_cfg["type"]
            try:
                FieldType(f_type_str)
            except ValueError as e:
                raise ConfigurationError(f"Invalid FieldType '{f_type_str}' defined for field '{f_name}'") from e

            # Validate referenced merge strategy
            f_strategy = f_cfg["strategy"]
            if not isinstance(f_strategy, str):
                raise ConfigurationError(f"Strategy for field '{f_name}' must be a string")
            
            try:
                strategy_enum = MergeStrategy(f_strategy)
            except ValueError as e:
                raise ConfigurationError(f"Invalid MergeStrategy '{f_strategy}' defined for field '{f_name}'") from e

            strategy_lower = strategy_enum.value.lower()
            if strategy_lower not in merge:
                raise ConfigurationError(
                    f"Unsupported merge strategy '{f_strategy}' referenced by field '{f_name}'. "
                    f"Strategy '{strategy_lower}' not defined in merge.yaml."
                )

            # Validate aliases and description
            if "aliases" in f_cfg:
                if not isinstance(f_cfg["aliases"], list):
                    raise ConfigurationError(f"Aliases for field '{f_name}' must be a list")
                for alias in f_cfg["aliases"]:
                    if not isinstance(alias, str):
                        raise ConfigurationError(f"Alias items for field '{f_name}' must be strings")

            if "description" in f_cfg and f_cfg["description"] is not None:
                if not isinstance(f_cfg["description"], str):
                    raise ConfigurationError(f"Description for field '{f_name}' must be a string")

    def _validate_merge(self, merge: dict[str, Any]) -> None:
        """Validates merge configs single_value, union, and timeline options."""
        for sec in ("single_value", "union", "timeline"):
            if sec not in merge:
                raise ConfigurationError(f"Missing required section '{sec}' in merge.yaml")
            if not isinstance(merge[sec], dict):
                raise ConfigurationError(f"Section '{sec}' in merge.yaml must be a dictionary")

        if "tie_breaker" not in merge["single_value"]:
            raise ConfigurationError("Missing field 'tie_breaker' in merge.yaml single_value strategy")
        if "remove_duplicates" not in merge["union"]:
            raise ConfigurationError("Missing field 'remove_duplicates' in merge.yaml union strategy")
        if "sort" not in merge["timeline"]:
            raise ConfigurationError("Missing field 'sort' in merge.yaml timeline strategy")

    def _validate_confidence(self, confidence: dict[str, Any]) -> None:
        """Validates weights sum and thresholds correctness."""
        if "weights" not in confidence:
            raise ConfigurationError("Missing required section 'weights' in confidence.yaml")
        if "thresholds" not in confidence:
            raise ConfigurationError("Missing required section 'thresholds' in confidence.yaml")

        weights_sec = confidence["weights"]
        if not isinstance(weights_sec, dict):
            raise ConfigurationError("'weights' section in confidence.yaml must be a dictionary")
        for key in ("agreement", "freshness", "validation", "source_reliability"):
            if key not in weights_sec:
                raise ConfigurationError(f"Missing weight field '{key}' in confidence.yaml")
            val = weights_sec[key]
            if not isinstance(val, (int, float)) or val < 0.0 or val > 1.0:
                raise ConfigurationError(f"Weight '{key}' must be a float between 0.0 and 1.0")

        # Confidence weights sum to 1.0
        total_weight = sum(weights_sec.get(k, 0.0) for k in ("agreement", "freshness", "validation", "source_reliability"))
        if not math.isclose(total_weight, 1.0, rel_tol=1e-9):
            raise ConfigurationError(f"Confidence weights must sum to 1.0 (got {total_weight})")

        thresholds_sec = confidence["thresholds"]
        if not isinstance(thresholds_sec, dict):
            raise ConfigurationError("'thresholds' section in confidence.yaml must be a dictionary")
        for key in ("accepted", "uncertain"):
            if key not in thresholds_sec:
                raise ConfigurationError(f"Missing threshold field '{key}' in confidence.yaml")
            val = thresholds_sec[key]
            if not isinstance(val, (int, float)) or val < 0.0 or val > 1.0:
                raise ConfigurationError(f"Threshold '{key}' must be a float between 0.0 and 1.0")

        accepted_threshold = thresholds_sec["accepted"]
        uncertain_threshold = thresholds_sec["uncertain"]
        if accepted_threshold < uncertain_threshold:
            raise ConfigurationError(
                f"Confidence thresholds are illogical: 'accepted' threshold ({accepted_threshold}) "
                f"cannot be less than 'uncertain' threshold ({uncertain_threshold})."
            )

    def _validate_validation_rules(self, validation: dict[str, Any]) -> None:
        """Validates validation rule shapes."""
        if "rules" not in validation:
            raise ConfigurationError("Missing required section 'rules' in validation.yaml")
        rules_sec = validation["rules"]
        if not isinstance(rules_sec, dict):
            raise ConfigurationError("'rules' section in validation.yaml must be a dictionary")

        for f_name, r_cfg in rules_sec.items():
            if not isinstance(r_cfg, dict):
                raise ConfigurationError(f"Validation rule for field '{f_name}' must be a dictionary")
            if "required" not in r_cfg:
                raise ConfigurationError(f"Missing field 'required' in validation rule for field '{f_name}'")
            if not isinstance(r_cfg["required"], bool):
                raise ConfigurationError(f"Field 'required' in validation rule for field '{f_name}' must be a boolean")
            if "format" in r_cfg and r_cfg["format"] is not None:
                if not isinstance(r_cfg["format"], str):
                    raise ConfigurationError(f"Field 'format' in validation rule for field '{f_name}' must be a string")

    def _validate_projection(self, projection: dict[str, Any]) -> None:
        """Validates projection profiles inclusion and trace visibility flags."""
        if "profiles" not in projection:
            raise ConfigurationError("Missing required section 'profiles' in projection.yaml")
        profiles_sec = projection["profiles"]
        if not isinstance(profiles_sec, dict):
            raise ConfigurationError("'profiles' section in projection.yaml must be a dictionary")
        for p_name, p_cfg in profiles_sec.items():
            if not isinstance(p_cfg, dict):
                raise ConfigurationError(f"Projection profile '{p_name}' must be a dictionary")
            for field_key in ("include", "include_confidence", "include_trace"):
                if field_key not in p_cfg:
                    raise ConfigurationError(f"Missing field '{field_key}' in projection profile '{p_name}'")

            if not isinstance(p_cfg["include"], list):
                raise ConfigurationError(f"Projection profile '{p_name}' 'include' field must be a list")
            for item in p_cfg["include"]:
                if not isinstance(item, str):
                    raise ConfigurationError(f"Projection profile '{p_name}' include items must be strings")

            if not isinstance(p_cfg["include_confidence"], bool):
                raise ConfigurationError(f"Projection profile '{p_name}' 'include_confidence' must be a boolean")
            if not isinstance(p_cfg["include_trace"], bool):
                raise ConfigurationError(f"Projection profile '{p_name}' 'include_trace' must be a boolean")

    def _build_configuration_models(self, raw_configs: dict[str, dict[str, Any]]) -> PlatformConfiguration:
        """Converts raw dictionary configurations into strongly typed PlatformConfiguration."""
        platform = raw_configs["platform"]
        sources = raw_configs["sources"]
        fields = raw_configs["fields"]
        merge = raw_configs["merge"]
        confidence = raw_configs["confidence"]
        validation = raw_configs["validation"]
        projection = raw_configs["projection"]

        # Pipeline and features
        pipeline_cfg = PipelineConfig(
            fail_fast=platform["pipeline"]["fail_fast"],
            keep_observation_history=platform["pipeline"]["keep_observation_history"],
            generate_decision_trace=platform["pipeline"]["generate_decision_trace"],
        )
        features_cfg = FeaturesConfig(
            confidence_scoring=platform["features"]["confidence_scoring"],
            projection=platform["features"]["projection"],
        )
        platform_cfg = PlatformConfig(
            version=platform["version"],
            pipeline=pipeline_cfg,
            features=features_cfg,
        )

        # Sources
        sources_cfg: dict[str, SourceConfig] = {}
        for src_name, src_val in sources["sources"].items():
            sources_cfg[src_name] = SourceConfig(
                name=src_name,
                reliability=float(src_val["reliability"]),
                adapter=src_val["adapter"],
                enabled=src_val["enabled"],
            )

        # Fields
        fields_cfg: dict[str, FieldConfig] = {}
        for f_name, f_val in fields["fields"].items():
            fields_cfg[f_name] = FieldConfig(
                field_name=f_name,
                field_type=FieldType(f_val["type"]),
                merge_strategy=MergeStrategy(f_val["strategy"]),
                required=f_val.get("required", False),
                validator=f_val.get("validator"),
                aliases=list(f_val.get("aliases", [])),
                description=f_val.get("description"),
            )

        # Merge Strategies
        single_val_cfg = SingleValueStrategyConfig(
            tie_breaker=merge["single_value"]["tie_breaker"]
        )
        union_cfg = UnionStrategyConfig(
            remove_duplicates=merge["union"]["remove_duplicates"]
        )
        timeline_cfg = TimelineStrategyConfig(
            sort=merge["timeline"]["sort"]
        )
        merge_cfg = MergeConfig(
            single_value=single_val_cfg,
            union=union_cfg,
            timeline=timeline_cfg,
        )

        # Confidence
        weights_cfg = WeightsConfig(
            agreement=float(confidence["weights"]["agreement"]),
            freshness=float(confidence["weights"]["freshness"]),
            validation=float(confidence["weights"]["validation"]),
            source_reliability=float(confidence["weights"]["source_reliability"]),
        )
        thresholds_cfg = ThresholdsConfig(
            accepted=float(confidence["thresholds"]["accepted"]),
            uncertain=float(confidence["thresholds"]["uncertain"]),
        )
        confidence_cfg = ConfidenceConfig(
            weights=weights_cfg,
            thresholds=thresholds_cfg,
        )

        # Validation rules
        validation_rules: dict[str, ValidationRuleConfig] = {}
        for f_name, r_val in validation["rules"].items():
            validation_rules[f_name] = ValidationRuleConfig(
                required=r_val["required"],
                format=r_val.get("format"),
            )
        validation_cfg = ValidationConfig(
            rules=validation_rules
        )

        # Projection
        projection_profiles: dict[str, ProjectionProfileConfig] = {}
        for p_name, p_val in projection["profiles"].items():
            projection_profiles[p_name] = ProjectionProfileConfig(
                include=list(p_val["include"]),
                include_confidence=p_val["include_confidence"],
                include_trace=p_val["include_trace"],
            )
        projection_cfg = ProjectionConfig(
            profiles=projection_profiles
        )

        # Root PlatformConfiguration
        return PlatformConfiguration(
            platform=platform_cfg,
            fields=fields_cfg,
            sources=sources_cfg,
            merge=merge_cfg,
            confidence=confidence_cfg,
            validation=validation_cfg,
            projection=projection_cfg,
        )
