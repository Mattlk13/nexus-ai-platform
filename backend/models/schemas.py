"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone
import uuid


class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


class OpenClawStartRequest(BaseModel):
    provider: str = "emergent"  # "emergent", "anthropic", or "openai"
    apiKey: Optional[str] = None  # Optional - uses Emergent key if not provided


class OpenClawStartResponse(BaseModel):
    ok: bool
    controlUrl: str
    token: str
    message: str


class OpenClawStatusResponse(BaseModel):
    running: bool
    pid: Optional[int] = None
    provider: Optional[str] = None
    started_at: Optional[str] = None
    controlUrl: Optional[str] = None
    owner_user_id: Optional[str] = None
    is_owner: Optional[bool] = None


class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: Optional[datetime] = None


class SessionRequest(BaseModel):
    session_id: str
