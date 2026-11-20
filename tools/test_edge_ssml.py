import asyncio
import edge_tts

async def test():
    # Test 1: Plain Madhur
    c1 = edge_tts.Communicate("आधी रात हो चुकी थी। वार्ता अभी चल रही थी।", "hi-IN-MadhurNeural", rate="-5%")
    await c1.save("test_plain.mp3")

    # Test 2: SSML with natural pacing, micro-pauses, and prosody
    ssml_narrator = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-4%" pitch="-1Hz">
आधी रात हो चुकी थी... <break time="400ms"/> वार्ता अभी चल रही थी।
</prosody>
</voice>
</speak>"""
    c2 = edge_tts.Communicate(ssml_narrator, "hi-IN-MadhurNeural")
    await c2.save("test_ssml_narrator.mp3")

    # Test 3: Gokulnathji with deep reverent pacing
    ssml_guru = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="-8%" pitch="-3Hz">
आज मैं... <break time="300ms"/> कथा का फल कह रहा हूँ।
</prosody>
</voice>
</speak>"""
    c3 = edge_tts.Communicate(ssml_guru, "hi-IN-MadhurNeural")
    await c3.save("test_ssml_guru.mp3")

    # Test 4: Young Vaishnav with natural human rate
    ssml_young = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
<voice name="hi-IN-MadhurNeural">
<prosody rate="+2%" pitch="+1Hz">
महाराजाधिराज... <break time="250ms"/> आज कथा कब कहोगे?
</prosody>
</voice>
</speak>"""
    c4 = edge_tts.Communicate(ssml_young, "hi-IN-MadhurNeural")
    await c4.save("test_ssml_young.mp3")

    print("Generated 4 test files successfully!")

asyncio.run(test())
