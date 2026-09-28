"""
Whisper Pill Pro 2.0
--------------------
High-performance local speech-to-text floating HUD for Windows.
"""

__version__ = "2.0.0"
__author__ = "Chris & Got System Orchestration"

from whisper_pill.core.config import AppConfig
from whisper_pill.ui.overlay import WhisperOverlayApp

__all__ = ["AppConfig", "WhisperOverlayApp", "__version__"]
