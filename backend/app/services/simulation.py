import logging
import threading
import time
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.graph.workflow import run_simulation_tick
from app.graph.workflow_civilization import run_civilization_tick
from app.graph.nodes.save_state import save_state_node
from app.graph.nodes.world_state import world_state_node
from app.models.business import Business
from app.models.conversation import Conversation
from app.models.event import Event
from app.models.organization import Organization
from app.models.simulation_run import SimulationRun
from app.models.story import Story
from app.models.villager import Villager
from app.world.loader import WorldStateLoader
from app.world.persister import WorldStatePersister

logger = logging.getLogger(__name__)

_continuous_thread: threading.Thread | None = None
_stop_continuous = threading.Event()
_tick_lock = threading.Lock()


def _get_sim(db: Session) -> SimulationRun:
    sim = db.query(SimulationRun).order_by(SimulationRun.id.desc()).first()
    if not sim:
        sim = SimulationRun()
        db.add(sim)
        db.commit()
        db.refresh(sim)
    return sim


def _continuous_running() -> bool:
    return _continuous_thread is not None and _continuous_thread.is_alive()


def _is_pausing() -> bool:
    return _stop_continuous.is_set() and _continuous_running()


def _write_status(
    session_factory,
    status: str,
    *,
    last_error: str | None = None,
    max_attempts: int = 8,
) -> bool:
    """Persist simulation status with retries (SQLite may be busy mid-tick)."""
    for attempt in range(max_attempts):
        db = session_factory()
        try:
            with _tick_lock:
                sim = _get_sim(db)
                sim.status = status
                if last_error is not None:
                    sim.last_error = last_error[:500]
                db.commit()
            return True
        except OperationalError as exc:
            db.rollback()
            if "locked" not in str(exc).lower() or attempt == max_attempts - 1:
                logger.warning("Could not write simulation status=%s: %s", status, exc)
                return False
            time.sleep(min(0.5 * (2**attempt), 5.0))
        except Exception as exc:
            db.rollback()
            logger.warning("Could not write simulation status=%s: %s", status, exc)
            return False
        finally:
            db.close()
    return False


def run_tick(db: Session, *, manage_status: bool = True) -> dict:
    sim = _get_sim(db)
    if manage_status:
        if _continuous_running():
            raise HTTPException(
                status_code=409,
                detail="Pause continuous simulation before running a manual tick.",
            )
        if sim.status == "running":
            raise HTTPException(status_code=409, detail="Simulation is already running")

    previous_status = sim.status
    if manage_status:
        with _tick_lock:
            sim.status = "running"
            db.commit()

    try:
        # Lock not held during tick — graph steps commit individually so pause/status can interleave.
        settings = get_settings()
        mode = settings.simulation_mode.lower()
        if mode == "hybrid":
            sim_pre = _get_sim(db)
            use_civ = (sim_pre.tick_count or 0) % 2 == 1
            result = _run_civilization_tick_service(db) if use_civ else run_simulation_tick(db)
        elif mode == "civilization":
            result = _run_civilization_tick_service(db)
        else:
            result = run_simulation_tick(db)
        with _tick_lock:
            sim = _get_sim(db)
            if manage_status and not _continuous_running():
                sim.status = "idle"
                if result.get("error"):
                    sim.last_error = str(result["error"])[:500]
                else:
                    sim.last_error = None
            db.commit()
        return {
            "tick_id": result.get("tick_id"),
            "events": len(result.get("events", [])),
            "stories": len(result.get("feed_entries", [])),
            "error": result.get("error"),
        }
    except Exception as exc:
        logger.exception("Tick failed")
        db.rollback()
        with _tick_lock:
            sim = _get_sim(db)
            if not _continuous_running():
                sim.status = "paused" if previous_status == "paused" else "idle"
            sim.last_error = str(exc)[:500]
            try:
                db.commit()
            except OperationalError:
                db.rollback()
        if "connection" in str(exc).lower() or "ollama" in str(exc).lower():
            raise HTTPException(status_code=503, detail=f"Ollama unavailable: {exc}") from exc
        if "locked" in str(exc).lower():
            raise HTTPException(
                status_code=503,
                detail="Database busy — wait for the current tick to finish, then retry.",
            ) from exc
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _run_civilization_tick_service(db: Session) -> dict:
    """Run one civilization tick and persist metrics + side-effect stories/events."""
    tick_meta = world_state_node({}, db)
    tick_id = tick_meta.get("tick_id")
    if not tick_id:
        raise RuntimeError("Missing tick_id for civilization tick")

    initial_state = {
        "tick_id": tick_id,
        "current_day": tick_meta.get("current_day", 1),
        "current_time": tick_meta.get("current_time", "Morning"),
        "weather": tick_meta.get("weather", "Clear"),
        "world_state": tick_meta.get("world_state", {}),
    }

    civ_state = run_civilization_tick(db, initial_state=initial_state)

    # Persist civilization metrics after tool execution.
    ws = WorldStateLoader(db).load(tick_id=tick_id, selected_agent_ids=[])
    tool_results = civ_state.get("tool_results", []) if isinstance(civ_state, dict) else []
    successful_actions = sum(1 for r in tool_results if isinstance(r, dict) and r.get("success"))
    active_biz = ws.economy.active_businesses
    active_orgs = ws.economy.active_organizations
    ws.civilization_stage = "Town" if active_biz >= 5 or active_orgs >= 3 else "Village"
    ws.technology_level = min(1.0, float(ws.technology_level or 0.1) + active_orgs * 0.05)
    activity_bonus = (successful_actions * 250.0) + (active_biz * 100.0) + (active_orgs * 150.0)
    ws.economy.total_wealth = float(ws.economy.total_wealth) + activity_bonus
    ws.economy.gdp = float(ws.economy.total_wealth) * 0.1
    WorldStatePersister(db).save_metrics(ws)

    # Update time/tick counters in simulation_runs
    save_state_node(tick_meta, db)

    return {
        "tick_id": tick_id,
        "events": [],
        "feed_entries": civ_state.get("feed_entries", []) if isinstance(civ_state, dict) else [],
        "tool_results": tool_results,
        "error": civ_state.get("error") if isinstance(civ_state, dict) else None,
    }


