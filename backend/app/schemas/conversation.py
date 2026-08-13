import json
from typing import Any

from pydantic import BaseModel, field_validator

from app.schemas.story import coerce_string_list


class ConversationLine(BaseModel):
    speaker: str
    message: str
    emotion: str | None = None


class ConversationResponse(BaseModel):
    id: int
    tick_id: int
    location_id: str | None
    location_name: str | None = None
    event_id: str | None
    participants: list[str] = []
    lines: list[ConversationLine] = []
    important_moments: list[str] = []

    model_config = {"from_attributes": True}


def parse_conversation_lines(value: Any) -> list[ConversationLine]:
    if value is None:
        return []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return []
    if not isinstance(value, list):
        return []

    lines: list[ConversationLine] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            lines.append(ConversationLine(speaker="Someone", message=item.strip()))
        elif isinstance(item, dict):
            speaker = str(item.get("speaker") or item.get("name") or "Someone").strip()
            message = str(item.get("message") or item.get("text") or item.get("content") or "").strip()
            if not message:
                continue
            emotion = item.get("emotion")
            lines.append(
                ConversationLine(
                    speaker=speaker,
                    message=message,
                    emotion=str(emotion).strip() if emotion else None,
                )
            )
    return lines


class ConversationListResponse(BaseModel):
    items: list[ConversationResponse]
    total: int
    offset: int
    limit: int


def conversation_from_row(row: Any, location_name: str | None = None) -> ConversationResponse:
    return ConversationResponse(
        id=row.id,
        tick_id=row.tick_id,
        location_id=row.location_id,
        location_name=location_name,
        event_id=row.event_id,
        participants=coerce_string_list(row.participants),
        lines=parse_conversation_lines(row.transcript),
        important_moments=coerce_string_list(row.important_moments),
    )
