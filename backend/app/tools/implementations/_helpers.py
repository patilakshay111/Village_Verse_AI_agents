import uuid
from pathlib import Path

from app.config import get_settings


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def agent_workspace(agent_id: str) -> Path:
    root = get_settings().agent_workspace_dir
    path = root / agent_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_workspace_path(agent_id: str, relative: str) -> Path:
    base = agent_workspace(agent_id).resolve()
    target = (base / relative).resolve()
    if not str(target).startswith(str(base)):
        raise PermissionError("Path escapes agent workspace")
    return target
