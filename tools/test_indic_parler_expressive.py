import torch
import traceback
import sys
import time

try:
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer
    import soundfile as sf

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    # bfloat16 is natively supported on RTX 3050 and uses half memory
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    print(f"Loading Indic Parler-TTS on {device} with {dtype}...")

    model_id = "ai4bharat/indic-parler-tts"
    model = ParlerTTSForConditionalGeneration.from_pretrained(model_id)
    # Convert entire composite model (text_encoder, decoder, audio_encoder) to same dtype and device
    model.to(device=device, dtype=dtype)
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

    test_voices = [
        {
            "name": "Rohit_Narrator",
            "prompt": "आधी रात हो चुकी थी। वार्ता अभी चल रही थी।",
            "description": "Rohit speaks in a warm, calm, and expressive storytelling tone with a moderate pace. The recording is very clear audio, high quality and close up with no background noise."
        },
        {
            "name": "Divya_Female",
            "prompt": "आधी रात हो चुकी थी। वार्ता अभी चल रही थी।",
            "description": "Divya speaks with a clear, expressive, and slightly fast pace. The recording is very clear audio, close up with no background noise."
        },
        {
            "name": "Aman_Young",
            "prompt": "महाराजाधिराज, आज कथा कब कहोगे?",
            "description": "Aman speaks in a polite, curious, and respectful tone with a moderate pace. The recording is very clear audio, close up with no background noise."
        }
    ]

    for tv in test_voices:
        print(f"\n--- Generating {tv['name']} ---")
        t0 = time.time()
        
        desc_inputs = description_tokenizer(tv["description"], return_tensors="pt").to(device)
        prompt_inputs = tokenizer(tv["prompt"], return_tensors="pt").to(device)

        with torch.no_grad():
            generation = model.generate(
                input_ids=desc_inputs.input_ids,
                attention_mask=desc_inputs.attention_mask,
                prompt_input_ids=prompt_inputs.input_ids,
                prompt_attention_mask=prompt_inputs.attention_mask
            )
            
        audio = generation.cpu().to(torch.float32).numpy().squeeze()
        out_wav = f"parler_{tv['name']}.wav"
        sf.write(out_wav, audio, model.config.sampling_rate)
        dur = len(audio) / model.config.sampling_rate
        print(f"SUCCESS in {time.time()-t0:.2f}s | Saved {out_wav} (dur: {dur:.2f}s, sr: {model.config.sampling_rate})")

except Exception as e:
    print(f"EXCEPTION: {e}", file=sys.stderr)
    traceback.print_exc()
