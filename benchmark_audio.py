import time
import os
from faster_whisper import WhisperModel

AUDIO_FILE = r"C:\Users\UserS2025\Downloads\Diana_vorwaerts.wav"

def benchmark_model(model_name, compute_type="int8", cpu_threads=8):
    print(f"\n==========================================")
    print(f"[*] Teste Modell: {model_name} (compute={compute_type}, threads={cpu_threads})")
    print(f"==========================================")
    
    t_load_start = time.time()
    model = WhisperModel(model_name, device="cpu", compute_type=compute_type, cpu_threads=cpu_threads)
    t_load = round(time.time() - t_load_start, 2)
    print(f"[+] Modell geladen in: {t_load}s")
    
    t_trans_start = time.time()
    segments, info = model.transcribe(
        AUDIO_FILE,
        language="de",
        beam_size=1,
        temperature=0.0,
        vad_filter=True,
        initial_prompt="Transkribiere akkurat auf Deutsch mit korrekter Zeichensetzung."
    )
    results = [seg.text.strip() for seg in segments]
    t_trans = round(time.time() - t_trans_start, 2)
    
    full_text = " ".join(results)
    audio_dur = round(info.duration, 2)
    rtf = round(audio_dur / max(t_trans, 0.01), 2)
    
    print(f"[+] Audio-Dauer: {audio_dur}s")
    print(f"[+] Rechenzeit: {t_trans}s ({rtf}x Echtzeit)")
    print(f"[+] Erkannt:\n   \"{full_text}\"")
    return {"model": model_name, "audio_dur": audio_dur, "calc_time": t_trans, "rtf": rtf, "text": full_text}

if __name__ == "__main__":
    if not os.path.exists(AUDIO_FILE):
        print(f"[!] Testdatei nicht gefunden: {AUDIO_FILE}")
        exit(1)
        
    print("[*] Starte automatisierten Benchmark auf Intel i5-13500H...")
    for m in ["small", "medium", "large-v3-turbo"]:
        benchmark_model(m, compute_type="int8", cpu_threads=8)
