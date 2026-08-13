import json
from typing import Any

from pydantic import BaseModel, field_validator


def coerce_string_list(value: Any) -> list[str]:
    """Normalize LLM/DB list fields to plain strings (models often return nested objects)."""
    if value is None:
        return []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return [value.strip()] if value.strip() else []
    if not isinstance(value, list):
        return [str(value)] if value else []

    out: list[str] = []
    for item in value:
        if isinstance(item, str):
            text = item.strip()
            if text:
                out.append(text)
        elif isinstance(item, dict):
            for key in ("name", "speaker", "title", "content", "family", "surname", "summary", "hook"):
                raw = item.get(key)
                if raw:
                    out.append(str(raw).strip())
                    break
            else:
                joined = " ".join(str(v) for v in item.values() if v).strip()
                if joined:
                    out.append(joined[:200])
        elif item is not None:
            out.append(str(item))
    return out


class StoryResponse(BaseModel):
    id: int
    story_id: str
    tick_id: int | None = None
    title: str
    summary: str
    full_story: str | None
    date: str | None
    time: str | None
    location: str | None
    category: str | None
    importance: float
    participants: list[str] = []
    families: list[str] = []
    tags: list[str] = []
    keywords: list[str] = []
    future_hooks: list[str] = []

    model_config = {"from_attributes": True}

    @field_validator(
        "participants", "families", "tags", "keywords", "future_hooks", mode="before"
    )
    @classmethod
    def parse_json_list(cls, v: Any) -> list[str]:
        return coerce_string_list(v)


class StoryListResponse(BaseModel):
    items: list[StoryResponse]
    total: int
    offset: int
    limit: int