def run_ticks(db: Session, n: int) -> dict:
    if _continuous_running():
        raise HTTPException(
            status_code=409,
            detail="Pause continuous simulation before running a tick batch.",
        )
    results = []
    for _ in range(n):
        sim = _get_sim(db)
        if sim.status == "paused":
            break
        results.append(run_tick(db))
    return {"ticks_completed": len(results), "results": results}


def pause_simulation(db: Session) -> dict:
    global _stop_continuous
    _stop_continuous.set()

    if _continuous_running():
        # Do not fight the background tick for a row update — stop signal is enough.
        return {
            "status": "pausing",
            "message": "Stopping after the current step finishes.",
        }

    from app.database.base import SessionLocal

    if not _write_status(SessionLocal, "paused"):
        try:
            sim = _get_sim(db)
            sim.status = "paused"
            db.commit()
        except OperationalError as exc:
            db.rollback()
            if "locked" in str(exc).lower():
                raise HTTPException(
                    status_code=503,
                    detail="Database busy — retry pause in a few seconds.",
                ) from exc
            raise
    return {"status": "paused"}


def get_status(db: Session) -> dict:
    sim = _get_sim(db)
    population = db.query(Villager).count()
    latest_events = db.query(Event).order_by(Event.id.desc()).limit(5).all()
    latest_stories = db.query(Story).order_by(Story.id.desc()).limit(5).all()
    active_conversations = (
        db.query(Conversation)
        .filter(Conversation.tick_id == sim.tick_count)
        .count()
    )

    settings = get_settings()
    status = sim.status
    if _is_pausing():
        status = "pausing"
    elif _continuous_running() and status != "paused":
        status = "running"

    active_businesses = db.query(Business).filter(Business.status == "active").count()
    active_organizations = db.query(Organization).filter(Organization.status == "active").count()
    unemployed = db.query(Villager).filter(Villager.employment_status == "unemployed").count()
    unemployment = sim.unemployment_rate or (unemployed / population if population else 0)

    return {
        "current_day": sim.current_day,
        "current_time": sim.current_time,
        "tick_count": sim.tick_count,
        "status": status,
        "weather": sim.weather,
        "population": population,
        "fast_mode": settings.simulation_fast_mode,
        "agents_per_tick": settings.effective_agents_per_tick,
        "simulation_mode": settings.simulation_mode,
        "active_conversations": active_conversations,
        "civilization_stage": sim.civilization_stage or "Village",
        "technology_level": sim.technology_level or 0.1,
        "gdp": sim.gdp or 0.0,
        "total_wealth": sim.total_wealth or 0.0,
        "unemployment_rate": unemployment,
        "active_businesses": active_businesses,
        "active_organizations": active_organizations,
        "latest_events": [
            {"title": e.title, "category": e.category, "importance": e.importance}
            for e in latest_events
        ],
        "latest_stories": [
            {"title": s.title, "importance": s.importance, "category": s.category}
            for s in latest_stories
        ],
        "last_error": sim.last_error,
    }


def _continuous_loop(session_factory, delay: float) -> None:
    """Background thread: run ticks until pause or error."""
    from app.database.base import SessionLocal

    logger.info("Continuous simulation started (delay=%ss)", delay)
    while not _stop_continuous.is_set():
        db = session_factory()
        try:
            sim = _get_sim(db)
            if sim.status == "paused":
                break
            if _stop_continuous.is_set():
                break
            run_tick(db, manage_status=False)
        except HTTPException as exc:
            logger.error("Continuous tick HTTP error: %s", exc.detail)
            _set_sim_error(session_factory, str(exc.detail))
            break
        except Exception as exc:
            logger.exception("Continuous tick error")
            _set_sim_error(session_factory, str(exc))
            break
        finally:
            db.close()

        if _stop_continuous.wait(timeout=delay):
            break

    final_status = "paused" if _stop_continuous.is_set() else "idle"
    _write_status(session_factory, final_status)
    logger.info("Continuous simulation stopped (%s)", final_status)


def _set_sim_error(session_factory, message: str) -> None:
    _write_status(session_factory, "idle", last_error=message)


def start_continuous(db: Session) -> dict:
    global _continuous_thread, _stop_continuous

    if _continuous_running():
        raise HTTPException(status_code=409, detail="Continuous simulation already running")

    settings = get_settings()
    sim = _get_sim(db)
    sim.status = "running"
    sim.last_error = None
    sim.last_tick_at = datetime.utcnow()
    db.commit()

    from app.database.base import SessionLocal

    _stop_continuous.clear()
    _continuous_thread = threading.Thread(
        target=_continuous_loop,
        args=(SessionLocal, settings.simulation_tick_delay_seconds),
        daemon=True,
        name="villageverse-continuous",
    )
    _continuous_thread.start()

    return {
        "status": "running",
        "delay_seconds": settings.simulation_tick_delay_seconds,
        "message": "Continuous simulation started. Click Pause to stop.",
    }
