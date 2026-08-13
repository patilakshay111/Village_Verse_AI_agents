from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.villager import Villager
from app.tools.implementations._helpers import safe_workspace_path


def read_file(db: Session, *, villager: Villager, path: str, **_) -> dict:
    target = safe_workspace_path(villager.id, path)
    if not target.is_file():
        raise FileNotFoundError(path)
    content = target.read_text(encoding="utf-8")
    return {"message": f"Read {path}", "content": content[:8000]}


def write_file(db: Session, *, villager: Villager, path: str, content: str, **_) -> dict:
    target = safe_workspace_path(villager.id, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {"message": f"Wrote {path}", "bytes": len(content.encode("utf-8"))}


def edit_file(
    db: Session,
    *,
    villager: Villager,
    path: str,
    old_text: str,
    new_text: str,
    **_,
) -> dict:
    target = safe_workspace_path(villager.id, path)
    if not target.is_file():
        raise FileNotFoundError(path)
    text = target.read_text(encoding="utf-8")
    if old_text not in text:
        raise ValueError("old_text not found in file")
    target.write_text(text.replace(old_text, new_text, 1), encoding="utf-8")
    return {"message": f"Edited {path}"}
