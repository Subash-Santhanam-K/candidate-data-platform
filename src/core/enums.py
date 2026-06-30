from enum import Enum


class SourceType(str, Enum):
    """Represents supported input source types."""
    RESUME = "RESUME"
    LINKEDIN = "LINKEDIN"
    GITHUB = "GITHUB"
    CSV = "CSV"
    RECRUITER_NOTES = "RECRUITER_NOTES"


class ObservationStatus(str, Enum):
    """Represents the processing stage of an Observation."""
    RAW = "RAW"
    NORMALIZED = "NORMALIZED"
    VALID = "VALID"
    INVALID = "INVALID"


class DecisionState(str, Enum):
    """Represents the final state of a reasoning decision."""
    ACCEPTED = "ACCEPTED"
    UNCERTAIN = "UNCERTAIN"
    REJECTED = "REJECTED"


class FieldType(str, Enum):
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
