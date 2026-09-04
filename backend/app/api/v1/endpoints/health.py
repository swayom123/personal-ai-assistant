from fastapi import APIRouter
from backend.app.schemas.health import HealthResponse

router = APIRouter()

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns current service operational health status"
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="personal-ai-assistant")
