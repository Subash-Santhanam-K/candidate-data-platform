from datetime import datetime, timezone


class TimeProvider:
    """Provider for obtaining current timestamps."""

    def now(self) -> datetime:
        """Returns the current timezone-aware UTC datetime.

        Returns:
            datetime: Current UTC datetime.
        """
        return datetime.now(timezone.utc)
