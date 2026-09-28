"""
whisper_pill.ui.theme
---------------------
Catppuccin Mocha color palette and styling definitions for the Floating Pill UI.
"""

from __future__ import annotations
from tkinter import ttk


class CatppuccinMocha:
    BASE = "#1E1E2E"
    MANTLE = "#181825"
    CRUST = "#11111B"
    SURFACE0 = "#313244"
    SURFACE1 = "#45475A"
    SURFACE2 = "#585B70"
    OVERLAY0 = "#6C7086"
    OVERLAY1 = "#7F849C"
    TEXT = "#CDD6F4"
    SUBTEXT0 = "#A6ADC8"
    SUBTEXT1 = "#BAC2DE"
    
    # Accents
    BLUE = "#89B4FA"
    GREEN = "#A6E3A1"
    TEAL = "#94E2D5"
    PEACH = "#FAB387"
    RED = "#F38BA8"
    MAUVE = "#CBA6F7"


SHEEN_GRADIENT = [
    CatppuccinMocha.GREEN,
    CatppuccinMocha.TEAL,
    CatppuccinMocha.BLUE,
    CatppuccinMocha.MAUVE,
    CatppuccinMocha.BASE
]

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def apply_pill_theme(style: ttk.Style) -> None:
    """Configures ttk styles for progress bars and comboboxes."""
    try:
        style.theme_use("default")
    except Exception:
        pass

    style.configure(
        "Pill.Horizontal.TProgressbar",
        troughcolor=CatppuccinMocha.SURFACE0,
        background=CatppuccinMocha.BLUE,
        bordercolor=CatppuccinMocha.BASE,
        lightcolor=CatppuccinMocha.BLUE,
        darkcolor=CatppuccinMocha.BLUE
    )
