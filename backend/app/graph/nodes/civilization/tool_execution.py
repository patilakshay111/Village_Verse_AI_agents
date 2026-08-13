from sqlalchemy.orm import Session

from app.graph.civilization_state import CivilizationSimulationState
from app.tools.executor import ToolExecutor
from app.tools.schemas import ToolCallRequest


def civ_tool_execution_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    executor = ToolExecutor(db)
    results: list[dict] = []
    for call in state.get("tool_calls", []):
        if not isinstance(call, dict):
            continue
        req = ToolCallRequest.model_validate(call)
        res = executor.execute(req)
        results.append(res.model_dump())
    return {"tool_results": results}

