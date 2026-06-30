# Candidate Data Platform

A configuration-driven pipeline for merging candidate data from multiple sources into unified profiles.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Sample Dataset](#sample-dataset)
- [Running the Project](#running-the-project)
- [CLI Arguments](#cli-arguments)
- [Example Output](#example-output)
- [Design Decisions](#design-decisions)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)
- [Conclusion](#conclusion)

---

## Overview

Recruiting teams ingest candidate details from various platforms, including resumes, LinkedIn profiles, GitHub JSON exports, and ATS spreadsheets. This data is naturally heterogeneous, using varying field keys (such as `mail` vs `email`) and carrying format discrepancies, typos, and conflicting values. 

To create a consistent view of a candidate, this data must be mapped to a canonical model. The process involves parsing inputs, normalizing values, validating formats, clustering records representing the same individual, and resolving conflicting values into a single Golden Record.

This project implements a pipeline that executes these steps sequentially. Data validation, normalization, clustering, and conflict-resolution rules are driven by external YAML configurations, allowing adjustments to pipeline behavior without altering python code.

---

## Features

- **Ingestion Adapters**: Modules for parsing Resume, LinkedIn, GitHub, and CSV formats.
- **Canonical Observation Model**: Translates raw attributes into standardized observations with tracking metadata.
- **Alias Resolution**: Maps raw keys to canonical fields using field registry definitions.
- **Data Normalization**: Cleans casing, whitespace, and formatting (e.g., phone numbers, emails, skill lists).
- **Validation**: Rules-based format verification scoring value quality.
- **Transitive Identity Resolution**: DSU clustering grouping profiles by shared email or phone.
- **Pluggable Merge Strategies**: Single Value, Union, and Timeline conflict resolution.
- **Confidence Calculator**: Weighted scoring based on source reliability, validation, agreement, and age.
- **Projection Layer**: Restricts final JSON output structures to minimal, recruiter, or audit profiles.
- **CLI Interface**: Ingests files and prints output profiles directly to stdout.

---

## Architecture

```
External Payloads (Resume, LinkedIn, GitHub, CSV)
    │
    ▼
Adapters -> Observation Builder -> Normalization -> Validation -> Identity -> Reasoning -> Projection -> Output
```

- **Adapters**: Translate raw dictionaries into candidate transport documents.
- **Observation Builder**: Standardizes raw attributes using alias mappings from the field registry.
- **Normalization**: Cleans format discrepancies in-place.
- **Validation**: Inspects value formats and sets validation metrics.
- **Identity Resolution**: Links profiles by matching unique identifiers through a DSU structure.
- **Reasoning**: Resolves attribute conflicts using the merge configurations.
- **Projection**: Filters fields to return structured dictionaries depending on the profile selected.
- **CLI Output**: Serves as the composition root, executing the orchestrator and printing results.

---

## Project Structure

```
configs/                  # Configuration files
samples/                  # Ingestion sample data
src/
    adapters/             # Conversion adapters
    cli/                  # Parser and CLI main entrypoint
    config/               # Configuration mappings
    core/                 # Shared enums and models
    identity/             # DSU clustering logic
    normalization/        # Text normalization utils
    observations/         # Canonical observation builder
    orchestrator/         # Pipeline orchestration logic
    projection/           # Field projection profiles
    reasoning/            # Conflict merge strategies
    registries/           # Field and source registries
    validation/           # Formats validation rules
```

---

## Configuration

Configuration values are declared across isolated YAML files in the `configs/` folder:
- `fields.yaml`: Maps canonical names, semantic categories, merge strategies, aliases, and descriptions.
- `sources.yaml`: Defines target adapters, toggling flags, and source reliability levels.
- `merge.yaml`: Maps tie-breaker algorithms and sorting directions.
- `confidence.yaml`: Configures factors weighting and acceptance thresholds.
- `projection.yaml`: Defines what metrics and fields are visible per visibility profile.

A change to these files adjusts the pipeline execution logic without requiring code edits.

---

## Sample Dataset

- `resume_simple.json`: Ingests clean candidate values using canonical fields to verify the happy path.
- `resume_alias.json`: Employs non-canonical fields to verify alias mapping logic.
- `resume_invalid.json`: Formulates malformed email, phone, and blank attributes to verify validator logic.
- `resume_duplicate.json`: Maps Alice Johnson with slightly different formats to test normalization rules.
- `linkedin_simple.json` / `linkedin_duplicate.json`: Test multi-source profile merges and email casing normalization.
- `github_simple.json` / `github_duplicate.json`: Test GitHub adapter mapping and skill lists union accumulation.
- `candidates.csv`: Ingests multiple candidate rows to verify CSV ingestion.

---

## Running the Project

### Installation & Execution
```bash
# Install dependency
pip install pyyaml

# JSON Ingestion under Recruiter Profile
python -m src.cli.main process --adapter resume --input samples/resume_simple.json --profile recruiter

# CSV Ingestion under Recruiter Profile
python -m src.cli.main process --adapter csv --input samples/candidates.csv --profile recruiter

# JSON Ingestion under Audit Profile
python -m src.cli.main process --adapter resume --input samples/resume_simple.json --profile audit
```

---

## CLI Arguments

| Argument | Description |
|---|---|
| `--adapter` | Ingestion parser type: `resume`, `linkedin`, `github`, or `csv`. |
| `--input` | Path to the candidate input file. |
| `--profile` | Projection format: `minimal`, `recruiter`, or `audit`. |

---

## Example Output

Process output using `recruiter` profile:
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
        "education": [
            "B.Tech Computer Science, IIT Delhi"
        ],
        "experience": [
            "Software Engineer at TechCorp (2022-2025)"
        ],
        "location": "Bangalore, India",
        "confidence": {
            "name": 0.9875,
            "email": 0.9875,
            "phone": 0.9875,
            "skills": 0.9875,
            "education": 0.9875,
            "experience": 0.9875,
            "location": 0.9875
        }
    }
]
```

---

## Design Decisions

- **Layered Architecture**: Keeps pipeline logic partitioned into simple stages to make testing straightforward.
- **Registry Pattern**: Decouples logic from metadata structures by looking up fields and sources in registries.
- **Strategy Pattern**: Isolates value merge behaviors (`SINGLE_VALUE`, `UNION`, `TIMELINE`) in modular strategy classes.
- **Builder Pattern**: Encapsulates observation formatting and logs process warnings during alias matching.
- **Dependency Injection**: Passes registries and engines via class constructors to simplify unit testing.
- **YAML Configuration**: Decouples settings from python logic to enable behavior modifications without code updates.

---

## Current Limitations

- Runtime output projection schemas are not implemented.
- Field remapping configs (e.g. `from`) are not supported.
- CSV list-type cells are parsed as scalar strings rather than lists.
- Recruiter Notes adapter is declared but disabled.

---

## Future Improvements

- Support runtime field schemas.
- Introduce key remapping configurations.
- Parse collection fields from CSV cells.
- Integrate active applicant tracking adapters.
- Implement REST API gateways.
- Support batch pipeline runs.
- Support fuzzy candidate matching.

---

## Conclusion

This Candidate Data Platform parses, standardizes, clusters, and aggregates profile data across multiple source networks. Relying on a decoupled layered structure and declarative configuration maps, the pipeline builds conflict-resolved Golden Record views.
