from uuid import UUID, uuid4


class IdentifierProvider:
    """Provider for generating unique observation identifiers."""

    def next_observation_id(self) -> UUID:
        """Generates a new unique UUID.

        Returns:
            UUID: A new uuid4 instance.
        """
        return uuid4()
