"""
Code Duel Arena

Build EXE:
    python -m PyInstaller --noconfirm --clean --onefile --windowed --name CodeDuelArena --add-data "data;data" main.py
"""

import sys
import time

import pygame

from audio import Sfx
from game_logic import DuelEngine
from persistence import has_save, load_game, save_game
from questions import Question, load_questions
from settings import FPS, TITLE, TYPEWRITER_MS, WINDOW_HEIGHT, WINDOW_WIDTH
from ui import UI, generate_icon


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        pygame.display.set_icon(generate_icon())
        self.clock = pygame.time.Clock()

        questions = load_questions()
        self.engine = DuelEngine(questions)
        self.ui = UI()
        self.sfx = Sfx()

        self.state = "menu"  # menu, battle, game_over, victory
        self.running = True
        self.current_question: Question | None = None
        self.round_start = time.time()
        self.round_time_limit = self.engine.round_time_limit
        self.campaign_goal_stage = 6

    def start_new(self):
        self.engine = DuelEngine(self.engine.questions)
        self.engine.new_match()
        self.ui.lines = []
        self.ui.pending = []
        self.state = "battle"
        self.ui.push(
            [
                "[INFO] Welcome to Code Duel Arena.",
                "[INFO] Answer using: A / B / C / D",
                "[INFO] Extra commands: hint, clear, help",
            ]
        )
        self.next_question()
        save_game(self.engine)

    def continue_game(self):
        if load_game(self.engine):
            self.state = "battle"
            self.ui.lines = []
            self.ui.pending = []
            self.ui.push(["[INFO] Save loaded.", "[INFO] Continue your duel."])
            self.next_question()
            return True
        return False

    def next_question(self):
        self.current_question = self.engine.choose_question()
        self.round_start = time.time()
        q = self.current_question
        self.ui.push(
            [
                "",
                f"[INFO] Challenge [{q.category}] diff={q.difficulty}",
                q.prompt,
                f"A) {q.options[0]}",
                f"B) {q.options[1]}",
                f"C) {q.options[2]}",
                f"D) {q.options[3]}",
            ]
        )

    def time_left(self) -> float:
        return max(0.0, self.round_time_limit - (time.time() - self.round_start))

    def process_input(self, text: str):
        cmd = text.strip()
        if not cmd:
            return
        self.ui.add_line("> " + cmd)
        self.ui.hist.append(cmd)
        self.ui.hist_idx = len(self.ui.hist)

        if cmd.lower() == "clear":
            self.ui.lines = []
            return
        if cmd.lower() == "help":
            self.ui.push(["[INFO] Use A/B/C/D to answer. Optional: hint, clear, help"])
            return
        if cmd.lower() == "hint":
            if self.current_question:
                self.ui.push([f"[INFO] Hint: {self.current_question.explanation}"])
            return

        if cmd.upper() not in {"A", "B", "C", "D"}:
            self.ui.push(["[ERR] Invalid input. Enter A/B/C/D or help."])
            self.sfx.play_bad()
            return

        if not self.current_question:
            self.ui.push(["[ERR] No active challenge loaded."])
            return

        time_left = self.time_left()
        correct, _ = self.engine.evaluate_player(cmd.upper(), time_left)
        if correct:
            self.ui.push([f"[INFO] Correct. {self.current_question.explanation}"])
            self.sfx.play_ok()
        else:
            ans = self.current_question.answer
            self.ui.push([f"[ERR] Wrong. Correct answer: {ans}", self.current_question.explanation])
            self.sfx.play_bad()

        if self.engine.is_ai_dead():
            self.resolve_stage_win()
            return

        ai_ok, _, _ = self.engine.run_ai_turn(self.current_question)
        self.sfx.play_bad() if ai_ok else self.sfx.play_ok()
        if self.engine.is_player_dead():
            self.engine.grant_progress(won=False)
            save_game(self.engine)
            self.state = "game_over"
            return

        save_game(self.engine)
        self.next_question()

    def resolve_stage_win(self):
        self.engine.grant_progress(won=True)
        self.sfx.play_win()
        if self.engine.stage >= self.campaign_goal_stage:
            save_game(self.engine)
            self.state = "victory"
            return
        self.ui.push([f"[INFO] Stage cleared. Entering stage {self.engine.stage}..."])
        self.engine.player.hp = self.engine.player.max_hp
        self.engine.ai_hp = self.engine.ai_max_hp
        save_game(self.engine)
        self.next_question()

    def update_battle(self):
        if self.time_left() <= 0 and self.current_question is not None:
            self.engine.apply_timeout_penalty()
            self.ui.push(["[WARN] You ran out of time this round."])
            self.sfx.play_bad()
            if self.engine.is_player_dead():
                self.engine.grant_progress(won=False)
                save_game(self.engine)
                self.state = "game_over"
                return
            self.engine.run_ai_turn(self.current_question)
            if self.engine.is_player_dead():
                self.engine.grant_progress(won=False)
                save_game(self.engine)
                self.state = "game_over"
                return
            save_game(self.engine)
            self.next_question()

    def build_hud(self):
        p = self.engine.player
        return {
            "stage": self.engine.stage,
            "player_hp": f"{p.hp}/{p.max_hp}",
            "ai_hp": f"{self.engine.ai_hp}/{self.engine.ai_max_hp}",
            "level": p.level,
            "xp": p.xp,
            "rep": p.reputation,
            "streak": p.streak,
            "timer": f"{self.time_left():.1f}s",
        }

    def question_block(self):
        if not self.current_question:
            return ["No challenge loaded."]
        return [
            f"Type: {self.current_question.qtype}",
            "Answer with A, B, C or D.",
            "Use 'hint' if stuck.",
        ]

    def handle_key(self, event: pygame.event.Event):
        if event.key == pygame.K_RETURN:
            typed = self.ui.input_text
            self.ui.input_text = ""
            self.process_input(typed)
            return
        if event.key == pygame.K_BACKSPACE:
            self.ui.input_text = self.ui.input_text[:-1]
            return
        if event.key == pygame.K_UP:
            if self.ui.hist and self.ui.hist_idx > 0:
                self.ui.hist_idx -= 1
                self.ui.input_text = self.ui.hist[self.ui.hist_idx]
            return
        if event.key == pygame.K_DOWN:
            if self.ui.hist and self.ui.hist_idx < len(self.ui.hist) - 1:
                self.ui.hist_idx += 1
                self.ui.input_text = self.ui.hist[self.ui.hist_idx]
            else:
                self.ui.hist_idx = len(self.ui.hist)
                self.ui.input_text = ""
            return
        if event.unicode and event.unicode.isprintable():
            self.ui.input_text += event.unicode
            self.sfx.play_tick()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.ui.update(TYPEWRITER_MS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        action = self.ui.menu_click(event.pos, has_save())
                        if action == "start":
                            self.start_new()
                        elif action == "continue":
                            self.continue_game()
                        elif action == "exit":
                            self.running = False
                elif self.state == "battle":
                    if event.type == pygame.KEYDOWN:
                        self.handle_key(event)
                elif self.state in ("game_over", "victory"):
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.state = "menu"

            if self.state == "battle":
                self.update_battle()

            if self.state == "menu":
                self.ui.draw_menu(self.screen, has_save())
            elif self.state == "battle":
                self.ui.draw_game(self.screen, self.build_hud(), self.question_block(), self.time_left())
            elif self.state == "game_over":
                self.ui.draw_end(self.screen, "Game Over", "The AI outplayed your coding duel.")
            elif self.state == "victory":
                self.ui.draw_end(self.screen, "Victory", "You dominated the arena and became Code Champion.")

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    App().run()
