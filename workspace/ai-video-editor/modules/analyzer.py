"""
analyzer.py - 视频分析模块

提供共用的视频分析能力，供 V2/V3/V4 阶段复用：
  - extract_audio()        提取音频轨道
  - detect_scenes()        场景切换检测
  - extract_thumbnail()    提取帧缩略图
  - analyze_audio_energy() 音频能量曲线分析
"""

import os
import re
import subprocess
import tempfile
from typing import Optional

import cv2
import numpy as np


class AnalyzerError(Exception):
    pass


class Analyzer:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run(self, cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )

    def _require_file(self, path: str) -> None:
        if not os.path.exists(path):
            raise AnalyzerError(f"File not found: {path}")

    # ------------------------------------------------------------------
    # extract_audio
    # ------------------------------------------------------------------

    def extract_audio(
        self,
        input_video: str,
        output_audio: Optional[str] = None,
        sample_rate: int = 16000,
        channels: int = 1,
    ) -> str:
        """Extract audio track from a video file.

        Args:
            input_video:  Path to the source video.
            output_audio: Destination path (.wav/.mp3/etc.).
                          Defaults to a temp .wav file.
            sample_rate:  Output sample rate in Hz (default 16000 for Whisper).
            channels:     Number of audio channels (default 1 = mono).

        Returns:
            Absolute path to the extracted audio file.

        Raises:
            AnalyzerError: If extraction fails.
        """
        self._require_file(input_video)

        if output_audio is None:
            fd, output_audio = tempfile.mkstemp(suffix=".wav", prefix="audio_")
            os.close(fd)

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", input_video,
            "-vn",                          # drop video stream
            "-ar", str(sample_rate),        # sample rate
            "-ac", str(channels),           # channels
            "-f", "wav",
            output_audio,
        ]

        result = self._run(cmd)
        if result.returncode != 0 or not os.path.exists(output_audio):
            raise AnalyzerError(
                f"Audio extraction failed.\nFFmpeg stderr:\n{result.stderr[-500:]}"
            )

        return os.path.abspath(output_audio)

    # ------------------------------------------------------------------
    # detect_scenes
    # ------------------------------------------------------------------

    def detect_scenes(
        self,
        input_video: str,
        threshold: float = 0.4,
        min_scene_duration: float = 1.0,
    ) -> list[dict]:
        """Detect scene cuts in a video using frame-difference analysis (OpenCV).

        Args:
            input_video:          Path to the source video.
            threshold:            Frame-difference threshold (0–1).
                                  Lower = more sensitive. Default 0.4.
            min_scene_duration:   Minimum scene length in seconds. Scenes
                                  shorter than this are merged into the previous.

        Returns:
            List of scene dicts, e.g.:
            [
              {"index": 0, "start": 0.0,  "end": 12.3, "duration": 12.3},
              {"index": 1, "start": 12.3, "end": 25.0, "duration": 12.7},
              ...
            ]

        Raises:
            AnalyzerError: If the video cannot be opened.
        """
        self._require_file(input_video)

        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            raise AnalyzerError(f"Cannot open video: {input_video}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        total_duration = total_frames / fps

        cut_times: list[float] = [0.0]  # scene start times

        prev_gray: Optional[np.ndarray] = None
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_gray is not None:
                diff = cv2.absdiff(gray, prev_gray)
                score = diff.mean() / 255.0
                if score > threshold:
                    timestamp = frame_idx / fps
                    # Enforce minimum scene duration
                    if timestamp - cut_times[-1] >= min_scene_duration:
                        cut_times.append(timestamp)

            prev_gray = gray
            frame_idx += 1

        cap.release()

        cut_times.append(total_duration)

        scenes = []
        for i in range(len(cut_times) - 1):
            start = round(cut_times[i], 3)
            end = round(cut_times[i + 1], 3)
            scenes.append({
                "index": i,
                "start": start,
                "end": end,
                "duration": round(end - start, 3),
            })

        return scenes

    # ------------------------------------------------------------------
    # extract_thumbnail
    # ------------------------------------------------------------------

    def extract_thumbnail(
        self,
        input_video: str,
        timestamp: float,
        output_image: Optional[str] = None,
        width: int = 320,
    ) -> str:
        """Extract a single frame as a thumbnail image.

        Args:
            input_video:  Path to the source video.
            timestamp:    Time in seconds to capture.
            output_image: Destination path (.jpg/.png).
                          Defaults to a temp .jpg file.
            width:        Output image width in pixels (height auto-scaled).

        Returns:
            Absolute path to the thumbnail image.

        Raises:
            AnalyzerError: If extraction fails.
        """
        self._require_file(input_video)

        if output_image is None:
            fd, output_image = tempfile.mkstemp(suffix=".jpg", prefix="thumb_")
            os.close(fd)

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-ss", str(timestamp),
            "-i", input_video,
            "-vframes", "1",
            "-vf", f"scale={width}:-1",
            output_image,
        ]

        result = self._run(cmd, timeout=30)
        if result.returncode != 0 or not os.path.exists(output_image):
            raise AnalyzerError(
                f"Thumbnail extraction failed at {timestamp}s.\n"
                f"FFmpeg stderr:\n{result.stderr[-300:]}"
            )

        return os.path.abspath(output_image)

    # ------------------------------------------------------------------
    # analyze_audio_energy
    # ------------------------------------------------------------------

    def analyze_audio_energy(
        self,
        input_video: str,
        window_size: float = 1.0,
    ) -> list[dict]:
        """Compute RMS audio energy per time window.

        Useful for detecting high-energy (exciting) segments in V4.

        Args:
            input_video:  Path to the source video.
            window_size:  Analysis window in seconds (default 1.0).

        Returns:
            List of energy dicts, e.g.:
            [
              {"start": 0.0,  "end": 1.0,  "energy": 0.032},
              {"start": 1.0,  "end": 2.0,  "energy": 0.187},
              ...
            ]
            Energy values are normalised to [0, 1].

        Raises:
            AnalyzerError: If audio extraction or analysis fails.
        """
        self._require_file(input_video)

        # Step 1: extract audio to temp wav
        tmp_wav = self.extract_audio(input_video, sample_rate=16000, channels=1)

        try:
            # Step 2: read wav with ffmpeg → raw PCM via pipe
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-i", tmp_wav,
                "-f", "s16le",   # signed 16-bit little-endian PCM
                "-ar", "16000",
                "-ac", "1",
                "pipe:1",
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode != 0:
                raise AnalyzerError("Failed to decode audio to PCM")

            # Step 3: parse PCM samples
            samples = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32)
            samples /= 32768.0  # normalise to [-1, 1]

            sample_rate = 16000
            window_samples = int(window_size * sample_rate)

            windows = []
            for i in range(0, len(samples), window_samples):
                chunk = samples[i: i + window_samples]
                if len(chunk) == 0:
                    continue
                rms = float(np.sqrt(np.mean(chunk ** 2)))
                start = i / sample_rate
                end = (i + len(chunk)) / sample_rate
                windows.append({"start": round(start, 3), "end": round(end, 3), "energy": rms})

            # Step 4: normalise energy to [0, 1]
            if windows:
                max_energy = max(w["energy"] for w in windows) or 1.0
                for w in windows:
                    w["energy"] = round(w["energy"] / max_energy, 4)

            return windows

        finally:
            if os.path.exists(tmp_wav):
                os.remove(tmp_wav)

    # ------------------------------------------------------------------
    # remove_static  (实现 Executor 中的空壳)
    # ------------------------------------------------------------------

    def detect_static_segments(
        self,
        input_video: str,
        threshold: float = 0.01,
        min_static_duration: float = 1.0,
    ) -> list[tuple[float, float]]:
        """Detect static (frozen-frame) segments using frame-difference analysis.

        Args:
            input_video:          Path to the source video.
            threshold:            Mean per-pixel diff threshold (0–1).
                                  Below this = static. Default 0.01.
            min_static_duration:  Minimum consecutive static time (seconds)
                                  before a segment is reported.

        Returns:
            List of (start, end) tuples for static segments (in seconds).

        Raises:
            AnalyzerError: If the video cannot be opened.
        """
        self._require_file(input_video)

        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            raise AnalyzerError(f"Cannot open video: {input_video}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        static_segments: list[tuple[float, float]] = []

        prev_gray: Optional[np.ndarray] = None
        static_start: Optional[float] = None
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            timestamp = frame_idx / fps

            if prev_gray is not None:
                diff = cv2.absdiff(gray, prev_gray)
                score = diff.mean() / 255.0

                if score < threshold:
                    # Frame is static
                    if static_start is None:
                        static_start = (frame_idx - 1) / fps
                else:
                    # Frame changed — close any open static segment
                    if static_start is not None:
                        duration = timestamp - static_start
                        if duration >= min_static_duration:
                            static_segments.append((
                                round(static_start, 3),
                                round(timestamp, 3),
                            ))
                        static_start = None

            prev_gray = gray
            frame_idx += 1

        # Close segment that runs to end of video
        if static_start is not None:
            end_time = frame_idx / fps
            duration = end_time - static_start
            if duration >= min_static_duration:
                static_segments.append((round(static_start, 3), round(end_time, 3)))

        cap.release()
        return static_segments
