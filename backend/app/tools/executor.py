"""Execute tools separately from agent reasoning."""

from __future__ import annotations

import json
import logging

from sqlalchemy.orm import Session

from app.models.tool_execution import ToolExecution
from app.models.villager import Villager
from app.tools.registry import get_tool_registry
from app.tools.schemas import ToolCallRequest, ToolCallResult

logger = logging.getLogger(__name__)


class ToolExecutor:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.registry = get_tool_registry()

    def execute(self, request: ToolCallRequest) -> ToolCallResult:
        villager = self.db.query(Villager).filter(Villager.id == request.agent_id).first()
        if not villager:
            return self._fail(request, "Agent not found")

        role = villager.agent_role or "villager"
        allowed, reason = self.registry.can_use(role, request.tool_name)
        if not allowed:
            self._audit(request, success=False, error=reason)
            return self._fail(request, reason or "Permission denied")

        handler = self.registry.get_handler(request.tool_name)
        if not handler:
            return self._fail(request, "Handler missing")

        try:
            data = handler(self.db, villager=villager, tick_id=request.tick_id, **request.arguments)
            result = ToolCallResult(
                success=True,
                tool_name=request.tool_name,
                agent_id=request.agent_id,
                message=data.get("message", "OK"),
                data={k: v for k, v in data.items() if k != "message"},
            )
            self._audit(request, success=True, result=result.model_dump())
            return result
        except Exception as exc:
            logger.exception("Tool %s failed for %s", request.tool_name, request.agent_id)
            self._audit(request, success=False, error=str(exc))
            return self._fail(request, str(exc))

    def _fail(self, request: ToolCallRequest, error: str) -> ToolCallResult:
        return ToolCallResult(
            success=False,
            tool_name=request.tool_name,
            agent_id=request.agent_id,
            message="Failed",
            error=error,
        )

    def _audit(
        self,
        request: ToolCallRequest,
        *,
        success: bool,
        result: dict | None = None,
        error: str | None = None,
    ) -> None:
        row = ToolExecution(
            tick_id=request.tick_id,
            agent_id=request.agent_id,
            tool_name=request.tool_name,
            arguments=json.dumps(request.arguments),
            result=json.dumps(result) if result else None,
            success=success,
            error_message=(error or "")[:512] or None,
        )
        self.db.add(row)
        self.db.flush()
