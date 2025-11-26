"""
Execution Service - Domain Models
Defines the core data structures for execution plans, requests, and results.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .enums import StepStatus, ExecutionStatus


class ExecutionStep(BaseModel):
    """Represents a single step in an execution plan."""
    step_id: str = Field(..., description="Unique identifier for this step")
    name: str = Field(..., description="Human-readable name of the step")
    description: str = Field(..., description="Description of what this step does")
    tool: str = Field(..., description="Name of the tool to execute (e.g., 'gmail_auth', 'slack_post')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters to pass to the tool")
    is_critical: bool = Field(default=True, description="Whether this step is critical for execution")


class ExecutionPlan(BaseModel):
    """Represents a complete execution plan with multiple steps."""
    plan_id: str = Field(..., description="Unique identifier for this plan")
    correlation_id: str = Field(..., description="Global correlation ID for tracing")
    agent_type: str = Field(..., description="Type of agent this plan is for")
    steps: List[ExecutionStep] = Field(..., description="Ordered list of steps to execute")
    schema_version: str = Field(default="1.0", description="Schema version for compatibility")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When this plan was created")


class ApprovalInfo(BaseModel):
    """Information about plan approval status"""
    required: bool = Field(default=True, description="Whether approval is required")
    status: str = Field(default="pending", description="Current approval status: pending, approved, rejected")
    approved_by: Optional[str] = Field(default=None, description="User who approved/rejected the plan")
    approved_at: Optional[datetime] = Field(default=None, description="When the plan was approved/rejected")


class ExecutionRequest(BaseModel):
    """Request to execute a plan."""
    correlation_id: str = Field(..., description="Global correlation ID for tracing")
    request_id: str = Field(..., description="Unique identifier for this execution request")
    agent_instance: Dict[str, Any] = Field(..., description="Agent instance configuration from Orchestrator")
    execution_plan: ExecutionPlan = Field(..., description="The plan to execute")
    approval: ApprovalInfo = Field(..., description="Approval information")
    dry_run: bool = Field(default=False, description="If true, simulate execution without calling real tools")


class StepError(BaseModel):
    """Error information for a failed step."""
    message: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type/category")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class StepResult(BaseModel):
    """Result of executing a single step."""
    step_id: str = Field(..., description="ID of the step that was executed")
    status: StepStatus = Field(..., description="Execution status of this step")
    started_at: datetime = Field(..., description="When step execution started")
    ended_at: datetime = Field(..., description="When step execution ended")
    tool: str = Field(..., description="Name of the tool that was executed")
    input: Dict[str, Any] = Field(default_factory=dict, description="Parameters actually used")
    output: Dict[str, Any] = Field(default_factory=dict, description="Output produced by the tool")
    error: Optional[StepError] = Field(default=None, description="Error information if step failed")


class ExecutionResult(BaseModel):
    """Overall result of an execution."""
    correlation_id: str = Field(..., description="Global correlation ID for tracing")
    request_id: str = Field(..., description="ID of the execution request")
    plan_id: str = Field(..., description="ID of the plan that was executed")
    status: ExecutionStatus = Field(..., description="Overall execution status")
    steps: List[StepResult] = Field(default_factory=list, description="Results of all executed steps")
    created_at: datetime = Field(..., description="When execution started")
    finished_at: datetime = Field(..., description="When execution finished")
    context: Dict[str, Any] = Field(default_factory=dict, description="Final execution context (shared state)")
