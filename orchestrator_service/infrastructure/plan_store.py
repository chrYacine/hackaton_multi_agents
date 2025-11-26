"""
Orchestrator Service - Plan Store
In-memory storage for orchestration plans pending approval.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from ..domain import OrchestrationResponse, ApprovalStatus

logger = logging.getLogger(__name__)


class InMemoryPlanStore:
    """
    In-memory storage for orchestration plans.
    
    This is a V2 implementation. For production, consider:
    - Redis for distributed storage
    - Database for persistence
    - TTL for automatic cleanup
    """
    
    def __init__(self):
        """Initialize empty plan storage."""
        self._store: Dict[str, OrchestrationResponse] = {}
    
    def save(self, response: OrchestrationResponse) -> None:
        """
        Save an orchestration response.
        
        Args:
            response: Orchestration response to save
        """
        plan_id = response.execution_plan.plan_id
        self._store[plan_id] = response
        logger.info(f"📦 Saved plan {plan_id} with status: {response.approval.status}")
    
    def get(self, plan_id: str) -> Optional[OrchestrationResponse]:
        """
        Retrieve a plan by ID.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            OrchestrationResponse if found, None otherwise
        """
        return self._store.get(plan_id)
    
    def approve(self, plan_id: str, approved_by: str) -> OrchestrationResponse:
        """
        Approve a plan.
        
        Args:
            plan_id: Plan identifier
            approved_by: User approving the plan
            
        Returns:
            Updated OrchestrationResponse
            
        Raises:
            KeyError: If plan not found
        """
        if plan_id not in self._store:
            raise KeyError(f"Plan {plan_id} not found in store")
        
        resp = self._store[plan_id]
        resp.approval.status = ApprovalStatus.APPROVED
        resp.approval.approved_by = approved_by
        resp.approval.approved_at = datetime.utcnow()
        
        logger.info(f"✅ Plan {plan_id} approved by {approved_by}")
        return resp
    
    def reject(self, plan_id: str, rejected_by: str) -> OrchestrationResponse:
        """
        Reject a plan.
        
        Args:
            plan_id: Plan identifier
            rejected_by: User rejecting the plan
            
        Returns:
            Updated OrchestrationResponse
            
        Raises:
            KeyError: If plan not found
        """
        if plan_id not in self._store:
            raise KeyError(f"Plan {plan_id} not found in store")
        
        resp = self._store[plan_id]
        resp.approval.status = ApprovalStatus.REJECTED
        resp.approval.approved_by = rejected_by
        resp.approval.approved_at = datetime.utcnow()
        
        logger.warning(f"❌ Plan {plan_id} rejected by {rejected_by}")
        return resp
    
    def list_pending(self) -> List[OrchestrationResponse]:
        """
        List all plans with pending approval.
        
        Returns:
            List of pending orchestration responses
        """
        pending = [
            resp for resp in self._store.values()
            if resp.approval.status == ApprovalStatus.PENDING
        ]
        logger.info(f"📋 Found {len(pending)} pending plans")
        return pending
    
    def list_all(self) -> List[OrchestrationResponse]:
        """
        List all plans.
        
        Returns:
            List of all orchestration responses
        """
        return list(self._store.values())
    
    def delete(self, plan_id: str) -> bool:
        """
        Delete a plan.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            True if deleted, False if not found
        """
        if plan_id in self._store:
            del self._store[plan_id]
            logger.info(f"🗑️  Deleted plan {plan_id}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all stored plans (useful for testing)."""
        count = len(self._store)
        self._store.clear()
        logger.info(f"🧹 Cleared {count} plans from store")
