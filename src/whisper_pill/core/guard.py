"""
whisper_pill.core.guard
-----------------------
Fire Team Elite Security Guard for Whisper Pill Pro.
Defensive boundaries against:
- Malicious model path traversal
- Buffer overflow / RAM exhaustion (audio DoS)
- Audio NaN/Inf float poison payloads
- Focus hijacking & sensitive target window paste protection
- Untrusted config payload sanitization
"""

from __future__ import annotations
import os
import re
from typing import Optional, Set
import numpy as np


class SecurityGuard:
    """
    Central validation and protection shield for Whisper Pill Pro.
    """

    # Whitelist of trusted HuggingFace / CTranslate2 model identifiers
    ALLOWED_MODELS: Set[str] = {
        "tiny",
        "base",
        "small",
        "medium",
        "large-v1",
        "large-v2",
        "large-v3",
        "large-v3-turbo",
        "Systran/faster-whisper-tiny",
        "Systran/faster-whisper-small",
        "Systran/faster-whisper-medium",
        "Systran/faster-whisper-large-v3",
        "deepdml/faster-whisper-large-v3-turbo-ct2"
    }

    # Maximum audio recording duration (in seconds) to prevent RAM exhaustion (DoS)
    # 180 seconds @ 16 kHz 32-bit float = ~11.5 MB RAM cap
    MAX_RECORDING_SECONDS: float = 180.0

    # Disallowed processes / window titles where automatic pasting is blocked for safety
    SENSITIVE_TARGET_TITLES: Set[str] = {
        "keepass",
        "1password",
        "bitwarden",
        "uac",
        "credential manager",
        "registry editor",
        "powershell as administrator"
    }

    @classmethod
    def validate_model_identifier(cls, model_name_or_path: str) -> bool:
        """
        Validates model identifier to prevent arbitrary local path traversal.
        Allows official model names or explicitly existing local directories without traversal.
        """
        if not model_name_or_path or not isinstance(model_name_or_path, str):
            return False

        clean_name = model_name_or_path.strip()

        # 1. Exact match on official models
        if clean_name in cls.ALLOWED_MODELS:
            return True

        # 2. Block obvious directory traversal attempts
        if ".." in clean_name or clean_name.startswith("/") or clean_name.startswith("\\"):
            return False

        # 3. If local path, ensure it exists and does not escape expected project directories
        if os.path.exists(clean_name):
            abs_path = os.path.abspath(clean_name)
            # Cannot target sensitive system root
            if abs_path.lower().startswith("c:\\windows") or abs_path.lower().startswith("c:\\program files"):
                return False
            return True

        # HuggingFace repository format: org/repo (alphanumeric, dashes, dots, underscores)
        if re.match(r"^[a-zA-Z0-9_\.-]+/[a-zA-Z0-9_\.-]+$", clean_name):
            return True

        return False

    @classmethod
    def sanitize_audio_buffer(cls, audio_data: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
        """
        Ensures audio buffer is finite, bounded, and within safe memory limits.
        Discards NaN/Inf values and clips audio to MAX_RECORDING_SECONDS.
        """
        if audio_data is None or len(audio_data) == 0:
            return np.array([], dtype=np.float32)

        # 1. NaN and Inf Protection (Poisoned Float Defense)
        if not np.all(np.isfinite(audio_data)):
            audio_data = np.nan_to_num(audio_data, nan=0.0, posinf=1.0, neginf=-1.0)

        # 2. Hard RAM Cap / Duration Limitation
        max_samples = int(cls.MAX_RECORDING_SECONDS * sample_rate)
        if len(audio_data) > max_samples:
            # Retain only up to max_samples
            audio_data = audio_data[:max_samples]

        # 3. Audio Amplitude Clamping (-1.0 to 1.0)
        audio_data = np.clip(audio_data, -1.0, 1.0)

        return audio_data.astype(np.float32)

    @classmethod
    def verify_paste_safety(
        cls,
        target_hwnd: Optional[int],
        current_hwnd: int,
        window_title: str = ""
    ) -> tuple[bool, str]:
        """
        Evaluates whether injecting Ctrl+V is safe.
        Protects against Focus-Hijacking and pasting into sensitive credential vaults.
        """
        # If target window was destroyed
        if target_hwnd is not None and target_hwnd != 0 and current_hwnd != target_hwnd:
            return False, f"Fokus-Verlust abgewehrt: Ziel-Fenster ({target_hwnd}) weicht von aktivem Fenster ({current_hwnd}) ab."

        # Check for blacklisted sensitive targets
        lowered_title = window_title.lower()
        for sensitive in cls.SENSITIVE_TARGET_TITLES:
            if sensitive in lowered_title:
                return False, f"Sicherheits-Blockade: Einfügen in sensibles Fenster ('{window_title}') verweigert."

        return True, "OK"
