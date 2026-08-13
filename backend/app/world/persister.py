"""Persist civilization metrics back to simulation_runs."""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models.simulation_run import SimulationRun
from app.world.state import WorldState


class WorldStatePersister:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _sim(self) -> SimulationRun:
        sim = self.db.query(SimulationRun).order_by(SimulationRun.id.desc()).first()
        if not sim:
            sim = SimulationRun()
            self.db.add(sim)
            self.db.flush()
        return sim

    def save_metrics(self, state: WorldState) -> None:
        sim = self._sim()
        sim.civilization_stage = state.civilization_stage
        sim.technology_level = state.technology_level
        sim.gdp = state.economy.gdp
        sim.total_wealth = state.economy.total_wealth
        sim.unemployment_rate = state.economy.unemployment_rate
        sim.economy_snapshot = json.dumps(
            {
                "inflation_rate": state.economy.inflation_rate,
                "active_businesses": state.economy.active_businesses,
                "active_organizations": state.economy.active_organizations,
            }
        )
        self.db.flush()
