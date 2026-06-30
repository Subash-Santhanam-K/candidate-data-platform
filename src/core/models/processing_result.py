from __future__ import annotations
from dataclasses import dataclass, field
from .golden_record import GoldenRecord
from .decision_trace import DecisionTrace
from .processing_report import ProcessingReport


@dataclass(slots=True)
class ProcessingResult:
    """Represents the final output of the Candidate Data Platform pipeline execution.

    Attributes:
        golden_record (GoldenRecord): The final canonical profile generated for the candidate.
        processing_report (ProcessingReport): Execution statistics, warnings, and errors.
        decision_trace (list[DecisionTrace]): The detailed traces explaining decisions made for each field.
    """
    golden_record: GoldenRecord
    processing_report: ProcessingReport
    decision_trace: list[DecisionTrace] = field(default_factory=list)

