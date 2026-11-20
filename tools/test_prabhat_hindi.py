import asyncio
import edge_tts

async def test():
    try:
        c = edge_tts.Communicate("आधी रात हो चुकी थी। वार्ता अभी चल रही थी।", "en-IN-PrabhatNeural")
        await c.save("test_prabhat.mp3")
        print("Prabhat succeeded!")
    except Exception as e:
        print("Prabhat failed:", e)

    try:
        c2 = edge_tts.Communicate("महाराजाधिराज, आज कथा कब कहोगे?", "bn-IN-BashkarNeural")
        await c2.save("test_bashkar.mp3")
        print("Bashkar succeeded!")
    except Exception as e:
        print("Bashkar failed:", e)

    try:
        c3 = edge_tts.Communicate("महाराजाधिराज, आज कथा कब कहोगे?", "gu-IN-NiranjanNeural")
        await c3.save("test_niranjan.mp3")
        print("Niranjan succeeded!")
    except Exception as e:
        print("Niranjan failed:", e)

asyncio.run(test())
