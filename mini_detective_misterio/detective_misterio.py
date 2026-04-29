import sys
import time
from dataclasses import dataclass

import pygame


WIDTH, HEIGHT = 1200, 760
FPS = 60
CASE_TIME_LIMIT = 300

BG = (14, 14, 18)
PANEL = (28, 30, 36)
CARD = (38, 41, 49)
CARD_HOVER = (53, 58, 70)
BORDER = (90, 95, 110)
TEXT = (230, 232, 238)
MUTED = (170, 175, 190)
ACCENT = (196, 167, 99)
GOOD = (80, 180, 120)
BAD = (196, 78, 78)


@dataclass
class Sospechoso:
    nombre: str
    descripcion: str
    coartada: str


@dataclass
class Caso:
    titulo: str
    historia: str
    sospechosos: list[Sospechoso]
    pistas: list[str]
    culpable_idx: int
    explicacion: str


class Button:
    def __init__(self, rect, text, font, base_color=CARD, hover_color=CARD_HOVER):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color

    def draw(self, screen, mouse_pos):
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BORDER, self.rect, width=1, border_radius=10)
        txt = self.font.render(self.text, True, TEXT)
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Mini Detective / Misterio")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("consolas", 36, bold=True)
        self.font_subtitle = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_text = pygame.font.SysFont("segoeui", 20)
        self.font_small = pygame.font.SysFont("segoeui", 17)
        self.font_btn = pygame.font.SysFont("segoeui", 24, bold=True)
