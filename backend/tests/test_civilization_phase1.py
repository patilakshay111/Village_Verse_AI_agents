import os
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.roles import AgentRole, permissions_for_role
from app.database.base import Base
from app.models.family import Family
from app.models.villager import Villager
from app.services.civilization_seed import backfill_villager_finances, seed_markets
from app.graph.nodes.civilization.tool_selection import civ_tool_selection_node
from app.graph.nodes.conversation import conversation_node
from app.graph.nodes.event_generator import event_generator_node
from app.tools.executor import ToolExecutor
from app.tools.registry import get_tool_registry
from app.tools.schemas import ToolCallRequest
from app.world.loader import WorldStateLoader


@pytest.fixture
def db_session():
    td = tempfile.mkdtemp()
    db_path = Path(td) / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["AGENT_WORKSPACE_DIR"] = str(Path(td) / "workspace")
    from app.config import get_settings

    get_settings.cache_clear()

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        get_settings.cache_clear()


def _add_farmer(db, agent_id="farmer_1"):
    if not db.query(Family).filter(Family.id == "patil").first():
        db.add(Family(id="patil", name="Patil Family", surname="Patil"))
        db.flush()
    v = Villager(
        id=agent_id,
        name="Test Farmer",
        age=40,
        gender="Male",
        occupation="Farmer",
        family_id="patil",
        financial_status="Middle",
        cash=50000,
        agent_role=AgentRole.FARMER.value,
    )
    db.add(v)
    db.commit()
    return v


def test_farmer_cannot_use_read_file(db_session):
    _add_farmer(db_session)
    registry = get_tool_registry()
    allowed, reason = registry.can_use(AgentRole.FARMER, "read_file")
    assert not allowed
    assert reason is not None


def test_software_founder_can_use_file_tools_when_enabled(db_session, monkeypatch):
    monkeypatch.setenv("ENABLE_FILE_TOOLS", "true")
    from app.config import get_settings

    get_settings.cache_clear()
    perms = permissions_for_role(AgentRole.SOFTWARE_FOUNDER)
    assert "read_file" in perms
    registry = get_tool_registry()
    allowed, _ = registry.can_use(AgentRole.SOFTWARE_FOUNDER, "read_file")
    assert allowed


def test_buy_asset_tool(db_session):
    v = _add_farmer(db_session)
    executor = ToolExecutor(db_session)
    result = executor.execute(
        ToolCallRequest(
            tool_name="buy_asset",
            agent_id=v.id,
            arguments={"asset_type": "tractor", "name": "Mahindra Tractor", "price": 10000},
            tick_id=1,
        )
    )
    assert result.success
    db_session.refresh(v)
    assert v.cash == 40000


def test_farmer_blocked_from_write_file(db_session):
    v = _add_farmer(db_session)
    executor = ToolExecutor(db_session)
    result = executor.execute(
        ToolCallRequest(
            tool_name="write_file",
            agent_id=v.id,
            arguments={"path": "main.py", "content": "print('hi')"},
        )
    )
    assert not result.success
    assert "permission" in (result.error or "").lower() or "disabled" in (result.error or "").lower()


def test_world_state_loader(db_session):
    _add_farmer(db_session)
    seed_markets(db_session)
    backfill_villager_finances(db_session)
    state = WorldStateLoader(db_session).load(selected_agent_ids=["farmer_1"])
    assert state.population == 1
    assert state.economy.total_wealth >= 0
    assert len(state.market_prices) >= 1
    assert state.selected_agents[0].agent_role == AgentRole.FARMER.value


def test_civilization_tool_selection_recovers_from_malformed_tool_name(db_session):
    villager = _add_farmer(db_session)
    state = {
        "tick_id": 1,
        "world_state": {"market_prices": []},
        "selected_agents": [
            {
                "agent_id": villager.id,
                "name": villager.name,
                "occupation": villager.occupation,
                "agent_role": villager.agent_role,
                "cash": villager.cash,
                "bank_balance": villager.bank_balance,
                "monthly_income": villager.monthly_income,
                "monthly_expenses": villager.monthly_expenses,
                "net_worth": villager.net_worth,
                "reputation": villager.reputation,
                "skills": [],
                "goals": {},
                "active_goal_plan": {},
                "assets": [],
                "liabilities": [],
                "businesses": [],
                "organizations": [],
                "permissions": [],
            }
        ],
        "decisions": [
            {
                "agent_id": villager.id,
                "selected_tool": "Buy Asset",
                "reason": "malformed model output",
            }
        ],
    }

    result = civ_tool_selection_node(state, db_session)
    assert result["tool_calls"]
    assert result["tool_calls"][0]["tool_name"] == "buy_asset"


def test_conversation_node_falls_back_when_llm_json_breaks(db_session, monkeypatch):
    villager = _add_farmer(db_session)
    other = _add_farmer(db_session, agent_id="farmer_2")
    monkeypatch.setattr("app.graph.nodes.conversation.invoke_json", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    result = conversation_node(
        {
            "tick_id": 2,
            "location": {"id": "loc_1", "name": "Village Center"},
            "events": [{"event_id": "evt_1", "title": "Road dispute"}],
            "selected_agents": [
                {
                    "agent_id": villager.id,
                    "name": villager.name,
                    "occupation": villager.occupation,
                    "agent_role": villager.agent_role,
                    "cash": villager.cash,
                    "bank_balance": villager.bank_balance,
                    "monthly_income": villager.monthly_income,
                    "monthly_expenses": villager.monthly_expenses,
                    "net_worth": villager.net_worth,
                    "reputation": villager.reputation,
                    "skills": [],
                    "goals": {},
                    "active_goal_plan": {},
                    "assets": [],
                    "liabilities": [],
                    "businesses": [],
                    "organizations": [],
                    "permissions": [],
                },
                {
                    "agent_id": other.id,
                    "name": other.name,
                    "occupation": other.occupation,
                    "agent_role": other.agent_role,
                    "cash": other.cash,
                    "bank_balance": other.bank_balance,
                    "monthly_income": other.monthly_income,
                    "monthly_expenses": other.monthly_expenses,
                    "net_worth": other.net_worth,
                    "reputation": other.reputation,
                    "skills": [],
                    "goals": {},
                    "active_goal_plan": {},
                    "assets": [],
                    "liabilities": [],
                    "businesses": [],
                    "organizations": [],
                    "permissions": [],
                },
            ],
        },
        db_session,
    )

    assert result["conversation"]
    assert result["important_moments"]


def test_event_generator_falls_back_when_llm_json_breaks(db_session, monkeypatch):
    monkeypatch.setattr("app.graph.nodes.event_generator.invoke_json", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    result = event_generator_node(
        {
            "tick_id": 3,
            "world_state": {
                "current_day": 4,
                "current_time": "Morning",
                "weather": "Clear",
                "village_name": "Anandgaon",
            },
        },
        db_session,
    )

    assert result["events"]
    assert result["events"][0]["category"] == "Economic"
