import huggingface_hub
try:
    files = huggingface_hub.list_repo_files("vibevoice/VibeVoice-1.5B")
    print("Files in vibevoice/VibeVoice-1.5B:")
    for f in files:
        print(f" - {f}")
except Exception as e:
    print(f"Error checking vibevoice/VibeVoice-1.5B: {e}")
