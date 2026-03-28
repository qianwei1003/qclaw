"""
audio.py - 音频处理模块

Audio extraction and analysis:
  - extract_audio()        Extract audio track from video
  - analyze_audio_energy() Compute RMS energy per time window
"""

import os
import subprocess
import tempfile
from typing import Optional

import numpy as np

from .utils import run_cmd, require_file, get_duration


class AudioError(Exception):
    pass


def extract_audio(
    input_video: str,
    output_audio: Optional[str] = None,
    sample_rate: int = 16000,
    channels: int = 1,
    ffmpeg_path: str = "ffmpeg",
) -> str | None:
    """Extract audio track from a video file.

    Args:
        input_video:  Path to the source video.
        output_audio: Destination path (.wav/.mp3/etc.).
                      Defaults to a temp .wav file.
        sample_rate:  Output sample rate in Hz (default 16000 for Whisper).
        channels:     Number of audio channels (default 1 = mono).

    Returns:
        Absolute path to the extracted audio file.
        Returns None if the video has no audio stream.

    Raises:
        AudioError: If extraction fails for other reasons.
    """
    require_file(input_video)

    if output_audio is None:
        fd, output_audio = tempfile.mkstemp(suffix=".wav", prefix="audio_")
        os.close(fd)

    cmd = [
        ffmpeg_path,
        "-y",
        "-i", input_video,
        "-vn",
        "-ar", str(sample_rate),
        "-ac", str(channels),
        "-f", "wav",
        output_audio,
    ]

    result = run_cmd(cmd)
    if result.returncode != 0 or not os.path.exists(output_audio):
        stderr = result.stderr or ""
        if "does not contain any stream" in stderr or "no audio" in stderr.lower():
            if os.path.exists(output_audio):
                try:
                    os.remove(output_audio)
                except OSError:
                    pass
            return None
        raise AudioError(
            f"Audio extraction failed.\nFFmpeg stderr:\n{result.stderr[-500:]}"
        )

    return os.path.abspath(output_audio)


def analyze_audio_energy(
    input_video: str,
    window_size: float = 1.0,
    sample_rate: int = 16000,
    ffmpeg_path: str = "ffmpeg",
) -> list[dict]:
    """Compute RMS audio energy per time window.

    Args:
        input_video:  Path to the source video.
        window_size:  Analysis window in seconds (default 1.0).
        sample_rate:  Sample rate for audio decoding (default 16000).

    Returns:
        List of energy dicts (energy normalised to [0, 1]):
        [{"start": 0.0, "end": 1.0, "energy": 0.032}, ...]

    Raises:
        AudioError: If audio extraction or analysis fails.
    """
    require_file(input_video)

    tmp_wav = extract_audio(input_video, sample_rate=sample_rate, channels=1, ffmpeg_path=ffmpeg_path)

    # Video has no audio track
    if tmp_wav is None:
        duration = get_duration(input_video, ffmpeg_path)
        windows: list[dict] = []
        window_count = int(duration / window_size) if window_size > 0 else 0
        for i in range(max(window_count, 0)):
            windows.append({
                "start": round(i * window_size, 3),
                "end": round((i + 1) * window_size, 3),
                "energy": 0.0,
            })
        return windows

    try:
        cmd = [
            ffmpeg_path,
            "-y",
            "-i", tmp_wav,
            "-f", "s16le",
            "-ar", str(sample_rate),
            "-ac", "1",
            "pipe:1",
        ]
        # Use subprocess directly for binary output (not run_cmd which decodes text)
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise AudioError("Failed to decode audio to PCM")

        samples = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32)
        samples /= 32768.0

        window_samples = int(window_size * sample_rate)
        windows: list[dict] = []

        for i in range(0, len(samples), window_samples):
            chunk = samples[i: i + window_samples]
            if len(chunk) == 0:
                continue
            rms = float(np.sqrt(np.mean(chunk ** 2)))
            windows.append({
                "start": round(i / sample_rate, 3),
                "end": round((i + len(chunk)) / sample_rate, 3),
                "energy": rms,
            })

        if windows:
            max_energy = max(w["energy"] for w in windows) or 1.0
            for w in windows:
                w["energy"] = round(w["energy"] / max_energy, 4)

        return windows

    finally:
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)