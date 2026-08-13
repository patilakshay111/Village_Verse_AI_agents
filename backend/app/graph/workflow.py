import logging

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.config import get_settings
from app.graph.nodes import (
    agent_selector_node,
    conversation_node,
    emotion_node,
    event_generator_node,
    gossip_node,
    memory_node,
    relationship_node,
    save_state_node,
    story_logger_node,
    world_state_node,
)
from app.graph.nodes.fast_steps import (
    emotion_fast_node,
    gossip_skip_node,
    memory_fast_node,
    relationship_fast_node,
)
from app.graph.state import SimulationState
from app.graph.utils import wrap_node

logger = logging.getLogger(__name__)


def build_simulation_graph(db: Session):
    settings = get_settings()
    graph = StateGraph(SimulationState)

    graph.add_node("world_state", wrap_node(world_state_node, db))
    graph.add_node("event_generator", wrap_node(event_generator_node, db))
    graph.add_node("agent_selector", wrap_node(agent_selector_node, db))
    graph.add_node("conversation", wrap_node(conversation_node, db))
    graph.add_node("story_logger", wrap_node(story_logger_node, db))
    graph.add_node("save_state", wrap_node(save_state_node, db))

    graph.set_entry_point("world_state")
    graph.add_edge("world_state", "event_generator")
    graph.add_edge("event_generator", "agent_selector")
    graph.add_edge("agent_selector", "conversation")

    if settings.simulation_fast_mode:
        logger.info("Simulation graph: FAST mode (3 LLM calls per tick)")
        graph.add_node("memory", wrap_node(memory_fast_node, db))
        graph.add_node("relationship", wrap_node(relationship_fast_node, db))
        graph.add_node("emotion", wrap_node(emotion_fast_node, db))
        graph.add_node("gossip", wrap_node(gossip_skip_node, db))
        graph.add_edge("conversation", "memory")
        graph.add_edge("memory", "relationship")
        graph.add_edge("relationship", "emotion")
        graph.add_edge("emotion", "gossip")
        graph.add_edge("gossip", "story_logger")
    else:
        logger.info("Simulation graph: FULL mode (~8 LLM calls per tick)")
        graph.add_node("memory", wrap_node(memory_node, db))
        graph.add_node("relationship", wrap_node(relationship_node, db))
        graph.add_node("emotion", wrap_node(emotion_node, db))
        graph.add_node("gossip", wrap_node(gossip_node, db))
        graph.add_edge("conversation", "memory")
        graph.add_edge("memory", "relationship")
        graph.add_edge("relationship", "emotion")
        graph.add_edge("emotion", "gossip")
        graph.add_edge("gossip", "story_logger")

    graph.add_edge("story_logger", "save_state")
    graph.add_edge("save_state", END)

    return graph.compile()


def run_simulation_tick(db: Session) -> SimulationState:
    settings = get_settings()
    logger.info(
        "Tick start (fast_mode=%s, agents=%s, model=%s)",
        settings.simulation_fast_mode,
        settings.effective_agents_per_tick,
        settings.ollama_model,
    )
    app = build_simulation_graph(db)
    result = app.invoke({})
    return result
