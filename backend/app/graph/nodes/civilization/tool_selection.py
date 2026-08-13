import re

from sqlalchemy.orm import Session

from app.graph.civilization_prompt import fallback_decision
from app.graph.civilization_state import CivilizationSimulationState
from app.config import get_settings
from app.tools.registry import get_tool_registry


def civ_tool_selection_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    """Convert decisions into tool calls.

    Phase 3: fill required arguments heuristically so tool handlers can execute.
    """

    settings = get_settings()
    registry = get_tool_registry()
    tick_id = state.get("tick_id")
    world_state = state.get("world_state", {}) or {}
    market_prices: list[dict] = world_state.get("market_prices", []) or []

    def _min_price() -> float:
        ps = [float(p.get("price", 0) or 0) for p in market_prices if p.get("price") is not None]
        ps = [p for p in ps if p > 0]
        return min(ps) if ps else 100.0

    def _asset_type_for(agent: dict) -> str:
        role = agent.get("agent_role") or "villager"
        occ = agent.get("occupation") or ""
        if role == "farmer":
            return "tractor"
        if role == "shopkeeper":
            return "shop_inventory"
        if role == "teacher":
            return "school"
        if role in ("contractor", "sarpanch", "gram_sevak"):
            return "construction_machinery"
        if role in ("business_owner", "milkman", "mechanic", "driver"):
            return "transport_truck"
        if "Software" in occ or role in ("software_founder", "developer", "researcher"):
            return "software_license"
        return "land"

    def _business_type_for(agent: dict) -> str:
        role = agent.get("agent_role") or "villager"
        occ = agent.get("occupation") or ""
        if role == "farmer":
            return "Dairy"
        if role == "shopkeeper":
            return "Grocery"
        if role == "teacher":
            return "Education Company"
        if role in ("contractor", "sarpanch", "gram_sevak"):
            return "Construction"
        if role == "driver":
            return "Logistics"
        return "Tea Stall"

    def _choose_project_for(agent: dict, status: str) -> dict | None:
        projects: list[dict] = world_state.get("active_projects", []) or []
        for p in projects:
            if p.get("owner_id") == agent.get("agent_id") and p.get("status") == status:
                return p
        return None

    def _agent_by_id(agent_id: str) -> dict | None:
        for a in state.get("selected_agents", []) or []:
            if a.get("agent_id") == agent_id:
                return a
        return None

    def _normalize_tool_name(tool: str | None) -> str:
        if not tool:
            return ""
        cleaned = re.sub(r"[^a-z0-9]+", "_", str(tool).strip().lower()).strip("_")
        aliases = {
            "buyasset": "buy_asset",
            "sellasset": "sell_asset",
            "takealoan": "take_loan",
            "repayloan": "repay_loan",
            "createbusiness": "create_business",
            "startconstruction": "start_construction",
            "completeconstruction": "complete_construction",
            "hireworker": "hire_worker",
            "fireworker": "fire_worker",
        }
        return aliases.get(cleaned, cleaned)

    def _fallback_tool(agent: dict, available_tools: list[dict], *, exclude: set[str] | None = None) -> str | None:
        exclude = exclude or set()
        available_names = [t.get("name") for t in available_tools if t.get("name")]
        filtered = [name for name in available_names if name not in exclude]
        if not filtered:
            return None
        preferred = _normalize_tool_name(fallback_decision(agent, available_tools).get("selected_tool"))
        if preferred in filtered and preferred not in exclude:
            return preferred
        return filtered[0]

    calls: list[dict] = []
    for d in state.get("decisions", []) or []:
        if not isinstance(d, dict):
            continue
        tool = _normalize_tool_name(d.get("selected_tool"))
        agent_id = d.get("agent_id")
        if not tool or not agent_id:
            continue

        agent = _agent_by_id(agent_id) or {}
        available_tools = registry.list_tools_for_role(agent.get("agent_role", "villager"))
        available_tool_names = {t.get("name") for t in available_tools if t.get("name")}
        if tool not in available_tool_names:
            tool = _fallback_tool(agent, available_tools)
            if not tool:
                continue
        cash = float(agent.get("cash") or 0)
        base = _min_price()

        args: dict = {}
        reason = d.get("reason") or "LLM decision"

        # --- Argument heuristics per tool ---
        if tool == "buy_asset":
            asset_type = _asset_type_for(agent)
            price = max(5000.0, base * (10.0 if asset_type == "tractor" else 2.0))
            price = min(price, max(100.0, cash * 0.6))
            args = {
                "asset_type": asset_type,
                "name": f"{asset_type.title()} for {agent.get('name', 'Villager')}",
                "price": float(price),
                "monthly_revenue": 0.0,
                "monthly_cost": 0.0,
                "location_id": agent.get("location_id"),
            }
            # If even the reduced price is not affordable, skip.
            if float(price) <= 0 or cash < float(price):
                continue

        elif tool == "sell_asset":
            owned_assets: list[dict] = agent.get("assets", []) or []
            asset = next((a for a in owned_assets if a.get("status") == "active"), None) or (owned_assets[0] if owned_assets else None)
            if not asset:
                tool = "buy_asset"
                asset_type = _asset_type_for(agent)
                price = max(5000.0, base * (10.0 if asset_type == "tractor" else 2.0))
                price = min(price, max(100.0, cash * 0.6))
                args = {
                    "asset_type": asset_type,
                    "name": f"{asset_type.title()} for {agent.get('name', 'Villager')}",
                    "price": float(price),
                    "monthly_revenue": 0.0,
                    "monthly_cost": 0.0,
                    "location_id": agent.get("location_id"),
                }
                if float(price) <= 0 or cash < float(price):
                    continue
            else:
                args = {
                    "asset_id": asset.get("id"),
                    "sale_price": float(asset.get("value") or 0),
                }

        elif tool == "take_loan":
            amount = max(5000.0, base * 20.0)
            amount = min(amount, max(10000.0, cash * 2.0))
            args = {"amount": float(amount)}

        elif tool == "repay_loan":
            liabilities: list[dict] = agent.get("liabilities", []) or []
            liab = next((l for l in liabilities if l.get("status") == "active"), None) or (liabilities[0] if liabilities else None)
            if not liab:
                continue
            amount = min(float(liab.get("balance") or 0), cash * 0.5)
            args = {"liability_id": liab.get("id"), "amount": float(max(0.0, amount))}

        elif tool == "create_business":
            business_type = _business_type_for(agent)
            # Keep it affordable: create_business checks villager.cash >= startup_cost
            startup_cost = min(max(5000.0, base * 25.0), cash * 0.5) if cash > 0 else base * 25.0
            business_name = f"{business_type} of {agent.get('name', 'Villager')}"
            args = {
                "name": business_name,
                "business_type": business_type,
                "startup_cost": float(max(0.0, startup_cost)),
                "tick_id": tick_id,
            }
            if cash < float(args["startup_cost"]):
                continue

        elif tool == "start_construction":
            project_type = "Road/Gutter (PMGSY-style)"
            # Tool requires cash >= cost*0.1
            total_cost = min(max(50000.0, base * 800.0), cash * 6.0)
            if cash <= 0:
                continue
            loc_id = agent.get("location_id") or "construction_site"
            args = {
                "project_type": project_type,
                "total_cost": float(max(0.0, total_cost)),
                "duration_days": 30,
                "location_id": loc_id,
            }
            if cash < total_cost * 0.1:
                continue

        elif tool == "complete_construction":
            p = _choose_project_for(agent, "in_progress")
            if not p:
                continue
            args = {"project_id": p.get("id")}

        elif tool in ("hire_worker", "fire_worker"):
            orgs: list[dict] = agent.get("organizations", []) or []
            org = orgs[0] if orgs else None
            if tool == "hire_worker":
                if not org:
                    continue
                args = {
                    "organization_id": org.get("id"),
                    "worker_type": "Research Agent",
                    "name": f"AI worker for {agent.get('name', 'Org')}",
                    "monthly_cost": 20000.0,
                }
            else:
                # fire_worker
                continue

        else:
            # Unknown or unhandled tool => skip in Phase 3.
            continue

        calls.append(
            {
                "tool_name": tool,
                "agent_id": agent_id,
                "arguments": args,
                "reason": reason,
                "tick_id": tick_id,
            }
        )

    return {"tool_calls": calls}

