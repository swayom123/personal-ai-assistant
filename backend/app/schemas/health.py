from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(
        default="ok",
        description="Operational status of the service",
        json_schema_extra={"example": "ok"}
    )
    service: str = Field(
        default="personal-ai-assistant",
        description="Name of the service",
        json_schema_extra={"example": "personal-ai-assistant"}
    )
