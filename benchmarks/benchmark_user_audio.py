import time
import os
from faster_whisper import WhisperModel

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_FILE = os.path.join(PROJECT_ROOT, "records", "aufnahme_20260926_121311.wav")

def benchmark_model(model_name, compute_type="int8", cpu_threads=8):
    print(f"\n" + "="*60)
    print(f"[*] Benchmark: {model_name} (compute={compute_type}, threads={cpu_threads})")
    print("="*60)
    
    t_load_start = time.time()
    model = WhisperModel(model_name, device="cpu", compute_type=compute_type, cpu_threads=cpu_threads)
    t_load = round(time.time() - t_load_start, 2)
    print(f"[+] Modell geladen: {t_load}s")
    
    t_trans_start = time.time()
    segments, info = model.transcribe(
        AUDIO_FILE,
        language="de",
        beam_size=1,
        temperature=0.0,
        vad_filter=True,
        repetition_penalty=1.15,
        no_repeat_ngram_size=3,
        initial_prompt="Transkribiere akkurat auf Deutsch mit korrekter Zeichensetzung und Fachbegriffen."
    )
    results = [seg.text.strip() for seg in segments]
    t_trans = round(time.time() - t_trans_start, 2)
    
    full_text = " ".join(results)
    audio_dur = round(info.duration, 2)
    rtf = round(audio_dur / max(t_trans, 0.01), 2)
    
    print(f"[+] Audio-Länge:   {audio_dur}s")
    print(f"[+] Rechenzeit:    {t_trans}s ({rtf}x Echtzeit)")
    print(f"[+] Ergebnis:\n\n\"{full_text}\"\n")
    return {"model": model_name, "audio_dur": audio_dur, "calc_time": t_trans, "rtf": rtf, "text": full_text}

if __name__ == "__main__":
    print(f"[*] Starte Hardware-Benchmark mit: {AUDIO_FILE}")
    for m in ["small", "medium", "large-v3-turbo"]:
        benchmark_model(m, compute_type="int8", cpu_threads=8)
