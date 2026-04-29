import json
import os
import sys
from dataclasses import dataclass

from settings import QUESTIONS_FILE


@dataclass
class Question:
    qid: str
    qtype: str
    prompt: str
    options: list[str]
    answer: str
    explanation: str
    difficulty: int
    category: str


def load_questions() -> list[Question]:
    path = _resource_path(QUESTIONS_FILE)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Questions file not found: {QUESTIONS_FILE}")
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    out: list[Question] = []
    for idx, item in enumerate(payload):
        try:
            out.append(
                Question(
                    qid=str(item["id"]),
                    qtype=str(item["type"]),
                    prompt=str(item["prompt"]),
                    options=list(item["options"]),
                    answer=str(item["answer"]),
                    explanation=str(item["explanation"]),
                    difficulty=int(item["difficulty"]),
                    category=str(item["category"]),
                )
            )
        except KeyError as err:
            raise ValueError(f"Malformed question at index {idx}: missing {err}") from err
    return out


def _resource_path(relative_path: str) -> str:
    """
    Resolve resources in both development mode and PyInstaller onefile mode.
    """
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)
