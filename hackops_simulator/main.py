"""
HackOps Simulator - main entrypoint

Build notes (PyInstaller):
    python -m PyInstaller --noconfirm --clean --onefile --windowed --name HackOpsSimulator main.py
"""

import sys

import pygame

from audio import AudioManager
from commands import CommandProcessor
from game_logic import GameLogic
from persistence import load_progress, save_progress
from settings import FPS, TITLE, WINDOW_HEIGHT, WINDOW_WIDTH
from ui import TerminalUI, ensure_icon


class HackOpsApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        pygame.display.set_icon(ensure_icon())
        self.clock = pygame.time.Clock()

        self.logic = GameLogic()
        self.commands = CommandProcessor(self.logic)
        self.ui = TerminalUI()
        self.audio = AudioManager()

        self.state = "menu"  # menu, playing, game_over, victory
        self.running = True

    def start_new_game(self):
        self.logic = GameLogic()
        self.commands = CommandProcessor(self.logic)
        self.ui.terminal_lines = []
        self.ui.pending_output = []
        self._push_intro_lines()
        self.state = "playing"

    def continue_game(self):
        loaded = load_progress()
        if loaded is None:
            return False
        self.logic = GameLogic()
        self.logic.progress = loaded
        self.logic.reset_session()
        self.commands = CommandProcessor(self.logic)
        self.ui.terminal_lines = []
        self.ui.pending_output = []
        self._push_intro_lines(continued=True)
        self.state = "playing"
        return True

    def _push_intro_lines(self, continued=False):
        prefix = "[INFO] Resume loaded." if continued else "[INFO] New campaign started."
        mission = self.logic.current_mission()
        self.ui.flush_immediate(
            [
                prefix,
                "Type 'help' for command list.",
                f"[INFO] Mission: {mission.name}",
                mission.briefing,
            ]
        )

    def handle_game_input(self, event: pygame.event.Event):
        if event.key == pygame.K_RETURN:
            cmd = self.ui.current_input.strip()
            if not cmd:
                return
            self.ui.append_line("> " + cmd)
            self.ui.command_history.append(cmd)
            self.ui.history_index = len(self.ui.command_history)
            self.ui.current_input = ""

            lines, success = self.commands.process(cmd)
            mission_before = self.logic.progress.mission_index
            for ln in lines:
                if ln == "__CLEAR__":
                    self.ui.terminal_lines = []
                else:
                    self.ui.queue_output([ln])

            if success:
                self.audio.play_success()
            else:
                if cmd.split()[0].lower() != "help":
                    self.audio.play_fail()

            mission_after = self.logic.progress.mission_index
            if mission_after > mission_before:
                self.audio.play_mission_complete()
                if self.logic.is_victory():
                    save_progress(self.logic.progress)
                    self.state = "victory"
                    return
                next_mission = self.logic.current_mission()
                self.ui.queue_output(
                    [
                        f"[INFO] Next mission: {next_mission.name}",
                        next_mission.briefing,
                    ]
                )

            if self.logic.is_game_over():
                save_progress(self.logic.progress)
                self.state = "game_over"
                return

            save_progress(self.logic.progress)
            return

        if event.key == pygame.K_BACKSPACE:
            self.ui.current_input = self.ui.current_input[:-1]
            return

        if event.key == pygame.K_UP:
            if self.ui.command_history and self.ui.history_index > 0:
                self.ui.history_index -= 1
                self.ui.current_input = self.ui.command_history[self.ui.history_index]
            return

        if event.key == pygame.K_DOWN:
            if self.ui.command_history and self.ui.history_index < len(self.ui.command_history) - 1:
                self.ui.history_index += 1
                self.ui.current_input = self.ui.command_history[self.ui.history_index]
            else:
                self.ui.history_index = len(self.ui.command_history)
                self.ui.current_input = ""
            return

        if event.unicode and event.unicode.isprintable():
            self.ui.current_input += event.unicode
            self.audio.play_type()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.ui.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        choice = self.ui.handle_menu_click(event.pos, has_continue=load_progress() is not None)
                        if choice == "start":
                            self.start_new_game()
                        elif choice == "continue":
                            self.continue_game()
                        elif choice == "exit":
                            self.running = False
                elif self.state == "playing":
                    if event.type == pygame.KEYDOWN:
                        self.handle_game_input(event)
                elif self.state in ("game_over", "victory"):
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.state = "menu"

            if self.state == "menu":
                self.ui.draw_menu(self.screen, has_continue=load_progress() is not None)
            elif self.state == "playing":
                mission = self.logic.current_mission()
                p = self.logic.progress
                self.ui.draw_game(
                    self.screen,
                    mission_name=mission.name,
                    briefing=mission.briefing,
                    rep=p.reputation,
                    level=p.level,
                    exp=p.exp,
                    alerts=p.alerts,
                    max_alerts=p.max_alerts,
                )
            elif self.state == "game_over":
                self.ui.draw_end(
                    self.screen,
                    "Game Over",
                    "Counter-intel tracked your operation.",
                    "Press ENTER to return to menu",
                )
            elif self.state == "victory":
                self.ui.draw_end(
                    self.screen,
                    "Victory",
                    "All missions completed. HackOps campaign cleared.",
                    "Press ENTER to return to menu",
                )

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    HackOpsApp().run()

