"""
Whisper Pill Pro 2.0 - Standalone Application Launcher
------------------------------------------------------
Entrypoint for direct script execution:
    python run.py
"""

from __future__ import annotations
import os
import sys

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from whisper_pill.__main__ import main

if __name__ == "__main__":
    main()
