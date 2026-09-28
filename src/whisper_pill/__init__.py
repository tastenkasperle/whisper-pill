"""
Whisper Pill Pro 2.1 (Hardened Edition)
--------------------------------------
High-performance local speech-to-text floating HUD for Windows.
"""

__version__ = "2.1.0"
__author__ = "Christopher Hailfinger (@tastenkasperle) & GOT System Orchestration"

from whisper_pill.core.config import AppConfig
from whisper_pill.ui.overlay import WhisperOverlayApp

__all__ = ["AppConfig", "WhisperOverlayApp", "__version__"]
