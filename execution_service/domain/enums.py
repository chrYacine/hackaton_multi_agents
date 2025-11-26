"""
Execution Service - Domain Enums
Defines status enumerations for execution steps and overall execution.
"""

from enum import Enum


class StepStatus(str, Enum):
    """Status of an individual execution step."""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionStatus(str, Enum):
    """Overall status of an execution."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"


class ApprovalStatus(str, Enum):
    """Status of plan approval."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
