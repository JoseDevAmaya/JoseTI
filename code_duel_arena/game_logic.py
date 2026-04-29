import random
from dataclasses import dataclass

from ai import AIOpponent
from questions import Question


@dataclass
class PlayerState:
    hp: int = 100
    max_hp: int = 100
    xp: int = 0
    level: int = 1
    wins: int = 0
    losses: int = 0
    streak: int = 0
    reputation: int = 0


class DuelEngine:
    def __init__(self, questions: list[Question]):
        self.questions = questions
        self.player = PlayerState()
        self.ai_hp = 100
        self.ai_max_hp = 100
        self.round_time_limit = 18
        self.current_question: Question | None = None
        self.used_qids: set[str] = set()
        self.logs: list[str] = []
        self.ai = AIOpponent(difficulty=1)
        self.stage = 1

    def add_log(self, line: str):
        self.logs.append(line)
        if len(self.logs) > 260:
            self.logs = self.logs[-260:]

    def new_match(self):
        self.player.hp = self.player.max_hp
        self.ai_hp = self.ai_max_hp
        self.used_qids.clear()
        self.add_log("[INFO] New duel session started.")

    def choose_question(self) -> Question:
        candidates = [q for q in self.questions if q.qid not in self.used_qids and q.difficulty <= self.stage + 1]
        if not candidates:
            self.used_qids.clear()
            candidates = [q for q in self.questions if q.difficulty <= self.stage + 1]
        q = random.choice(candidates)
        self.used_qids.add(q.qid)
        self.current_question = q
        return q

    def evaluate_player(self, answer: str, time_left: float) -> tuple[bool, int]:
        if not self.current_question:
            return False, 0
        is_correct = answer.strip().upper() == self.current_question.answer.upper()
        damage = 0
        if is_correct:
            speed_bonus = int(max(0, time_left) * 1.2)
            damage = 10 + (self.current_question.difficulty * 4) + speed_bonus
            self.ai_hp = max(0, self.ai_hp - damage)
            self.player.streak += 1
            self.add_log(f"[INFO] Correct! You hit AI for {damage} damage.")
        else:
            self.player.streak = 0
            self.add_log("[ERR] Wrong answer.")
        return is_correct, damage

    def run_ai_turn(self, question: Question) -> tuple[bool, int, float]:
        ai_correct, ai_time = self.ai.decide(question.difficulty)
        if ai_correct:
            damage = 8 + (question.difficulty * 3) + int(self.stage * 1.5)
            self.player.hp = max(0, self.player.hp - damage)
            self.add_log(f"[WARN] AI answered correctly in {ai_time:.1f}s and dealt {damage}.")
            return True, damage, ai_time
        self.add_log(f"[INFO] AI failed its answer in {ai_time:.1f}s.")
        return False, 0, ai_time

    def apply_timeout_penalty(self):
        dmg = 10 + self.stage * 2
        self.player.hp = max(0, self.player.hp - dmg)
        self.player.streak = 0
        self.add_log(f"[WARN] Timeout! You received {dmg} damage.")

    def grant_progress(self, won: bool):
        if won:
            self.player.wins += 1
            xp_gain = 45 + self.stage * 12 + self.player.streak * 3
            rep_gain = 18 + self.stage * 5
            self.player.xp += xp_gain
            self.player.reputation += rep_gain
            self.add_log(f"[INFO] Victory rewards: +{xp_gain} XP, +{rep_gain} REP.")
            self.stage += 1
            self.ai.set_difficulty(min(5, self.stage))
            self.ai_max_hp = min(180, 100 + self.stage * 10)
        else:
            self.player.losses += 1
            self.player.reputation = max(0, self.player.reputation - 8)
            self.add_log("[ERR] Defeat. Reputation reduced by 8.")

        self._level_up()

    def _level_up(self):
        needed = self.player.level * 120
        while self.player.xp >= needed:
            self.player.xp -= needed
            self.player.level += 1
            self.player.max_hp = min(220, self.player.max_hp + 8)
            self.player.hp = self.player.max_hp
            self.add_log(f"[INFO] LEVEL UP! You are now level {self.player.level}.")
            needed = self.player.level * 120

    def is_player_dead(self) -> bool:
        return self.player.hp <= 0

    def is_ai_dead(self) -> bool:
        return self.ai_hp <= 0
