import os
import asyncio
from pathlib import Path
import soundfile as sf
import edge_tts

RAW_SHOTS = [
    {
        "id": "s01",
        "speaker": "narrator",
        "text": "आधी रात हो चुकी थी... वार्ता अभी चल रही थी।",
        "rate": "-5%",
        "pitch": "-1Hz"
    },
    {
        "id": "s02",
        "speaker": "narrator",
        "text": "श्रीगोकुलनाथजी चौरासी वैष्णवन की वार्ता कर रहे थे... कल्याणभट्ट और सब वैष्णव सुन रहे थे।",
        "rate": "-5%",
        "pitch": "-1Hz"
    },
    {
        "id": "s03",
        "speaker": "narrator",
        "text": "वार्ता के रस में वे इतने डूब गये... कि श्रीसुबोधिनी की कथा कहना भूल गये।",
        "rate": "-5%",
        "pitch": "-1Hz"
    },
    {
        "id": "s04",
        "speaker": "narrator",
        "text": "रात ढल गई...",
        "rate": "-8%",
        "pitch": "-2Hz"
    },
    {
        "id": "s05",
        "speaker": "young-vaishnav",
        "text": "महाराजाधिराज, आज कथा कब कहोगे?",
        "rate": "+3%",
        "pitch": "+2Hz"
    },
    {
        "id": "s06",
        "speaker": "narrator",
        "text": "आधी रात हो चुकी थी...",
        "rate": "-8%",
        "pitch": "-2Hz"
    },
    {
        "id": "s07",
        "speaker": "gokulnathji",
        "text": "आज मैं कथा का फल कह रहा हूँ।",
        "rate": "-10%",
        "pitch": "-4Hz"
    },
    {
        "id": "s08",
        "speaker": "gokulnathji",
        "text": "सारा फल वैष्णव की बात में है... वैष्णव से बढ़कर और कोई पदार्थ नहीं है।",
        "rate": "-8%",
        "pitch": "-3Hz"
    },
    {
        "id": "s09",
        "speaker": "gokulnathji",
        "text": "यह पुष्टिमार्ग है — वैष्णव के द्वारा ही फलित होता है।",
        "rate": "-8%",
        "pitch": "-3Hz"
    },
    {
        "id": "s10",
        "speaker": "gokulnathji",
        "text": "श्रीआचार्यजी ने भी कहा — दमला, ये मार्ग तेरे लिये प्रकट किया है। इसलिये वैष्णव की वार्ता सर्वोपरि है।",
        "rate": "-8%",
        "pitch": "-3Hz"
    },
    {
        "id": "s11",
        "speaker": "narrator",
        "text": "तो चलिए शुरुआत करते हैं श्री दामोदरदास हरसानी वैष्णव की वार्ता एक वार्ता प्रसंग एक से... जय श्री कृष्ण!",
        "rate": "-4%",
        "pitch": "-1Hz"
    }
]

async def generate_clean_stems():
    out_dir = Path("reels/intro-gokulnath/audio/clean_stems")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("--- Generating clean stems (Raw Text with Emotional Punctuation) ---")
    results = []
    
    for shot in RAW_SHOTS:
        shot_id = shot["id"]
        mp3_path = out_dir / f"{shot_id}.mp3"
        wav_path = out_dir / f"{shot_id}.wav"
        
        c = edge_tts.Communicate(
            shot["text"],
            "hi-IN-MadhurNeural",
            rate=shot["rate"],
            pitch=shot["pitch"]
        )
        await c.save(str(mp3_path))
        
        # Character acoustic filters
        speaker = shot["speaker"]
        if speaker == "gokulnathji":
            # Deep guru resonance + subtle sacred room acoustic
            audio_filter = "equalizer=f=180:width_type=o:w=1.5:g=3.0,aecho=0.8:0.7:30|50:0.12|0.08"
        elif speaker == "young-vaishnav":
            # Youthful devotee: brighter acoustic, +1.5 semitones pitch, clear presence
            audio_filter = "asetrate=24000*1.04,aresample=24000,equalizer=f=3200:width_type=o:w=1.0:g=2.5"
        else:
            # Narrator: clean, warm studio tone
            audio_filter = "equalizer=f=220:width_type=o:w=1.0:g=1.5"
            
        cmd = f'ffmpeg -y -v error -i "{mp3_path}" -af "{audio_filter}" -ar 24000 -ac 1 "{wav_path}"'
        os.system(cmd)
        if mp3_path.exists():
            mp3_path.unlink()
            
        data, sr = sf.read(str(wav_path))
        dur = len(data) / sr
        results.append({
            "id": shot_id,
            "speaker": speaker,
            "text": shot["text"],
            "duration": dur
        })
        print(f"[{shot_id}] ({speaker}) -> {dur:.2f}s | {shot['text']}")
        
    total_dur = sum(r["duration"] for r in results)
    print(f"\nTotal speech audio duration: {total_dur:.2f}s")
    return results

if __name__ == "__main__":
    asyncio.run(generate_clean_stems())
