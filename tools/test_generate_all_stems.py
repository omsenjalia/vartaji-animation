import os
import sys
import json
import asyncio
from pathlib import Path
import soundfile as sf
import edge_tts

# SSML Dialogue Scripts for all 11 shots with natural emotional phrasing and pauses
SHOT_SCRIPTS = [
    {
        "id": "s01",
        "speaker": "narrator",
        "ssml": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-4%" pitch="-1Hz">
आधी रात हो चुकी थी... <break time="350ms"/> वार्ता अभी चल रही थी।
</prosody>
</voice>
</speak>""",
        "text": "आधी रात हो चुकी थी। वार्ता अभी चल रही थी।"
    },
    {
        "id": "s02",
        "speaker": "narrator",
        "ssml": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-4%" pitch="-1Hz">
श्रीगोकुलनाथजी चौरासी वैष्णवन की वार्ता कर रहे थे... <break time="400ms"/> कल्याणभट्ट और सब वैष्णव सुन रहे थे।
</prosody>
</voice>
</speak>""",
        "text": "श्रीगोकुलनाथजी चौरासी वैष्णवन की वार्ता कर रहे थे। कल्याणभट्ट और सब वैष्णव सुन रहे थे।"
    },
    {
        "id": "s03",
        "speaker": "narrator",
        "ssml": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-4%" pitch="-1Hz">
वार्ता के रस में वे इतने डूब गये... <break time="350ms"/> कि श्रीसुबोधिनी की कथा कहना भूल गये।
</prosody>
</voice>
</speak>""",
        "text": "वार्ता के रस में वे इतने डूब गये कि श्रीसुबोधिनी की कथा कहना भूल गये।"
    },
    {
        "id": "s04",
        "speaker": "narrator",
        "ssml": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-6%" pitch="-2Hz">
रात ढल गई...
</prosody>
</voice>
</speak>""",
        "text": "रात ढल गई।"
    },
    {
        "id": "s05",
        "speaker": "young-vaishnav",
        "ssml": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="+4%" pitch="+2Hz">
महाराजाधिराज... <break time="250ms"/> आज कथा कब कहोगे?
</prosody>
</voice>
</speak>""",
        "text": "महाराजाधिराज, आज कथा कब कहोगे?"
    },
    {
        "id": "s06",
        "speaker": "narrator",
        "ssml": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-6%" pitch="-2Hz">
आधी रात हो चुकी थी...
</prosody>
</voice>
</speak>""",
        "text": "आधी रात हो चुकी थी।"
    },
    {
        "id": "s07",
        "speaker": "gokulnathji",
        "ssml": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-9%" pitch="-4Hz">
आज मैं... <break time="450ms"/> कथा का फल कह रहा हूँ।
</prosody>
</voice>
</speak>""",
        "text": "आज मैं कथाका फल कह रहा हूँ।"
    },
    {
        "id": "s08",
        "speaker": "gokulnathji",
        "ssml": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-8%" pitch="-4Hz">
सारा फल वैष्णव की बात में है... <break time="400ms"/> वैष्णव से बढ़कर और कोई पदार्थ नहीं है।
</prosody>
</voice>
</speak>""",
        "text": "सारा फल वैष्णव की बात में है। वैष्णव से बढ़कर और कोई पदार्थ नहीं है।"
    },
    {
        "id": "s09",
        "speaker": "gokulnathji",
        "ssml": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-7%" pitch="-3Hz">
यह पुष्टिमार्ग है... <break time="350ms"/> वैष्णव के द्वारा ही फलित होता है।
</prosody>
</voice>
</speak>""",
        "text": "यह पुष्टिमार्ग है — वैष्णव के द्वारा ही फलित होता है।"
    },
    {
        "id": "s10",
        "speaker": "gokulnathji",
        "ssml": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-7%" pitch="-3Hz">
श्रीआचार्यजी ने भी कहा... <break time="300ms"/> दमला, ये मार्ग तेरे लिये प्रकट किया है... <break time="450ms"/> इसलिये वैष्णव की वार्ता सर्वोपरि है।
</prosody>
</voice>
</speak>""",
        "text": "श्रीआचार्यजीने भी कहा — दमला, ये मार्ग तेरे लिये प्रकट किया है। इसलिये वैष्णव की वार्ता सर्वोपरि है।"
    },
    {
        "id": "s11",
        "speaker": "narrator",
        "ssml": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-3%" pitch="-1Hz">
तो चलिए शुरुआत करते हैं... <break time="300ms"/> श्री दामोदरदास हरसानी वैष्णव की वार्ता एक वार्ता प्रसंग एक से... <break time="500ms"/> जय श्री कृष्ण!
</prosody>
</voice>
</speak>""",
        "text": "तो चलिए शुरुआत करते हैं श्री दामोदरदास हरसानी वैष्णव की वार्ता १ वार्ता प्रसंग १ से... जय श्री कृष्ण!"
    }
]

async def generate_stems():
    out_dir = Path("reels/intro-gokulnath/audio/stems")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating 11 expressive stems with SSML...")
    durations = {}
    
    for shot in SHOT_SCRIPTS:
        shot_id = shot["id"]
        mp3_path = out_dir / f"{shot_id}.mp3"
        wav_path = out_dir / f"{shot_id}.wav"
        
        c = edge_tts.Communicate(shot["ssml"], "hi-IN-MadhurNeural")
        await c.save(str(mp3_path))
        
        # Acoustic processing per character:
        # Narrator: clean, warm EQ
        # Young-vaishnav: youthful, slightly lighter pitch & high pass
        # Gokulnathji: deep resonance, subtle reverent room acoustics
        speaker = shot["speaker"]
        if speaker == "gokulnathji":
            # Deep bass warmth + subtle temple hall reverb
            audio_filter = "equalizer=f=180:width_type=o:w=1.5:g=3.5,aecho=0.8:0.7:30|50:0.15|0.1"
        elif speaker == "young-vaishnav":
            # Youthful clarity + subtle pitch lift
            audio_filter = "asetrate=24000*1.04,aresample=24000,equalizer=f=3000:width_type=o:w=1.0:g=2.0"
        else:
            # Narrator: smooth studio warmth
            audio_filter = "equalizer=f=200:width_type=o:w=1.0:g=1.5"
            
        cmd = f'ffmpeg -y -v error -i "{mp3_path}" -af "{audio_filter}" -ar 24000 -ac 1 "{wav_path}"'
        os.system(cmd)
        if mp3_path.exists():
            mp3_path.unlink()
            
        data, sr = sf.read(str(wav_path))
        dur = len(data) / sr
        durations[shot_id] = dur
        print(f"[{shot_id}] ({speaker}) -> {dur:.2f}s | {shot['text'][:40]}...")
        
    print(f"\nAll 11 stems generated. Total speech duration = {sum(durations.values()):.2f}s")
    with open(out_dir / "stem_durations.json", "w", encoding="utf-8") as f:
        json.dump(durations, f, indent=2)

if __name__ == "__main__":
    asyncio.run(generate_stems())
