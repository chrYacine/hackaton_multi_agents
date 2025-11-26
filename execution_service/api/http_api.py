"""
Execution Service - HTTP API
FastAPI router for execution endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import logging

from ..domain import ExecutionRequest, ExecutionResult
from ..core import ExecutionEngine
from ..infrastructure import ToolRegistry

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["execution"])

# Initialize execution engine with tool registry
tool_registry = ToolRegistry()
execution_engine = ExecutionEngine(tool_registry=tool_registry)


@router.post("/execute", response_model=ExecutionResult)
async def execute_plan(request: ExecutionRequest) -> ExecutionResult:
    """
    Execute an execution plan.
    
    This endpoint receives an execution request containing:
    - agent_instance: Configuration from the Orchestrator
    - execution_plan: The plan to execute
    - dry_run: Whether to simulate execution
    - approved_by: User who approved the execution
    
    Returns:
        ExecutionResult with all step results and final status
    """
    try:
        logger.info(f"📥 Received execution request: {request.request_id}")
        
        # Execute the plan
        result = await execution_engine.execute(request)
        
        logger.info(f"📤 Execution completed: {result.status.value}")
        
        return result
    
    except PermissionError as e:
        logger.warning(f"⛔ Execution denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Execution failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution failed: {str(e)}"
        )


@router.get("/tools")
async def list_tools():
    """
    List all available tools in the registry.
    
    Returns:
        Dictionary with list of available tool names
    """
    try:
        tools = tool_registry.list_tools()
        return {
            "tools": tools,
            "count": len(tools)
        }
    except Exception as e:
        logger.error(f"❌ Failed to list tools: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the execution service.
    
    Returns:
        Service status and available tools count
    """
    return {
        "service": "execution_service",
        "status": "healthy",
        "tools_available": len(tool_registry.list_tools())
    }
