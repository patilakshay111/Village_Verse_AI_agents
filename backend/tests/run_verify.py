"""Run verification checks. Usage: python tests/run_verify.py"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["MOCK_LLM"] = "true"

from test_api import (  # noqa: E402
    test_health,
    test_run_ticks,
    test_seed_and_lists,
    test_simulation_status,
    test_simulation_tick_and_stories,
)

if __name__ == "__main__":
    test_health()
    print("health ok")
    test_seed_and_lists()
    print("seed ok")
    test_simulation_tick_and_stories()
    print("tick and stories ok")
    test_run_ticks()
    print("run ticks ok")
    test_simulation_status()
    print("status ok")
    print("All verification checks passed.")
