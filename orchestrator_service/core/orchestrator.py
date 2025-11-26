import uuid
import logging
from typing import Dict, Any

from orchestrator_service.domain import (
    AgentType,
    ExecutionPlan,
    ExecutionStep,
    AgentInstance,
    OrchestrationRequest,
    OrchestrationResponse,
    ApprovalInfo,
    ApprovalStatus,
)

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Agent 3: Orchestrator Service.
    Decides which agent to create and how to execute it.
    """

    def orchestrate(self, request: OrchestrationRequest) -> OrchestrationResponse:
        """
        Main orchestration method.
        1. Generate/validate correlation_id
        2. Classify agent type
        3. Generate execution plan
        4. Create agent instance
        5. Create approval info
        6. Return orchestration response
        """
        logger.info(f"🎯 Orchestrating request {request.request_id}")
        
        # 1. Generate correlation_id if not provided
        correlation_id = request.correlation_id or str(uuid.uuid4())
        logger.info(f"   Correlation ID: {correlation_id}")
        
        agent_spec = request.agent_spec
        
        # 2. Classify Agent Type (Simple heuristic for V1)
        agent_type = self._classify_agent(agent_spec)
        logger.info(f"   Classified as: {agent_type}")
        
        # 3. Generate Execution Plan
        plan = self._generate_plan(agent_type, agent_spec, correlation_id)
        logger.info(f"   Generated plan: {plan.plan_id} with {len(plan.steps)} steps")
        
        # 4. Create Agent Instance
        instance = AgentInstance(
            instance_id=str(uuid.uuid4()),
            correlation_id=correlation_id,
            agent_type=agent_type,
            config=agent_spec,
            execution_plan=plan,
        )
        
        # 5. Create Approval Info (default: pending)
        approval = ApprovalInfo(
            required=True,
            status=ApprovalStatus.PENDING,
        )
        logger.info(f"   Approval status: {approval.status}")
        
        # 6. Return Orchestration Response
        return OrchestrationResponse(
            correlation_id=correlation_id,
            request_id=request.request_id,
            agent_instance=instance,
            execution_plan=plan,
            approval=approval,
        )

    def _classify_agent(self, spec: Dict[str, Any]) -> AgentType:
        """
        Determine agent type based on spec keywords.
        In V2, this could use an LLM.
        """
        goal = spec.get("high_level_goal", "").lower()
        purpose = spec.get("agent_purpose", "").lower()
        agent_type_hint = spec.get("agent_type", "").lower()
        text = f"{goal} {purpose} {agent_type_hint}"
        
        if "email" in text and ("summar" in text or "résumé" in text):
            return AgentType.EMAIL_SUMMARY
        elif "slack" in text and "rout" in text:
            return AgentType.SLACK_ROUTER
        elif "github" in text:
            return AgentType.GITHUB_WATCHER
        
        return AgentType.GENERIC

    def _generate_plan(
        self, 
        agent_type: AgentType, 
        spec: Dict[str, Any],
        correlation_id: str
    ) -> ExecutionPlan:
        """
        Generate a static execution plan based on type.
        In V2, this will be dynamic/LLM-generated or config-driven.
        """
        steps = []
        
        if agent_type == AgentType.EMAIL_SUMMARY:
            steps = [
                ExecutionStep(
                    step_id="1",
                    name="Connect to Gmail",
                    description="Authenticate with Gmail API",
                    tool="gmail_auth",
                    is_critical=True,
                ),
                ExecutionStep(
                    step_id="2",
                    name="Fetch Emails",
                    description="Fetch unread emails from last 30 minutes",
                    tool="gmail_fetch",
                    parameters={"filter": "is:unread newer_than:30m"},
                    is_critical=True,
                ),
                ExecutionStep(
                    step_id="3",
                    name="Summarize",
                    description="Generate summary of fetched emails",
                    tool="llm_summarize",
                    is_critical=True,
                ),
                ExecutionStep(
                    step_id="4",
                    name="Send to Slack",
                    description="Post summary to Slack channel",
                    tool="slack_post",
                    is_critical=False,  # Non-critical: summary is still useful even if Slack fails
                ),
            ]
        else:
            # Generic plan
            steps = [
                ExecutionStep(
                    step_id="1",
                    name="Analyze Request",
                    description="Analyze generic request",
                    tool="llm_summarize",
                    is_critical=True,
                ),
                ExecutionStep(
                    step_id="2",
                    name="Execute Logic",
                    description="Execute generic logic",
                    tool="llm_summarize",
                    is_critical=True,
                ),
            ]
            
        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            correlation_id=correlation_id,
            agent_type=agent_type,
            steps=steps,
        )
