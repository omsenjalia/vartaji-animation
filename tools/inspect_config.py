import huggingface_hub
import json

path = huggingface_hub.hf_hub_download("tarun7r/vibevoice-hindi-1.5B", "config.json")
with open(path, "r", encoding="utf-8") as f:
    cfg = json.load(f)
print("Keys in config.json:", list(cfg.keys()))
print("Model type:", cfg.get("model_type"))
print("Base model name or path:", cfg.get("_name_or_path"))
