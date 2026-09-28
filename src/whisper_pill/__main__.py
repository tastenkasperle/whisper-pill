"""
Main application entry point for Whisper Pill Pro.
Usage:
    python -m whisper_pill
    whisper-pill
"""

from __future__ import annotations
import argparse
import sys
import tkinter as tk

from whisper_pill.core.config import AppConfig
from whisper_pill.core.hardware import detect_optimal_hardware
from whisper_pill.ui.overlay import WhisperOverlayApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Whisper Pill Pro 2.0 - Fast Local STT HUD")
    parser.add_argument("--config", "-c", default="config.json", help="Path to custom config.json")
    parser.add_argument("--threads", "-t", type=int, default=None, help="Override CPU inference threads")
    parser.add_argument("--model", "-m", choices=["Very Low", "Low", "Medium", "High"], default=None, help="Initial model tier")
    parser.add_argument("--no-sound", action="store_true", help="Disable acoustic chime feedback")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = AppConfig.load(args.config)

    if args.threads is not None:
        config.cpu_threads_override = args.threads
    if args.model is not None:
        config.default_model_tier = args.model
    if args.no_sound:
        config.sound_enabled = False

    hw = detect_optimal_hardware()
    print("=" * 60)
    print("🎙️  Whisper Pill Pro 2.0 (Modular Engine Edition)")
    print(f"💻 CPU: {hw.cpu_architecture}")
    print(f"⚙️  Topology: {hw.description}")
    print(f"⚡ Allocated Threads: {config.cpu_threads_override or hw.optimal_threads}")
    print(f"🎯 Default Model Tier: {config.default_model_tier}")
    print("=" * 60)

    root = tk.Tk()
    app = WhisperOverlayApp(root, config)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.on_close()
        sys.exit(0)


if __name__ == "__main__":
    main()
