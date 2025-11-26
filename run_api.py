import uvicorn
from fastapi import FastAPI

from interpretation_service.api.http_api import router as interpret_http_router
from interpretation_service.api.ws_api import router as interpret_ws_router
from chat_service.api.chat_api import router as chat_router
from orchestrator_service.api.http_api import router as orchestrator_router
from debug_service.api.http_api import router as debug_router
from execution_service.api.http_api import router as execution_router
from interpretation_service.infrastructure.logging_config import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Multi-Agent Service", version="0.1.0")

    # Agent 2 (Interpretation Service)
    app.include_router(interpret_http_router, prefix="/api", tags=["Agent 2 - Interpretation"])
    app.include_router(interpret_ws_router, prefix="/api", tags=["Agent 2 - Interpretation"])
    
    # Agent 1 (Chat Service)
    app.include_router(chat_router, prefix="/api", tags=["Agent 1 - Chat"])

    # Agent 3 (Orchestrator Service)
    app.include_router(orchestrator_router, prefix="/api", tags=["Agent 3 - Orchestrator"])
    
    # Agent Debugger (Debug Service)
    app.include_router(debug_router, prefix="/api", tags=["Agent Debugger"])
    
    # Agent 4 (Execution Service)
    app.include_router(execution_router, tags=["Agent 4 - Execution"])

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "run_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
