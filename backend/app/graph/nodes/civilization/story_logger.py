import json
import uuid

from sqlalchemy.orm import Session

from app.graph.civilization_state import CivilizationSimulationState
from app.models.event import Event
from app.models.story import Story


def _pick_category_from_tool_results(tool_results: list[dict]) -> str:
    for r in tool_results or []:
        if not isinstance(r, dict):
            continue
        if not r.get("success"):
            continue
        name = r.get("tool_name") or ""
        if name in ("create_business",):
            return "Business"
        if name in ("buy_asset", "sell_asset"):
            return "Asset"
        if name in ("start_construction", "complete_construction"):
            return "Farming"
        if name in ("hire_worker", "fire_worker"):
            return "Politics"
        if name in ("take_loan", "repay_loan"):
            return "Economic"
    return "Economic"


def civ_story_logger_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    """Deterministic side-effect: log tool outcomes as Story + Event rows.

    Phase 3 requirement: keep existing story feed working in both modes.
    """
    tick_id = state.get("tick_id") or 0
    tool_results: list[dict] = state.get("tool_results", []) or []
    selected_agents: list[dict] = state.get("selected_agents", []) or []
    participants = [a.get("name") for a in selected_agents if a.get("name")]

    n_success = sum(1 for r in tool_results if isinstance(r, dict) and r.get("success"))
    category = _pick_category_from_tool_results(tool_results)

    snippets: list[str] = []
    for r in tool_results:
        if not isinstance(r, dict):
            continue
        msg = r.get("message")
        if msg and len(snippets) < 5 and r.get("success"):
            snippets.append(str(msg))

    summary = f"{n_success} successful action(s) in this tick."
    if snippets:
        summary += " " + " · ".join(snippets)
    location = "Village"

    story_id = f"civ_{tick_id}_{uuid.uuid4().hex[:8]}"
    db.add(
        Event(
            event_id=f"evt_{tick_id}_{uuid.uuid4().hex[:8]}",
            tick_id=tick_id,
            title=f"Civilization action(s): {n_success}",
            category=category,
            description=summary,
            importance=0.6,
            affected_agents="[]",
            expected_consequences=summary[:400],
            location_id=None,
        )
    )

    db.add(
        Story(
            story_id=story_id,
            tick_id=tick_id,
            title=f"Civilization growth: {n_success} actions",
            summary=summary,
            full_story=summary,
            date=f"Day {state.get('current_day', 1)}",
            time=state.get("current_time", "Morning"),
            location=location,
            category=category,
            importance=0.6,
            participants=json.dumps(participants),
            families=json.dumps([]),
            tags=json.dumps([category]),
            keywords=json.dumps(["civilization", "economy", "growth"]),
            relationship_changes=json.dumps([]),
            future_hooks=json.dumps(["Next: expand assets or resolve debts"]),
            related_story_ids=json.dumps([]),
        )
    )

    db.flush()
    return {"feed_entries": []}

