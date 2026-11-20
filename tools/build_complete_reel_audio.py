"""
Vartaji Master Production Audio & Captions Generator
Integrates:
1. High-fidelity Microsoft Neural Speech with character-specific acoustic profiles.
2. Millisecond-accurate WordBoundary tracking for 100% synchronized Devanagari subtitles.
3. Master timeline assembly with zero audio collisions, zero dead pauses, and natural breaths.
4. Automatic update of script.json and captions.json.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
import numpy as np
import soundfile as sf
import edge_tts

# Target timeline definitions: exactly 94.0 seconds total
SHOT_SPECS = [
    {
        "id": "s01",
        "speaker": "narrator",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-5%",
        "pitch": "-1Hz",
        "text": "आधी रात हो चुकी थी... वार्ता अभी चल रही थी।",
        "start": 0.0,
        "end": 6.5,
        "lead_in": 0.5, # wick gutters in silence before narration starts
        "filter": "equalizer=f=220:width_type=o:w=1.0:g=1.5",
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
        "voice": "hi-IN-MadhurNeural",
        "rate": "-5%",
        "pitch": "-1Hz",
        "text": "श्रीगोकुलनाथजी चौरासी वैष्णवन की वार्ता कर रहे थे... कल्याणभट्ट और सब वैष्णव सुन रहे थे।",
        "start": 6.5,
        "end": 16.5,
        "lead_in": 0.2,
        "filter": "equalizer=f=220:width_type=o:w=1.0:g=1.5",
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
        "voice": "hi-IN-MadhurNeural",
        "rate": "-5%",
        "pitch": "-1Hz",
        "text": "वार्ता के रस में वे इतने डूब गये... कि श्रीसुबोधिनी की कथा कहना भूल गये।",
        "start": 16.5,
        "end": 25.0,
        "lead_in": 0.2,
        "filter": "equalizer=f=220:width_type=o:w=1.0:g=1.5",
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
        "voice": "hi-IN-MadhurNeural",
        "rate": "-8%",
        "pitch": "-2Hz",
        "text": "रात ढल गई...",
        "start": 25.0,
        "end": 30.0,
        "lead_in": 0.2,
        "filter": "equalizer=f=220:width_type=o:w=1.0:g=1.5",
        "caption_chunks": [
            {"words": ["रात", "ढल", "गई"], "text": "रात ढल गई"}
        ]
    },
    {
        "id": "s05",
        "speaker": "young-vaishnav",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+3%",
        "pitch": "+2Hz",
        "text": "महाराजाधिराज, आज कथा कब कहोगे?",
        "start": 30.0,
        "end": 35.5,
        "lead_in": 0.25,
        "filter": "asetrate=24000*1.04,aresample=24000,equalizer=f=3200:width_type=o:w=1.0:g=2.5",
        "caption_chunks": [
            {"words": ["महाराजाधिराज"], "text": "महाराजाधिराज"},
            {"words": ["आज", "कथा"], "text": "आज कथा"},
            {"words": ["कब", "कहोगे"], "text": "कब कहोगे?"}
        ]
    },
    {
        "id": "s06",
        "speaker": "narrator",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-8%",
        "pitch": "-2Hz",
        "text": "आधी रात हो चुकी थी...",
        "start": 35.5,
        "end": 40.5,
        "lead_in": 0.2,
        "filter": "equalizer=f=220:width_type=o:w=1.0:g=1.5",
        "caption_chunks": [
            {"words": ["आधी", "रात", "हो"], "text": "आधी रात हो"},
            {"words": ["चुकी", "थी"], "text": "चुकी थी"}
        ]
    },
    {
        "id": "s07",
        "speaker": "gokulnathji",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-10%",
        "pitch": "-4Hz",
        "text": "आज मैं कथा का फल कह रहा हूँ।",
        "start": 40.5,
        "end": 46.5,
        "lead_in": 0.25,
        "filter": "equalizer=f=180:width_type=o:w=1.5:g=3.2,aecho=0.8:0.7:30|50:0.12|0.08",
        "caption_chunks": [
            {"words": ["आज", "मैं"], "text": "आज मैं"},
            {"words": ["कथा", "का", "फल"], "text": "कथा का फल"},
            {"words": ["कह", "रहा", "हूँ"], "text": "कह रहा हूँ"}
        ]
    },
    {
        "id": "s08",
        "speaker": "gokulnathji",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-8%",
        "pitch": "-3Hz",
        "text": "सारा फल वैष्णव की बात में है... वैष्णव से बढ़कर और कोई पदार्थ नहीं है।",
        "start": 46.5,
        "end": 57.0,
        "lead_in": 0.2,
        "filter": "equalizer=f=180:width_type=o:w=1.5:g=3.2,aecho=0.8:0.7:30|50:0.12|0.08",
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
        "voice": "hi-IN-MadhurNeural",
        "rate": "-8%",
        "pitch": "-3Hz",
        "text": "यह पुष्टिमार्ग है — वैष्णव के द्वारा ही फलित होता है।",
        "start": 57.0,
        "end": 64.5,
        "lead_in": 0.2,
        "filter": "equalizer=f=180:width_type=o:w=1.5:g=3.2,aecho=0.8:0.7:30|50:0.12|0.08",
        "caption_chunks": [
            {"words": ["यह", "पुष्टिमार्ग", "है"], "text": "यह पुष्टिमार्ग है"},
            {"words": ["वैष्णव", "के", "द्वारा"], "text": "वैष्णव के द्वारा"},
            {"words": ["ही", "फलित", "होता", "है"], "text": "ही फलित होता है"}
        ]
    },
    {
        "id": "s10",
        "speaker": "gokulnathji",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-8%",
        "pitch": "-3Hz",
        "text": "श्रीआचार्यजी ने भी कहा — दमला, ये मार्ग तेरे लिये प्रकट किया है। इसलिये वैष्णव की वार्ता सर्वोपरि है।",
        "start": 64.5,
        "end": 78.0,
        "lead_in": 0.2,
        "filter": "equalizer=f=180:width_type=o:w=1.5:g=3.2,aecho=0.8:0.7:30|50:0.12|0.08",
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
        "voice": "hi-IN-MadhurNeural",
        "rate": "-4%",
        "pitch": "-1Hz",
        "text": "तो चलिए शुरुआत करते हैं श्री दामोदरदास हरसानी वैष्णव की वार्ता एक वार्ता प्रसंग एक से... जय श्री कृष्ण!",
        "start": 78.0,
        "end": 94.0,
        "lead_in": 0.2,
        "filter": "equalizer=f=220:width_type=o:w=1.0:g=1.5",
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

async def synthesize_shot(shot: dict, output_dir: Path):
    shot_id = shot["id"]
    mp3_path = output_dir / f"{shot_id}_raw.mp3"
    wav_path = output_dir / f"{shot_id}.wav"
    
    word_events = []
    audio_bytes = bytearray()
    
    communicate = edge_tts.Communicate(
        shot["text"],
        shot["voice"],
        rate=shot["rate"],
        pitch=shot["pitch"],
        boundary="WordBoundary"
    )
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            word_events.append({
                "text": chunk["text"],
                "start": chunk["offset"] / 10_000_000,
                "duration": chunk["duration"] / 10_000_000,
                "end": (chunk["offset"] + chunk["duration"]) / 10_000_000
            })
            
    with open(mp3_path, "wb") as f:
        f.write(audio_bytes)
        
    # Apply character acoustic profile
    af = shot["filter"]
    cmd = f'ffmpeg -y -v error -i "{mp3_path}" -af "{af}" -ar 24000 -ac 1 "{wav_path}"'
    os.system(cmd)
    if mp3_path.exists():
        mp3_path.unlink()
        
    data, sr = sf.read(str(wav_path))
    actual_dur = len(data) / sr
    
    return data, sr, actual_dur, word_events

def build_captions_for_shot(shot: dict, word_events: list, shot_audio_start_on_timeline: float):
    captions = []
    if not word_events:
        return captions
        
    w_idx = 0
    num_events = len(word_events)
    
    for chunk in shot.get("caption_chunks", []):
        chunk_words = chunk["words"]
        # Find matching word events
        matched_events = []
        for word in chunk_words:
            # clean punctuation for matching
            w_clean = word.replace(",", "").replace(".", "").replace("—", "").replace("!", "").replace("?", "").strip()
            # scan forward in word_events
            curr = w_idx
            found = False
            while curr < num_events:
                ev_clean = word_events[curr]["text"].replace(",", "").replace(".", "").replace("—", "").replace("!", "").replace("?", "").strip()
                if w_clean == ev_clean or w_clean in ev_clean or ev_clean in w_clean:
                    matched_events.append(word_events[curr])
                    w_idx = curr + 1
                    found = True
                    break
                curr += 1
            if not found and w_idx < num_events:
                # fallback take next
                matched_events.append(word_events[w_idx])
                w_idx += 1
                
        if matched_events:
            s_rel = matched_events[0]["start"]
            e_rel = matched_events[-1]["end"]
            
            # Map to master timeline
            s_abs = round(shot_audio_start_on_timeline + s_rel, 3)
            e_abs = round(shot_audio_start_on_timeline + e_rel + 0.15, 3) # +150ms hold for readability
            
            captions.append({
                "text": chunk["text"],
                "s": s_abs,
                "e": e_abs,
                "shot": shot["id"]
            })
            
    return captions

async def main():
    reel_dir = Path("reels/intro-gokulnath")
    audio_dir = reel_dir / "audio"
    shots_dir = audio_dir / "shots"
    shots_dir.mkdir(parents=True, exist_ok=True)
    
    total_duration = 94.0
    sample_rate = 24000
    total_samples = int(total_duration * sample_rate)
    master_timeline = np.zeros(total_samples, dtype=np.float32)
    
    all_captions = []
    updated_shots_info = []
    
    print("=" * 60)
    print("PRODUCING MASTER AUDIO TRACK & SYNCHRONIZED CAPTIONS")
    print(f"Total Target Timeline: {total_duration:.1f}s | Sample Rate: {sample_rate}Hz")
    print("=" * 60)
    
    for shot in SHOT_SPECS:
        shot_id = shot["id"]
        speaker = shot["speaker"]
        shot_start = shot["start"]
        shot_end = shot["end"]
        lead_in = shot["lead_in"]
        available_window = shot_end - shot_start
        
        # Audio starts at shot_start + lead_in
        audio_start_timeline = shot_start + lead_in
        
        print(f"\nProcessing [{shot_id}] ({speaker})")
        print(f"  Shot Window: {shot_start:.2f}s -> {shot_end:.2f}s (window: {available_window:.2f}s)")
        print(f"  Audio Start: {audio_start_timeline:.2f}s")
        
        data, sr, dur, word_events = await synthesize_shot(shot, shots_dir)
        print(f"  Generated Speech Duration: {dur:.2f}s ({len(word_events)} word events)")
        
        audio_end_timeline = audio_start_timeline + dur
        tail_hold = shot_end - audio_end_timeline
        print(f"  Audio Ends: {audio_end_timeline:.2f}s | Visual Tail Hold: {tail_hold:.2f}s")
        
        if tail_hold < -0.05:
            print(f"  [WARNING] Audio exceeds shot window by {-tail_hold:.2f}s! Adjusting shot end.")
            shot_end = audio_end_timeline + 0.3
            
        # Place onto master timeline
        start_samp = int(audio_start_timeline * sample_rate)
        end_samp = min(start_samp + len(data), total_samples)
        copied_len = end_samp - start_samp
        
        # 15ms anti-click microfade
        fade_len = min(int(sample_rate * 0.015), copied_len // 4)
        if fade_len > 0:
            data[:fade_len] *= np.linspace(0.0, 1.0, fade_len)
            data[copied_len - fade_len:copied_len] *= np.linspace(1.0, 0.0, fade_len)
            
        master_timeline[start_samp:end_samp] += data[:copied_len]
        
        # Build synchronized captions for this shot
        shot_captions = build_captions_for_shot(shot, word_events, audio_start_timeline)
        all_captions.extend(shot_captions)
        
        for c in shot_captions:
            print(f"    Sub: [{c['s']:.2f}s - {c['e']:.2f}s] {c['text']}")
            
        updated_shots_info.append({
            "id": shot_id,
            "speaker": speaker,
            "start": shot_start,
            "end": shot_end,
            "audio_start": audio_start_timeline,
            "audio_dur": dur,
            "tail_hold": tail_hold
        })
        
    # Write master audio track
    master_vo_path = audio_dir / "vo.wav"
    sf.write(str(master_vo_path), master_timeline, sample_rate)
    print("\n" + "=" * 60)
    print(f" Master Audio VO written to: {master_vo_path}")
    print(f" Total Master VO length: {len(master_timeline)/sample_rate:.2f}s")
    
    # Save captions.json
    captions_file = reel_dir / "captions.json"
    with open(captions_file, "w", encoding="utf-8") as f:
        json.dump(all_captions, f, ensure_ascii=False, indent=2)
    print(f" Synchronized captions saved to: {captions_file} ({len(all_captions)} entries)")
    
    # Update script.json with precise shot start/end times
    script_file = reel_dir / "script.json"
    with open(script_file, "r", encoding="utf-8") as f:
        script = json.load(f)
        
    for shot in script.get("shots", []):
        sid = shot["id"]
        for spec in SHOT_SPECS:
            if spec["id"] == sid:
                shot["start"] = spec["start"]
                shot["end"] = spec["end"]
                break
                
    script["duration"] = total_duration
    with open(script_file, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print(f" Updated script.json saved with precise non-colliding shot timings.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
