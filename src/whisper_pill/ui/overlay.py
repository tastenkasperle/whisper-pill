"""
whisper_pill.ui.overlay
-----------------------
Floating Pill GUI window implemented in Tkinter.
Features:
- Catppuccin Mocha aesthetic
- Always-on-top compact HUD
- Smooth sheen light bar animation on ready
- Dynamic witty loading messages
- Robust resource teardown (WM_DELETE_WINDOW protocol)
"""

from __future__ import annotations
import random
import threading
import time
import tkinter as tk
from tkinter import ttk
from typing import Optional
import keyboard

from whisper_pill.core.config import AppConfig
from whisper_pill.core.audio import AudioRecorder
from whisper_pill.core.engine import WhisperEngine
from whisper_pill.core.injector import TextInjector
from whisper_pill.ui.sounds import SoundManager
from whisper_pill.ui.theme import CatppuccinMocha, SHEEN_GRADIENT, SPINNER_FRAMES, apply_pill_theme


class WhisperOverlayApp:
    """
    Main application coordinator and floating window interface.
    """

    def __init__(self, root: tk.Tk, config: AppConfig):
        self.root = root
        self.config = config
        
        # Subsystems
        self.audio = AudioRecorder(sample_rate=16000)
        self.engine = WhisperEngine(config)
        self.sounds = SoundManager(enabled=config.sound_enabled)
        
        # UI State
        self.is_transcribing = False
        self.target_hwnd: Optional[int] = None
        self.current_model_tier = config.default_model_tier
        self.current_model_name = config.model_presets.get(self.current_model_tier, "large-v3-turbo")
        self.hotkey_hook = None
        
        # Animation states
        self.spinner_idx = 0
        self.current_quip = ""
        self.last_quip_time = 0.0

        # Window setup
        self._init_window()
        self._build_widgets()
        self._setup_hotkey()

        # Protocol bindings
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start asynchronous model initialization
        threading.Thread(target=self._async_load_model, args=(self.current_model_name,), daemon=True).start()

    def _init_window(self) -> None:
        self.root.title("Whisper Pill Pro 2.0")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        
        w, h = 380, 130
        x = self.config.window_x if self.config.window_x is not None else (self.root.winfo_screenwidth() - w) // 2
        y = self.config.window_y
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.configure(bg=CatppuccinMocha.BASE)

    def _build_widgets(self) -> None:
        # Top Accent Sheen Bar
        self.light_bar = tk.Frame(self.root, height=3, bg=CatppuccinMocha.BASE)
        self.light_bar.pack(fill="x", side="top")

        # Main Container
        self.main_frame = tk.Frame(self.root, bg=CatppuccinMocha.BASE)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=6)

        # Header Row
        self.top_row = tk.Frame(self.main_frame, bg=CatppuccinMocha.BASE)
        self.top_row.pack(fill="x", pady=(0, 2))

        self.status_label = tk.Label(
            self.top_row,
            text="⏳ Initialisiere Engine...",
            fg=CatppuccinMocha.SUBTEXT1,
            bg=CatppuccinMocha.BASE,
            font=("Segoe UI", 9)
        )
        self.status_label.pack(side="left")

        # Tier Dropdown
        self.model_var = tk.StringVar(value=self.current_model_tier)
        self.model_combo = ttk.Combobox(
            self.top_row,
            textvariable=self.model_var,
            values=list(self.config.model_presets.keys()),
            state="readonly",
            width=12
        )
        self.model_combo.pack(side="right")
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_change)

        # Progress bar
        self.style = ttk.Style()
        apply_pill_theme(self.style)
        
        self.prog_bar = ttk.Progressbar(
            self.main_frame,
            mode="indeterminate",
            style="Pill.Horizontal.TProgressbar",
            length=340
        )
        self.prog_bar.pack(fill="x", pady=(2, 3))
        self.prog_bar.start(12)

        # Primary Action Button
        self.btn = tk.Button(
            self.main_frame,
            text="Bitte warten...",
            command=self.toggle_recording,
            font=("Segoe UI Bold", 10),
            fg=CatppuccinMocha.SUBTEXT0,
            bg=CatppuccinMocha.SURFACE0,
            activebackground=CatppuccinMocha.SURFACE1,
            activeforeground="#FFFFFF",
            relief="groove",
            bd=1,
            cursor="hand2",
            state="disabled"
        )
        self.btn.pack(fill="x", expand=True, pady=3)

        # Footer Row
        self.footer_row = tk.Frame(self.main_frame, bg=CatppuccinMocha.BASE)
        self.footer_row.pack(fill="x", side="bottom")

        self.hint_label = tk.Label(
            self.footer_row,
            text=f"💡 [{self.config.hotkey}] = Start/Stop",
            fg=CatppuccinMocha.OVERLAY0,
            bg=CatppuccinMocha.BASE,
            font=("Segoe UI", 8)
        )
        self.hint_label.pack(side="left")

        self.sound_check_var = tk.BooleanVar(value=self.sounds.enabled)
        self.sound_check = tk.Checkbutton(
            self.footer_row,
            text="🔔 Sound",
            variable=self.sound_check_var,
            command=self.toggle_sound,
            fg=CatppuccinMocha.SUBTEXT1,
            bg=CatppuccinMocha.BASE,
            selectcolor=CatppuccinMocha.SURFACE0,
            activebackground=CatppuccinMocha.BASE,
            activeforeground=CatppuccinMocha.GREEN,
            font=("Segoe UI", 8)
        )
        self.sound_check.pack(side="right")

    def _setup_hotkey(self) -> None:
        try:
            self.hotkey_hook = keyboard.add_hotkey(self.config.hotkey, self._on_hotkey_pressed)
        except Exception as e:
            print(f"[!] Warning: Could not register global hotkey {self.config.hotkey}: {e}")

    def _on_hotkey_pressed(self) -> None:
        self.root.after(0, self.toggle_recording)

    def toggle_sound(self) -> None:
        self.sounds.enabled = self.sound_check_var.get()
        self.config.sound_enabled = self.sounds.enabled

    def on_model_change(self, event=None) -> None:
        val = self.model_var.get()
        new_model = self.config.model_presets.get(val, "large-v3-turbo")
        if new_model != self.current_model_name:
            self.current_model_tier = val
            self.current_model_name = new_model
            self.prog_bar.pack(fill="x", pady=(2, 3), before=self.btn)
            self.prog_bar.start(12)
            self.btn.config(state="disabled", text="Lade Modell...", bg=CatppuccinMocha.SURFACE0, fg=CatppuccinMocha.SUBTEXT0)
            self.status_label.config(text=f"⏳ Wechsle zu {val}...", fg=CatppuccinMocha.PEACH)
            threading.Thread(target=self._async_load_model, args=(new_model,), daemon=True).start()

    def _async_load_model(self, model_name: str) -> None:
        try:
            self.engine.load_model(model_name)
            self.root.after(0, self._on_model_ready)
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Fehler: {e}", fg=CatppuccinMocha.RED))

    def _on_model_ready(self) -> None:
        self.prog_bar.stop()
        self.prog_bar.pack_forget()
        self.status_label.config(text=f"● Bereit ({self.model_var.get()})", fg=CatppuccinMocha.GREEN)
        self.btn.config(text=f"🎙️ Diktieren [{self.config.hotkey}]", bg=CatppuccinMocha.BLUE, fg=CatppuccinMocha.CRUST, state="normal")
        self.flash_sheen()

    def flash_sheen(self) -> None:
        """Visual accent reflection along the top light bar."""
        def _step(idx: int):
            if idx < len(SHEEN_GRADIENT):
                self.light_bar.config(bg=SHEEN_GRADIENT[idx])
                self.root.after(45, _step, idx + 1)
            else:
                self.light_bar.config(bg=CatppuccinMocha.BASE)
        _step(0)
        
        # Subtle emerald pulse on button
        self.btn.config(bg=CatppuccinMocha.GREEN, fg=CatppuccinMocha.CRUST)
        self.root.after(160, lambda: self.btn.config(bg=CatppuccinMocha.BLUE, fg=CatppuccinMocha.CRUST))
        self.sounds.play("ready")

    def toggle_recording(self) -> None:
        if not self.engine.model or self.is_transcribing:
            return

        if not self.audio.is_recording:
            # Capture foreground window handle
            fg = TextInjector.get_foreground_window()
            if fg != self.root.winfo_id():
                self.target_hwnd = fg
            self.start_capture()
        else:
            self.stop_capture_and_process()

    def start_capture(self) -> None:
        self.audio.start()
        self.status_label.config(text=f"🔴 Höre zu... [{self.config.hotkey} Stopp]", fg=CatppuccinMocha.RED)
        self.btn.config(text=f"⏹️ Stoppen & Einfügen [{self.config.hotkey}]", bg=CatppuccinMocha.RED, fg=CatppuccinMocha.CRUST)
        self.sounds.play("start")

    def stop_capture_and_process(self) -> None:
        self.is_transcribing = True
        self.sounds.play("stop")
        
        self.current_quip = random.choice(self.config.quips)
        self.last_quip_time = time.time()
        self.spinner_idx = 0
        self._update_loading_animation()

        audio_data = self.audio.stop()
        threading.Thread(target=self._process_worker, args=(audio_data,), daemon=True).start()

    def _update_loading_animation(self) -> None:
        if not self.is_transcribing:
            return

        now = time.time()
        if now - self.last_quip_time > 1.2:
            self.current_quip = random.choice(self.config.quips)
            self.last_quip_time = now

        spinner = SPINNER_FRAMES[self.spinner_idx % len(SPINNER_FRAMES)]
        self.spinner_idx += 1

        self.status_label.config(text=f"{spinner} Rechnet...", fg=CatppuccinMocha.PEACH)
        self.btn.config(text=f"{self.current_quip}", bg=CatppuccinMocha.PEACH, fg=CatppuccinMocha.CRUST, state="disabled")

        self.root.after(80, self._update_loading_animation)

    def _process_worker(self, audio_data) -> None:
        try:
            res = self.engine.transcribe(audio_data, sample_rate=self.audio.sample_rate)
            if res.text:
                TextInjector.paste_text(res.text, target_hwnd=self.target_hwnd)
                self.sounds.play("success")
                
            self.root.after(0, lambda: self.status_label.config(
                text=f"● Fertig ({res.inference_duration_sec}s / {res.real_time_factor}x)",
                fg=CatppuccinMocha.GREEN
            ))
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Fehler: {e}", fg=CatppuccinMocha.RED))
        finally:
            self.is_transcribing = False
            self.root.after(0, lambda: self.btn.config(
                text=f"🎙️ Diktieren [{self.config.hotkey}]",
                bg=CatppuccinMocha.BLUE,
                fg=CatppuccinMocha.CRUST,
                state="normal"
            ))

    def on_close(self) -> None:
        """Gracefully release all system resources and hooks."""
        # Unhook global keyboard listener
        try:
            if self.hotkey_hook:
                keyboard.remove_hotkey(self.hotkey_hook)
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass

        # Stop audio stream if active
        if self.audio.is_recording:
            self.audio.stop()

        self.root.destroy()
