from fastapi import APIRouter
from backend.app.schemas.llm import ModelsResponse
from backend.app.services.llm.factory import llm_factory

router = APIRouter()

@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="List Available Models",
    description="Returns available models from configured AI providers (OpenAI, Ollama, and local engines)."
)
async def get_models() -> ModelsResponse:
    return await llm_factory.list_all_models()
