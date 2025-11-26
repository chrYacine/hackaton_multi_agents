from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from orchestrator_service.domain import (
    OrchestrationRequest,
    OrchestrationResponse,
    ApproveRequest,
)
from orchestrator_service.core.orchestrator import Orchestrator
from orchestrator_service.infrastructure import InMemoryPlanStore

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
# Note: In production, use dependency injection
orchestrator = Orchestrator()
plan_store = InMemoryPlanStore()


@router.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate(request: OrchestrationRequest) -> OrchestrationResponse:
    """
    Orchestrator endpoint (Agent 3).
    
    Receives AgentSpec (from Agent 2) and returns:
    - AgentInstance
    - ExecutionPlan
    - ApprovalInfo (status=pending by default)
    
    The plan is saved in the PlanStore for later approval.
    """
    try:
        logger.info(f"📥 Received orchestration request: {request.request_id}")
        
        # Generate orchestration response
        response = orchestrator.orchestrate(request)
        
        # Save to plan store for approval workflow
        plan_store.save(response)
        
        logger.info(f"📤 Orchestration complete: plan_id={response.execution_plan.plan_id}, status={response.approval.status}")
        
        return response
    
    except Exception as e:
        logger.error(f"❌ Orchestration failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestration failed: {str(e)}"
        )


@router.post("/orchestrate/{plan_id}/approve", response_model=OrchestrationResponse)
async def approve_plan(plan_id: str, body: ApproveRequest) -> OrchestrationResponse:
    """
    Approve a pending execution plan.
    
    This endpoint allows the "commandeur" to authorize execution.
    Once approved, the plan can be sent to the Executor.
    
    Args:
        plan_id: ID of the plan to approve
        body: Approval request with approved_by field
        
    Returns:
        Updated OrchestrationResponse with approval.status = "approved"
    """
    try:
        logger.info(f"✅ Approval request for plan {plan_id} by {body.approved_by}")
        
        response = plan_store.approve(plan_id, body.approved_by)
        
        logger.info(f"📤 Plan {plan_id} approved successfully")
        
        return response
    
    except KeyError:
        logger.error(f"❌ Plan {plan_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} not found in store"
        )
    except Exception as e:
        logger.error(f"❌ Approval failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Approval failed: {str(e)}"
        )


@router.post("/orchestrate/{plan_id}/reject", response_model=OrchestrationResponse)
async def reject_plan(plan_id: str, body: ApproveRequest) -> OrchestrationResponse:
    """
    Reject a pending execution plan.
    
    Args:
        plan_id: ID of the plan to reject
        body: Rejection request with approved_by field (user who rejected)
        
    Returns:
        Updated OrchestrationResponse with approval.status = "rejected"
    """
    try:
        logger.info(f"❌ Rejection request for plan {plan_id} by {body.approved_by}")
        
        response = plan_store.reject(plan_id, body.approved_by)
        
        logger.info(f"📤 Plan {plan_id} rejected")
        
        return response
    
    except KeyError:
        logger.error(f"❌ Plan {plan_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} not found in store"
        )
    except Exception as e:
        logger.error(f"❌ Rejection failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rejection failed: {str(e)}"
        )


@router.get("/orchestrate/pending", response_model=List[OrchestrationResponse])
async def list_pending_plans() -> List[OrchestrationResponse]:
    """
    List all plans with pending approval.
    
    This endpoint is useful for:
    - UI Console to show plans awaiting approval
    - Monitoring pending executions
    - Debugging approval workflow
    
    Returns:
        List of OrchestrationResponse with approval.status = "pending"
    """
    try:
        pending = plan_store.list_pending()
        logger.info(f"📋 Retrieved {len(pending)} pending plans")
        return pending
    
    except Exception as e:
        logger.error(f"❌ Failed to list pending plans: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list pending plans: {str(e)}"
        )


@router.get("/orchestrate/{plan_id}", response_model=OrchestrationResponse)
async def get_plan(plan_id: str) -> OrchestrationResponse:
    """
    Retrieve a specific plan by ID.
    
    Args:
        plan_id: ID of the plan to retrieve
        
    Returns:
        OrchestrationResponse
    """
    try:
        response = plan_store.get(plan_id)
        
        if response is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan {plan_id} not found"
            )
        
        logger.info(f"📤 Retrieved plan {plan_id}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to retrieve plan: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve plan: {str(e)}"
        )
