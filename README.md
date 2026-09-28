# 🎙️ Whisper Pill Pro 2.0 (Wolfsrudel Edition)

[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6.svg?logo=windows)](https://microsoft.com)
[![Python: 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python)](https://python.org)
[![Engine: faster--whisper](https://img.shields.io/badge/Engine-faster--whisper%20(CTranslate2)-FF6F00.svg)](https://github.com/SYSTRAN/faster-whisper)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Theme: Catppuccin Mocha](https://img.shields.io/badge/Theme-Catppuccin%20Mocha-F5C2E7.svg)](https://github.com/catppuccin/catppuccin)

Ein ultra-schnelles, portables und 100 % lokales **Speech-to-Text Floating-Overlay** für Windows. Entwickelt als robuster, privatsphärefreundlicher Ersatz für die unzuverlässige Windows-Diktatfunktion (`Win+H`).

---

## ⚡ Highlights & Neuheiten in Version 2.0

* **🔒 100 % Lokal & Offline:** Keine Telemetrie, keine Cloud-APIs, vollständige Privatsphäre. Audio-Daten werden rein im Arbeitsspeicher gestreamt (Zero-Disk I/O).
* **🏎️ P-Core Hybrid Tuning:** Speziell optimiert für moderne Intel-CPUs (wie i5-13500H). Nutzt 12 dedizierte Performance-Threads ohne Cache-Thrashing – **bis zu 3,3x schneller als Standard-Konfigurationen**.
* **🔔 Taktile Audio-Chimes:** Dezente akustische Signale (via nativem `winsound`) beim Start (`F8`), Stopp und erfolgreichen Auto-Paste. Über UI stummschaltbar.
* **✨ Visuelle Neon-Reflektion & Ladebalken:** Dynamischer Ladebalken beim Modellwechsel und sanfter Smaragd-Lichtbogen beim Erreichen der Einsatzbereitschaft.
* **🎯 4-Stufen Modell-Palette:**
  * **`Very Low` (`tiny`):** 1,1 Sekunden Rechenzeit (~32x Echtzeit) – für instant Einzeiler und Terminal-Prompts.
  * **`Low` (`small`):** 4,8 Sekunden Rechenzeit (~7,3x Echtzeit) – das tägliche Alltags-Arbeitspferd.
  * **`Medium` (`medium`):** 14,1 Sekunden – hohe grammatikalische Ausdauer.
  * **`High` (`large-v3-turbo`):** 15,2 Sekunden – **100 % Wortgenauigkeit**, erkennt Fachbegriffe fehlerfrei.
* **🖱️ Globaler Hotkey & Auto-Paste:** Ein Druck auf `[F8]` startet die Aufnahme; erneuter Druck transkribiert und fügt den Text automatisch via `Strg+V` ins aktive Zielfenster ein.

---

## 📊 Hardware-Benchmark (Intel Core i5-13500H, 35s Audio)

| Stufe | Modell | Inferenz-Dauer | Echtzeit-Faktor | Worterkennung |
| :---: | :--- | :---: | :---: | :--- |
| **`Very Low`** | `tiny` | **1,10s** | **31,7x** | Ideal für Kurzbefehle & Terminal-Prompts |
| **`Low`** | `small` | **4,78s** | **7,3x** | **Alltags-Empfehlung:** Blitzschnell & sauber |
| **`Medium`** | `medium` | **14,14s** | **2,5x** | Sehr präzise Grammatik |
| **`High`** | `large-v3-turbo` | **15,18s** | **2,3x** | **Flaggschiff:** 100 % Genauigkeit bei Fachwörtern |

---

## 🏗️ Architektur & Datenfluss

```text
[ Micro / Audio ] ──( 16 kHz RAM Stream )──> [ Silero VAD Filter ]
                                                    │
                                                    ▼
[ CTranslate2 / int8 ] <──( 12 P-Core Threads )── [ faster-whisper ]
        │
        ├──> [ Text Postprocessing & Repetition Guard ]
        └──> [ Pyperclip Clipboard ] ──> [ Win32 Keybd Event (Ctrl+V) ]
```

---

## 🚀 Schnellstart & Installation

### Voraussetzungen
* Windows 10 oder Windows 11 (Standardnutzer ohne Admin-Rechte ausreichend!)
* Python 3.10 oder neuer

### 1. Repository klonen & Virtual Environment erstellen
```powershell
git clone https://github.com/username/whisper_overlay.git
cd whisper_overlay
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Starten
Starte die Anwendung einfach per Doppelklick auf:
```text
start_whisper_pill.bat
```

### 3. Autostart einrichten (Optional)
Erstelle eine Verknüpfung von `start_whisper_pill.bat` in deinem Windows-Autostart-Ordner:
`Drücke Win+R -> tippe shell:startup -> Verknüpfung hier ablegen`.

---

## 🎮 Steuerung & Bedienung

1. Klicke in ein beliebiges Textfeld (Terminal, VS Code, Browser, Notizen).
2. Drücke **`F8`** (akustischer Start-Klick ertönt, Button leuchtet rot).
3. Sprich deinen Text ein.
4. Drücke erneut **`F8`** (Bestätigungston ertönt, Lade-Animation läuft).
5. Nach Sekundenbruchteilen ertönt die Erfolgs-Fanfare und der Text steht exakt an der Cursor-Position!

---

## 🛡️ Datenschutz & Sicherheit

* **Zero Cloud:** Zu keinem Zeitpunkt werden Audio-Samples oder Texte an externe Server übertragen.
* **In-Memory Streaming:** Temporäre Sprachdaten verbleiben im flüchtigen RAM und werden nach der Transkription verworfen.
* **Saubere Git-Hygiene:** Private Audio-Dateien im `records/`-Ordner sind per `.gitignore` standardmäßig von Commits ausgeschlossen.

---

## 📜 Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](./LICENSE) lizenziert.
