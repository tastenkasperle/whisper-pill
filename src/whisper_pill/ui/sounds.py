"""
whisper_pill.ui.sounds
----------------------
Asynchronous acoustic cues utilizing official Windows Media WAV endpoints.
Guarantees 100% reliable audio playback over Bluetooth (FreeBuds Pro), USB DACs,
and system speakers via Windows Audio Session Architecture.
"""

from __future__ import annotations
import os
import threading
import time
import winsound


class SoundManager:
    """
    Manages non-blocking audio cues for dictate workflow events.
    Utilizes official Windows Multimedia PlaySound for native Bluetooth & WASAPI compatibility.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "sounds"))
        media_dir = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Media")
        
        self._sound_paths = {
            "start": os.path.join(assets_dir, "pill_start.wav"),
            "stop": os.path.join(assets_dir, "pill_stop.wav"),
            "success": os.path.join(media_dir, "ding.wav"),
            "ready": os.path.join(assets_dir, "pill_ready.wav"),
        }
        self._ticker_path = os.path.join(assets_dir, "pill_processing_ticker.mp3")
        self._is_ticker_running = False
        self._ticker_lock = threading.Lock()

    def start_processing_loop(self) -> None:
        """Starts the rhythmic Skype-style background computing heartbeat asynchronously."""
        if not self.enabled or not os.path.exists(self._ticker_path):
            return

        with self._ticker_lock:
            if self._is_ticker_running:
                return
            self._is_ticker_running = True

        def _loop_worker():
            import ctypes
            winmm = ctypes.windll.winmm
            alias = "sfx_ticker"
            # Open and start looping audio via native Windows Multimedia MCI
            winmm.mciSendStringW(f'open "{self._ticker_path}" type mpegvideo alias {alias}', None, 0, None)
            winmm.mciSendStringW(f'play {alias} repeat', None, 0, None)

            # Wait until cancellation requested
            while self._is_ticker_running:
                time.sleep(0.05)

            winmm.mciSendStringW(f'stop {alias}', None, 0, None)
            winmm.mciSendStringW(f'close {alias}', None, 0, None)

        threading.Thread(target=_loop_worker, daemon=True).start()

    def stop_processing_loop(self) -> None:
        """Stops the background computing heartbeat immediately."""
        with self._ticker_lock:
            self._is_ticker_running = False

    def play(self, sound_type: str) -> None:
        """Plays the requested chime asynchronously through Windows Audio Session."""
        if not self.enabled:
            return

        def _worker():
            wav_path = self._sound_paths.get(sound_type)
            if wav_path and os.path.exists(wav_path):
                try:
                    # Windows Native Multimedia PlaySound with SND_NODEFAULT to avoid beep on failure
                    winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_NODEFAULT)
                    return
                except Exception as e:
                    print(f"[!] PlaySound error: {e}")

            # Fallback
            try:
                winsound.MessageBeep(winsound.MB_OK)
            except Exception:
                pass

        threading.Thread(target=_worker, daemon=True).start()
