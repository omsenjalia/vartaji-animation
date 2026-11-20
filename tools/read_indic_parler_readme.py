import os
import huggingface_hub

token = os.environ.get("HF_TOKEN")
try:
    readme_path = huggingface_hub.hf_hub_download("ai4bharat/indic-parler-tts", "README.md", token=token)
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    print("--- Indic-Parler-TTS README ---")
    print(content[:3000])
    
    # Save full README to inspect
    with open("tools/indic_parler_readme.md", "w", encoding="utf-8") as out:
        out.write(content)
    print("\nFull README saved to tools/indic_parler_readme.md")
except Exception as e:
    print(f"Error reading README: {e}")
