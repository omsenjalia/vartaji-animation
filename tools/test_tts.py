import os
import sys
import traceback
import torch
import soundfile as sf
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

model_name = "ai4bharat/indic-parler-tts"
hf_token = os.environ.get("HF_TOKEN")

print("--- Testing Indic-Parler-TTS on CPU ---", flush=True)

device = "cpu"
dtype = torch.float32
print(f"Using device: {device}, dtype: {dtype}", flush=True)

try:
    print("Loading model...", flush=True)
    model = ParlerTTSForConditionalGeneration.from_pretrained(
        model_name,
        torch_dtype=dtype,
        token=hf_token
    ).to(device)
    print("Model loaded successfully.", flush=True)

    print("Loading tokenizers...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
    desc_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path, token=hf_token)
    print("Tokenizers loaded successfully.", flush=True)

    prompt = "जय श्री कृष्ण। आधी रात हो चुकी थी।"
    description = "A male speaker delivers a spiritual discourse with a calm, deep, clear and slow voice in high quality."

    print("Tokenizing prompt and description...", flush=True)
    desc_inputs = desc_tokenizer(description, return_tensors="pt")
    prompt_inputs = tokenizer(prompt, return_tensors="pt")

    input_ids = desc_inputs.input_ids.to(device)
    attention_mask = desc_inputs.attention_mask.to(device)

    prompt_input_ids = prompt_inputs.input_ids.to(device)
    prompt_attention_mask = prompt_inputs.attention_mask.to(device)

    print(f"Prompt tokens: {prompt_input_ids.shape}, Desc tokens: {input_ids.shape}", flush=True)
    print("Generating speech audio...", flush=True)

    with torch.no_grad():
        generation = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            prompt_input_ids=prompt_input_ids,
            prompt_attention_mask=prompt_attention_mask
        )

    print(f"Generated output tensor shape: {generation.shape}", flush=True)
    audio_arr = generation.cpu().numpy().squeeze().astype("float32")
    sample_rate = model.config.sampling_rate

    out_file = "test_indic_tts.wav"
    sf.write(out_file, audio_arr, sample_rate)
    print(f"SUCCESS: Audio saved to {out_file} (duration: {len(audio_arr)/sample_rate:.2f}s, {sample_rate} Hz)!", flush=True)

except Exception as e:
    print(f"ERROR OCCURRED: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)
