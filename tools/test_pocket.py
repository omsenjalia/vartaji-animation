import os
import traceback
import scipy.io.wavfile
import numpy as np

print("Testing pocket-tts with saryps-labs/pocket-tts-hindi...", flush=True)

try:
    from pocket_tts import TTSModel
    print("Loading model...", flush=True)
    tts_model = TTSModel.load_model("hf://saryps-labs/pocket-tts-hindi/config.yaml")
    print("Model loaded successfully!", flush=True)

    text = "आधी रात हो चुकी थी। वार्ता अभी चल रही थी।"
    print(f"Generating speech for: {text}...", flush=True)
    
    # Try generating with default voice or voice prompt
    audio = tts_model.generate_audio(text=text)
    
    out_file = "test_pocket_hindi.wav"
    audio_data = audio.numpy() if hasattr(audio, "numpy") else np.array(audio)
    scipy.io.wavfile.write(out_file, tts_model.sample_rate, audio_data)
    print(f"SUCCESS: Saved audio to {out_file} (sample rate: {tts_model.sample_rate})!", flush=True)

except Exception as e:
    print(f"Error: {e}", flush=True)
    traceback.print_exc()
