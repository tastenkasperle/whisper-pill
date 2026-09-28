"""
whisper_pill.core.audio
-----------------------
Zero-disk in-memory audio capture engine utilizing sounddevice.
Streams directly into 16 kHz float32 NumPy arrays without temporary files.
"""

from __future__ import annotations
import threading
from typing import Optional, List
import numpy as np
import sounddevice as sd


class AudioRecorder:
    """
    Manages non-blocking microphone capture into volatile RAM buffers.
    """

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self._frames: List[np.ndarray] = []
        self._lock = threading.Lock()
        self._stream: Optional[sd.InputStream] = None
        self._is_recording = False

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags) -> None:
        """Collects microphone chunks directly into RAM with overflow guard."""
        if status:
            pass  # Overflow or underflow handling if needed
        with self._lock:
            # 180s @ 16kHz float32 max frame limit
            # Guard against uncontrolled RAM consumption if dictation is left running
            max_frames_count = int((180 * self.sample_rate) / frames)
            if len(self._frames) < max_frames_count:
                self._frames.append(indata.copy())

    def start(self) -> None:
        """Starts real-time microphone capture."""
        with self._lock:
            self._frames.clear()
            self._is_recording = True

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._audio_callback
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        """
        Stops the microphone stream and returns the concatenated float32 audio waveform.
        """
        self._is_recording = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            finally:
                self._stream = None

        with self._lock:
            if not self._frames:
                return np.array([], dtype=np.float32)
            audio = np.concatenate(self._frames, axis=0).flatten()
            self._frames.clear()
            return audio

    def get_duration_seconds(self, audio_data: np.ndarray) -> float:
        """Calculates duration in seconds of captured audio array."""
        if len(audio_data) == 0:
            return 0.0
        return round(len(audio_data) / self.sample_rate, 2)
