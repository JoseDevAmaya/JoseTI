import math
from array import array

import pygame


def _generate_tone(frequency: float, duration: float, volume: float = 0.35) -> pygame.mixer.Sound:
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    amp = int(32767 * max(0.0, min(1.0, volume)))
    buf = array("h")
    for i in range(n_samples):
        t = i / sample_rate
        buf.append(int(amp * math.sin(2.0 * math.pi * frequency * t)))
    return pygame.mixer.Sound(buffer=buf.tobytes())


class AudioManager:
    def __init__(self):
        self.enabled = True
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1)
            self.sfx_ok = _generate_tone(920, 0.08, 0.28)
            self.sfx_fail = _generate_tone(240, 0.10, 0.28)
            self.sfx_type = _generate_tone(1200, 0.02, 0.12)
            self.sfx_mission = _generate_tone(650, 0.20, 0.35)
        except pygame.error:
            self.enabled = False

    def _play(self, sound: pygame.mixer.Sound | None):
        if self.enabled and sound is not None:
            sound.play()

    def play_success(self):
        self._play(getattr(self, "sfx_ok", None))

    def play_fail(self):
        self._play(getattr(self, "sfx_fail", None))

    def play_type(self):
        self._play(getattr(self, "sfx_type", None))

    def play_mission_complete(self):
        self._play(getattr(self, "sfx_mission", None))

