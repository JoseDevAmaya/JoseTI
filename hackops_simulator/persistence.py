import json
import os

from models import PlayerProgress
from settings import SAVE_FILE


def save_progress(progress: PlayerProgress) -> None:
    payload = {
        "mission_index": progress.mission_index,
        "reputation": progress.reputation,
        "level": progress.level,
        "exp": progress.exp,
        "max_alerts": progress.max_alerts,
        "alerts": progress.alerts,
        "command_count": progress.command_count,
        "logs": progress.logs[-80:],
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_progress() -> PlayerProgress | None:
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return PlayerProgress(
            mission_index=int(data.get("mission_index", 0)),
            reputation=int(data.get("reputation", 0)),
            level=max(1, int(data.get("level", 1))),
            exp=max(0, int(data.get("exp", 0))),
            max_alerts=max(1, int(data.get("max_alerts", 4))),
            alerts=max(0, int(data.get("alerts", 0))),
            command_count=max(0, int(data.get("command_count", 0))),
            logs=list(data.get("logs", [])),
        )
    except (ValueError, OSError, json.JSONDecodeError):
        return None

