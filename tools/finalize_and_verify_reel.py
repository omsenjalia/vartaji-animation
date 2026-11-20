"""
Muxes clean video and master Parler-TTS audio, and runs exhaustive ffprobe verification.
"""

import os
import subprocess
import json

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr

def main():
    video_file = "reels/intro-gokulnath/final_intro_reel.mp4"
    audio_file = "reels/intro-gokulnath/audio/vo.wav"
    output_file = "reels/intro-gokulnath/final_intro_reel_with_vo.mp4"

    if not os.path.exists(video_file):
        print(f"Error: {video_file} not found!")
        return
    if not os.path.exists(audio_file):
        print(f"Error: {audio_file} not found!")
        return

    print(f"Muxing {video_file} with {audio_file} -> {output_file}...")
    mux_cmd = f'ffmpeg -y -v error -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac -b:a 192k -shortest "{output_file}"'
    code, out, err = run_cmd(mux_cmd)
    if code != 0:
        print(f"Error during ffmpeg mux: {err}")
        return

    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"Successfully muxed! File size: {file_size_mb:.2f} MB")

    # ffprobe probe
    probe_cmd = f'ffprobe -v error -show_entries format=duration,size,bit_rate -show_entries stream=codec_name,codec_type,width,height,r_frame_rate,nb_frames,sample_rate,channels -of json "{output_file}"'
    code, out, err = run_cmd(probe_cmd)
    if code == 0:
        info = json.loads(out)
        streams = info.get("streams", [])
        fmt = info.get("format", {})
        dur = float(fmt.get("duration", 0))

        v_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        a_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})

        print("\n=== FINAL REEL VERIFICATION REPORT ===")
        print(f"Output File:     {output_file}")
        print(f"Total Duration:  {dur:.3f} s (Target: 64.500 s)")
        print(f"Video Format:    {v_stream.get('width')}x{v_stream.get('height')} @ {v_stream.get('r_frame_rate')} fps ({v_stream.get('codec_name')})")
        print(f"Video Frames:    {v_stream.get('nb_frames')} frames")
        print(f"Audio Format:    {a_stream.get('codec_name')} @ {a_stream.get('sample_rate')} Hz, {a_stream.get('channels')} channels")
        print(f"Total Size:      {file_size_mb:.2f} MB")
        print("=======================================")

if __name__ == "__main__":
    main()
