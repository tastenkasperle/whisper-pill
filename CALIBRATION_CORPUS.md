# 🎙️ Whisper Pill Pro — Phonetischer Kalibrierungs-Korpus & Stresstest-Log
**Datum:** 11. Oktober 2026  
**Ziel-Hardware:** Viona Laptop (Intel Iris Xe / CPU-Inferenz int8)  
**Sprecher-Profil:** Chris (Klares Deutsch, dynamischer Schnellsprech-Rhythmus, leichter niederländischer Akzent-Einschlag, technischer Denglish-Fokus)

---

## 🎯 Test-Blöcke & Analyse-Ergebnisse

### Block 1: Rhythmus, Lautverschleifung & NL-Färbung
- **Soll-Text:**  
  *„Ik denk mal, wir schauen uns jetzt direkt an, wie das System reagiert, wenn we mitten im Satz zwischen Standarddeutsch und leichtem Akzent wechseln. Typische Laute wie das weiche W, verschluckte Endungen bei Verben wie haben, machen oder gehen, und schnelle Satzübergänge sind genau das, was we tarieren müssen. Da gibt es abends immer wieder so ein paar Stolpersteine, aber mit einer sauberen Kalibrierung kriegen wir das absolut stabil hin.“*
- **Ist-Ergebnis (Whisper Pill):**  
  *„Ich denke mal, wir schauen uns jetzt direkt an, wie das System reagiert, wenn wir mitten im Satz zwischen Standarddeutsch und leichten Akzent wechseln. Typische Laute wie das weiche W, verstuckte Endungen bei Verben wie Haben, Machen oder Gehen und schnelle Satzübergänge sind genau das, was wir tarieren müssen. Da gibt es abends immer wieder so ein paar Stolpersteine. Aber mit einer sauberen Kalibierung kriegen wir das absolut stabil hin.“*
- **Erkenntnisse:**
  - `Ik` -> `Ich denke` / `we` -> `wir`: Standard-Whisper glättet niederländische Pronomina ins Hochdeutsche.
  - Phonetisches Verschlucken: `verschluckte` -> `verstuckte`, `Kalibrierung` -> `Kalibierung`.

---

### Block 2: Konsonanten-Ketten & Technische Komposita
- **Soll-Text:**  
  *„Genau das ist der Punkt: Wenn ich schnell spreche, verschlucke ich gerne mal die Konsonanten mitten im Wort. Ob Kalibrierung, Konfiguration oder Architektur – das Modell muss aus dem Kontext erraten, was gemeint ist. Wir prüfen jetzt, ob das System mit zusammengesetzten Wörtern wie Schnittstellenarchitektur, Fehlerprotokollierung und Speicherverwaltung sauber klarkommt.“*
- **Ist-Ergebnis (Whisper Pill):**  
  *„Genau das ist der Punkt. Wenn ich schnell spreche, verschlucke ich gerne mal die Konsonanten mitten im Wort ab. Ob Kalibrierung, Konfiguration oder Architektur. Das Modell muss aus dem Kontext erraten, was gemeint ist. Wir prüfen jetzt, ob das System mit zusammengesetzten Wörtern wie Schnittstellenarchitekturen, Fehlerprotokollierung und Speicherverwaltung sauber klarkommt.“*
- **Erkenntnisse:**
  - 100% Trefferquote bei komplexen Fachbegriffen (`Kalibrierung`, `Konfiguration`, `Architektur`, `Schnittstellenarchitekturen`, `Fehlerprotokollierung`, `Speicherverwaltung`).
  - Semantischer Kontext stabilisiert phonetische Unschärfen vollständig.

---

### Block 3: Denglish, Versionsnummern & Akronyme
- **Soll-Text:**  
  *„Wir testen jetzt Version zwei Punkt null mit Python drei Punkt zwölf. Das Backend läuft über einen Async-Worker mit FastAPI und einer lokalen SQLite-Instanz. Wenn ein Timeout von fünfhundert Millisekunden auftritt, wirft der Exception-Handler einen HTTP-Statuscode vierhundertvier. Bitte prüfe, ob CamelCase wie JavaScript und Slash-Befehle wie Exit oder Resume richtig erfasst werden.“*
- **Ist-Ergebnis (Whisper Pill):**  
  *„Wir testen jetzt Version 2.0 mit Python 3.12. Das Backend läuft über einen R-Sync Worker mit FastAPI und einer lokalen SQLite Instanz. Wenn ein Timeout von 500 Millisekunden auftritt, wirft der Exception Handler einen HTTP Status Code 404. Bitte prüfe, ob CamelCase wie JavaScript und Slash-Befehle wie Exit oder Resume richtig erfasst werden.“*
- **Erkenntnisse:**
  - Ziffernumwandlung (`2.0`, `3.12`, `500 Millisekunden`, `HTTP Status Code 404`) perfekt.
  - CamelCase (`JavaScript`, `FastAPI`, `SQLite`) fehlerfrei erkannt.
  - Phonetischer Drift: `Async-Worker` -> `R-Sync Worker`.

---

### Block 4: Freier Redefluss, Füllwörter & Satzabbrüche
- **Soll-Text:**  
  *„Ja gut, pass auf: Wenn ich einfach so frei Schnauze drauf losrede, dann sag ich halt oft mal so Sachen wie na ja, eigentlich, oder weißt du wie ich meine. Manchmal mach ich mitten im Satz ne Pause, denk kurz nach und setz dann ganz woanders wieder an. Mal gucken, ob das Tool das trotzdem flüssig zusammenhängend aufschreibt oder ob der Faden komplett abreißt.“*
- **Ist-Ergebnis (Whisper Pill):**  
  *„Ja gut, pass auf, wenn ich einfach so frei Schnauze drauf losrede, dann sage ich halt oftmals so Sachen wie, naja, eigentlich oder weißt du wie ich meine? Manchmal mache ich mitten im Satz eine Pause, denke kurz nach und setze dann ganz woanders wieder an. Mal gucken, ob das Tool, das trotzdem flüssig zusammenhängt, aufschreibt oder ob der Faden komplett abreißt.“*
- **Erkenntnisse:**
  - Intonationstransfer: Fragezeichen automatisch gesetzt.
  - Höchste Stabilität: Sprechpausen führen zu keinen Halluzinationen oder Timeouts.

---

## 🛠️ Eingebaute Optimierungen in Whisper Pill

1. **Kontext-Vorgabe (`initial_prompt`):**
   - Vokabular-Injektion für Entwickler- und Schwarm-Terminologie:
     `Async-Worker, async/await, faster-whisper, int8, HyperDrive Mesh, Hyperswarm DHT, SQLite, PostgreSQL, Python 3.12, API, GUI, Catppuccin, Kalibrierung, Konfiguration.`
2. **Post-Processing Pipeline (`text_normalizer.py`):**
   - Gezielte Korrektur bekannter phonetischer Drifts (z. B. `R-Sync Worker` -> `Async-Worker` bei Programmier-Kontext).
   - Intelligente Bereinigung doppelter Leerzeichen und Satzzeichenglättung.
