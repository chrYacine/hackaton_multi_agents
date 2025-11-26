"""
Execution Service - Core Execution Engine
The heart of the execution service that runs execution plans step by step.
"""

from datetime import datetime
from typing import Any, Dict
import logging

from ..domain import (
    ExecutionPlan,
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
    StepResult,
    StepStatus,
    StepError,
)
from ..interfaces import IToolRegistry

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """
    Core execution engine that executes plans step by step.
    
    Features:
    - Sequential step execution
    - Context management (shared state between steps)
    - Error handling with detailed step results
    - Dry-run mode for testing
    - Approval validation
    """
    
    def __init__(self, tool_registry: IToolRegistry):
        """
        Initialize the execution engine.
        
        Args:
            tool_registry: Registry of available tools
        """
        self.tool_registry = tool_registry
    
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Execute an execution plan.
        
        Args:
            request: Execution request containing plan and configuration
            
        Returns:
            Execution result with all step results and final status
            
        Raises:
            PermissionError: If approval is required but not granted
        """
        logger.info(f"🚀 Starting execution for request: {request.request_id}")
        logger.info(f"   Correlation ID: {request.correlation_id}")
        logger.info(f"   Plan ID: {request.execution_plan.plan_id}")
        logger.info(f"   Agent Type: {request.execution_plan.agent_type}")
        logger.info(f"   Steps: {len(request.execution_plan.steps)}")
        logger.info(f"   Dry Run: {request.dry_run}")
        
        # CRITICAL: Check approval FIRST before any execution
        self._check_approval(request)
        
        # Initialize execution context and results
        context: Dict[str, Any] = {}
        step_results: list[StepResult] = []
        started_at = datetime.utcnow()
        
        # Execute each step sequentially
        for step in request.execution_plan.steps:
            logger.info(f"\n{'='*60}")
            logger.info(f"📍 Step {step.step_id}: {step.name}")
            logger.info(f"   Tool: {step.tool}")
            logger.info(f"   Description: {step.description}")
            
            step_result = await self._execute_step(
                step=step,
                context=context,
                dry_run=request.dry_run
            )
            
            step_results.append(step_result)
            
            # If step failed, decide whether to continue
            if step_result.status == StepStatus.FAILED:
                logger.error(f"❌ Step {step.step_id} failed: {step_result.error.message if step_result.error else 'Unknown error'}")
                # V1 policy: stop execution on first failure
                logger.warning("⚠️  Stopping execution due to step failure")
                break
            
            # Merge step output into context for next steps
            if step_result.output:
                context.update(step_result.output)
                logger.info(f"✅ Step {step.step_id} completed successfully")
        
        # Determine overall execution status
        finished_at = datetime.utcnow()
        overall_status = self._determine_overall_status(step_results, request.execution_plan)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🏁 Execution completed: {overall_status.value}")
        logger.info(f"   Total steps: {len(request.execution_plan.steps)}")
        logger.info(f"   Executed: {len(step_results)}")
        logger.info(f"   Successful: {sum(1 for r in step_results if r.status == StepStatus.SUCCESS)}")
        logger.info(f"   Failed: {sum(1 for r in step_results if r.status == StepStatus.FAILED)}")
        logger.info(f"   Duration: {(finished_at - started_at).total_seconds():.2f}s")
        
        return ExecutionResult(
            correlation_id=request.correlation_id,
            request_id=request.request_id,
            plan_id=request.execution_plan.plan_id,
            status=overall_status,
            steps=step_results,
            created_at=started_at,
            finished_at=finished_at,
            context=context
        )
    
    def _check_approval(self, request: ExecutionRequest) -> None:
        """
        Verify that execution is approved.
        
        This is a CRITICAL security check. Execution will be blocked
        if approval is required but not granted.
        
        Args:
            request: Execution request with approval information
            
        Raises:
            PermissionError: If approval is required but not granted
        """
        approval = request.approval
        
        if approval.required and approval.status != "approved":
            error_msg = (
                f"🚫 Execution BLOCKED: approval status is '{approval.status}' "
                f"(required=True, approved_by={approval.approved_by})"
            )
            logger.error(error_msg)
            raise PermissionError(error_msg)
        
        logger.info(f"✅ Execution approved by: {approval.approved_by}")
        logger.info(f"   Approved at: {approval.approved_at}")

    
    async def _execute_step(
        self,
        step,
        context: Dict[str, Any],
        dry_run: bool
    ) -> StepResult:
        """
        Execute a single step.
        
        Args:
            step: Execution step to run
            context: Current execution context
            dry_run: If True, simulate execution without calling real tools
            
        Returns:
            Step result with status, output, and error (if any)
        """
        started_at = datetime.utcnow()
        
        try:
            # Check if tool exists
            if not self.tool_registry.has(step.tool):
                raise KeyError(f"Tool '{step.tool}' not found in registry")
            
            # Dry run mode: simulate execution
            if dry_run:
                logger.info(f"   🔍 DRY RUN: Simulating {step.tool}")
                output = {
                    "dry_run": True,
                    "simulated": True,
                    "message": f"Dry run simulation of {step.tool}"
                }
            else:
                # Get tool and execute
                tool = self.tool_registry.get(step.tool)
                logger.info(f"   ⚙️  Executing {step.tool}...")
                output = await tool.run(context, step.parameters)
            
            ended_at = datetime.utcnow()
            duration = (ended_at - started_at).total_seconds()
            logger.info(f"   ⏱️  Completed in {duration:.3f}s")
            
            return StepResult(
                step_id=step.step_id,
                status=StepStatus.SUCCESS,
                started_at=started_at,
                ended_at=ended_at,
                tool=step.tool,
                input=step.parameters,
                output=output,
                error=None
            )
        
        except Exception as e:
            ended_at = datetime.utcnow()
            logger.error(f"   ❌ Error executing step: {str(e)}")
            
            return StepResult(
                step_id=step.step_id,
                status=StepStatus.FAILED,
                started_at=started_at,
                ended_at=ended_at,
                tool=step.tool,
                input=step.parameters,
                output={},
                error=StepError(
                    message=str(e),
                    type=type(e).__name__,
                    details={"context_keys": list(context.keys())}
                )
            )
    
    def _determine_overall_status(
        self,
        step_results: list[StepResult],
        plan: ExecutionPlan
    ) -> ExecutionStatus:
        """
        Determine overall execution status based on step results.
        
        Args:
            step_results: List of step results
            plan: Original execution plan
            
        Returns:
            Overall execution status
        """
        if not step_results:
            return ExecutionStatus.FAILED
        
        total_steps = len(plan.steps)
        executed_steps = len(step_results)
        successful_steps = sum(1 for r in step_results if r.status == StepStatus.SUCCESS)
        failed_steps = sum(1 for r in step_results if r.status == StepStatus.FAILED)
        
        # All steps executed successfully
        if successful_steps == total_steps:
            return ExecutionStatus.SUCCESS
        
        # Some steps executed successfully, but not all
        if successful_steps > 0 and (failed_steps > 0 or executed_steps < total_steps):
            return ExecutionStatus.PARTIAL_SUCCESS
        
        # No successful steps or all failed
        return ExecutionStatus.FAILED
