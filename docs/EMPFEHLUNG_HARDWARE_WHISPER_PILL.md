# Technisches Empfehlungsschreiben: Hardware-Dimensionierung für lokale Speech-to-Text-Inferenz

**Projekt:** Whisper Pill Pro (Low-Latency Autopaste HUD)  
**Kern-Engine:** `faster-whisper` / `CTranslate2`  
**Referenz-Modell:** `large-v3-turbo` (Tier High, ~800M Parameter, INT8/FP16)  
**Präzisions-Standard:** `beam_size = 5` (Kompromisslose Erkennungsgenauigkeit)  
**Ersteller:** GOT (Good Old Terminal) // System-Orchestrator  
**Datum:** 29. Oktober 2026  

---

## 1. Executive Summary & Problemstellung

Die lokale Spracherkennung mit Whisper Pill Pro nutzt derzeit das Flaggschiff-Modell `large-v3-turbo` mit einem festen Beam-Search-Faktor von `5`. Dieser Beam-Faktor ist für den Produktiveinsatz bei freier, schneller Alltagssprache zwingend erforderlich, um Wortverwechslungen und Verzweigungsfehler (Greedy Search Drifts) auszuschließen.

Auf der aktuellen Mobil-Hardware (Intel Core i5-13500H, 16 logische Threads, DDR5-Dual-Channel) benötigt eine 35-sekündige Sprachaufnahme unter realen thermischen Bedingungen und im Akkubetrieb zwischen **17 und 35 Sekunden Rechenzeit**. 

**Diagnose:**  
Whisper basiert auf einer autoregressiven Transformer-Architektur. Während der Audio-Encoder parallel rechnet, generiert der Decoder Wort für Wort nacheinander. Bei `beam_size = 5` müssen die Modellgewichte (~1,6 GB bei INT8) für jeden einzelnen Schritt mehrfach durch den Speicherbus geschleust werden. **Der Flaschenhals ist nicht die CPU-Rechenleistung (IPC), sondern die Speicherbandbreite (Memory Bandwidth).**

---

## 2. Technische Gewichtungsmatrix für Neuanschaffungen

Für eine spürbare Beschleunigung (Faktor **5x bis 15x schneller**) müssen Neugeräte nach folgender Priorität ausgewählt werden:

| Priorität | Komponente | Mindestanforderung | Empfohlenes Optimum | Technischer Grund |
| :---: | :--- | :--- | :--- | :--- |
| **Prio 1** | **Dedizierte GPU (NVIDIA RTX)** | RTX 4050 Laptop (6 GB VRAM) | **RTX 4060 / 4070 Laptop (8 GB VRAM)** | Bandbreite von **256–500 GB/s**; CTranslate2 nutzt native CUDA FP16/INT8 Tensor Cores. |
| **Prio 2** | **RAM / Speicherbandbreite** | 16 GB DDR5-5200 | **32 GB LPDDR5X (7500–8533 MT/s)** | Bei reiner CPU-Nutzung skaliert die Inferenz direkt proportional zum Speichertakt. |
| **Prio 3** | **CPU-Topologie** | 6 P-Cores | **8 P-Cores / Zen 4/5 (Hoher Single-Core Turbo & großer L3-Cache)** | Autoregressives Decoding benötigt wenige, hoch getaktete Kerne mit schnellem L3-Cache (32 MB+). |
| **Prio 4** | **NPU / AI-Engine** | Keine Priorität | Optional (Zukunftssicherheit) | CTranslate2 läuft derzeit auf CUDA/CPU. NPUs erfordern noch Software-Bridges (ONNX/DirectML). |

---

## 3. Konkrete Hardware-Profile im Vergleich

### Profil A: Das Performance-Optimum (Mobiles Arbeitstier mit dGPU)
*Empfohlene Geräteklasse: Kompakte Creator- oder Gaming-Laptops (z. B. Lenovo Legion Slim, ASUS Zephyrus G14/G16, Dell XPS 14/16 mit RTX)*

* **Grafikkarte:** NVIDIA GeForce RTX 4060 Laptop GPU (8 GB GDDR6)
* **Prozessor:** AMD Ryzen 7 8845HS / AI 9 365 oder Intel Core Ultra 7 155H
* **Arbeitsspeicher:** 32 GB DDR5-5600 oder LPDDR5X
* **Erwartete Inferenzzeit (35s Diktat, Beam 5):** **2,0 bis 3,5 Sekunden** (Echtzeitfaktor **10x bis 15x**)
* **Praxisnutzen:** Die Transkription ist nahezu zeitgleich mit dem Drücken des Stopp-Hotkeys (`F8`) abgeschlossen und per Auto-Paste im Dokument.

---

### Profil B: Das Ultrabook-Profil (Geräuschlos, hohe Akkulaufzeit, ohne dGPU)
*Empfohlene Geräteklasse: Dünne Business-Ultrabooks (z. B. ThinkPad T14s, ASUS Zenbook S 14/16)*

* **Plattform:** **Intel Core Ultra 7 258V (Lunar Lake)** oder **AMD Ryzen AI 9 HX 370**
* **Arbeitsspeicher:** 32 GB verlöteter **LPDDR5X-8533** (Zwingend! On-Package oder Fast Dual-Channel)
* **Erwartete Inferenzzeit (35s Diktat, Beam 5):** **10 bis 14 Sekunden** (Echtzeitfaktor **2,5x bis 3,5x**)
* **Praxisnutzen:** Etwa doppelt so schnell wie der bisherige Laptop-Zustand, lautlos und effizient, erreicht jedoch nicht die Instant-Paste-Geschwindigkeit einer RTX-GPU.

---

## 4. Klare Kaufempfehlung & Richtlinie

1. **Jeder investierte Euro fließt am effizientesten in eine mobile NVIDIA GeForce RTX (ab RTX 4050/4060 mit 6–8 GB VRAM).**  
   Ein Wechsel von einer mobilen CPU zu einer Einstiegs-RTX bringt bei CTranslate2 einen Leistungszuwachs von ca. **800 % bis 1000 %**.
2. **Reine CPU-Upgrades ohne GPU bieten ein schlechtes Preis-Leistungs-Verhältnis für Whisper.**  
   Selbst die modernsten High-End-CPUs (Core Ultra 9 / Ryzen 9) können aufgrund des Flaschenhalses der Dual-Channel-Speicheranbindung im Vergleich zu dediziertem Grafikspeicher (GDDR6) maximal eine Verdopplung der Leistung erzielen.
3. **RAM-Empfehlung:** Unabhängig von der GPU sollten **mindestens 32 GB System-RAM** gewählt werden, um parallele Lasten (IDE, Docker, Browser, Office) ohne Paging-Latenzen neben der KI-Engine zu bewältigen.
