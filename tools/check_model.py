import huggingface_hub
try:
    files = huggingface_hub.list_repo_files("tarun7r/vibevoice-hindi-1.5B")
    print("Files in tarun7r/vibevoice-hindi-1.5B:")
    for f in files:
        print(f" - {f}")
except Exception as e:
    print(f"Error checking tarun7r/vibevoice-hindi-1.5B: {e}")
