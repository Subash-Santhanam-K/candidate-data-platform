from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from ..core.enums import FieldType, MergeStrategy


@dataclass(slots=True)
class PipelineConfig:
    """Configuration for the pipeline execution flags.

    Attributes:
        fail_fast (bool): If True, pipeline aborts on validation errors.
        keep_observation_history (bool): If True, retains intermediate observations.
        generate_decision_trace (bool): If True, explains final decisions.
    """
    fail_fast: bool
    keep_observation_history: bool
    generate_decision_trace: bool


@dataclass(slots=True)
class FeaturesConfig:
    """Configuration for active pipeline features.

    Attributes:
        confidence_scoring (bool): If True, confidence is calculated for chosen values.
        projection (bool): If True, outputs are projected according to active profile.
    """
    confidence_scoring: bool
    projection: bool


@dataclass(slots=True)
class PlatformConfig:
    """Main platform config metadata and sub-configurations.

    Attributes:
        version (int): Schema version of the platform configuration.
        pipeline (PipelineConfig): Pipeline execution configurations.
        features (FeaturesConfig): Feature flags configurations.
    """
    version: int
    pipeline: PipelineConfig
    features: FeaturesConfig


@dataclass(slots=True)
class SourceConfig:
    """Configuration representing a single source mapping.

    Attributes:
        name (str): Unique name of the source (e.g., 'resume').
        reliability (float): Trust score of the source between 0.0 and 1.0.
        adapter (str): Adapter class/module name to process the source.
        enabled (bool): Flag determining if the source should be parsed.
    """
    name: str
    reliability: float
    adapter: str
    enabled: bool


@dataclass(slots=True)
class FieldConfig:
    """Configuration representing canonical semantic field properties.

    Attributes:
        field_name (str): Unique canonical name of the field (e.g., 'email').
        field_type (FieldType): Semantic field type enum value.
        merge_strategy (MergeStrategy): The logic strategy to resolve conflicts.
        required (bool): Whether the field must be resolved.
        validator (str | None): Registered validator name.
        aliases (list[str]): Alternative field names mapped to this definition.
        description (str | None): Optional descriptive text of the field.
    """
    field_name: str
    field_type: FieldType
    merge_strategy: MergeStrategy
    required: bool = False
    validator: str | None = None
    aliases: list[str] = field(default_factory=list)
    description: str | None = None


@dataclass(slots=True)
class SingleValueStrategyConfig:
    """Settings for the single value resolution strategy.

    Attributes:
        tie_breaker (str): Tie breaking strategy (e.g., 'newest').
    """
    tie_breaker: str


@dataclass(slots=True)
class UnionStrategyConfig:
    """Settings for the union strategy used for collections.

    Attributes:
        remove_duplicates (bool): If True, eliminates identical entries.
    """
    remove_duplicates: bool


@dataclass(slots=True)
class TimelineStrategyConfig:
    """Settings for the timeline strategy used for chronological structures.

    Attributes:
        sort (str): Sorting order (e.g., 'descending').
    """
    sort: str


@dataclass(slots=True)
class MergeConfig:
    """Strategy configurations used by the merging process.

    Attributes:
        single_value (SingleValueStrategyConfig): Settings for single value strategy.
        union (UnionStrategyConfig): Settings for union strategy.
        timeline (TimelineStrategyConfig): Settings for timeline strategy.
    """
    single_value: SingleValueStrategyConfig
    union: UnionStrategyConfig
    timeline: TimelineStrategyConfig


@dataclass(slots=True)
class WeightsConfig:
    """Agreement and metadata weights for confidence scoring.

    Attributes:
        agreement (float): Weight assigned to observation consensus.
        freshness (float): Weight assigned to how recent the observation is.
        validation (float): Weight assigned to validation check passes.
        source_reliability (float): Weight assigned to the source's trust score.
    """
    agreement: float
    freshness: float
    validation: float
    source_reliability: float


@dataclass(slots=True)
class ThresholdsConfig:
    """Confidence thresholds defining outcome buckets.

    Attributes:
        accepted (float): Minimum confidence to auto-accept a value.
        uncertain (float): Minimum confidence to keep value as uncertain.
    """
    accepted: float
    uncertain: float


@dataclass(slots=True)
class ConfidenceConfig:
    """Scoring parameters for the confidence estimator.

    Attributes:
        weights (WeightsConfig): Weights summing to 1.0.
        thresholds (ThresholdsConfig): Minimum decision values.
    """
    weights: WeightsConfig
    thresholds: ThresholdsConfig


@dataclass(slots=True)
class ValidationRuleConfig:
    """Configuration representing a validation rule for a field.

    Attributes:
        required (bool): Whether the field is mandatory.
        format (str | None): Optional string format pattern or format type identifier.
    """
    required: bool
    format: str | None = None


@dataclass(slots=True)
class ValidationConfig:
    """Validation rules definitions.

    Attributes:
        rules (dict[str, ValidationRuleConfig]): Mapped validation rule configurations.
    """
    rules: dict[str, ValidationRuleConfig] = field(default_factory=dict)


@dataclass(slots=True)
class ProjectionProfileConfig:
    """A profile mapping output visibility and inclusion constraints.

    Attributes:
        include (list[str]): List of fields (or '*') to project in final payload.
        include_confidence (bool): Flag determining if confidence score is written.
        include_trace (bool): Flag determining if decision trace is written.
    """
    include: list[str] = field(default_factory=list)
    include_confidence: bool = False
    include_trace: bool = False


@dataclass(slots=True)
class ProjectionConfig:
    """Projection profiles definitions.

    Attributes:
        profiles (dict[str, ProjectionProfileConfig]): Mapped profile configurations.
    """
    profiles: dict[str, ProjectionProfileConfig] = field(default_factory=dict)


@dataclass(slots=True)
class PlatformConfiguration:
    """Root configuration object representing the unified platform setup.

    Attributes:
        platform (PlatformConfig): Global pipeline and execution setup.
        fields (dict[str, FieldConfig]): Defined fields mapped by field name.
        sources (dict[str, SourceConfig]): Configured data source mappings.
        merge (MergeConfig): Configured merge strategy behaviors.
        confidence (ConfidenceConfig): Scoring weight and threshold settings.
        validation (ValidationConfig): Global validation rule templates.
        projection (ProjectionConfig): Profiles for output projection layout.
    """
    platform: PlatformConfig
    fields: dict[str, FieldConfig]
    sources: dict[str, SourceConfig]
    merge: MergeConfig
    confidence: ConfidenceConfig
    validation: ValidationConfig
    projection: ProjectionConfig
