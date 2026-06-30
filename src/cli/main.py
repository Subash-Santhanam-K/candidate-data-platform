from __future__ import annotations
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ..core.enums import SourceType, ProjectionProfile
from ..core.exceptions import PipelineError
from ..core.models.source_instance import SourceInstance
from ..config.configuration_manager import ConfigurationManager
from ..registries.field_registry import FieldDefinitionRegistry
from ..registries.source_registry import SourceRegistry
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


def main() -> None:
    """CLI Main Entry Point representing the platform's composition root."""
    parser = create_parser()
    args = parser.parse_args()

    # 1. Select Adapter
    adapters = {
        "resume": ResumeAdapter(),
        "linkedin": LinkedInAdapter(),
        "github": GitHubAdapter(),
        "csv": CSVAdapter(),
    }
    adapter_name = args.adapter.lower()
    if adapter_name not in adapters:
        sys.stderr.write(f"Error: Unsupported adapter '{args.adapter}'.\n")
        sys.exit(1)
    adapter = adapters[adapter_name]

    # 2. Select Projection Profile
    try:
        profile = ProjectionProfile(args.profile.lower())
    except ValueError:
        sys.stderr.write(f"Error: Unsupported projection profile '{args.profile}'.\n")
        sys.exit(1)

    # 3. Read Input File
    input_path = Path(args.input)
    if not input_path.exists() or not input_path.is_file():
        sys.stderr.write(f"Error: Missing or invalid input file '{args.input}'.\n")
        sys.exit(1)

    payload_list = []
    if adapter_name in ("resume", "linkedin", "github"):
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

    elif adapter_name == "csv":
        try:
            with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    payload_list.append(row)
        except Exception as exc:
            sys.stderr.write(f"Error: Malformed or unreadable CSV file: {str(exc)}.\n")
            sys.exit(1)

    # 4. Load Configuration
    # Locate the configs folder relative to Cwd, falling back relative to script path
    cwd = Path.cwd()
    configs_dir = cwd / "configs"
    if not configs_dir.exists():
        configs_dir = Path(__file__).resolve().parent.parent.parent / "configs"

    try:
        config_manager = ConfigurationManager(configs_dir)
        config = config_manager.load()
    except Exception as exc:
        sys.stderr.write(f"Configuration Error: {str(exc)}.\n")
        sys.exit(1)

    # 5. Map SourceType Enum
    source_type_map = {
        "resume": SourceType.RESUME,
        "linkedin": SourceType.LINKEDIN,
        "github": SourceType.GITHUB,
        "csv": SourceType.CSV,
    }
    source_type = source_type_map[adapter_name]

    # 6. Adapt payloads to RawCandidateDocuments
    documents = []
    for payload in payload_list:
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

    # 7. Construct Registries and Engines (Composition Root)
    try:
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

        orchestrator = PipelineOrchestrator(
            observation_builder=obs_builder,
            normalization_engine=norm_engine,
            validation_engine=val_engine,
            identity_engine=ident_engine,
            reasoning_engine=reason_engine,
            projection_engine=proj_engine,
        )

        # 8. Run Pipeline Orchestration
        projected_results = orchestrator.run(documents, profile)

        # 9. Format Output to Stdout
        print(json.dumps(projected_results, indent=4, ensure_ascii=False))

    except PipelineError as exc:
        sys.stderr.write(f"Pipeline Error: {str(exc)}.\n")
        sys.exit(1)
    except Exception as exc:
        sys.stderr.write(f"Unexpected Error: {str(exc)}.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
