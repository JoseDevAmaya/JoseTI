import math
from array import array

import pygame


def _tone(freq: float, duration: float, vol: float) -> pygame.mixer.Sound:
    sample_rate = 44100
    samples = int(sample_rate * duration)
    amp = int(32767 * vol)
    buf = array("h")
    for i in range(samples):
        t = i / sample_rate
        buf.append(int(amp * math.sin(2.0 * math.pi * freq * t)))
    return pygame.mixer.Sound(buffer=buf.tobytes())


class Sfx:
    def __init__(self):
        self.enabled = True
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1)
            self.ok = _tone(860, 0.08, 0.25)
            self.bad = _tone(240, 0.09, 0.28)
            self.tick = _tone(1220, 0.02, 0.1)
            self.win = _tone(560, 0.25, 0.28)
        except pygame.error:
            self.enabled = False

    def _play(self, snd):
        if self.enabled and snd is not None:
            snd.play()

    def play_ok(self):
        self._play(getattr(self, "ok", None))

    def play_bad(self):
        self._play(getattr(self, "bad", None))

    def play_tick(self):
        self._play(getattr(self, "tick", None))

    def play_win(self):
        self._play(getattr(self, "win", None))
