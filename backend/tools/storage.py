import json
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
RUNS_PATH = BASE_DIR / "data" / "campaign_runs.json"


def load_campaign_runs() -> list[dict[str, Any]]:
    """
    Loads previous campaign runs from a JSON file.
    """

    if not RUNS_PATH.exists():
        return []

    with open(RUNS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_campaign_run(brief_data: dict, campaign_plan: dict) -> dict:
    """
    Saves one campaign run with timestamp, input brief, and generated outputs.
    """

    runs = load_campaign_runs()

    run_record = {
        "run_id": f"run_{len(runs) + 1}",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "brief": brief_data,
        "campaign_plan": campaign_plan,
    }

    runs.append(run_record)

    with open(RUNS_PATH, "w", encoding="utf-8") as file:
        json.dump(runs, file, indent=4, ensure_ascii=False)

    return run_record