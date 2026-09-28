"""
whisper_pill.ui.sounds
----------------------
Asynchronous acoustic chimes utilizing native Windows winsound.
Provides tactical acoustic feedback without blocking the UI or audio capture.
"""

from __future__ import annotations
import threading
import time
import winsound


class SoundManager:
    """
    Manages non-blocking audio cues for dictate workflow events.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def play(self, sound_type: str) -> None:
        """Plays the requested chime asynchronously if sound is enabled."""
        if not self.enabled:
            return

        def _worker():
            try:
                if sound_type == "start":
                    winsound.Beep(880, 70)  # A5 (70ms)
                elif sound_type == "stop":
                    winsound.Beep(587, 70)  # D5 (70ms)
                elif sound_type == "success":
                    winsound.Beep(1046, 50)  # C6 (50ms)
                    time.sleep(0.02)
                    winsound.Beep(1318, 80)  # E6 (80ms)
                elif sound_type == "ready":
                    winsound.Beep(1175, 40)  # D6 (40ms)
                    time.sleep(0.02)
                    winsound.Beep(1568, 60)  # G6 (60ms)
            except Exception:
                pass  # Graceful fallback on headless or systems without sound cards

        threading.Thread(target=_worker, daemon=True).start()
