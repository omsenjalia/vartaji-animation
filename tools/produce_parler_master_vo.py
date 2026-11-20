import os
import sys
import json
import time
import torch
import soundfile as sf
import numpy as np
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

device = "cuda:0" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

print(f"Loading Indic Parler-TTS on {device} ({dtype})...")
model_id = "ai4bharat/indic-parler-tts"
model = ParlerTTSForConditionalGeneration.from_pretrained(model_id)
model.to(device=device, dtype=dtype)
model.eval()

tokenizer = AutoTokenizer.from_pretrained(model_id)
description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

# Prompt descriptions chosen by user:
# 1. Narrator: Aman Hard Broadcast
DESC_NARRATOR = "Aman speaks in a crisp, forceful, and commanding documentary style with a low pitch and firm delivery. Very clear audio, close up, no background noise."

# 2. Young Vaishnav: Aman Youthful & Respectful
DESC_YOUNG = "Aman speaks in a youthful, polite, curious, and respectful tone with a moderate pace. The recording is very clear audio, close up with no background noise."

# 3. Shri Gokulnathji: Yash Devout Vaishnav
DESC_GURU = "Yash speaks in a calm, devout, and deeply serene spiritual tone at a slow, peaceful pace. The recording is very clear audio, close up with no background noise."

SHOTS = [
    {
        "id": "s01",
        "speaker": "narrator",
        "desc": DESC_NARRATOR,
        "text": "आधी रात हो चुकी थी। वार्ता अभी चल रही थी।",
        "caption_chunks": [
            {"words": ["आधी", "रात", "हो"], "text": "आधी रात हो"},
            {"words": ["चुकी", "थी"], "text": "चुकी थी"},
            {"words": ["वार्ता", "अभी", "चल"], "text": "वार्ता अभी चल"},
            {"words": ["रही", "थी"], "text": "रही थी"}
        ]
    },
    {
        "id": "s02",
        "speaker": "narrator",
        "desc": DESC_NARRATOR,
        "text": "श्रीगोकुलनाथजी चौरासी वैष्णवन की वार्ता कर रहे थे। कल्याणभट्ट और सब वैष्णव सुन रहे थे।",
        "caption_chunks": [
            {"words": ["श्रीगोकुलनाथजी", "चौरासी"], "text": "श्रीगोकुलनाथजी चौरासी"},
            {"words": ["वैष्णवन", "की", "वार्ता"], "text": "वैष्णवन की वार्ता"},
            {"words": ["कर", "रहे", "थे"], "text": "कर रहे थे"},
            {"words": ["कल्याणभट्ट", "और"], "text": "कल्याणभट्ट और"},
            {"words": ["सब", "वैष्णव"], "text": "सब वैष्णव"},
            {"words": ["सुन", "रहे", "थे"], "text": "सुन रहे थे"}
        ]
    },
    {
        "id": "s03",
        "speaker": "narrator",
        "desc": DESC_NARRATOR,
        "text": "वार्ता के रस में वे इतने डूब गये कि श्रीसुबोधिनी की कथा कहना भूल गये।",
        "caption_chunks": [
            {"words": ["वार्ता", "के", "रस", "में"], "text": "वार्ता के रस में"},
            {"words": ["वे", "इतने", "डूब", "गये"], "text": "वे इतने डूब गये"},
            {"words": ["कि", "श्रीसुबोधिनी", "की"], "text": "कि श्रीसुबोधिनी की"},
            {"words": ["कथा", "कहना", "भूल", "गये"], "text": "कथा कहना भूल गये"}
        ]
    },
    {
        "id": "s04",
        "speaker": "narrator",
        "desc": DESC_NARRATOR,
        "text": "रात ढल गई।",
        "caption_chunks": [
            {"words": ["रात", "ढल", "गई"], "text": "रात ढल गई"}
        ]
    },
    {
        "id": "s05",
        "speaker": "young-vaishnav",
        "desc": DESC_YOUNG,
        "text": "महाराजाधिराज, आज कथा कब कहोगे?",
        "caption_chunks": [
            {"words": ["महाराजाधिराज"], "text": "महाराजाधिराज"},
            {"words": ["आज", "कथा"], "text": "आज कथा"},
            {"words": ["कब", "कहोगे"], "text": "कब कहोगे?"}
        ]
    },
    {
        "id": "s06",
        "speaker": "narrator",
        "desc": DESC_NARRATOR,
        "text": "आधी रात हो चुकी थी।",
        "caption_chunks": [
            {"words": ["आधी", "रात", "हो"], "text": "आधी रात हो"},
            {"words": ["चुकी", "थी"], "text": "चुकी थी"}
        ]
    },
    {
        "id": "s07",
        "speaker": "gokulnathji",
        "desc": DESC_GURU,
        "text": "आज मैं कथा का फल कह रहा हूँ।",
        "caption_chunks": [
            {"words": ["आज", "मैं"], "text": "आज मैं"},
            {"words": ["कथा", "का", "फल"], "text": "कथा का फल"},
            {"words": ["कह", "रहा", "हूँ"], "text": "कह रहा हूँ"}
        ]
    },
    {
        "id": "s08",
        "speaker": "gokulnathji",
        "desc": DESC_GURU,
        "text": "सारा फल वैष्णव की बात में है। वैष्णव से बढ़कर और कोई पदार्थ नहीं है।",
        "caption_chunks": [
            {"words": ["सारा", "फल", "वैष्णव"], "text": "सारा फल वैष्णव"},
            {"words": ["की", "बात", "में", "है"], "text": "की बात में है"},
            {"words": ["वैष्णव", "से", "बढ़कर"], "text": "वैष्णव से बढ़कर"},
            {"words": ["और", "कोई", "पदार्थ"], "text": "और कोई पदार्थ"},
            {"words": ["नहीं", "है"], "text": "नहीं है"}
        ]
    },
    {
        "id": "s09",
        "speaker": "gokulnathji",
        "desc": DESC_GURU,
        "text": "यह पुष्टिमार्ग है — वैष्णव के द्वारा ही फलित होता है।",
        "caption_chunks": [
            {"words": ["यह", "पुष्टिमार्ग", "है"], "text": "यह पुष्टिमार्ग है"},
            {"words": ["वैष्णव", "के", "द्वारा"], "text": "वैष्णव के द्वारा"},
            {"words": ["ही", "फलित", "होता", "है"], "text": "ही फलित होता है"}
        ]
    },
    {
        "id": "s10",
        "speaker": "gokulnathji",
        "desc": DESC_GURU,
        "text": "श्रीआचार्यजी ने भी कहा — दमला, ये मार्ग तेरे लिये प्रकट किया है। इसलिये वैष्णव की वार्ता सर्वोपरि है।",
        "caption_chunks": [
            {"words": ["श्रीआचार्यजी", "ने", "भी", "कहा"], "text": "श्रीआचार्यजी ने भी कहा"},
            {"words": ["दमला"], "text": "दमला,"},
            {"words": ["ये", "मार्ग", "तेरे", "लिये"], "text": "ये मार्ग तेरे लिये"},
            {"words": ["प्रकट", "किया", "है"], "text": "प्रकट किया है"},
            {"words": ["इसलिये", "वैष्णव", "की"], "text": "इसलिये वैष्णव की"},
            {"words": ["वार्ता", "सर्वोपरि", "है"], "text": "वार्ता सर्वोपरि है"}
        ]
    },
    {
        "id": "s11",
        "speaker": "narrator",
        "desc": DESC_NARRATOR,
        "text": "तो चलिए शुरुआत करते हैं श्री दामोदरदास हरसानी वैष्णव की वार्ता एक वार्ता प्रसंग एक से... जय श्री कृष्ण!",
        "caption_chunks": [
            {"words": ["तो", "चलिए", "शुरुआत"], "text": "तो चलिए शुरुआत"},
            {"words": ["करते", "हैं"], "text": "करते हैं"},
            {"words": ["श्री", "दामोदरदास", "हरसानी"], "text": "श्री दामोदरदास हरसानी"},
            {"words": ["वैष्णव", "की", "वार्ता"], "text": "वैष्णव की वार्ता १"},
            {"words": ["वार्ता", "प्रसंग", "एक", "से"], "text": "वार्ता प्रसंग १ से"},
            {"words": ["जय", "श्री", "कृष्ण"], "text": "जय श्री कृष्ण!"}
        ]
    }
]

