from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = f"sqlite:///{PROJECT_ROOT / 'data' / 'village.db'}"
    prompts_dir: Path = PROJECT_ROOT / "configs" / "prompts"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    village_name: str = "Anandgaon"
    seed_families: int = 10
    seed_villagers: int = 40
    active_agents_per_tick: int = 5
    simulation_tick_delay_seconds: float = 3.0
    mock_llm: bool = False
    # Fast mode: 3 LLM calls/tick (~2-4 min on small models). Full mode: ~9 calls (~10-20 min).
    simulation_fast_mode: bool = True
    # Civilization engine (Phase 1 foundation — graph integration in Phase 2+)
    simulation_mode: str = "village"  # village | civilization | hybrid
    agent_workspace_dir: Path = PROJECT_ROOT / "data" / "agent_workspace"
    enable_web_tools: bool = False
    enable_file_tools: bool = False
    enable_execute_python: bool = False

    @property
    def effective_agents_per_tick(self) -> int:
        if self.simulation_fast_mode:
            return min(3, self.active_agents_per_tick)
        return self.active_agents_per_tick

    @property
    def prompts_path(self) -> Path:
        path = self.prompts_dir
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
