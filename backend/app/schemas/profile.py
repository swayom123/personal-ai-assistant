from typing import Any, Dict
from pydantic import BaseModel, Field

class AssistantProfile(BaseModel):
    name: str = Field(default="Aether", description="Assistant display name")
    personality: str = Field(..., description="Personality characteristics")
    response_style: str = Field(..., description="Guidelines for response structure")
    system_instructions: str = Field(..., description="Core behavioral instructions")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="Custom user configuration")
