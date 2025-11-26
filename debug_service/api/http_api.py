from fastapi import APIRouter, HTTPException
import logging

from orchestrator_service.domain.models import OrchestrationRequest 
# Note: The user asked to use AgentRequest from interpretation_service, but let's check what models are available.
# interpretation_service.domain.models has AgentRequest.
from interpretation_service.domain.models import AgentRequest
from debug_service.domain.models import DebugReport
from debug_service.core.debug_engine import DebugEngine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Agent Debugger"])

_debug_engine = DebugEngine()


@router.post("/debug/analyze", response_model=DebugReport)
async def analyze_agent(agent_request: AgentRequest) -> DebugReport:
    """
    Analyse statique simple de l'AgentSpec.
    """
    try:
        report = _debug_engine.analyze(agent_request)
        return report
    except Exception as e:
        logger.exception("Erreur dans /api/debug/analyze")
        raise HTTPException(status_code=500, detail=str(e))
