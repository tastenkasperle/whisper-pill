"""
whisper_pill.core.config
------------------------
Configuration management, model definitions, customizable loading quips,
and persistence for Whisper Pill Pro.
"""

from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List


MODEL_PRESETS: Dict[str, str] = {
    "High": "large-v3-turbo",
    "Medium": "medium",
    "Low": "small",
    "Very Low": "tiny"
}

DEFAULT_QUIPS: List[str] = [
    "🤔 Denke über die Eingabe nach...",
    "🧐 Was redet der eigentlich?!",
    "📚 Gibt es dieses Wort überhaupt?",
    "☕ Dekodiere Gehirnwellen...",
    "🧠 Neuronen feuern auf Hochtouren...",
    "🔍 Suche im Duden nach Ausreden...",
    "🤖 Übersetze menschliches Kauderwelsch...",
    "🧬 Verhandle mit der KI-Logik...",
    "🎧 Entwirre den Satzbau...",
    "🧹 Kehre Sprachbaustellen zusammen...",
    "🧙‍♂️ Wirke Transkriptionszauber...",
    "⏳ Sortiere Kommata und Punkte..."
]


@dataclass
class AppConfig:
    default_model_tier: str = "High"
    hotkey: str = "F8"
    sound_enabled: bool = True
    cpu_threads_override: int | None = None
    language: str = "de"
    beam_size: int = 1
    vad_filter: bool = True
    repetition_penalty: float = 1.15
    no_repeat_ngram_size: int = 3
    initial_prompt: str = "Transkribiere akkurat auf Deutsch mit korrekter Zeichensetzung und Fachbegriffen."
    window_x: int | None = None
    window_y: int = 30
    quips: List[str] = field(default_factory=lambda: list(DEFAULT_QUIPS))
    model_presets: Dict[str, str] = field(default_factory=lambda: dict(MODEL_PRESETS))

    @classmethod
    def load(cls, config_path: str = "config.json") -> AppConfig:
        """Loads configuration from JSON file or falls back to defaults."""
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            except Exception as e:
                print(f"[!] Warning: Could not read config file {config_path}: {e}. Using defaults.")
        return cls()

    def save(self, config_path: str = "config.json") -> None:
        """Persists current configuration to JSON file."""
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.__dict__, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Warning: Could not save config to {config_path}: {e}")
