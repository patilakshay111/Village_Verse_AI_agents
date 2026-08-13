from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.villager import Villager


def search_web(db: Session, *, villager: Villager, query: str, **_) -> dict:
    # Stub — real web search wired in Phase 5 or when enable_web_tools=true
    return {
        "message": f"Web search stub for: {query}",
        "results": [
            {"title": "Local market bulletin", "snippet": f"No live search; query logged: {query}"},
        ],
    }


def execute_python(db: Session, *, villager: Villager, code: str, **_) -> dict:
    # Stub — sandboxed execution deferred; permission-gated to software roles only
    if len(code) > 2000:
        raise ValueError("Code too long")
    return {
        "message": "Python execution stub (not run in Phase 1)",
        "stdout": "",
        "note": "Enable sandbox in a later phase",
    }
