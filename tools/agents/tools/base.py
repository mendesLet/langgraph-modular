# tools/agents/tools/base.py

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from tools.logger import log_message

class CompleteOrEscalate(BaseModel):
    """Marks the task as completed or escalates the dialogue to the supervisor."""
    cancel: bool = True
    reason: str

    class Config:
        json_schema_extra = {
            "example": {
                "cancel": True,
                "reason": "The user changed their mind.",
            },
            "example 2": {
                "cancel": True,
                "reason": "I have already completed the task.",
            },
            "example 3": {
                "cancel": False,
                "reason": "I need more information.",
            },
        }

class ToActor(BaseModel):
    """Transfers the work to the agent specialized in active action."""
    request: str = Field(
        description="The user's demand, rewritten in a coherent and clear way, "
        "and any other information that is valid for active action."
    )