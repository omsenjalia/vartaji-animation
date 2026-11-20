import inspect
import edge_tts

c = edge_tts.Communicate("test", "hi-IN-MadhurNeural")
print("edge_tts Communicate attributes / methods:")
for m in dir(c):
    if not m.startswith("__"):
        print(" -", m)

# Let's inspect how Communicate builds the request
import edge_tts.communicate
src = inspect.getsource(edge_tts.communicate.Communicate)
print("\nFirst 40 lines of Communicate source:")
for line in src.splitlines()[:40]:
    print(line)
