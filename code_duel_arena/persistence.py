import json
import os

from game_logic import DuelEngine
from settings import SAVE_FILE


def save_game(engine: DuelEngine):
    payload = {
        "stage": engine.stage,
        "ai_max_hp": engine.ai_max_hp,
        "player": {
            "hp": engine.player.hp,
            "max_hp": engine.player.max_hp,
            "xp": engine.player.xp,
            "level": engine.player.level,
            "wins": engine.player.wins,
            "losses": engine.player.losses,
            "streak": engine.player.streak,
            "reputation": engine.player.reputation,
        },
        "logs": engine.logs[-120:],
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def has_save() -> bool:
    return os.path.exists(SAVE_FILE)


def load_game(engine: DuelEngine) -> bool:
    if not has_save():
        return False
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        p = data["player"]
        engine.stage = max(1, int(data.get("stage", 1)))
        engine.ai_max_hp = max(100, int(data.get("ai_max_hp", 100)))
        engine.player.hp = int(p.get("hp", 100))
        engine.player.max_hp = int(p.get("max_hp", 100))
        engine.player.xp = int(p.get("xp", 0))
        engine.player.level = int(p.get("level", 1))
        engine.player.wins = int(p.get("wins", 0))
        engine.player.losses = int(p.get("losses", 0))
        engine.player.streak = int(p.get("streak", 0))
        engine.player.reputation = int(p.get("reputation", 0))
        engine.logs = list(data.get("logs", []))
        engine.ai.set_difficulty(min(5, engine.stage))
        return True
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False
