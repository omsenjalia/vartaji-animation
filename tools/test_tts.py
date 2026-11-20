import os
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

model_name = "ai4bharat/indic-parler-tts"
hf_token = os.environ.get("HF_TOKEN")

print("Loading model and tokenizers on CUDA...")
model = ParlerTTSForConditionalGeneration.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    token=hf_token
).to("cuda:0")
print("Model loaded onto GPU.")

tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
print("Main tokenizer loaded.")

desc_tok_name = model.config.text_encoder._name_or_path
print("Text encoder path:", desc_tok_name)
desc_tokenizer = AutoTokenizer.from_pretrained(desc_tok_name, token=hf_token)
print("Description tokenizer loaded.")

prompt = "जय श्री कृष्ण"
desc = "An elderly Indian male spiritual speaker delivers a sacred story with a calm, resonant, slow voice. High quality recording."
input_ids = desc_tokenizer(desc, return_tensors="pt").input_ids.to("cuda:0")
prompt_ids = tokenizer(prompt, return_tensors="pt").input_ids.to("cuda:0")

print("Generating test speech...")
with torch.no_grad():
    gen = model.generate(input_ids=input_ids, prompt_input_ids=prompt_ids)

print("Generated audio shape:", gen.shape, "Sample rate:", model.config.sampling_rate)
print("SUCCESS_TTS_VERIFIED")