out_stems_dir = "reels/intro-gokulnath/audio/parler_stems"
os.makedirs(out_stems_dir, exist_ok=True)

stem_results = []
print("\n--- Synthesizing all 11 shots with Indic Parler-TTS ---")
for shot in SHOTS:
    sid = shot["id"]
    spk = shot["speaker"]
    txt = shot["text"]
    desc = shot["desc"]
    print(f"\n[{sid}] ({spk}) -> '{txt}'")
    t0 = time.time()
    
    desc_inputs = description_tokenizer(desc, return_tensors="pt").to(device)
    prompt_inputs = tokenizer(txt, return_tensors="pt").to(device)

    with torch.no_grad():
        generation = model.generate(
            input_ids=desc_inputs.input_ids,
            attention_mask=desc_inputs.attention_mask,
            prompt_input_ids=prompt_inputs.input_ids,
            prompt_attention_mask=prompt_inputs.attention_mask
        )
        
    audio = generation.cpu().to(torch.float32).numpy().squeeze()
    sr = model.config.sampling_rate
    raw_wav = os.path.join(out_stems_dir, f"{sid}_raw.wav")
    sf.write(raw_wav, audio, sr)
    
    # Resample to 24000Hz standard project rate
    clean_wav = os.path.join(out_stems_dir, f"{sid}.wav")
    os.system(f'ffmpeg -y -v error -i "{raw_wav}" -ar 24000 -ac 1 "{clean_wav}"')
    if os.path.exists(raw_wav):
        os.remove(raw_wav)
        
    data, final_sr = sf.read(clean_wav)
    dur = len(data) / final_sr
    print(f"Generated {sid}.wav in {time.time()-t0:.2f}s (duration: {dur:.2f}s)")
    
    stem_results.append({
        "id": sid,
        "speaker": spk,
        "text": txt,
        "duration": dur,
        "path": clean_wav,
        "caption_chunks": shot["caption_chunks"]
    })

# Save manifest of stems
manifest_path = os.path.join(out_stems_dir, "manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(stem_results, f, ensure_ascii=False, indent=2)
print(f"\nAll 11 stems generated and saved to {out_stems_dir}!")
