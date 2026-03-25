"""
analyzer.py - Video analysis module

Shared analysis layer for V2/V3/V4 stages:
  - extract_audio()           Extract audio track
  - detect_scenes()           Scene-cut detection (frame-difference analysis)
  - extract_thumbnail()        Extract a frame as thumbnail
  - analyze_audio_energy()     Per-window RMS energy curve
  - detect_static_segments()   Detect frozen-frame segments
  - extract_scene_thumbnails() Extract one thumbnail per scene
"""

import os
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

    def _iter_frame_diffs(
        self,
        input_video: str,
    ) -> tuple[float, list[tuple[int, float, float]]]:
        """Iterate over frames and compute per-frame grayscale diff scores.

        Args:
            input_video: Path to the source video.

        Returns:
            (fps, [(frame_idx, timestamp, diff_score), ...])
            diff_score is mean absolute pixel diff normalised to [0, 1].
            First frame has diff_score = 0.0 (no previous frame).

        Raises:
            AnalyzerError: If the video cannot be opened.
        """
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            raise AnalyzerError(f"Cannot open video: {input_video}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        results: list[tuple[int, float, float]] = []
        prev_gray: Optional[np.ndarray] = None
        frame_idx = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                timestamp = frame_idx / fps

                if prev_gray is not None:
                    diff = cv2.absdiff(gray, prev_gray)
                    score = float(diff.mean()) / 255.0
                else:
                    score = 0.0

                results.append((frame_idx, timestamp, score))
                prev_gray = gray
                frame_idx += 1
        finally:
            cap.release()

        return fps, results

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
            "-vn",
            "-ar", str(sample_rate),
            "-ac", str(channels),
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
        """Detect scene cuts using frame-difference analysis.

        Args:
            input_video:         Path to the source video.
            threshold:           Diff score threshold (0–1). Lower = more sensitive.
            min_scene_duration:  Minimum scene length in seconds.

        Returns:
            List of scene dicts:
            [{"index": 0, "start": 0.0, "end": 12.3, "duration": 12.3}, ...]

        Raises:
            AnalyzerError: If the video cannot be opened.
        """
        self._require_file(input_video)

        fps, frame_diffs = self._iter_frame_diffs(input_video)
        if not frame_diffs:
            return []

        total_duration = frame_diffs[-1][1] + (1.0 / fps)
        cut_times: list[float] = [0.0]

        for _, timestamp, score in frame_diffs:
            if score > threshold:
                if timestamp - cut_times[-1] >= min_scene_duration:
                    cut_times.append(timestamp)

        cut_times.append(total_duration)

        return [
            {
                "index": i,
                "start": round(cut_times[i], 3),
                "end": round(cut_times[i + 1], 3),
                "duration": round(cut_times[i + 1] - cut_times[i], 3),
            }
            for i in range(len(cut_times) - 1)
        ]

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
            output_image: Destination path (.jpg/.png). Defaults to a temp .jpg.
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
        sample_rate: int = 16000,
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
            AnalyzerError: If audio extraction or analysis fails.
        """
        self._require_file(input_video)

        tmp_wav = self.extract_audio(input_video, sample_rate=sample_rate, channels=1)

        try:
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-i", tmp_wav,
                "-f", "s16le",
                "-ar", str(sample_rate),
                "-ac", "1",
                "pipe:1",
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode != 0:
                raise AnalyzerError("Failed to decode audio to PCM")

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

    # ------------------------------------------------------------------
    # detect_static_segments
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
            threshold:            Diff score threshold (0–1). Below = static.
            min_static_duration:  Minimum consecutive static seconds to report.

        Returns:
            List of (start, end) tuples for static segments (seconds).

        Raises:
            AnalyzerError: If the video cannot be opened.
        """
        self._require_file(input_video)

        fps, frame_diffs = self._iter_frame_diffs(input_video)
        static_segments: list[tuple[float, float]] = []
        static_start: Optional[float] = None

        for frame_idx, timestamp, score in frame_diffs:
            if score < threshold:
                if static_start is None:
                    static_start = max(0.0, timestamp - (1.0 / fps))
            else:
                if static_start is not None:
                    duration = timestamp - static_start
                    if duration >= min_static_duration:
                        static_segments.append((round(static_start, 3), round(timestamp, 3)))
                    static_start = None

        # Close segment that runs to end of video
        if static_start is not None and frame_diffs:
            end_time = frame_diffs[-1][1] + (1.0 / fps)
            duration = end_time - static_start
            if duration >= min_static_duration:
                static_segments.append((round(static_start, 3), round(end_time, 3)))

        return static_segments

    # ------------------------------------------------------------------
    # extract_scene_thumbnails
    # ------------------------------------------------------------------

    def extract_scene_thumbnails(
        self,
        input_video: str,
        scenes: list[dict],
        output_dir: Optional[str] = None,
        width: int = 320,
    ) -> list[str]:
        """Extract one thumbnail per detected scene.

        Args:
            input_video:     Path to the source video.
            scenes:          List of scene dicts from detect_scenes().
            output_dir:      Directory to save thumbnails. Defaults to a temp dir.
            width:           Output image width in pixels (height auto-scaled).

        Returns:
            List of absolute paths to the saved thumbnail images.

        Raises:
            AnalyzerError: If extraction fails.
        """
        self._require_file(input_video)

        if not scenes:
            return []

        if output_dir is None:
            fd, output_dir = tempfile.mkstemp(dir=".", suffix="_thumbs")[0]
            os.close(fd)
            output_dir = os.path.dirname(output_dir) or "."
        else:
            os.makedirs(output_dir, exist_ok=True)

        paths: list[str] = []
        for scene in scenes:
            mid_time = (scene["start"] + scene["end"]) / 2.0
            filename = f"scene_{scene['index']:03d}.jpg"
            output_path = os.path.join(output_dir, filename)
            saved = self.extract_thumbnail(input_video, mid_time, output_path, width)
            paths.append(saved)

        return paths
