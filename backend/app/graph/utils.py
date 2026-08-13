import json
import logging
from typing import Any, Callable

from sqlalchemy.orm import Session

from app.graph.state import SimulationState

logger = logging.getLogger(__name__)


def to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def clamp(value: float, low: float = -100.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def checkpoint_db(db: Session) -> None:
    """Commit after each graph step — avoids holding SQLite write locks across LLM calls."""
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def wrap_node(node_fn: Callable[..., SimulationState], db: Session) -> Callable[[SimulationState], SimulationState]:
    def wrapped(state: SimulationState) -> SimulationState:
        result = node_fn(state, db=db)
        checkpoint_db(db)
        return result

    return wrapped
