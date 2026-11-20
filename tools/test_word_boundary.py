import asyncio
import edge_tts

async def test():
    c = edge_tts.Communicate(
        "आधी रात हो चुकी थी।",
        "hi-IN-MadhurNeural",
        boundary="WordBoundary"
    )
    
    async for chunk in c.stream():
        if chunk["type"] == "WordBoundary":
            start_sec = chunk["offset"] / 10_000_000
            dur_sec = chunk["duration"] / 10_000_000
            text = chunk["text"]
            print(f"Word: '{text}' | start={start_sec:.3f}s | dur={dur_sec:.3f}s | end={start_sec+dur_sec:.3f}s")

asyncio.run(test())
