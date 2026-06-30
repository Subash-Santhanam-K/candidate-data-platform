from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class ValidationResult:
    """Represents the results and metadata of a validation check.

    Attributes:
        passed (bool): Flag determining if all rules satisfied.
        score (float): Validation trust/confidence score (1.0 or 0.0).
        validator_name (str): Identifier of the validator that executed.
        rule_name (str): Name of the rule evaluated (or failing rule, or 'all').
        messages (list[str]): Accompanying status/error messages.
    """
    passed: bool
    score: float
    validator_name: str
    rule_name: str
    messages: list[str] = field(default_factory=list)
