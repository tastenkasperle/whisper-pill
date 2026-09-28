import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import winsound
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
import pyperclip
import ctypes
import os
import keyboard

user32 = ctypes.windll.user32

# Sims-Style / Witty Loading Phrases
QUIP_LIST = [
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

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

def play_sound_async(sound_type):
    """Play subtle acoustic chimes without blocking audio or UI."""
    def _play():
        try:
            if sound_type == "start":
                winsound.Beep(880, 70)  # A5 (70ms)
            elif sound_type == "stop":
                winsound.Beep(587, 70)  # D5 (70ms)
            elif sound_type == "success":
                winsound.Beep(1046, 50) # C6 (50ms)
                time.sleep(0.02)
                winsound.Beep(1318, 80) # E6 (80ms)
            elif sound_type == "ready":
                winsound.Beep(1175, 40) # D6 (40ms)
                time.sleep(0.02)
                winsound.Beep(1568, 60) # G6 (60ms)
        except Exception:
            pass
    threading.Thread(target=_play, daemon=True).start()

def send_paste_raw():
    """Simulate Ctrl+V directly to active focused application."""
    VK_CONTROL = 0x11
    VK_V = 0x56
    KEYEVENTF_KEYUP = 0x0002
    
    time.sleep(0.06)
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_V, 0, 0, 0)
    time.sleep(0.03)
    user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

class WhisperOverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Pill Pro 2.0 (Wolfsrudel Edition)")
        
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        
        # Geometry
        w, h = 380, 130
        x = (self.root.winfo_screenwidth() - w) // 2
        y = 30
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.configure(bg="#1E1E2E")

        # Audio / Whisper state
        self.is_recording = False
        self.is_transcribing = False
        self.audio_frames = []
        self.sample_rate = 16000
        self.stream = None
        self.target_hwnd = None
        self.sound_enabled = True
        
        # Animation & Quip state
        self.spinner_idx = 0
        self.current_quip = ""
        self.last_quip_time = 0
        
        # Optimized Hybrid CPU config (Intel i5-13500H: 6 P-Cores / 12 Threads)
        total_cpus = os.cpu_count() or 4
        self.cpu_threads = min(12, total_cpus) if total_cpus >= 12 else total_cpus
        
        self.model = None
        self.current_model_name = "large-v3-turbo"

        # Top Accent Light Bar (Visual flash / light reflection on ready)
        self.light_bar = tk.Frame(root, height=3, bg="#1E1E2E")
        self.light_bar.pack(fill="x", side="top")

        # UI Components
        self.main_frame = tk.Frame(root, bg="#1E1E2E")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=6)
        
        # Header Row: Status & Sound Toggle
        self.top_row = tk.Frame(self.main_frame, bg="#1E1E2E")
        self.top_row.pack(fill="x", pady=(0, 2))

        self.status_label = tk.Label(
            self.top_row,
            text="⏳ Lade Modell...",
            fg="#BAC2DE",
            bg="#1E1E2E",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(side="left")

        # Dropdown for Model Switch (Very Low, Low, Medium, High)
        self.model_map = {
            "High": "large-v3-turbo",
            "Medium": "medium",
            "Low": "small",
            "Very Low": "tiny"
        }
        self.model_var = tk.StringVar(value="High")
        self.model_combo = ttk.Combobox(
            self.top_row,
            textvariable=self.model_var,
            values=list(self.model_map.keys()),
            state="readonly",
            width=12
        )
        self.model_combo.pack(side="right")
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_change)

        # Styled Indeterminate Progress Bar for Model Loading
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure(
            "Pill.Horizontal.TProgressbar",
            troughcolor='#313244',
            background='#89B4FA',
            bordercolor='#1E1E2E',
            lightcolor='#89B4FA',
            darkcolor='#89B4FA'
        )
        self.prog_bar = ttk.Progressbar(
            self.main_frame,
            mode="indeterminate",
            style="Pill.Horizontal.TProgressbar",
            length=340
        )
        self.prog_bar.pack(fill="x", pady=(2, 3))
        self.prog_bar.start(12)

        # Big Action Button
        self.btn = tk.Button(
            self.main_frame,
            text="Bitte warten...",
            command=self.toggle_recording,
            font=("Segoe UI Bold", 10),
            fg="#A6ADC8",
            bg="#313244",
            activebackground="#45475A",
            activeforeground="#FFFFFF",
            relief="groove",
            bd=1,
            cursor="hand2",
            state="disabled"
        )
        self.btn.pack(fill="x", expand=True, pady=3)

        # Footer Row: Hint & Sound Toggle Checkbox
        self.footer_row = tk.Frame(self.main_frame, bg="#1E1E2E")
        self.footer_row.pack(fill="x", side="bottom")

        self.hint_label = tk.Label(
            self.footer_row,
            text="💡 [F8] = Start/Stop",
            fg="#6C7086",
            bg="#1E1E2E",
            font=("Segoe UI", 8)
        )
        self.hint_label.pack(side="left")

        self.sound_check_var = tk.BooleanVar(value=True)
        self.sound_check = tk.Checkbutton(
            self.footer_row,
            text="🔔 Sound",
            variable=self.sound_check_var,
            command=self.toggle_sound,
            fg="#BAC2DE",
            bg="#1E1E2E",
            selectcolor="#313244",
            activebackground="#1E1E2E",
            activeforeground="#A6E3A1",
            font=("Segoe UI", 8)
        )
        self.sound_check.pack(side="right")

        # Global Hotkey (F8)
        try:
            keyboard.add_hotkey("F8", self.on_hotkey_pressed)
        except Exception as e:
            print(f"[!] Hotkey error: {e}")

        # Async Model Initialization
        threading.Thread(target=self.load_model, args=(self.current_model_name,), daemon=True).start()

    def toggle_sound(self):
        self.sound_enabled = self.sound_check_var.get()

    def on_hotkey_pressed(self):
        self.root.after(0, self.toggle_recording)

    def on_model_change(self, event):
        val = self.model_var.get()
        new_model = self.model_map.get(val, "large-v3-turbo")
        if new_model != self.current_model_name:
            self.current_model_name = new_model
            self.prog_bar.pack(fill="x", pady=(2, 3), before=self.btn)
            self.prog_bar.start(12)
            self.btn.config(state="disabled", text="Lade Modell...", bg="#313244", fg="#A6ADC8")
            self.status_label.config(text=f"⏳ Wechsle zu {val}...", fg="#FAB387")
            threading.Thread(target=self.load_model, args=(new_model,), daemon=True).start()

    def load_model(self, model_name):
        try:
            print(f"[*] Initialisiere Whisper ({model_name}) mit {self.cpu_threads} CPU-Threads (1 Worker)...")
            self.model = WhisperModel(
                model_name,
                device="cpu",
                compute_type="int8",
                cpu_threads=self.cpu_threads,
                num_workers=1
            )
            print(f"[+] Model {model_name} optimiert geladen!")
            self.root.after(0, self.on_model_ready)
        except Exception as e:
            print(f"[!] Model error: {e}")
            self.root.after(0, lambda: self.status_label.config(text=f"Fehler: {e}", fg="#F38BA8"))

    def on_model_ready(self):
        self.prog_bar.stop()
        self.prog_bar.pack_forget()
        self.status_label.config(text=f"● Bereit ({self.model_var.get()})", fg="#A6E3A1")
        self.btn.config(text="🎙️ Diktieren [F8]", bg="#89B4FA", fg="#11111B", state="normal")
        self.flash_ready()

    def flash_ready(self):
        """Neon sheen reflection across top light bar and subtle button glow."""
        sheen_colors = ["#A6E3A1", "#94E2D5", "#89B4FA", "#CBA6F7", "#1E1E2E"]
        def _step(idx):
            if idx < len(sheen_colors):
                self.light_bar.config(bg=sheen_colors[idx])
                self.root.after(50, _step, idx + 1)
            else:
                self.light_bar.config(bg="#1E1E2E")
        _step(0)
        
        # Emerald glow pulse on button
        self.btn.config(bg="#A6E3A1", fg="#11111B")
        self.root.after(160, lambda: self.btn.config(bg="#89B4FA", fg="#11111B"))
        
        if self.sound_enabled:
            play_sound_async("ready")

    def toggle_recording(self):
        if not self.model or self.is_transcribing:
            return

        if not self.is_recording:
            fg = user32.GetForegroundWindow()
            if fg != self.root.winfo_id():
                self.target_hwnd = fg
            self.start_audio()
        else:
            self.stop_audio_and_transcribe()

    def audio_callback(self, indata, frames, time_info, status):
        self.audio_frames.append(indata.copy())

    def start_audio(self):
        self.is_recording = True
        self.audio_frames = []
        self.status_label.config(text="🔴 Höre zu... [F8 Stopp]", fg="#F38BA8")
        self.btn.config(text="⏹️ Stoppen & Einfügen [F8]", bg="#F38BA8", fg="#11111B")
        
        if self.sound_enabled:
            play_sound_async("start")
            
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self.audio_callback
        )
        self.stream.start()

    def stop_audio_and_transcribe(self):
        self.is_recording = False
        self.is_transcribing = True
        
        if self.sound_enabled:
            play_sound_async("stop")
            
        self.current_quip = random.choice(QUIP_LIST)
        self.last_quip_time = time.time()
        self.spinner_idx = 0
        
        self.update_loading_animation()

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        threading.Thread(target=self.process_transcription, daemon=True).start()

    def update_loading_animation(self):
        if not self.is_transcribing:
            return

        now = time.time()
        if now - self.last_quip_time > 1.2:
            self.current_quip = random.choice(QUIP_LIST)
            self.last_quip_time = now

        spinner = SPINNER_FRAMES[self.spinner_idx % len(SPINNER_FRAMES)]
        self.spinner_idx += 1

        self.status_label.config(text=f"{spinner} Rechnet...", fg="#FAB387")
        self.btn.config(text=f"{self.current_quip}", bg="#FAB387", fg="#11111B", state="disabled")

        self.root.after(80, self.update_loading_animation)

    def process_transcription(self):
        t0 = time.time()
        try:
            if not self.audio_frames:
                self.is_transcribing = False
                self.root.after(0, self.on_model_ready)
                return

            audio_data = np.concatenate(self.audio_frames, axis=0).flatten()
            duration_sec = round(len(audio_data) / self.sample_rate, 1)
            
            # --- OPTIMIZED SINGLE-PASS BATCH INFERENCE ---
            segments, info = self.model.transcribe(
                audio_data,
                language="de",
                beam_size=1,
                temperature=0.0,
                vad_filter=True,
                repetition_penalty=1.15,
                no_repeat_ngram_size=3,
                initial_prompt="Transkribiere akkurat auf Deutsch mit korrekter Zeichensetzung und Fachbegriffen."
            )
            text = " ".join([seg.text.strip() for seg in segments]).strip()
            calc_time = round(time.time() - t0, 2)
            rtf = round(duration_sec / max(calc_time, 0.01), 1)
            print(f"[+] {duration_sec}s Audio in {calc_time}s transkribiert ({self.current_model_name}, {rtf}x): {text}")

            if text:
                pyperclip.copy(text)

                if self.target_hwnd and user32.IsWindow(self.target_hwnd):
                    user32.SetForegroundWindow(self.target_hwnd)
                
                send_paste_raw()
                
                if self.sound_enabled:
                    play_sound_async("success")
                    
            self.root.after(0, lambda: self.status_label.config(
                text=f"● Fertig ({calc_time}s / {rtf}x)", fg="#A6E3A1"
            ))
            
        except Exception as e:
            print(f"[!] Transkriptions-Fehler: {e}")
            self.root.after(0, lambda: self.status_label.config(text=f"Fehler: {e}", fg="#F38BA8"))
        finally:
            self.is_transcribing = False
            self.root.after(0, lambda: self.btn.config(text="🎙️ Diktieren [F8]", bg="#89B4FA", fg="#11111B", state="normal"))

if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperOverlayApp(root)
    root.mainloop()
