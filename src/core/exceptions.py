# Core exceptions definitions


class ConfigurationError(Exception):
    """
    Raised when platform configuration cannot be loaded
    or violates configuration constraints.
    """
    pass


class PipelineError(Exception):
    """Raised when orchestration fails."""
    pass

