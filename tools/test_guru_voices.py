import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
import time

device = "cuda:0" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

print(f"Loading Indic Parler-TTS on {device}...")
model_id = "ai4bharat/indic-parler-tts"
model = ParlerTTSForConditionalGeneration.from_pretrained(model_id)
model.to(device=device, dtype=dtype)
model.eval()

tokenizer = AutoTokenizer.from_pretrained(model_id)
description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

prompt = "आज मैं कथा का फल कह रहा हूँ। सारा फल वैष्णव की बात में है।"

guru_variants = [
    {
        "name": "Aryan_Sacred",
        "desc": "Aryan speaks with a deep, calm, resonant, and sacred authoritative tone at a slow, deliberate pace. The recording is very clear audio, high quality and close up with no background noise."
    },
    {
        "name": "Kabir_Deep",
        "desc": "Kabir speaks with a deep, resonant, and calm baritone voice at a slow, reverent pace. The recording is very clear audio, high quality and close up with no background noise."
    },
    {
        "name": "Sanjay_Wise",
        "desc": "Sanjay speaks with a mature, calm, and wise tone at a slow pace. The recording is very clear audio, high quality and close up with no background noise."
    }
]

for g in guru_variants:
    print(f"\nTesting {g['name']}...")
    t0 = time.time()
    desc_inputs = description_tokenizer(g["desc"], return_tensors="pt").to(device)
    prompt_inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        generation = model.generate(
            input_ids=desc_inputs.input_ids,
            attention_mask=desc_inputs.attention_mask,
            prompt_input_ids=prompt_inputs.input_ids,
            prompt_attention_mask=prompt_inputs.attention_mask
        )
        
    audio = generation.cpu().to(torch.float32).numpy().squeeze()
    out_wav = f"parler_guru_{g['name']}.wav"
    sf.write(out_wav, audio, model.config.sampling_rate)
    dur = len(audio) / model.config.sampling_rate
    print(f"Generated {out_wav} in {time.time()-t0:.2f}s (duration: {dur:.2f}s)")
