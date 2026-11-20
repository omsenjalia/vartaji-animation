import huggingface_hub

try:
    path = huggingface_hub.hf_hub_download("tarun7r/vibevoice-hindi-1.5B", "README.md")
    with open(path, "r", encoding="utf-8") as f:
        print(f.read())
except Exception as e:
    print(f"Error: {e}")
