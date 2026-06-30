from enum import StrEnum


class SourceType(StrEnum):
    """Represents supported input source types."""
    RESUME = "RESUME"
    LINKEDIN = "LINKEDIN"
    GITHUB = "GITHUB"
    CSV = "CSV"
    RECRUITER_NOTES = "RECRUITER_NOTES"


class ObservationStatus(StrEnum):
    """Represents the processing stage of an Observation."""
    RAW = "RAW"
    NORMALIZED = "NORMALIZED"
    VALID = "VALID"
    INVALID = "INVALID"


class DecisionState(StrEnum):
    """Represents the final state of a reasoning decision."""
    ACCEPTED = "ACCEPTED"
    UNCERTAIN = "UNCERTAIN"
    REJECTED = "REJECTED"


class FieldType(StrEnum):
    """Represents semantic field categories."""
    NAME = "NAME"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    SKILL = "SKILL"
    COMPANY = "COMPANY"
    EXPERIENCE = "EXPERIENCE"
    EDUCATION = "EDUCATION"
    LOCATION = "LOCATION"
    CERTIFICATION = "CERTIFICATION"
    OTHER = "OTHER"


class MergeStrategy(StrEnum):
    """Represents candidate record merging strategies."""
    SINGLE_VALUE = "SINGLE_VALUE"
    UNION = "UNION"
    TIMELINE = "TIMELINE"


class ProjectionProfile(StrEnum):
    """Represents profile visibility options for projected views."""
    MINIMAL = "minimal"
    RECRUITER = "recruiter"
    AUDIT = "audit"

