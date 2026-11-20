import huggingface_hub
import shutil
import os

target_dir = os.path.join("tools", "VibeVoice", "demo", "voices")
os.makedirs(target_dir, exist_ok=True)

for filename in ["hi-Priya_woman.wav", "demo.wav"]:
    print(f"Downloading {filename}...")
    try:
        path = huggingface_hub.hf_hub_download("tarun7r/vibevoice-hindi-1.5B", filename)
        dest = os.path.join(target_dir, filename)
        shutil.copyfile(path, dest)
        print(f"Copied {filename} to {dest}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
