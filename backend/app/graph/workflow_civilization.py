import logging

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.config import get_settings
from app.graph.civilization_state import CivilizationSimulationState
from app.graph.nodes.civilization import (
    civ_ai_worker_factory_node,
    civ_agent_selector_node,
    civ_asset_manager_node,
    civ_business_engine_node,
    civ_construction_engine_node,
    civ_decision_engine_node,
    civ_economy_engine_node,
    civ_evolution_node,
    civ_goal_planner_node,
    civ_innovation_engine_node,
    civ_organization_engine_node,
    civ_software_company_node,
    civ_story_logger_node,
    civ_tool_execution_node,
    civ_tool_selection_node,
    civ_world_loader_node,
)
from app.graph.utils import wrap_node

logger = logging.getLogger(__name__)


def build_civilization_graph(db: Session):
    settings = get_settings()
    graph = StateGraph(CivilizationSimulationState)

    graph.add_node("world_loader", wrap_node(civ_world_loader_node, db))
    graph.add_node("agent_selector", wrap_node(civ_agent_selector_node, db))
    graph.add_node("goal_planner", wrap_node(civ_goal_planner_node, db))
    graph.add_node("decision_engine", wrap_node(civ_decision_engine_node, db))
    graph.add_node("tool_selection", wrap_node(civ_tool_selection_node, db))
    graph.add_node("tool_execution", wrap_node(civ_tool_execution_node, db))
    graph.add_node("economy_engine", wrap_node(civ_economy_engine_node, db))
    graph.add_node("asset_manager", wrap_node(civ_asset_manager_node, db))
    graph.add_node("business_engine", wrap_node(civ_business_engine_node, db))
    graph.add_node("construction_engine", wrap_node(civ_construction_engine_node, db))
    graph.add_node("organization_engine", wrap_node(civ_organization_engine_node, db))
    graph.add_node("innovation_engine", wrap_node(civ_innovation_engine_node, db))
    graph.add_node("software_company", wrap_node(civ_software_company_node, db))
    graph.add_node("ai_worker_factory", wrap_node(civ_ai_worker_factory_node, db))
    graph.add_node("story_logger", wrap_node(civ_story_logger_node, db))
    graph.add_node("civilization_evolution", wrap_node(civ_evolution_node, db))

    graph.set_entry_point("world_loader")
    graph.add_edge("world_loader", "agent_selector")
    graph.add_edge("agent_selector", "goal_planner")
    graph.add_edge("goal_planner", "decision_engine")
    graph.add_edge("decision_engine", "tool_selection")
    graph.add_edge("tool_selection", "tool_execution")
    graph.add_edge("tool_execution", "economy_engine")
    graph.add_edge("economy_engine", "asset_manager")
    graph.add_edge("asset_manager", "business_engine")
    graph.add_edge("business_engine", "construction_engine")
    graph.add_edge("construction_engine", "organization_engine")
    graph.add_edge("organization_engine", "innovation_engine")
    graph.add_edge("innovation_engine", "software_company")
    graph.add_edge("software_company", "ai_worker_factory")
    graph.add_edge("ai_worker_factory", "story_logger")
    graph.add_edge("story_logger", "civilization_evolution")
    graph.add_edge("civilization_evolution", END)

    logger.info(
        "Civilization graph: %s mode",
        "FAST" if settings.simulation_fast_mode else "FULL",
    )
    return graph.compile()


def run_civilization_tick(db: Session, *, initial_state: CivilizationSimulationState) -> CivilizationSimulationState:
    app = build_civilization_graph(db)
    return app.invoke(initial_state)

