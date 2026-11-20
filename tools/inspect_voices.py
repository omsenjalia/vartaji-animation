import soundfile as sf
import os

names = ["demo.wav", "hi-Priya_woman.wav", "in-Samuel_man.wav", "en-Frank_man.wav", "en-Carter_man.wav"]
for name in names:
    path = os.path.join("tools", "VibeVoice", "demo", "voices", name)
    if os.path.exists(path):
        try:
            data, sr = sf.read(path)
            print(f"{name}: sr={sr}, channels={data.ndim}, dur={len(data)/sr:.2f}s")
        except Exception as e:
            print(f"{name}: error {e}")
    else:
        print(f"{name}: NOT FOUND")
