from __future__ import annotations
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ..core.enums import SourceType, ProjectionProfile
from ..core.exceptions import PipelineError
from ..core.models.source_instance import SourceInstance
from ..config.configuration_models import PlatformConfiguration
from ..config.configuration_manager import ConfigurationManager
from ..registries.field_registry import FieldDefinitionRegistry
from ..registries.source_registry import SourceRegistry
from ..adapters.base import BaseAdapter
from ..adapters.models import RawCandidateDocument
from ..adapters.resume_adapter import ResumeAdapter
from ..adapters.linkedin_adapter import LinkedInAdapter
from ..adapters.github_adapter import GitHubAdapter
from ..adapters.csv_adapter import CSVAdapter
from ..observations.builder import ObservationBuilder
from ..observations.identifier_provider import IdentifierProvider
from ..observations.time_provider import TimeProvider
from ..normalization.engine import NormalizationEngine
from ..validation.engine import ValidationEngine
from ..identity.engine import IdentityEngine
from ..reasoning.engine import ReasoningEngine
from ..projection.engine import ProjectionEngine
from ..orchestrator.engine import PipelineOrchestrator
from .parser import create_parser

# Consolidated adapter lookup and SourceType mapping
_ADAPTER_MAPPINGS: dict[str, tuple[BaseAdapter, SourceType]] = {
    "resume": (ResumeAdapter(), SourceType.RESUME),
    "linkedin": (LinkedInAdapter(), SourceType.LINKEDIN),
    "github": (GitHubAdapter(), SourceType.GITHUB),
    "csv": (CSVAdapter(), SourceType.CSV),
}


def main() -> None:
    """CLI Main Entry Point representing the platform's high-level workflow."""
    parser = create_parser()
    args = parser.parse_args()

    adapter, source_type = _select_adapter(args.adapter)
    payloads = _load_payloads(args.adapter, args.input)
    config = _load_configuration()
    documents = _create_documents(adapter, source_type, args.input, payloads)

    try:
        profile = ProjectionProfile(args.profile.lower())
    except ValueError:
        sys.stderr.write(f"Error: Unsupported projection profile '{args.profile}'.\n")
        sys.exit(1)

    try:
        orchestrator = _build_pipeline(config)
        projected_results = orchestrator.run(documents, profile)
        _print_results(projected_results)
    except PipelineError as exc:
        sys.stderr.write(f"Pipeline Error: {str(exc)}.\n")
        sys.exit(1)
    except Exception as exc:
        sys.stderr.write(f"Unexpected Error: {str(exc)}.\n")
        sys.exit(1)


def _select_adapter(adapter_name: str) -> tuple[BaseAdapter, SourceType]:
    """Selects the target adapter and maps its source type enum.

    Args:
        adapter_name (str): Configured adapter string.

    Returns:
        tuple[BaseAdapter, SourceType]: Matching adapter instance and SourceType.
    """
    key = adapter_name.lower()
    if key not in _ADAPTER_MAPPINGS:
        sys.stderr.write(f"Error: Unsupported adapter '{adapter_name}'.\n")
        sys.exit(1)
    return _ADAPTER_MAPPINGS[key]


def _load_payloads(adapter_name: str, input_file: str) -> list[dict[str, Any]]:
    """Loads external candidate data dictionary records from JSON or CSV.

    Args:
        adapter_name (str): Key of the target adapter.
        input_file (str): Storage path or URI of the input file.

    Returns:
        list[dict[str, Any]]: Extracted record dictionaries.
    """
    input_path = Path(input_file)
    if not input_path.exists() or not input_path.is_file():
        sys.stderr.write(f"Error: Missing or invalid input file '{input_file}'.\n")
        sys.exit(1)

    key = adapter_name.lower()
    payload_list: list[dict[str, Any]] = []

    if key in ("resume", "linkedin", "github"):
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                payloads = json.load(f)
        except json.JSONDecodeError as exc:
            sys.stderr.write(f"Error: Malformed JSON file: {str(exc)}.\n")
            sys.exit(1)
        except Exception as exc:
            sys.stderr.write(f"Error: Failed to read file: {str(exc)}.\n")
            sys.exit(1)

        if isinstance(payloads, dict):
            payload_list = [payloads]
        elif isinstance(payloads, list):
            payload_list = payloads
        else:
            sys.stderr.write("Error: Expected JSON object or list of objects.\n")
            sys.exit(1)

    elif key == "csv":
        try:
            with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    payload_list.append(row)
        except Exception as exc:
            sys.stderr.write(f"Error: Malformed or unreadable CSV file: {str(exc)}.\n")
            sys.exit(1)

    return payload_list


def _load_configuration() -> PlatformConfiguration:
    """Locates and loads platform configuration.

    Returns:
        PlatformConfiguration: Loaded configuration object.
    """
    cwd = Path.cwd()
    configs_dir = cwd / "configs"
    if not configs_dir.exists():
        configs_dir = Path(__file__).resolve().parent.parent.parent / "configs"

    try:
        config_manager = ConfigurationManager(configs_dir)
        return config_manager.load()
    except Exception as exc:
        sys.stderr.write(f"Configuration Error: {str(exc)}.\n")
        sys.exit(1)


def _create_documents(
    adapter: BaseAdapter,
    source_type: SourceType,
    input_file: str,
    payloads: list[dict[str, Any]],
) -> list[RawCandidateDocument]:
    """Generates source instances and adapt payload records to transport models.

    Args:
        adapter (BaseAdapter): Instantiated payload adapter.
        source_type (SourceType): Configured source data type enum.
        input_file (str): Absolute file path.
        payloads (list[dict[str, Any]]): Extracted raw candidate dictionaries.

    Returns:
        list[RawCandidateDocument]: Extracted candidate transport documents.
    """
    input_path = Path(input_file)
    documents = []
    for payload in payloads:
        source_instance = SourceInstance(
            id=uuid4(),
            source_type=source_type,
            version=1,
            path=str(input_path.absolute()),
            created_at=datetime.now(timezone.utc),
            metadata={},
        )
        doc = adapter.extract(source_instance, payload)
        documents.append(doc)
    return documents


def _build_pipeline(config: PlatformConfiguration) -> PipelineOrchestrator:
    """ wires platform registries, providers, and engine dependency layers.

    Args:
        config (PlatformConfiguration): Root configuration properties.

    Returns:
        PipelineOrchestrator: Pipeline execution service.
    """
    field_registry = FieldDefinitionRegistry(config)
    source_registry = SourceRegistry(config)

    id_provider = IdentifierProvider()
    time_provider = TimeProvider()

    obs_builder = ObservationBuilder(field_registry, id_provider, time_provider)
    norm_engine = NormalizationEngine()
    val_engine = ValidationEngine()
    ident_engine = IdentityEngine()
    reason_engine = ReasoningEngine(
        field_registry=field_registry,
        source_registry=source_registry,
        confidence_config=config.confidence,
        merge_config=config.merge,
    )
    proj_engine = ProjectionEngine(config.projection)

    return PipelineOrchestrator(
        observation_builder=obs_builder,
        normalization_engine=norm_engine,
        validation_engine=val_engine,
        identity_engine=ident_engine,
        reasoning_engine=reason_engine,
        projection_engine=proj_engine,
    )


def _print_results(results: list[dict[str, Any]]) -> None:
    """Formats and writes output projected candidate dictionaries to stdout.

    Args:
        results (list[dict[str, Any]]): Projected candidate record views.
    """
    print(json.dumps(results, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
