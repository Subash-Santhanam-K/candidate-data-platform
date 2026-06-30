from abc import ABC, abstractmethod
from typing import Any


class BaseNormalizer(ABC):
    """Abstract base class for field-specific normalization strategies."""

    @abstractmethod
    def normalize(self, value: Any) -> Any:
        """Normalizes a raw value according to the strategy's composed operations.

        Args:
            value (Any): The raw value to normalize.

        Returns:
            Any: The normalized value representation, or the original value if
                normalization cannot be safely applied.
        """
        pass
