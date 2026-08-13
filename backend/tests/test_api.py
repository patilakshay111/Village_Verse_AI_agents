"""API verification tests. Set MOCK_LLM=true for fast runs without Ollama."""

import os
import sys
from pathlib import Path

os.environ["MOCK_LLM"] = "true"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings

get_settings.cache_clear()

from fastapi.testclient import TestClient

from main import app


def _client() -> TestClient:
    get_settings.cache_clear()
    return TestClient(app)


def test_health():
    client = _client()
    assert client.get("/health").json()["status"] == "ok"


def test_seed_and_lists():
    client = _client()
    seeded = client.post("/admin/seed").json()
    assert seeded["villagers"] == 40
    assert len(client.get("/villagers").json()) == seeded["villagers"]
    assert len(client.get("/families").json()) == 10
    assert len(client.get("/locations").json()) == 15


def test_simulation_tick_and_stories():
    client = _client()
    client.post("/admin/seed")
    tick = client.post("/simulation/tick")
    assert tick.status_code == 200
    for _ in range(2):
        client.post("/simulation/tick")
    stories = client.get("/stories").json()
    assert stories["total"] >= 1
    filtered = client.get("/stories", params={"importance_min": 0.5}).json()
    assert filtered["total"] >= 1


def test_run_ticks():
    client = _client()
    client.post("/admin/seed")
    run = client.post("/simulation/run", json={"ticks": 3})
    assert run.status_code == 200
    assert run.json()["ticks_completed"] == 3


def test_simulation_status():
    client = _client()
    client.post("/admin/seed")
    client.post("/simulation/tick")
    status = client.get("/simulation/status").json()
    assert status["population"] == 40
    assert status["tick_count"] >= 1
