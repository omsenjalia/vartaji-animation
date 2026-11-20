import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
import os
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

out_dir = "tools/voice_candidates"
os.makedirs(out_dir, exist_ok=True)

# 1. Tests for NARRATOR (Aman made harder, firmer, more commanding)
narrator_prompt = "आधी रात हो चुकी थी। वार्ता अभी चल रही थी।"
narrator_candidates = [
    {
        "id": "narrator_aman_firm",
        "title": "Aman Firm & Authoritative",
        "desc": "Aman speaks in a firm, authoritative, and confident storytelling tone with a steady, commanding pace. His voice is hard, grounded, and deep. The recording is very clear audio, high quality, very close up with no background noise."
    },
    {
        "id": "narrator_aman_serious",
        "title": "Aman Serious & Resonant",
        "desc": "Aman speaks in a serious, strong, and powerful narration tone at a deliberate, measured pace. His voice is punchy, clear, and assertive. Very clear audio, high quality studio recording with no background noise."
    },
    {
        "id": "narrator_aman_hard_broadcast",
        "title": "Aman Hard Broadcast Style",
        "desc": "Aman speaks in a crisp, forceful, and commanding documentary style with a low pitch and firm delivery. Very clear audio, close up, no background noise."
    }
]

# 2. Tests for SHRI GOKULNATHJI (Seeking the perfect divine, wise, serene spiritual guru)
gokulnathji_prompt = "आज मैं कथा का फल कह रहा हूँ। सारा फल वैष्णव की बात में है।"
gokulnathji_candidates = [
    {
        "id": "guru_elderly_anonymous",
        "title": "Elderly Spiritual Master (Descriptive)",
        "desc": "An elderly male speaker speaks with a gentle, wise, serene, and deeply spiritual voice at a slow, peaceful pace. His tone is filled with divine warmth and quiet authority. The recording is very clear audio, high quality and close up with no background noise."
    },
    {
        "id": "guru_sanjay_wise",
        "title": "Sanjay - Mature Wise Elder",
        "desc": "Sanjay speaks with a mature, calm, wise, and spiritual tone at a slow, gentle pace. The recording is very clear audio, high quality and close up with no background noise."
    },
    {
        "id": "guru_yash_peaceful",
        "title": "Yash - Peaceful Vaishnav Cadence",
        "desc": "Yash speaks in a calm, devout, and deeply serene spiritual tone at a slow, peaceful pace. The recording is very clear audio, close up with no background noise."
    },
    {
        "id": "guru_karan_tranquil",
        "title": "Karan - Tranquil & Meditative",
        "desc": "Karan speaks in a tranquil, meditative, and holy voice with a slow, soft delivery filled with spiritual depth. Very clear audio, close up, no background noise."
    },
    {
        "id": "guru_suresh_gentle_guru",
        "title": "Suresh - Gentle Revered Guru",
        "desc": "Suresh speaks in a warm, elderly, gentle, and respectful guru voice at a slow pace. Very clear audio, high quality with no background noise."
    },
    {
        "id": "guru_tapan_deep_elder",
        "title": "Tapan - Deep Elder Tone",
        "desc": "Tapan speaks in a deep, elderly, calm, and solemn tone at a slow, deliberate pace. Very clear audio, close up with no background noise."
    }
]

all_tests = [("narrator", narrator_prompt, narrator_candidates), ("gokulnathji", gokulnathji_prompt, gokulnathji_candidates)]

for category, prompt, candidates in all_tests:
    print(f"\n=================== Generating {category.upper()} Candidates ===================")
    for c in candidates:
        print(f"\nSynthesizing {c['title']}...")
        t0 = time.time()
        desc_inputs = description_tokenizer(c["desc"], return_tensors="pt").to(device)
        prompt_inputs = tokenizer(prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            generation = model.generate(
                input_ids=desc_inputs.input_ids,
                attention_mask=desc_inputs.attention_mask,
                prompt_input_ids=prompt_inputs.input_ids,
                prompt_attention_mask=prompt_inputs.attention_mask
            )
            
        audio = generation.cpu().to(torch.float32).numpy().squeeze()
        wav_path = os.path.join(out_dir, f"{c['id']}.wav")
        mp3_path = os.path.join(out_dir, f"{c['id']}.mp3")
        sf.write(wav_path, audio, model.config.sampling_rate)
        # convert to mp3 via ffmpeg
        os.system(f'ffmpeg -y -v error -i "{wav_path}" -b:a 192k "{mp3_path}"')
        dur = len(audio) / model.config.sampling_rate
        print(f"Generated {c['id']}.mp3 in {time.time()-t0:.2f}s (dur: {dur:.2f}s)")

print("\nAll candidate voices generated successfully!")
