import os
import time
import torch
from vibevoice.modular.modeling_vibevoice_inference import VibeVoiceForConditionalGenerationInference
from vibevoice.processor.vibevoice_processor import VibeVoiceProcessor

model_id = "tarun7r/vibevoice-hindi-1.5B"
print(f"Loading processor from {model_id}...")
processor = VibeVoiceProcessor.from_pretrained(
    model_id,
    language_model_pretrained_name="Qwen/Qwen2.5-1.5B"
)

print("Loading model on cuda (bfloat16)...")
model = VibeVoiceForConditionalGenerationInference.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="cuda",
    attn_implementation="sdpa"
)
model.eval()
model.set_ddpm_inference_steps(num_steps=10)

voice_sample = "tools/VibeVoice/demo/voices/hi-Priya_woman.wav"
if not os.path.exists(voice_sample):
    print(f"Voice sample {voice_sample} not found!")

text = "Speaker 1: श्री गोकुलनाथजी की असीम कृपा से, आज हम पुष्टिमार्ग के महान भगवदीयों की वार्ताएं शुरू कर रहे हैं।"

print("Preparing inputs...")
inputs = processor(
    text=[text],
    voice_samples=[[voice_sample]],
    padding=True,
    return_tensors="pt",
    return_attention_mask=True
)

for k, v in inputs.items():
    if torch.is_tensor(v):
        inputs[k] = v.to("cuda")

print("Generating audio...")
t0 = time.time()
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=None,
        cfg_scale=1.3,
        tokenizer=processor.tokenizer,
        generation_config={'do_sample': False},
        verbose=True,
        is_prefill=True
    )
gen_time = time.time() - t0
print(f"Generation finished in {gen_time:.2f}s")

out_wav = "output_test_hindi.wav"
if outputs.speech_outputs and outputs.speech_outputs[0] is not None:
    processor.save_audio(
        outputs.speech_outputs[0],
        output_path=out_wav
    )
    duration = outputs.speech_outputs[0].shape[-1] / 24000
    print(f"Saved {out_wav} (duration: {duration:.2f}s)")
else:
    print("No speech output returned!")
