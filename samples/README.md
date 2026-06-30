# Smoke Test Sample Dataset

## Purpose

This directory contains realistic sample candidate data files designed to exercise every major pipeline stage of the Candidate Data Platform through the CLI.

These files serve as the basis for manual smoke testing and will later become the foundation for automated integration tests.

---

## Sample Files

### resume_simple.json

- **Candidate**: Alice Johnson
- **Adapter**: `resume`
- **Purpose**: Happy path — all fields use canonical names, values are clean.
- **Verifies**: Observation construction, normalization, validation (pass), identity resolution, reasoning, projection.

### resume_alias.json

- **Candidate**: Bob Smith
- **Adapter**: `resume`
- **Purpose**: Field names use aliases (`mail`, `mobile`, `technologies`, `work_history`) instead of canonical names.
- **Verifies**: `FieldDefinitionRegistry` alias resolution during observation construction.

### resume_invalid.json

- **Candidate**: Anonymous (whitespace name)
- **Adapter**: `resume`
- **Purpose**: Contains invalid email (`not-an-email`), malformed phone (`abc-def-ghij`), empty skills, and whitespace-only values.
- **Verifies**: Validation Layer produces validation failures without crashing the pipeline.

### resume_duplicate.json

- **Candidate**: Alice Johnson (duplicate)
- **Adapter**: `resume`
- **Purpose**: Same candidate as `resume_simple.json` with different casing (`ALICE JOHNSON`), phone formatting (`+91 98765 43210`), email casing (`Alice.Johnson@Example.com`), and slightly different skills.
- **Verifies**: Normalization (case, whitespace, phone formatting), identity resolution (same email → same cluster), merge strategies, confidence calculation.

### linkedin_simple.json

- **Candidate**: Alice Johnson
- **Adapter**: `linkedin`
- **Purpose**: LinkedIn profile with matching email to exercise multi-source merge.
- **Verifies**: LinkedIn adapter extraction, cross-source identity resolution, union merge for skills.

### linkedin_duplicate.json

- **Candidate**: Alice Johnson (variant: "Alice J.")
- **Adapter**: `linkedin`
- **Purpose**: Same candidate with different email casing (`Alice@Example.com`) and name abbreviation.
- **Verifies**: Email normalization resolves identity despite casing differences.

### github_simple.json

- **Candidate**: Alice Johnson
- **Adapter**: `github`
- **Purpose**: GitHub profile with matching email.
- **Verifies**: GitHub adapter extraction, cross-source identity resolution.

### github_duplicate.json

- **Candidate**: Alice Johnson (variant username)
- **Adapter**: `github`
- **Purpose**: Duplicate GitHub profile with uppercased email (`ALICE.JOHNSON@example.com`) and additional skills (`Terraform`, `CI/CD`).
- **Verifies**: Union merge strategy accumulates all unique skills across sources.

### candidates.csv

- **Candidates**: Alice Johnson, Bob Smith, Charlie Brown
- **Adapter**: `csv`
- **Purpose**: Three-row CSV with canonical column names.
- **Verifies**: CSV adapter row-by-row ingestion, multiple independent candidates in a single file, identity resolution grouping.

---

## Data Consistency

| Candidate | Files |
|---|---|
| Alice Johnson | `resume_simple.json`, `resume_duplicate.json`, `linkedin_simple.json`, `linkedin_duplicate.json`, `github_simple.json`, `github_duplicate.json`, `candidates.csv` (row 1) |
| Bob Smith | `resume_alias.json`, `candidates.csv` (row 2) |
| Charlie Brown | `candidates.csv` (row 3) |

Alice appears across multiple files with intentional variations:
- **Name**: `Alice Johnson`, `ALICE JOHNSON`, `Alice J.`
- **Email**: `alice.johnson@example.com`, `Alice.Johnson@Example.com`, `Alice@Example.com`, `ALICE.JOHNSON@example.com`
- **Phone**: `+919876543210`, `+91 98765 43210`
- **Skills**: `Python`, `python`, `SQL`, `Docker`, `AWS`, `Git`, `Linux`, `Terraform`, `CI/CD`, `Machine Learning`, `TensorFlow`

The pipeline should normalize these and merge them into a single candidate cluster.

---

## Expected Pipeline Behaviour

| Stage | Expected Behaviour |
|---|---|
| Adapter | Translates payload dictionaries to `RawCandidateDocument` objects |
| Observation Builder | Resolves aliases to canonical field names, creates typed observations |
| Normalization | Lowercases emails, strips whitespace, normalizes phone numbers, deduplicates skills |
| Validation | Passes valid fields, flags invalid email/phone in `resume_invalid.json` |
| Identity Resolution | Groups all Alice observations into one cluster based on normalized email |
| Reasoning Engine | Selects best values per field, unions skills, computes confidence |
| Projection | Returns minimal/recruiter/audit views depending on profile |

---

## CLI Commands

### Resume — Happy Path
```bash
python -m src.cli.main process --adapter resume --input samples/resume_simple.json --profile recruiter
```

### Resume — Alias Resolution
```bash
python -m src.cli.main process --adapter resume --input samples/resume_alias.json --profile recruiter
```

### Resume — Validation Failures
```bash
python -m src.cli.main process --adapter resume --input samples/resume_invalid.json --profile audit
```

### Resume — Duplicate Merge
```bash
python -m src.cli.main process --adapter resume --input samples/resume_duplicate.json --profile audit
```

### LinkedIn — Simple
```bash
python -m src.cli.main process --adapter linkedin --input samples/linkedin_simple.json --profile recruiter
```

### LinkedIn — Duplicate
```bash
python -m src.cli.main process --adapter linkedin --input samples/linkedin_duplicate.json --profile minimal
```

### GitHub — Simple
```bash
python -m src.cli.main process --adapter github --input samples/github_simple.json --profile recruiter
```

### GitHub — Duplicate
```bash
python -m src.cli.main process --adapter github --input samples/github_duplicate.json --profile audit
```

### CSV — Multi-Candidate
```bash
python -m src.cli.main process --adapter csv --input samples/candidates.csv --profile recruiter
```

### All Profiles
```bash
python -m src.cli.main process --adapter resume --input samples/resume_simple.json --profile minimal
python -m src.cli.main process --adapter resume --input samples/resume_simple.json --profile recruiter
python -m src.cli.main process --adapter resume --input samples/resume_simple.json --profile audit
```
