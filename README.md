# 🎙️ Whisper Pill Pro 2.0 (Engine Edition)

[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6.svg?logo=windows)](https://microsoft.com)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python)](https://python.org)
[![Engine: faster--whisper](https://img.shields.io/badge/Engine-faster--whisper%20(CTranslate2)-FF6F00.svg)](https://github.com/SYSTRAN/faster-whisper)
[![Architecture: Modular src/](https://img.shields.io/badge/Architecture-Modular%20Package-94E2D5.svg)](#-software-architektur--paketstruktur)
[![Theme: Catppuccin Mocha](https://img.shields.io/badge/Theme-Catppuccin%20Mocha-F5C2E7.svg)](https://github.com/catppuccin/catppuccin)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

Ein ultra-schnelles, modulares und 100 % lokales **Speech-to-Text Floating-Overlay** für Windows.  
Entwickelt als sauber orchestrierter, privatsphärefreundlicher Ersatz für die unzuverlässige Windows-Diktatfunktion (`Win+H`).

---

## ⚡ Highlights & Engineering-Features

* **🔒 100 % Lokal & Offline:** Keine Telemetrie, keine Cloud-APIs, Zero Disk-I/O. Audio-Samples streamen direkt im flüchtigen RAM (16 kHz float32 NumPy Arrays).
* **🏎️ Automatische CPU-Topologie-Erkennung:** Intelligente Hardware-Heuristik (`core.hardware`) ermittelt die optimale Thread-Allokation für moderne Intel Hybrid-CPUs (z. B. i5-13500H P-Core Binding) sowie AMD Zen Architekturen – **bis zu 3,3x schneller als Standardkonfigurationen**.
* **⌨️ Modernes Win32 `SendInput`:** Kein veraltetes `keybd_event` aus den 90ern. Atomare Ctrl+V Tastatureingabe mit exakter Fensterfokus-Wiederherstellung (`core.injector`).
* **🔔 Taktile Audio-Chimes:** Asynchrone akustische Signale (via nativem `winsound`) beim Start (`F8`), Stopp und erfolgreichen Auto-Paste. Über UI oder Config stummschaltbar.
* **✨ Catppuccin Mocha HUD:** Schwebendes, Always-on-Top Floating-Overlay mit dynamischem Progress-Indicator, Sims-inspirierten Status-Quips und fließendem Smaragd-Lichtsheen bei Einsatzbereitschaft.
* **🎯 4-Stufen Modell-Palette:**
  * **`Very Low` (`tiny`):** 1,1 Sekunden Rechenzeit (~32x Echtzeit) – für instant Einzeiler und Terminal-Prompts.
  * **`Low` (`small`):** 4,8 Sekunden Rechenzeit (~7,3x Echtzeit) – das tägliche Alltags-Arbeitspferd.
  * **`Medium` (`medium`):** 14,1 Sekunden – hohe grammatikalische Ausdauer.
  * **`High` (`large-v3-turbo`):** 15,2 Sekunden – **100 % Wortgenauigkeit**, erkennt Fachbegriffe fehlerfrei.
* **🧹 Sauberes Lifecycle-Management:** Vollständige Entkopplung (`WM_DELETE_WINDOW`), saubere Freigabe globaler Tastatur-Hooks und kein Zombie-Thread-Verhalten.

---

## 📊 Hardware-Benchmark (Intel Core i5-13500H, 35s Audio)

| Stufe | Modell | Inferenz-Dauer | Echtzeit-Faktor | Worterkennung |
| :---: | :--- | :---: | :---: | :--- |
| **`Very Low`** | `tiny` | **1,10s** | **31,7x** | Ideal für Kurzbefehle & Terminal-Prompts |
| **`Low`** | `small` | **4,78s** | **7,3x** | **Alltags-Empfehlung:** Blitzschnell & sauber |
| **`Medium`** | `medium` | **14,14s** | **2,5x** | Sehr präzise Grammatik |
| **`High`** | `large-v3-turbo` | **15,18s** | **2,3x** | **Flaggschiff:** 100 % Genauigkeit bei Fachwörtern |

---

## 🏛️ Software-Architektur & Paketstruktur

Die Codebase folgt strikter **Separation of Concerns (SoC)** nach modernsten Python-Standards:

```text
whisper_overlay/
├── pyproject.toml              # PEP 517/518/621 Build-Konfiguration & CLI-Entrypoint
├── config.example.json         # Konfigurations-Template (Hotkeys, Quips, VAD-Filter)
├── run.py                      # Standalone Direct Launcher
├── start_whisper_pill.bat      # 1-Click Starter
├── update_whisper.bat          # 1-Click Dependency Updater
├── src/
│   └── whisper_pill/
│       ├── __init__.py         # Package Metadata & Versioning (2.0.0)
│       ├── __main__.py         # CLI-Parser & Orchestrator
│       ├── core/
│       │   ├── hardware.py     # CPU-Topologie & P-Core/E-Core Thread-Heuristik
│       │   ├── engine.py       # CTranslate2 WhisperModel Lifecycle & VAD Gating
│       │   ├── audio.py        # Non-blocking RAM Audio Streamer (sounddevice)
│       │   ├── injector.py     # Win32 SendInput (ctypes standard) & Focus Restore
│       │   └── config.py       # Dataclass Configuration & JSON Serializer
│       └── ui/
│           ├── overlay.py      # Tkinter Floating HUD Controller & State-Machine
│           ├── theme.py        # Catppuccin Mocha Farbpalette & Styles
│           └── sounds.py       # Asynchrone Chime-Engine (winsound)
└── tests/
    ├── test_hardware.py        # Topologie-Validierung
    ├── test_injector.py        # Ctypes Struct & SendInput Alignment
    └── test_config.py          # Config Serialization & Fallbacks
```

### Datenfluss

```text
[ Micro / Audio ] ──( 16 kHz Float32 RAM Stream )──> [ Silero VAD Filter ]
                                                              │
                                                              ▼
[ CTranslate2 / int8 ] <──( Topologie-optimierte Threads )── [ faster-whisper ]
        │
        ├──> [ Text Postprocessing & Repetition Guard ]
        └──> [ Pyperclip Clipboard ] ──> [ Win32 SendInput (Ctrl+V) ]
```

---

## 🚀 Installation & Schnellstart

### Voraussetzungen
* Windows 10 oder Windows 11 (Standardnutzer ohne Admin-Rechte ausreichend!)
* Python 3.10 oder neuer

### 1. Klonen & Virtual Environment einrichten
```powershell
git clone https://github.com/username/whisper_overlay.git
cd whisper_overlay
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

### 2. Starten
Entweder direkt per Python oder über den 1-Click-Starter:
```powershell
# Via Script-Launcher:
python run.py

# Oder als CLI-Befehl:
whisper-pill --help

# Oder Doppelklick auf:
start_whisper_pill.bat
```

### 3. Autostart einrichten (Optional)
Erstelle eine Verknüpfung von `start_whisper_pill.bat` in deinem Windows-Autostart-Ordner:  
`Drücke Win+R -> tippe shell:startup -> Verknüpfung ablegen`.

---

## ⚙️ Konfiguration (`config.json`)

Kopiere `config.example.json` zu `config.json`, um Einstellungen dauerhaft anzupassen:

```json
{
    "default_model_tier": "High",
    "hotkey": "F8",
    "sound_enabled": true,
    "cpu_threads_override": null,
    "language": "de",
    "vad_filter": true,
    "repetition_penalty": 1.15
}
```

---

## 🧪 Tests ausführen

Das Repository enthält automatisierte Modultests:

```powershell
.\.venv\Scripts\python.exe tests/test_hardware.py
.\.venv\Scripts\python.exe tests/test_config.py
.\.venv\Scripts\python.exe tests/test_injector.py
```

---

## 🛡️ Datenschutz & Sicherheit

* **Zero Cloud:** Zu keinem Zeitpunkt werden Audiodaten oder Transkripte an externe Server gesendet.
* **In-Memory Buffer:** Sprachdaten verbleiben flüchtig im RAM und werden nach der Verarbeitung sofort freigegeben.
* **Git-Hygiene:** Lokale Audio-Testaufnahmen in `records/*.wav` sind durch `.gitignore` geschützt.

---

## 📜 Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](./LICENSE) lizenziert.
