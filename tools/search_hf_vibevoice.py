import huggingface_hub

api = huggingface_hub.HfApi()
models = api.list_models(search="vibevoice hindi")
print("Found models for 'vibevoice hindi':")
for m in models:
    print(f" - {m.id} (downloads: {m.downloads}, likes: {m.likes})")

models2 = api.list_models(search="vibevoice")
print("\nTop models for 'vibevoice':")
for m in sorted(models2, key=lambda x: x.downloads or 0, reverse=True)[:10]:
    print(f" - {m.id} (downloads: {m.downloads}, likes: {m.likes})")