4
        self.state = "menu"
        self.cases = self._build_cases()
        self.case_index = 0
        self.score = 0
        self.case_start_time = time.time()
        self.last_choice_correct = False
        self.last_explanation = ""
        self.running = True

        self.story_rect = pygame.Rect(20, 90, 760, 260)
        self.suspects_rect = pygame.Rect(20, 370, 760, 370)
        self.clues_rect = pygame.Rect(800, 90, 380, 650)

        self.play_btn = Button((470, 300, 260, 70), "Jugar", self.font_btn, ACCENT, (216, 185, 112))
        self.exit_btn = Button((470, 390, 260, 70), "Salir", self.font_btn)
        self.next_btn = Button((470, 610, 260, 60), "Siguiente caso", self.font_btn)
        self.menu_btn = Button((470, 680, 260, 50), "Volver al menu", self.font_btn)
        self.play_again_btn = Button((470, 360, 260, 70), "Jugar de nuevo", self.font_btn, ACCENT, (216, 185, 112))

    def _build_cases(self):
        return [
            Caso(
                "Caso 1: Robo en la Galeria Nocturna",
                "A las 22:30 desaparecio un reloj antiguo en una galeria privada. Solo tres personas estaban en el edificio.",
                [
                    Sospechoso("Marta Rios", "Curadora de arte.", "Dice que estaba en inventario digital."),
                    Sospechoso("Leo Vargas", "Guardia nocturno.", "Asegura que patrullaba el ala oeste."),
                    Sospechoso("Nora Salas", "Restauradora externa.", "Afirma que atendia una llamada."),
                ],
                [
                    "Polvo de guantes de latex azul en la vitrina.",
                    "Sesion de inventario abierta, pero sin actividad por 25 minutos.",
                    "Camara del ala oeste desenfocada entre 22:20 y 22:40.",
                ],
                0,
                "Marta dejo la sesion abierta para simular actividad y uso guantes azules. Tenia acceso y conocimiento de la vitrina.",
            ),
            Caso(
                "Caso 2: Sabotaje en la Startup",
                "Antes de una demo clave, el servidor principal fue apagado manualmente desde sala tecnica.",
                [
                    Sospechoso("Diego Mena", "DevOps senior.", "Dice que estaba en videollamada."),
                    Sospechoso("Paula Neri", "Gerente de producto.", "Asegura que preparaba slides."),
                    Sospechoso("Iker Sol", "Desarrollador backend.", "Afirma que corregia un bug."),
                ],
                [
                    "La sala tecnica se abrio con RFID de Diego.",
                    "La llamada de Diego estuvo en mute sin camara varios minutos.",
                    "No hubo indicios de intrusion externa.",
                ],
                0,
                "Diego tenia acceso fisico y tiempo para apagar el servidor sin levantar sospechas.",
            ),
            Caso(
                "Caso 3: Veneno en el Hotel Eclipse",
                "Un chef fue hospitalizado tras probar salsa antes del servicio. Solo tres empleados estaban cerca.",
                [
                    Sospechoso("Rene Pardo", "Sous chef de especias.", "Dice que no toco la salsa final."),
                    Sospechoso("Clara Ibanez", "Mesera.", "Afirma que solo retiro platos."),
                    Sospechoso("Fabio Luna", "Ayudante nuevo.", "Dice que limpiaba utensilios."),
                ],
                [
                    "Frasco adulterado con etiqueta cambiada.",
                    "Rene era quien escribia etiquetas a mano en turno.",
                    "Clara aparece en camaras fuera de la zona de especias.",
                ],
                0,
                "Rene manejo las especias y altero la etiqueta del frasco contaminado.",
            ),
        ]

    def wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines, current = [], ""
        for word in words:
            test = f"{current} {word}".strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw_multiline(self, surface, text, font, color, x, y, max_width, line_gap=5):
        offset = 0
        for line in self.wrap_text(text, font, max_width):
            img = font.render(line, True, color)
            surface.blit(img, (x, y + offset))
            offset += img.get_height() + line_gap

    def fade_transition(self, duration=0.35):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed >= duration:
                break
            overlay.set_alpha(int((elapsed / duration) * 255))
            self.screen.blit(overlay, (0, 0))
            pygame.display.flip()
            self.clock.tick(FPS)

    def reset_progress(self):
        self.case_index = 0
        self.score = 0
        self.case_start_time = time.time()
        self.state = "case"

    def current_case(self):
        return self.cases[self.case_index]

    def time_left(self):
        return max(0, CASE_TIME_LIMIT - int(time.time() - self.case_start_time))

    def suspect_buttons(self):
        buttons = []
        x, y = self.suspects_rect.x + 14, self.suspects_rect.y + 14
        w, h, gap = self.suspects_rect.width - 28, 110, 10
        for i in range(3):
            buttons.append(pygame.Rect(x, y + i * (h + gap), w, h))
        return buttons

    def resolve_accusation(self, idx):
        case = self.current_case()
        bonus = max(0, self.time_left() // 3)
        if idx == case.culpable_idx:
            self.last_choice_correct = True
            self.score += 100 + bonus
        else:
            self.last_choice_correct = False
            self.score += max(0, 20 + bonus // 2)
        self.last_explanation = case.explicacion
        self.state = "result"
        self.fade_transition()

    def auto_fail_if_time_up(self):
        if self.state == "case" and self.time_left() == 0:
            case = self.current_case()
            self.last_choice_correct = False
            culpable = case.sospechosos[case.culpable_idx].nombre
            self.last_explanation = f"Tiempo agotado. El culpable era {culpable}. {case.explicacion}"
            self.state = "result"
            self.fade_transition()

    def draw_menu(self):
        self.screen.fill(BG)
        title = self.font_title.render("Mini Detective / Misterio", True, ACCENT)
        subtitle = self.font_text.render("Resuelve casos rapidos con logica y observacion.", True, MUTED)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 170))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 220))
        mouse = pygame.mouse.get_pos()
        self.play_btn.draw(self.screen, mouse)
        self.exit_btn.draw(self.screen, mouse)

    def draw_case(self):
        case = self.current_case()
        mouse = pygame.mouse.get_pos()
        self.screen.fill(BG)

        self.screen.blit(self.font_subtitle.render(case.titulo, True, ACCENT), (20, 20))
        info = f"Caso {self.case_index + 1}/{len(self.cases)} | Puntuacion: {self.score} | Tiempo: {self.time_left()}s"
        self.screen.blit(self.font_small.render(info, True, MUTED), (20, 55))

        pygame.draw.rect(self.screen, PANEL, self.story_rect, border_radius=12)
        pygame.draw.rect(self.screen, BORDER, self.story_rect, width=1, border_radius=12)
        self.screen.blit(self.font_subtitle.render("Historia", True, TEXT), (self.story_rect.x + 14, self.story_rect.y + 12))
        self.draw_multiline(self.screen, case.historia, self.font_text, TEXT, self.story_rect.x + 14, self.story_rect.y + 50, self.story_rect.width - 28, 6)

        pygame.draw.rect(self.screen, PANEL, self.suspects_rect, border_radius=12)
        pygame.draw.rect(self.screen, BORDER, self.suspects_rect, width=1, border_radius=12)
        self.screen.blit(self.font_subtitle.render("Sospechosos (click para acusar)", True, TEXT), (self.suspects_rect.x + 14, self.suspects_rect.y + 10))

        for i, rect in enumerate(self.suspect_buttons()):
            pygame.draw.rect(self.screen, CARD_HOVER if rect.collidepoint(mouse) else CARD, rect, border_radius=10)
            pygame.draw.rect(self.screen, BORDER, rect, width=1, border_radius=10)
            avatar = pygame.Rect(rect.x + 10, rect.y + 12, 70, 84)
            pygame.draw.rect(self.screen, (70, 76, 90), avatar, border_radius=8)
            pygame.draw.rect(self.screen, BORDER, avatar, width=1, border_radius=8)
            s = case.sospechosos[i]
            self.screen.blit(self.font_text.render(s.nombre, True, ACCENT), (avatar.right + 12, rect.y + 8))
            desc = f"{s.descripcion} Coartada: {s.coartada}"
            self.draw_multiline(self.screen, desc, self.font_small, TEXT, avatar.right + 12, rect.y + 36, rect.width - 110, 3)

        pygame.draw.rect(self.screen, PANEL, self.clues_rect, border_radius=12)
        pygame.draw.rect(self.screen, BORDER, self.clues_rect, width=1, border_radius=12)
        self.screen.blit(self.font_subtitle.render("Pistas", True, TEXT), (self.clues_rect.x + 14, self.clues_rect.y + 12))

        y = self.clues_rect.y + 56
        for i, clue in enumerate(case.pistas):
            box = pygame.Rect(self.clues_rect.x + 14, y, self.clues_rect.width - 28, 170)
            pygame.draw.rect(self.screen, CARD, box, border_radius=10)
            pygame.draw.rect(self.screen, BORDER, box, width=1, border_radius=10)
            self.screen.blit(self.font_text.render(f"Pista {i + 1}", True, ACCENT), (box.x + 10, box.y + 8))
            self.draw_multiline(self.screen, clue, self.font_small, TEXT, box.x + 10, box.y + 40, box.width - 20, 4)
            y += 185

    def draw_result(self):
        case = self.current_case()
        self.screen.fill(BG)
        color = GOOD if self.last_choice_correct else BAD
        title = "Acusacion correcta" if self.last_choice_correct else "Acusacion incorrecta"
        img = self.font_title.render(title, True, color)
        self.screen.blit(img, (WIDTH // 2 - img.get_width() // 2, 60))

        panel = pygame.Rect(110, 150, 980, 420)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=14)
        pygame.draw.rect(self.screen, BORDER, panel, width=1, border_radius=14)

        culprit = case.sospechosos[case.culpable_idx].nombre
        self.screen.blit(self.font_subtitle.render(f"Culpable: {culprit}", True, ACCENT), (panel.x + 20, panel.y + 20))
        self.draw_multiline(self.screen, self.last_explanation, self.font_text, TEXT, panel.x + 20, panel.y + 70, panel.width - 40, 6)
        self.screen.blit(self.font_subtitle.render(f"Puntuacion actual: {self.score}", True, MUTED), (panel.x + 20, panel.y + panel.height - 50))

        mouse = pygame.mouse.get_pos()
        self.next_btn.draw(self.screen, mouse)
        self.menu_btn.draw(self.screen, mouse)

    def draw_finished(self):
        self.screen.fill(BG)
        t = self.font_title.render("Todos los casos resueltos", True, ACCENT)
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 140))
        s = self.font_subtitle.render(f"Puntuacion final: {self.score}", True, TEXT)
        self.screen.blit(s, (WIDTH // 2 - s.get_width() // 2, 210))
        msg = "Excelente trabajo detective. Puedes volver al menu o jugar otra vez."
        self.draw_multiline(self.screen, msg, self.font_text, MUTED, 280, 270, 650, 6)
        mouse = pygame.mouse.get_pos()
        self.play_again_btn.draw(self.screen, mouse)
        self.menu_btn.draw(self.screen, mouse)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.state == "menu":
                    if self.play_btn.clicked(event):
                        self.fade_transition()
                        self.reset_progress()
                    elif self.exit_btn.clicked(event):
                        self.running = False
                elif self.state == "case":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for i, rect in enumerate(self.suspect_buttons()):
                            if rect.collidepoint(event.pos):
                                self.resolve_accusation(i)
                                break
                elif self.state == "result":
                    if self.next_btn.clicked(event):
                        self.case_index += 1
                        if self.case_index >= len(self.cases):
                            self.state = "finished"
                        else:
                            self.case_start_time = time.time()
                            self.fade_transition()
                            self.state = "case"
                    elif self.menu_btn.clicked(event):
                        self.fade_transition()
                        self.state = "menu"
                elif self.state == "finished":
                    if self.play_again_btn.clicked(event):
                        self.fade_transition()
                        self.reset_progress()
                    elif self.menu_btn.clicked(event):
                        self.fade_transition()
                        self.state = "menu"

            self.auto_fail_if_time_up()

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "case":
                self.draw_case()
            elif self.state == "result":
                self.draw_result()
            elif self.state == "finished":
                self.draw_finished()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
