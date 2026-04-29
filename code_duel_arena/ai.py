import random


class AIOpponent:
    def __init__(self, difficulty: int = 1):
        self.difficulty = max(1, min(5, difficulty))

    def set_difficulty(self, difficulty: int):
        self.difficulty = max(1, min(5, difficulty))

    def decide(self, question_difficulty: int) -> tuple[bool, float]:
        """
        Returns:
            ai_correct (bool),
            response_time_seconds (float)
        """
        base = 0.45 + (self.difficulty * 0.08) - (question_difficulty * 0.04)
        chance = max(0.2, min(0.92, base))
        ai_correct = random.random() < chance
        response_time = random.uniform(max(1.2, 5.0 - self.difficulty), 6.5 - (self.difficulty * 0.5))
        return ai_correct, response_time
