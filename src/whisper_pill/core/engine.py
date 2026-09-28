"""
whisper_pill.core.engine
------------------------
CTranslate2 Whisper inference orchestration engine.
Handles model caching, parameter configuration, VAD gating,
and structured performance tracking.
"""

from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Optional, Callable
import numpy as np
from faster_whisper import WhisperModel

from whisper_pill.core.config import AppConfig
from whisper_pill.core.hardware import detect_optimal_hardware
from whisper_pill.core.guard import SecurityGuard


@dataclass(frozen=True)
class TranscriptionResult:
    text: str
    audio_duration_sec: float
    inference_duration_sec: float
    real_time_factor: float
    model_name: str


class WhisperEngine:
    """
    Encapsulates faster-whisper model lifecycle and optimized batch transcription.
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.hardware = detect_optimal_hardware()
        self.cpu_threads = config.cpu_threads_override or self.hardware.optimal_threads
        self.model: Optional[WhisperModel] = None
        self.current_model_name: Optional[str] = None

    def load_model(self, model_name: str, on_progress: Optional[Callable[[str], None]] = None) -> None:
        """
        Loads or switches the active Whisper model in RAM using optimal thread allocation.
        """
        if not SecurityGuard.validate_model_identifier(model_name):
            raise ValueError(f"Sicherheitsblockade: Modell-Identifier '{model_name}' ist nicht autorisiert oder ungültig!")

        if self.current_model_name == model_name and self.model is not None:
            return

        if on_progress:
            on_progress(f"Initialisiere {model_name}...")

        self.model = WhisperModel(
            model_size_or_path=model_name,
            device="cpu",
            compute_type="int8",
            cpu_threads=self.cpu_threads,
            num_workers=1
        )
        self.current_model_name = model_name

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> TranscriptionResult:
        """
        Executes single-pass batch inference on raw float32 audio.
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded. Call load_model() first.")

        # Sanitize audio buffer against NaN/Inf poisoning and DoS duration spikes
        audio_data = SecurityGuard.sanitize_audio_buffer(audio_data, sample_rate=sample_rate)

        if len(audio_data) == 0:
            return TranscriptionResult(
                text="",
                audio_duration_sec=0.0,
                inference_duration_sec=0.0,
                real_time_factor=0.0,
                model_name=self.current_model_name or "unknown"
            )

        audio_len_sec = round(len(audio_data) / sample_rate, 2)
        t_start = time.perf_counter()

        segments, _ = self.model.transcribe(
            audio_data,
            language=self.config.language,
            beam_size=self.config.beam_size,
            temperature=0.0,
            vad_filter=self.config.vad_filter,
            repetition_penalty=self.config.repetition_penalty,
            no_repeat_ngram_size=self.config.no_repeat_ngram_size,
            initial_prompt=self.config.initial_prompt
        )

        full_text = " ".join([seg.text.strip() for seg in segments]).strip()
        t_elapsed = round(time.perf_counter() - t_start, 2)
        rtf = round(audio_len_sec / max(t_elapsed, 0.01), 1)

        return TranscriptionResult(
            text=full_text,
            audio_duration_sec=audio_len_sec,
            inference_duration_sec=t_elapsed,
            real_time_factor=rtf,
            model_name=self.current_model_name or "unknown"
        )
