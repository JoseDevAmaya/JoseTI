import os

import pygame

from settings import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_BORDER,
    COLOR_GRID,
    COLOR_INFO,
    COLOR_PANEL,
    COLOR_PANEL_ALT,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_WARN,
    CURSOR_BLINK_MS,
    FONT_NAME,
    ICON_FILE,
    MAX_TERMINAL_LINES,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


def generate_icon() -> pygame.Surface:
    icon = pygame.Surface((64, 64), pygame.SRCALPHA)
    icon.fill((8, 10, 14))
    pygame.draw.rect(icon, (0, 210, 135), (4, 4, 56, 56), 2, border_radius=8)
    pygame.draw.line(icon, (0, 230, 150), (14, 22), (50, 22), 2)
    pygame.draw.line(icon, (0, 230, 150), (14, 32), (40, 32), 2)
    pygame.draw.line(icon, (0, 230, 150), (14, 42), (46, 42), 2)
    pygame.draw.circle(icon, (90, 180, 255), (50, 14), 6)

    os.makedirs(os.path.dirname(ICON_FILE), exist_ok=True)
    if not os.path.exists(ICON_FILE):
        pygame.image.save(icon, ICON_FILE)
    return icon


class UI:
    def __init__(self):
        self.f_title = pygame.font.SysFont(FONT_NAME, 34, bold=True)
        self.f_h = pygame.font.SysFont(FONT_NAME, 22, bold=True)
        self.f_t = pygame.font.SysFont(FONT_NAME, 20)
        self.f_s = pygame.font.SysFont(FONT_NAME, 17)

        self.lines: list[str] = []
        self.pending: list[str] = []
        self.input_text = ""
        self.cursor = True
        self.cursor_last = pygame.time.get_ticks()
        self.hist: list[str] = []
        self.hist_idx = -1
        self.type_last = pygame.time.get_ticks()

        self.btn_start = pygame.Rect(WINDOW_WIDTH // 2 - 150, 270, 300, 58)
        self.btn_continue = pygame.Rect(WINDOW_WIDTH // 2 - 150, 340, 300, 58)
        self.btn_exit = pygame.Rect(WINDOW_WIDTH // 2 - 150, 410, 300, 58)

    def push(self, lines: list[str]):
        self.pending.extend(lines)

    def add_line(self, line: str):
        self.lines.append(line)
        if len(self.lines) > 500:
            self.lines = self.lines[-500:]

    def update(self, type_ms: int):
        now = pygame.time.get_ticks()
        if now - self.cursor_last >= CURSOR_BLINK_MS:
            self.cursor = not self.cursor
            self.cursor_last = now
        if self.pending and now - self.type_last >= type_ms:
            self.add_line(self.pending.pop(0))
            self.type_last = now

    def draw_menu(self, screen, has_continue: bool):
        self._bg(screen)
        title = self.f_title.render("CODE DUEL ARENA", True, COLOR_ACCENT)
        sub = self.f_t.render("Terminal Hacker Trivia vs Adaptive AI", True, COLOR_TEXT_DIM)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 150))
        screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 197))
        self._btn(screen, self.btn_start, "Start", True)
        self._btn(screen, self.btn_continue, "Continue", has_continue)
        self._btn(screen, self.btn_exit, "Exit", True)

    def draw_game(self, screen, hud: dict, question_block: list[str], time_left: float):
        self._bg(screen)
        left = pygame.Rect(16, 16, 875, WINDOW_HEIGHT - 32)
        right = pygame.Rect(905, 16, WINDOW_WIDTH - 921, WINDOW_HEIGHT - 32)
        pygame.draw.rect(screen, COLOR_PANEL, left, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, left, 1, border_radius=8)
        pygame.draw.rect(screen, COLOR_PANEL_ALT, right, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, right, 1, border_radius=8)

        screen.blit(self.f_h.render("TERMINAL", True, COLOR_ACCENT), (30, 24))
        y = 60
        for ln in self.lines[-MAX_TERMINAL_LINES:]:
            c = COLOR_TEXT
            if ln.startswith("[ERR]"):
                c = COLOR_WARN
            elif ln.startswith("[INFO]"):
                c = COLOR_INFO
            screen.blit(self.f_t.render(ln, True, c), (30, y))
            y += 25

        prompt = "> " + self.input_text + ("_" if self.cursor else "")
        screen.blit(self.f_t.render(prompt, True, COLOR_ACCENT), (30, WINDOW_HEIGHT - 48))

        y2 = 24
        for key in ("stage", "player_hp", "ai_hp", "level", "xp", "rep", "streak", "timer"):
            label = key.upper()
            val = hud[key]
            screen.blit(self.f_s.render(label, True, COLOR_TEXT_DIM), (918, y2))
            screen.blit(self.f_t.render(str(val), True, COLOR_TEXT), (918, y2 + 16))
            y2 += 62

        pygame.draw.line(screen, COLOR_BORDER, (918, y2), (1250, y2), 1)
        y2 += 8
        screen.blit(self.f_s.render("ACTIVE CHALLENGE", True, COLOR_TEXT_DIM), (918, y2))
        y2 += 22
        for ln in question_block:
            for wr in self._wrap(ln, self.f_s, 330):
                screen.blit(self.f_s.render(wr, True, COLOR_TEXT), (918, y2))
                y2 += 20

        if time_left <= 5:
            warn = self.f_h.render("TIME CRITICAL", True, COLOR_WARN)
            screen.blit(warn, (1030, 20))

    def draw_end(self, screen, title: str, subtitle: str):
        self._bg(screen)
        t = self.f_title.render(title, True, COLOR_ACCENT if "Victory" in title else COLOR_WARN)
        s = self.f_t.render(subtitle, True, COLOR_TEXT)
        h = self.f_s.render("Press ENTER to return menu", True, COLOR_TEXT_DIM)
        screen.blit(t, (WINDOW_WIDTH // 2 - t.get_width() // 2, 230))
        screen.blit(s, (WINDOW_WIDTH // 2 - s.get_width() // 2, 290))
        screen.blit(h, (WINDOW_WIDTH // 2 - h.get_width() // 2, 340))

    def menu_click(self, pos, has_continue: bool):
        if self.btn_start.collidepoint(pos):
            return "start"
        if has_continue and self.btn_continue.collidepoint(pos):
            return "continue"
        if self.btn_exit.collidepoint(pos):
            return "exit"
        return None

    def _bg(self, screen):
        screen.fill(COLOR_BG)
        for x in range(0, WINDOW_WIDTH, 34):
            pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, 34):
            pygame.draw.line(screen, COLOR_GRID, (0, y), (WINDOW_WIDTH, y))

    def _btn(self, screen, rect, text, enabled=True):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        base = (20, 40, 30) if enabled else (20, 22, 26)
        color = (25, 55, 42) if hover and enabled else base
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=8)
        txt = self.f_h.render(text, True, COLOR_TEXT if enabled else COLOR_TEXT_DIM)
        screen.blit(txt, txt.get_rect(center=rect.center))

    def _wrap(self, text, font, width):
        words = text.split(" ")
        lines, cur = [], ""
        for w in words:
            t = f"{cur} {w}".strip()
            if font.size(t)[0] <= width:
                cur = t
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines
