from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .enums import AgentType, ApprovalStatus


class ExecutionStep(BaseModel):
    """Single step in the execution plan"""
    step_id: str
    name: str
    description: str
    tool: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    is_critical: bool = Field(default=True, description="Whether this step is critical for execution")


class ExecutionPlan(BaseModel):
    """High-level plan for agent execution"""
    plan_id: str
    correlation_id: str = Field(..., description="Global correlation ID for tracing")
    agent_type: AgentType
    steps: List[ExecutionStep]
    schema_version: str = Field(default="1.0", description="Schema version for compatibility")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentInstance(BaseModel):
    """Represents a created agent instance"""
    instance_id: str
    correlation_id: str = Field(..., description="Global correlation ID for tracing")
    agent_type: AgentType
    status: str = "created"
    config: Dict[str, Any] = Field(default_factory=dict)
    execution_plan: ExecutionPlan
    schema_version: str = Field(default="1.0", description="Schema version for compatibility")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApprovalInfo(BaseModel):
    """Information about plan approval status"""
    required: bool = Field(default=True, description="Whether approval is required")
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING, description="Current approval status")
    approved_by: Optional[str] = Field(default=None, description="User who approved/rejected the plan")
    approved_at: Optional[datetime] = Field(default=None, description="When the plan was approved/rejected")


class OrchestrationRequest(BaseModel):
    """Request to orchestrate an agent from a spec"""
    request_id: str
    correlation_id: Optional[str] = Field(default=None, description="Optional correlation ID (generated if not provided)")
    user_id: str
    agent_spec: Dict[str, Any]


class OrchestrationResponse(BaseModel):
    """Response from orchestration with approval information"""
    correlation_id: str = Field(..., description="Global correlation ID for tracing")
    request_id: str
    agent_instance: AgentInstance
    execution_plan: ExecutionPlan
    approval: ApprovalInfo = Field(default_factory=ApprovalInfo, description="Approval information")
    schema_version: str = Field(default="1.0", description="Schema version for compatibility")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApproveRequest(BaseModel):
    """Request to approve or reject a plan"""
    approved_by: str = Field(..., description="User approving/rejecting the plan")
