import soundfile as sf
import numpy as np

for name in ["s01.wav", "s04.wav", "s05.wav", "s07.wav"]:
    data, sr = sf.read(f"reels/intro-gokulnath/audio/stems/{name}")
    # find where audio energy actually starts and ends
    energy = np.abs(data)
    thresh = 0.01 * np.max(energy)
    active = np.where(energy > thresh)[0]
    if len(active) > 0:
        start_sec = active[0] / sr
        end_sec = active[-1] / sr
        actual_dur = end_sec - start_sec
        print(f"{name}: total={len(data)/sr:.2f}s, sound active from {start_sec:.2f}s to {end_sec:.2f}s (active duration: {actual_dur:.2f}s)")
    else:
        print(f"{name}: SILENT")
