import csv
from pathlib import Path
import numpy as np
import sounddevice as sd
import soundfile as sf

sample_rate = 16000
here = Path(__file__).parent
data = here / "data"
data.mkdir(exist_ok=True)
manifest = data / "manifest.csv"

phrases = [
    line.strip()
    for line in (here / "phrases.txt").read_text(encoding="utf-8").splitlines()
    if line.strip()
]

# Resume support: load what is already recorded.
rows = []
if manifest.exists():
    with open(manifest, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
recorded = {r["file"] for r in rows}


def record() -> np.ndarray:
    """Record from the mic until the user presses Enter."""
    chunks = []

    def callback(indata, frames, time_info, status):
        chunks.append(indata.copy())

    with sd.InputStream(samplerate=sample_rate, channels=1,
                        dtype="float32", callback=callback):
        input("   Recording... speak, then press Enter to stop")
    return np.concatenate(chunks)[:, 0] if chunks else np.zeros(0, dtype="float32")


for i, phrase in enumerate(phrases, start=1):
    name = f"{i:03d}.wav"
    if name in recorded:
        continue
    while True:
        print(f"\n[{i}/{len(phrases)}]  {phrase}")
        input("   Press Enter to start (Ctrl+C to quit, you can resume later)")
        audio = record()
        sf.write(data / name, audio, sample_rate)
        print(f"   saved {len(audio) / sample_rate:.1f} s")
        if input("   Enter = keep, r = redo: ").strip().lower() != "r":
            break
    rows.append({"file": name, "reference": phrase})
    with open(manifest, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "reference"])
        writer.writeheader()
        writer.writerows(rows)

print("\nDone. Files are in", data)