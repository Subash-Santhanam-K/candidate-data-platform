# Candidate Data Platform

A highly configurable, layered data integration pipeline for constructing canonical candidate profiles from heterogeneous resume and social media data sources.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Pipeline Explanation](#pipeline-explanation)
5. [Project Structure](#project-structure)
6. [Configuration](#configuration)
7. [Sample Dataset](#sample-dataset)
8. [Running the Project](#running-the-project)
9. [CLI Usage](#cli-usage)
10. [Example Outputs](#example-outputs)
11. [Smoke Testing](#smoke-testing)
12. [Design Decisions](#design-decisions)
13. [Assumptions](#assumptions)
14. [Current Limitations](#current-limitations)
15. [Future Enhancements](#future-enhancements)
16. [Technologies Used](#technologies-used)
17. [Conclusion](#conclusion)

---

## Project Overview

In modern recruiting, candidate profiles are scattered across multiple, heterogeneous sources including resumes, LinkedIn profiles, GitHub repositories, and internal applicant tracking system (ATS) databases. Integrating these disparate payloads presents significant challenges: data formats are inconsistent, field names vary widely (e.g., `mail` vs. `email`), data quality is unpredictable, and attributes frequently conflict.

The **Candidate Data Platform** is an enterprise-grade, configuration-driven data integration pipeline designed to solve this problem. The system extracts raw candidate data from multiple sources, maps it to a canonical model, applies normalization and validation rules, resolves identity linkages transitively, resolves attribute conflicts using field-specific merge strategies, and generates unified **Golden Records**. 

The platform relies on a strict separation of concerns, utilizing a decoupled, layered architecture. It is designed to be highly configuration-driven: all field definitions, aliases, source weights, reliability scores, merge strategies, validation rules, and projection templates are controlled via external YAML configuration files. This allows recruitment operations to adjust pipeline logic and visibility parameters dynamically without modifying the underlying Python code.

---

## Key Features

- **Multi-Source Ingestion**: Out-of-the-box adapters translating JSON payloads and CSV rows into the platform's unified transport models.
- **Layered Architecture**: Decoupled design where adapters, observation construction, normalization, validation, identity resolution, reasoning, and projection operate independently.
- **Alias Resolution**: Automatically maps diverse source attributes to canonical fields using a central metadata registry.
- **Field-Specific Normalization**: Extensible operations to strip whitespace, lowercase text, format phone numbers, and clean candidate attributes.
- **Validation Engine**: Performs format validation (e.g., emails and phone numbers) to score field reliability.
- **Transitive Identity Resolution**: Groups source observations from matching email or phone handles into candidate clusters using Disjoint Set Union (DSU) algorithms.
- **Configurable Merge Strategies**: Resolves field conflicts using `SINGLE_VALUE` (newest/most reliable), `UNION` (collection consolidation), and `TIMELINE` (chronological sorting) strategies.
- **Confidence Scoring**: Computes field-specific confidence values based on source reliability, validation outcomes, freshness, and consensus.
- **Projection Profiles**: Supports `minimal`, `recruiter`, and `audit` views to control candidate data visibility for different downstream consumers.
- **YAML-driven Configuration**: Centralizes all metadata definitions, feature toggles, and merge policies in declarative config files.
- **CLI Execution**: Thin CLI composition root executing files and printing outputs to stdout as formatted JSON.

---

## Architecture

The diagram below illustrates the sequential data flow from external raw payloads to the final projected CLI output:

```
External Payloads
(Resume, LinkedIn, GitHub, CSV)
       │
       ▼
  [ Adapters ]           <-- Translates payloads to RawCandidateDocument
       │
       ▼
[ Observation Builder ]  <-- Resolves aliases, constructs Canonical Observations
       │
       ▼
 [ Normalization ]       <-- Formats, lowercases, cleans raw observations
       │
       ▼
  [ Validation ]         <-- Evaluates value formats, records ValidationResult
       │
       ▼
[ Identity Resolution ]  <-- Groups documents into CandidateClusters via DSU
       │
       ▼
 [ Reasoning Engine ]    <-- Merges fields, calculates confidence, creates GoldenRecord
       │
       ▼
[ Projection Engine ]    <-- Formats view dictionary based on ProjectionProfile
       │
       ▼
    CLI Output           <-- Prints structured JSON payload to stdout
```

### Data Flow Execution
1. **Extraction**: The CLI loads raw data files and invokes the corresponding source adapter.
2. **Translation**: The adapter constructs `RawCandidateDocument` and `RawAttribute` models, preserving original keys.
3. **Canonicalization**: The `ObservationBuilder` maps raw attributes to canonical fields and issues observations.
4. **Enrichment**: Observations are successively normalized (in-place value cleaning) and validated (attaching passing scores).
5. **Clustering**: The `IdentityEngine` indexes observations, links shared identifiers (email or phone) via a DSU data structure, and outputs `CandidateCluster` objects.
6. **Conflict Resolution**: The `ReasoningEngine` merges attributes field-by-field, computes confidence scores, and produces a `GoldenRecord` containing detailed decision traces.
7. **Projection**: The `ProjectionEngine` filters the Golden Record to the requested visibility profile.

---

## Pipeline Explanation

### Adapter Layer
- **Purpose**: Translates raw external payloads into the platform's transport models.
- **Responsibilities**: Extracts raw key-value pairs, preserves original field names, maps source metadata, and initializes document envelopes. It does not perform validation, normalization, or mapping.
- **Input**: A parsed JSON payload or a CSV row dictionary, along with a `SourceInstance` definition.
- **Output**: A `RawCandidateDocument` containing a list of `RawAttribute` models.

### Observation Builder
- **Purpose**: Constructs canonical observations from raw attribute transport models.
- **Responsibilities**: Performs alias lookup using the `FieldDefinitionRegistry`. Maps recognized fields to typed `Observation` models, tracking source provenance and system metrics. Unmapped fields are categorized as `UNKNOWN_FIELD` diagnostic warnings.
- **Alias Resolution**: Resolves raw keys (e.g. `mail` or `tele`) to canonical names (`email`, `phone`) automatically.
- **Canonical Observations**: Formulates standard observations with UUID keys, original raw values, and timestamps.
- **Diagnostics**: Emits diagnostics reporting unrecognized fields and processing warnings.

### Normalization Layer
- **Purpose**: Standardizes raw attribute values to prevent formatting conflicts.
- **Responsibilities**: Mutates `Observation.normalized_value` in place.
- **Email Normalization**: Lowercases characters, strips leading and trailing whitespaces.
- **Phone Normalization**: Standardizes numbers by removing spaces, brackets, hyphens, and separating prefixes.
- **Skill Normalization**: Lowercases names, normalizes common version flags (e.g., Python 3 -> Python).
- **Default Normalization**: Strips whitespace and handles scalar fallbacks.

### Validation Layer
- **Purpose**: Assesses the semantic validity of normalized observations.
- **Responsibilities**: Attaches a `ValidationResult` tracking validation status, a quality score (0.0 to 1.0), and execution logs.
- **Rule-Based Validation**: Evaluates validators specified in the configuration files.
- **Validators**: Implements standard checks including `email` (regex checks) and `phone` (digit count and formatting).

### Identity Resolution
- **Purpose**: Merges candidates across multiple data sources into distinct entity clusters.
- **Responsibilities**: Performs identity linkage mapping and outputs grouped candidate observations.
- **IdentityIndex**: Indexes observations using email and phone identity keys.
- **DSU (Disjoint Set Union)**: Links source documents sharing matching identity keys, mapping multiple credentials to a single master candidate entity.
- **Transitive Identity Resolution**: Handles multi-key linkages (e.g., Resume has Email A and Phone A, LinkedIn has Email A and Phone B; all observations link to the same candidate).
- **CandidateCluster**: A collection of observations linked to a single candidate.

### Reasoning Layer
- **Purpose**: Resolves value conflicts across clustered observations to construct a profile.
- **Responsibilities**: Evaluates observations field-by-field to produce Accept/Reject decisions and confidence metrics.
- **DecisionContext**: Groups candidate cluster observations for a specific canonical field.
- **Merge Strategies**:
  - `SINGLE_VALUE`: Selects the single newest or most reliable valid observation.
  - `UNION`: Consolidates unique, non-empty, trimmed string values.
  - `TIMELINE`: Chronologically arranges observations (e.g., work history).
- **Confidence Scoring**: Computes a weighted confidence average from four factors: consensus (agreement), freshness, validation score, and source reliability.
- **Decision Creation**: Evaluates final confidence against configurable thresholds to accept, flag as uncertain, or reject.
- **Decision Traces**: Logs source references, policy references, and decision rationales.

### Projection Layer
- **Purpose**: Exposes tailored candidate views according to consumer requirements.
- **Responsibilities**: Filters fields and metadata without modifying the underlying domain data.
- **Projection Profiles**:
  - `minimal`: Exposes only basic contact info (e.g., name, email).
  - `recruiter`: Exposes all resolved fields along with confidence ratings.
  - `audit`: Exposes all resolved fields, confidence ratings, and complete decision traces.

### Pipeline Orchestrator
- **Purpose**: Coordinates execution flow across all pipeline stages.
- **Responsibilities**: Sequentially routes candidate states, wraps runtime errors, and executes stages within a try-except structure.
- **Error Handling**: Catches exceptions and raises `PipelineError` while preserving the stack trace using `raise PipelineError(...) from exc`.

---

## Project Structure

```
candidate-data-platform/
│
├── configs/                  # Declaration configurations files (YAML)
│   ├── confidence.yaml       # Confidence weights and threshold rules
│   ├── fields.yaml           # Canonical field definitions and aliases
│   ├── merge.yaml            # Tie-breaker and sort configurations
│   ├── platform.yaml         # Global execution and pipeline feature toggles
│   ├── projection.yaml       # Visibility layouts and profile structures
│   ├── sources.yaml          # Data source types, adapters, and reliability ratings
│   └── validation.yaml       # Field format checking templates
│
├── samples/                  # Smoke test sample data inputs
│   ├── README.md             # Dataset documentation
│   ├── candidates.csv        # Multi-candidate CSV import
│   ├── github_duplicate.json # Cased email duplicate profile
│   ├── github_simple.json    # Standard GitHub profile
│   ├── linkedin_duplicate.json # Cased email LinkedIn profile
│   ├── linkedin_simple.json  # Standard LinkedIn profile
│   ├── resume_alias.json     # Resume using field name aliases
│   ├── resume_duplicate.json # Cased duplicate resume
│   ├── resume_invalid.json   # Malformed value resume
│   └── resume_simple.json    # Happy-path resume
│
├── src/                      # Source code directory
│   ├── adapters/             # External payload extraction adapters
│   ├── cli/                  # CLI arguments parser and application entry point
│   ├── config/               # Configuration manager and dataclass mappings
│   ├── core/                 # Shared enums, domain models, and exception classes
│   ├── identity/             # DSU-based identity resolution clustering
│   ├── normalization/        # Attribute format normalizers
│   ├── observations/         # Alias resolution and observation builder
│   ├── orchestrator/         # Pipeline coordinator engine
│   ├── projection/           # Configurable visibility filters
│   ├── reasoning/            # Field merge strategies and confidence calculators
│   ├── registries/           # Registry lookups for fields and sources
│   └── validation/           # Format checking rules and validator engines
│
├── pyproject.toml            # Project packaging metadata
└── README.md                 # System documentation
```

---

## Configuration

Platform behavior is controlled via YAML configuration files located in the `configs/` directory.

### fields.yaml
Controls candidate field mappings. Defines canonical names, semantic types, merge strategies, format checks, and aliases:
```yaml
fields:
  name:
    type: NAME
    strategy: SINGLE_VALUE
    required: false
    aliases: [full_name, fullname, display_name]
...
```

### sources.yaml
Controls source parameters. Declares system-recognized data sources, mapped adapter module names, and source reliability ratings:
```yaml
sources:
  resume:
    reliability: 0.95
    adapter: resume_adapter
    enabled: true
...
```

### merge.yaml
Controls resolution rules. Specifies defaults for merge strategies, including tie-breakers and timeline sort order:
```yaml
single_value:
  tie_breaker: newest
timeline:
  sort: descending
...
```

### confidence.yaml
Controls confidence scoring. Defines weights (agreement, freshness, validation, and source reliability) and thresholds for accepted or uncertain values:
```yaml
weights:
  agreement: 0.40
  source_reliability: 0.25
  freshness: 0.20
  validation: 0.15
thresholds:
  accepted: 0.70
  uncertain: 0.45
```

### projection.yaml
Controls output visibility. Specifies include rules, confidence scores, and trace flags for `minimal`, `recruiter`, and `audit` profiles:
```yaml
profiles:
  minimal:
    include: [name, email]
    include_confidence: false
  recruiter:
    include: ["*"]
    include_confidence: true
```

---

## Sample Dataset

The `samples/` folder contains test candidate files designed to verify pipeline logic:

1. **resume_simple.json**: Standard resume payload containing canonical keys. Verifies the happy path.
2. **resume_alias.json**: Resume utilizing alias keys (e.g. `mail`, `mobile`). Verifies the registry's alias resolution.
3. **resume_invalid.json**: Malformed inputs (e.g. invalid email format, blank names, whitespace skills). Verifies formatting checks and validation score calculations.
4. **resume_duplicate.json**: Resume with varying case, spacing, and numbers. Verifies normalization.
5. **linkedin_simple.json** & **linkedin_duplicate.json**: LinkedIn profiles featuring cased emails. Verifies cross-source mapping and email casing normalization.
6. **github_simple.json** & **github_duplicate.json**: GitHub profiles mapping to the GitHub adapter, verifying collection consolidation and the `UNION` merge strategy.
7. **candidates.csv**: Three-row candidate list. Verifies the CSV ingestion process and multi-record index partitioning.

---

## Running the Project

### Prerequisites
- Python >= 3.12
- No external runtime dependencies (built entirely using standard libraries and standard dataclasses).

### Running the CLI
Execute the main entry point to parse, ingest, process, and project inputs:

```bash
# Process a resume using the recruiter view
python -m src.cli.main process \
    --adapter resume \
    --input samples/resume_simple.json \
    --profile recruiter

# Process a CSV spreadsheet using the audit view
python -m src.cli.main process \
    --adapter csv \
    --input samples/candidates.csv \
    --profile audit
```

---

## CLI Usage

The CLI parser supports the `process` command with the following options:

- `process`: Executes the processing pipeline.
- `--adapter`: Mapped adapter type (`resume`, `linkedin`, `github`, `csv`).
- `--input`: File path containing the candidate data records.
- `--profile`: Projection layout profile (`minimal`, `recruiter`, `audit`).

---

## Example Outputs

### Minimal Profile
Exposes basic candidate identifiers:
```json
[
    {
        "name": "Alice Johnson",
        "email": "alice.johnson@example.com"
    }
]
```

### Recruiter Profile
Exposes candidate details along with field confidence ratings:
```json
[
    {
        "name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "phone": "+919876543210",
        "skills": [
            "docker",
            "python",
            "sql"
        ],
        "confidence": {
            "name": 0.9875,
            "email": 0.9875,
            "phone": 0.9875,
            "skills": 0.9875
        }
    }
]
```

### Audit Profile
Exposes candidate details, confidence ratings, and decision traces for audit tracking:
```json
[
    {
        "name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "phone": "+919876543210",
        "skills": [
            "docker",
            "python",
            "sql"
        ],
        "confidence": {
            "name": 0.9875,
            "email": 0.9875,
            "phone": 0.9875,
            "skills": 0.9875
        },
        "decision_trace": {
            "name": {
                "decision_id": "cfa53b34-8cbb-462d-a2f0-7b98a032d9df",
                "decision_state": "ACCEPTED",
                "reason": "Selected newest valid observation",
                "observation_references": [
                    "0aefd90e-bf33-4f9e-bf33-da72a1bf33ef"
                ],
                "policy_references": [
                    "SINGLE_VALUE"
                ]
            }
        }
    }
]
```

---

## Smoke Testing

| Target Test | Ingestion Command | Expected Pipeline Outcome |
|---|---|---|
| **resume_simple** | `python -m src.cli.main process --adapter resume --input samples/resume_simple.json --profile recruiter` | Resolves canonical fields; constructs high-confidence attributes. |
| **resume_alias** | `python -m src.cli.main process --adapter resume --input samples/resume_alias.json --profile recruiter` | Resolves aliases like `mail` to `email`; generates valid outputs. |
| **resume_invalid**| `python -m src.cli.main process --adapter resume --input samples/resume_invalid.json --profile audit` | Flags malformed values; validates fields with reduced confidence. |
| **resume_duplicate**| `python -m src.cli.main process --adapter resume --input samples/resume_duplicate.json --profile audit` | Normalizes phone formats and casing; clusters duplicated profiles. |
| **linkedin_simple**| `python -m src.cli.main process --adapter linkedin --input samples/linkedin_simple.json --profile recruiter` | Parses LinkedIn structures; processes candidate profile. |
| **github_simple**  | `python -m src.cli.main process --adapter github --input samples/github_simple.json --profile recruiter` | Extracts profile details using the GitHub adapter mapping. |
| **candidates_csv** | `python -m src.cli.main process --adapter csv --input samples/candidates.csv --profile recruiter` | Ingests CSV rows; runs pipeline for Bob, Charlie, and Alice Johnson. |

---

## Design Decisions

- **Layered Architecture**: Isolates normalization, validation, clustering, and reasoning to maintain a clean separation of concerns.
- **Registry Pattern**: Centralizes candidate field and source definitions to decouple system components from hardcoded metadata.
- **Strategy Pattern**: Implements merge strategies (e.g. single-value, union, and timeline) as pluggable classes to simplify strategy registration.
- **Builder Pattern**: Encapsulates observation creation to decouple diagnostics tracking from core pipeline coordination.
- **Dependency Injection**: Passes all configurations, registries, and engines via constructors to ensure mockability and testability.
- **Configuration-Driven Design**: Drives system behavior via YAML files to support runtime changes without code modification.
- **Golden Record Model**: Generates unified candidate profiles with confidence ratings and decision traces for audit tracking.
- **Canonical Observation Model**: Tracks raw data, source metadata, and system timestamps to maintain complete data lineage.

---

## Assumptions

- Candidate identity keys (email and phone number) are reliable for matching and linking records.
- Source data timestamps are accurate and can be used to resolve newer vs. older values.
- Merged properties for `skills` and `certifications` are string lists, while other attributes are treated as scalars or timelines.

---

## Current Limitations

- **No Runtime Projection Schema**: Custom field projection schemas cannot be defined dynamically at runtime.
- **No Field Remapping**: Data remapping rules (e.g. `from` mapping declarations) are not supported.
- **CSV List Constraints**: Multi-valued columns in CSV files are parsed as scalar strings instead of string lists.
- **Disabled Recruiter Notes Adapter**: The adapter mapping for `recruiter_notes` is reserved for future implementation and is currently disabled.

---

## Future Enhancements

- Support for dynamic, runtime-defined projection schemas.
- Configurable missing-value fallback policies.
- Declarative key remapping parameters.
- Built-in adapters for external ATS APIs (e.g. Greenhouse, Lever).
- Fuzzy identity matching for names and addresses.
- Machine-learning-based confidence scoring.
- REST API layer for real-time candidate processing.
- Batch processing and parallel pipeline execution.

---

## Technologies Used

- **Python 3.12**: Core execution runtime.
- **PyYAML**: Parses platform configurations.
- **Dataclasses**: Defines domain model attributes with typing and slot constraints.
- **argparse**: Parses command-line inputs.
- **UUID**: Generates observation and candidate identifiers.
- **JSON & CSV**: Structured candidate file parsers.

---

## Conclusion

The **Candidate Data Platform** is a robust, modular, and configuration-driven candidate data integration pipeline. By leveraging a layered architecture, transitive identity resolution, and flexible merge strategies, the platform converts unstructured candidate information into reliable **Golden Records** with detailed decision traces. The YAML-driven design allows teams to adapt the platform's behavior without code changes, providing a maintainable and scalable solution for modern recruiting workflows.
