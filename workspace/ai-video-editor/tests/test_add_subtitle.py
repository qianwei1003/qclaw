import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.subtitle import transcribe, generate_srt

if __name__ == "__main__":
    input_video = os.path.join(os.path.dirname(__file__), "zimu.mp4")
    srt_output = "tests/zimu.srt"
    language = "zh"
    model = "medium"

    print(f"Transcribing {input_video} ...")
    segments = transcribe(input_video, language=language, model=model)
    print(f"Transcription done. {len(segments)} segments.")

    print(f"Generating SRT file: {srt_output} ...")
    generate_srt(segments, srt_output)
    print("SRT generation complete.")

    if os.path.exists(srt_output):
        print(f"SRT file generated: {srt_output}")
    else:
        print("SRT file generation failed.")
