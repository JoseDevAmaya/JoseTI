import os

import pygame

from settings import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_BORDER,
    COLOR_INFO,
    COLOR_PANEL,
    COLOR_PANEL_ALT,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_WARNING,
    CURSOR_BLINK_MS,
    FONT_NAME,
    ICON_PATH,
    MAX_VISIBLE_LINES,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


def ensure_icon():
    """Create and return a simple generated icon surface."""
    size = 64
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((8, 11, 14))
    pygame.draw.rect(surf, (0, 200, 130), (4, 4, 56, 56), 2, border_radius=8)
    pygame.draw.line(surf, (0, 240, 160), (14, 22), (50, 22), 2)
    pygame.draw.line(surf, (0, 240, 160), (14, 32), (40, 32), 2)
    pygame.draw.line(surf, (0, 240, 160), (14, 42), (46, 42), 2)
    pygame.draw.circle(surf, (0, 170, 255), (50, 14), 6)

    icon_dir = os.path.dirname(ICON_PATH)
    if icon_dir and not os.path.exists(icon_dir):
        os.makedirs(icon_dir, exist_ok=True)
    if not os.path.exists(ICON_PATH):
        pygame.image.save(surf, ICON_PATH)
    return surf


class TerminalUI:
    def __init__(self):
        self.font_title = pygame.font.SysFont(FONT_NAME, 34, bold=True)
        self.font_header = pygame.font.SysFont(FONT_NAME, 21, bold=True)
        self.font_text = pygame.font.SysFont(FONT_NAME, 20)
        self.font_small = pygame.font.SysFont(FONT_NAME, 17)

        self.terminal_lines: list[str] = []
        self.command_history: list[str] = []
        self.history_index: int = -1
        self.current_input = ""

        self.cursor_visible = True
        self.last_cursor_toggle = pygame.time.get_ticks()

        # Typewriter effect queue
        self.pending_output: list[str] = []
        self.last_output_tick = pygame.time.get_ticks()
        self.output_interval_ms = 42

        self.menu_buttons = {
            "start": pygame.Rect(WINDOW_WIDTH // 2 - 130, 260, 260, 56),
            "continue": pygame.Rect(WINDOW_WIDTH // 2 - 130, 330, 260, 56),
            "exit": pygame.Rect(WINDOW_WIDTH // 2 - 130, 400, 260, 56),
        }

    def queue_output(self, lines: list[str]):
        self.pending_output.extend(lines)

    def flush_immediate(self, lines: list[str]):
        for line in lines:
            self.append_line(line)

    def append_line(self, line: str):
        self.terminal_lines.append(line)
        if len(self.terminal_lines) > 400:
            self.terminal_lines = self.terminal_lines[-400:]

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_cursor_toggle >= CURSOR_BLINK_MS:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = now

        if self.pending_output and now - self.last_output_tick >= self.output_interval_ms:
            self.append_line(self.pending_output.pop(0))
            self.last_output_tick = now

    def draw_menu(self, screen, has_continue: bool):
        screen.fill(COLOR_BG)
        self._draw_grid(screen)
        title = self.font_title.render("HACKOPS SIMULATOR", True, COLOR_ACCENT)
        sub = self.font_text.render("Ethical infiltration terminal campaign", True, COLOR_TEXT_DIM)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 120))
        screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 168))

        for key, rect in self.menu_buttons.items():
            enabled = has_continue if key == "continue" else True
            label = key.capitalize()
            self._draw_button(screen, rect, label, enabled=enabled)

    def draw_game(self, screen, mission_name: str, briefing: str, rep: int, level: int, exp: int, alerts: int, max_alerts: int):
        screen.fill(COLOR_BG)
        self._draw_grid(screen)

        left = pygame.Rect(16, 16, 840, WINDOW_HEIGHT - 32)
        right = pygame.Rect(870, 16, WINDOW_WIDTH - 886, WINDOW_HEIGHT - 32)

        pygame.draw.rect(screen, COLOR_PANEL, left, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, left, 1, border_radius=8)
        pygame.draw.rect(screen, COLOR_PANEL_ALT, right, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, right, 1, border_radius=8)

        terminal_header = self.font_header.render(">> TERMINAL // ACTIVE", True, COLOR_ACCENT)
        screen.blit(terminal_header, (32, 28))

        # Terminal content
        y = 66
        visible = self.terminal_lines[-MAX_VISIBLE_LINES:]
        for line in visible:
            color = COLOR_TEXT
            if line.startswith("[ERR]"):
                color = COLOR_WARNING
            elif line.startswith("[INFO]"):
                color = COLOR_INFO
            txt = self.font_text.render(line, True, color)
            screen.blit(txt, (34, y))
            y += 26

        prompt = "> " + self.current_input
        if self.cursor_visible:
            prompt += "_"
        prompt_img = self.font_text.render(prompt, True, COLOR_ACCENT)
        screen.blit(prompt_img, (34, WINDOW_HEIGHT - 52))

        # Sidebar status
        side_y = 28
        for label, value in [
            ("Mission", mission_name),
            ("Reputation", str(rep)),
            ("Level", str(level)),
            ("EXP", str(exp)),
            ("Alerts", f"{alerts}/{max_alerts}"),
        ]:
            k = self.font_small.render(label.upper(), True, COLOR_TEXT_DIM)
            v = self.font_text.render(value, True, COLOR_TEXT)
            screen.blit(k, (888, side_y))
            screen.blit(v, (888, side_y + 18))
            side_y += 70

        pygame.draw.line(screen, COLOR_BORDER, (888, side_y), (1150, side_y), 1)
        side_y += 12
        b_title = self.font_small.render("BRIEFING", True, COLOR_TEXT_DIM)
        screen.blit(b_title, (888, side_y))
        side_y += 24
        for line in self._wrap_lines(briefing, self.font_small, 250):
            img = self.font_small.render(line, True, COLOR_TEXT)
            screen.blit(img, (888, side_y))
            side_y += 22

    def draw_end(self, screen, title: str, subtitle: str, hint: str):
        screen.fill(COLOR_BG)
        self._draw_grid(screen)
        t = self.font_title.render(title, True, COLOR_ACCENT if "Victory" in title else COLOR_WARNING)
        s = self.font_text.render(subtitle, True, COLOR_TEXT)
        h = self.font_small.render(hint, True, COLOR_TEXT_DIM)
        screen.blit(t, (WINDOW_WIDTH // 2 - t.get_width() // 2, 210))
        screen.blit(s, (WINDOW_WIDTH // 2 - s.get_width() // 2, 270))
        screen.blit(h, (WINDOW_WIDTH // 2 - h.get_width() // 2, 330))

    def handle_menu_click(self, pos: tuple[int, int], has_continue: bool) -> str | None:
        if self.menu_buttons["start"].collidepoint(pos):
            return "start"
        if has_continue and self.menu_buttons["continue"].collidepoint(pos):
            return "continue"
        if self.menu_buttons["exit"].collidepoint(pos):
            return "exit"
        return None

    def _draw_button(self, screen, rect: pygame.Rect, text: str, enabled=True):
        mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse)
        base = (18, 35, 28) if enabled else (20, 20, 20)
        hover_color = (24, 55, 43)
        color = hover_color if hover and enabled else base
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=8)
        txt_color = COLOR_TEXT if enabled else COLOR_TEXT_DIM
        txt = self.font_header.render(text, True, txt_color)
        screen.blit(txt, txt.get_rect(center=rect.center))

    def _draw_grid(self, screen):
        for x in range(0, WINDOW_WIDTH, 32):
            pygame.draw.line(screen, (10, 22, 18), (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, 32):
            pygame.draw.line(screen, (10, 22, 18), (0, y), (WINDOW_WIDTH, y))

    def _wrap_lines(self, text: str, font: pygame.font.Font, width: int) -> list[str]:
        words = text.split(" ")
        lines: list[str] = []
        curr = ""
        for w in words:
            test = f"{curr} {w}".strip()
            if font.size(test)[0] <= width:
                curr = test
            else:
                lines.append(curr)
                curr = w
        if curr:
            lines.append(curr)
        return lines

