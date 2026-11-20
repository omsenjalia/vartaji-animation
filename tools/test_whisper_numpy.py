import os
import soundfile as sf
from faster_whisper import WhisperModel

try:
    print("Loading faster-whisper tiny model...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    
    # Resample to 16k via ffmpeg
    os.system("ffmpeg -y -v error -i parler_Rohit_Narrator.wav -ar 16000 temp_16k.wav")
    data, sr = sf.read("temp_16k.wav")
    print(f"Read 16k audio: shape={data.shape}, sr={sr}")

    segments, info = model.transcribe(data, language="hi", word_timestamps=True)
    print("Transcription successful:")
    for s in segments:
        print(f"[{s.start:.2f}s - {s.end:.2f}s] {s.text}")
        if s.words:
            for w in s.words:
                print(f"   Word: '{w.word}' [{w.start:.2f}s - {w.end:.2f}s]")
    if os.path.exists("temp_16k.wav"):
        os.remove("temp_16k.wav")
except Exception as e:
    import traceback
    traceback.print_exc()
