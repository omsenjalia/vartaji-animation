import asyncio
import edge_tts
import soundfile as sf

async def test_character_voices():
    # 1. Narrator (Sutradhar) - Devotional storytelling
    ssml_narrator = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-5%" pitch="-1Hz">
आधी रात हो चुकी थी... <break time="350ms"/> वार्ता अभी चल रही थी।
</prosody>
</voice>
</speak>"""
    c1 = edge_tts.Communicate(ssml_narrator, "hi-IN-MadhurNeural")
    await c1.save("sample_narrator.mp3")

    # 2. Young Vaishnav - Inquisitive devotee (humble, respectful)
    ssml_young = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="+4%" pitch="+3Hz">
महाराजाधिराज... <break time="300ms"/> आज कथा कब कहोगे?
</prosody>
</voice>
</speak>"""
    c2 = edge_tts.Communicate(ssml_young, "hi-IN-MadhurNeural")
    await c2.save("sample_young.mp3")

    # 3. Shri Gokulnathji - Deep divine spiritual guru
    ssml_gokulnathji = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-10%" pitch="-4Hz">
आज मैं... <break time="450ms"/> कथा का फल कह रहा हूँ।
</prosody>
</voice>
</speak>"""
    c3 = edge_tts.Communicate(ssml_gokulnathji, "hi-IN-MadhurNeural")
    await c3.save("sample_gokulnathji.mp3")

    # 4. Outro Hook - Warm, inviting community call
    ssml_outro = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-3%" pitch="+0Hz">
तो चलिए शुरुआत करते हैं... <break time="300ms"/> श्री दामोदरदास हरसानी वैष्णव की वार्ता १ वार्ता प्रसंग १ से... <break time="400ms"/> जय श्री कृष्ण!
</prosody>
</voice>
</speak>"""
    c4 = edge_tts.Communicate(ssml_outro, "hi-IN-MadhurNeural")
    await c4.save("sample_outro.mp3")

    print("Character samples generated successfully!")

asyncio.run(test_character_voices())
