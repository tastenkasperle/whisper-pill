"""Whisper Pill Core Modules"""
from whisper_pill.core.config import AppConfig, MODEL_PRESETS
from whisper_pill.core.hardware import detect_optimal_hardware, HardwareProfile
from whisper_pill.core.audio import AudioRecorder
from whisper_pill.core.engine import WhisperEngine, TranscriptionResult
from whisper_pill.core.injector import TextInjector

__all__ = [
    "AppConfig",
    "MODEL_PRESETS",
    "detect_optimal_hardware",
    "HardwareProfile",
    "AudioRecorder",
    "WhisperEngine",
    "TranscriptionResult",
    "TextInjector",
]
