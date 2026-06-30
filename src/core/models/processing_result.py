from __future__ import annotations
from dataclasses import dataclass
from .golden_record import GoldenRecord
from .decision_trace import DecisionTrace
from .processing_report import ProcessingReport


@dataclass
class ProcessingResult:
    """Represents the final output of the Candidate Data Platform pipeline execution.

    Attributes:
        golden_record (GoldenRecord): The final canonical profile generated for the candidate.
        decision_trace (list[DecisionTrace]): The detailed traces explaining decisions made for each field.
        processing_report (ProcessingReport): Execution statistics, warnings, and errors.
    """
    golden_record: GoldenRecord
    decision_trace: list[DecisionTrace]
    processing_report: ProcessingReport
