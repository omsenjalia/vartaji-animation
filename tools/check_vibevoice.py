from huggingface_hub import hf_hub_download

repo_id = "tarun7r/vibevoice-hindi-1.5B"
readme_path = hf_hub_download(repo_id, "README.md")
with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()
print(readme[1000:3000])
