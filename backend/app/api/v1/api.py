from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, chat, models, conversations, voice

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(chat.router, tags=["AI Chat & Inference"])
api_router.include_router(models.router, tags=["Model Providers"])
api_router.include_router(conversations.router, tags=["Conversation Management"])
api_router.include_router(voice.router, prefix="/voice", tags=["Voice Assistant"])
