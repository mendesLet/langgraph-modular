"""Data models for the API endpoints."""

from typing import Optional
from pydantic import BaseModel


class UserInfo(BaseModel):
    """Model representing user information."""

    user_id: Optional[str] = ""

class Details(BaseModel):
    """Model containing request details."""

    request: str
    user_info: Optional[UserInfo] = None


class LlmRequest(BaseModel):
    """Model for a language model request."""

    id: str
    flag: str
    details: Details
