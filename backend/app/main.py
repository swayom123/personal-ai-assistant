from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import get_settings
from backend.app.logging_config import setup_logging
from backend.app.core.middleware import RequestIDMiddleware
from backend.app.core.exceptions import (
    AppException,
    app_exception_handler,
    unhandled_exception_handler,
)
from backend.app.api.v1.api import api_router
from backend.app.schemas.health import HealthResponse

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging(log_level=settings.log_level, log_file=settings.log_file)
    logger = logging.getLogger("app.lifecycle")
    logger.info(f"Starting {settings.app_name} in {settings.app_env} mode")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Production-grade Personal AI Assistant Backend Foundation",
        debug=settings.debug,
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID and Latency Middleware
    app.add_middleware(RequestIDMiddleware)

    # Global Exception Handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Direct root health endpoint (GET /health)
    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Service Health Check",
        description="Root health endpoint returning service operational status",
    )
    async def root_health() -> HealthResponse:
        return HealthResponse(status="ok", service="personal-ai-assistant")

    # API v1 versioned routes (/api/v1/...)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
