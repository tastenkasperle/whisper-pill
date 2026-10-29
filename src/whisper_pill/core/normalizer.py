"""
whisper_pill.core.normalizer
-----------------------------
Post-processing and phonetic error correction pipeline.
Tuned for Chris' speech rhythm, dialectical nuances, and developer terminology.
"""

from __future__ import annotations
import re
from typing import Dict, Pattern


# Phonetische und kontextuelle Mapping-Regeln
PHONETIC_REPLACEMENTS: Dict[str, str] = {
    # Block 3 Drift: "R-Sync Worker" / "R-Sync-Worker" -> "Async-Worker"
    r"\b[rR]-[sS]ync[-\s]+[wW]orker\b": "Async-Worker",
    # Whisper Training-Artifact Hallucinations (YouTube / TV Subtitle Scrapes)
    r"\bUntertitelung\s+(?:des\s+)?(?:ZDF|ARD|WDR|NDR|MDR|SWR|BR|hr|rbb|ORF|SRF)(?:[,\s\d]+)?\b": "",
    r"\bUntertitel\s+(?:von\s+|im\s+Auftrag\s+des\s+)?(?:ZDF|ARD|WDR|Funk)(?:[,\s\d]+)?\b": "",
    r"\bUntertitelung(?:\s+durch)?\s+[\w\s]+(?:20\d\d)?\b": "",
    r"\bVielen\s+Dank\s+für[s']?\s+(?:Zuhören|Zuschauen)[.!]?\b": "",
    # Block 1 Drifts & Typo-Prävention
    r"\bverstuckte(?:\s+Endungen)?\b": "verschluckte Endungen",
    r"\bKalibierung\b": "Kalibrierung",
    r"\bkalibieren\b": "kalibrieren",
    r"\bFasterWhisper\s+8\b": "faster-whisper int8",
    r"\bfaster-whisper\s+8\b": "faster-whisper int8",
}

# Vorkompilierte Regex-Patterns für Null-Latenz-Ausführung
_COMPILED_RULES = [(re.compile(pattern, re.IGNORECASE), replacement) for pattern, replacement in PHONETIC_REPLACEMENTS.items()]


class TextNormalizer:
    """
    Cleans, normalizes, and applies phonetic tuning rules to raw transcriptions.
    """

    @classmethod
    def normalize(cls, text: str) -> str:
        if not text:
            return ""

        result = text.strip()

        # 1. Phonetic Correction Patterns
        for pattern, replacement in _COMPILED_RULES:
            result = pattern.sub(replacement, result)

        # 2. Glättung von doppelten Satzzeichen oder Leerzeichen vor Satzzeichen
        result = re.sub(r"\s+([,.:;?!])", r"\1", result)
        result = re.sub(r"\s{2,}", " ", result)

        # 3. Entferne verwaiste Satzzeichen am Satzanfang (z.B. führendes Komma durch Sprachpausen)
        result = re.sub(r"^[,\s.:;?!]+", "", result)

        return result.strip()
