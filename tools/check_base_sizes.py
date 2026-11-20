import huggingface_hub

api = huggingface_hub.HfApi()
info = api.model_info("vibevoice/VibeVoice-1.5B", files_metadata=True)
print("Files and sizes in vibevoice/VibeVoice-1.5B:")
total_size = 0
for s in info.siblings:
    size_str = f"{s.size / 1024**2:.2f} MB" if s.size else "unknown"
    if s.size:
        total_size += s.size
    print(f" - {s.rfilename}: {size_str}")
print(f"Total size: {total_size / 1024**3:.2f} GB")
