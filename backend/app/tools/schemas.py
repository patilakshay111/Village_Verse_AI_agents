from typing import Any

from pydantic import BaseModel, Field


class ToolCallRequest(BaseModel):
    tool_name: str
    agent_id: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    tick_id: int | None = None
    reason: str | None = None


class ToolCallResult(BaseModel):
    success: bool
    tool_name: str
    agent_id: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
