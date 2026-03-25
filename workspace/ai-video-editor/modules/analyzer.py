"""
analyzer.py - Video analysis module

Shared analysis layer for V2/V3/V4 stages:
  - extract_audio()           Extract audio track
  - detect_scenes()           Scene-cut detection (frame-difference analysis)
  - extract_thumbnail()        Extract a frame as thumbnail
  - analyze_audio_energy()     Per-window RMS energy curve
  - detect_static_segments()   Detect frozen-frame segments
  - extract_scene_thumbnails() Extract one thumbnail per scene
  - analyze_content_density()  Scene + audio joint analysis (V2 Step 5)
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
            # Check if the error is "no audio stream"
            stderr = result.stderr or ""
            if "does not contain any stream" in stderr or "no audio" in stderr.lower():
                # Clean up the empty temp file created by mkstemp
                if os.path.exists(output_audio):
                    try:
                        os.remove(output_audio)
                    except OSError:
                        pass
                return ""
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
        _return_diffs: bool = False,
    ) -> list[dict] | tuple[list[dict], float, list[tuple[int, float, float]]]:
        """Detect scene cuts using frame-difference analysis.

        Args:
            input_video:         Path to the source video.
            threshold:           Diff score threshold (0–1). Lower = more sensitive.
            min_scene_duration:  Minimum scene length in seconds.
            _return_diffs:       If True, also return (fps, frame_diffs).
                                 Internal use — avoids redundant frame iteration.

        Returns:
            List of scene dicts, or (scenes, fps, frame_diffs) if _return_diffs.

        Raises:
            AnalyzerError: If the video cannot be opened.
        """
        self._require_file(input_video)

        fps, frame_diffs = self._iter_frame_diffs(input_video)
        if not frame_diffs:
            if _return_diffs:
                return [], fps, frame_diffs
            return []

        total_duration = frame_diffs[-1][1] + (1.0 / fps)
        cut_times: list[float] = [0.0]

        for _, timestamp, score in frame_diffs:
            if score > threshold:
                if timestamp - cut_times[-1] >= min_scene_duration:
                    cut_times.append(timestamp)

        cut_times.append(total_duration)

        scenes = [
            {
                "index": i,
                "start": round(cut_times[i], 3),
                "end": round(cut_times[i + 1], 3),
                "duration": round(cut_times[i + 1] - cut_times[i], 3),
            }
            for i in range(len(cut_times) - 1)
        ]

        if _return_diffs:
            return scenes, fps, frame_diffs
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

        # Video has no audio track
        if not tmp_wav or not os.path.exists(tmp_wav) or os.path.getsize(tmp_wav) == 0:
            # Get video duration to produce zero-energy windows
            cap = cv2.VideoCapture(input_video)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
                duration = frame_count / fps if fps else 0.0
            else:
                duration = 0.0
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

    # ------------------------------------------------------------------
    # analyze_content_density  (V2 Step 5)
    # ------------------------------------------------------------------

    def analyze_content_density(
        self,
        input_video: str,
        scene_threshold: float = 0.4,
        min_scene_duration: float = 1.0,
        energy_window_size: float = 1.0,
        audio_weight: float = 0.6,
        visual_weight: float = 0.4,
        content_threshold: float = 0.3,
    ) -> dict:
        """Joint scene + audio analysis to identify "content-rich" scenes.

        Combines audio energy distribution and visual frame-difference
        activity within each scene to produce a content density score.

        Args:
            input_video:         Path to the source video.
            scene_threshold:     Frame-diff threshold for scene detection (0–1).
            min_scene_duration:  Minimum scene length in seconds.
            energy_window_size:  Audio analysis window in seconds.
            audio_weight:        Weight for audio energy in final score (must be > 0).
            visual_weight:       Weight for visual activity in final score (must be > 0).
            content_threshold:   Scenes scoring above this are "has_content".

        Returns:
            {
                "scenes": [
                    {
                        "index": 0,
                        "start": 0.0, "end": 12.3, "duration": 12.3,
                        "audio_score": 0.72,     // mean energy in this scene [0,1]
                        "visual_score": 0.85,    // mean normalised diff in this scene [0,1]
                        "content_score": 0.77,   // weighted combination [0,1]
                        "has_content": true,     // content_score >= content_threshold
                    },
                    ...
                ],
                "content_scenes": [0, 2, 5],    // indices of scenes with content
                "summary": {
                    "total_scenes": 8,
                    "content_count": 3,
                    "content_ratio": 0.375,
                    "total_duration": 120.5,
                    "content_duration": 45.2,
                }
            }

        Raises:
            AnalyzerError: If analysis fails or weights are invalid.
        """
        self._require_file(input_video)

        # --- Validate & normalise weights ---
        weight_sum = audio_weight + visual_weight
        if weight_sum <= 0:
            raise AnalyzerError("audio_weight + visual_weight must be > 0")
        a_w = audio_weight / weight_sum
        v_w = visual_weight / weight_sum

        # --- Single-pass scene detection + frame diffs (avoids double iteration) ---
        scenes, fps, frame_diffs = self.detect_scenes(
            input_video,
            threshold=scene_threshold,
            min_scene_duration=min_scene_duration,
            _return_diffs=True,
        )

        if not scenes:
            return {
                "scenes": [],
                "content_scenes": [],
                "summary": {
                    "total_scenes": 0,
                    "content_count": 0,
                    "content_ratio": 0.0,
                    "total_duration": 0.0,
                    "content_duration": 0.0,
                },
            }

        energy_windows = self.analyze_audio_energy(
            input_video,
            window_size=energy_window_size,
        )

        # --- Global max frame diff for visual normalisation ---
        max_diff = max((score for _, _, score in frame_diffs), default=0.0) or 1.0

        # --- Downsample frame_diffs for visual scoring (cap ~2000 samples) ---
        total_frames = len(frame_diffs)
        sample_step = max(1, total_frames // 2000)
        sampled_diffs = frame_diffs[::sample_step]

        # --- Score each scene ---
        enriched: list[dict] = []
        content_indices: list[int] = []
        content_duration = 0.0
        total_duration = 0.0

        for scene in scenes:
            s_start = scene["start"]
            s_end = scene["end"]

            # Audio score: mean energy of windows overlapping this scene [0,1]
            audio_scores = [
                w["energy"]
                for w in energy_windows
                if w["end"] > s_start and w["start"] < s_end
            ]
            a_score = (sum(audio_scores) / len(audio_scores)) if audio_scores else 0.0

            # Visual score: mean normalised frame-diff within this scene [0,1]
            v_scores = [
                score / max_diff
                for _, timestamp, score in sampled_diffs
                if s_start <= timestamp <= s_end
            ]
            v_score = (sum(v_scores) / len(v_scores)) if v_scores else 0.0

            content_score = round(a_w * a_score + v_w * v_score, 4)
            has_content = content_score >= content_threshold

            enriched.append({
                **scene,
                "audio_score": round(a_score, 4),
                "visual_score": round(v_score, 4),
                "content_score": content_score,
                "has_content": has_content,
            })

            total_duration += scene["duration"]
            if has_content:
                content_indices.append(scene["index"])
                content_duration += scene["duration"]

        total_scenes = len(enriched)
        content_count = len(content_indices)

        return {
            "scenes": enriched,
            "content_scenes": content_indices,
            "summary": {
                "total_scenes": total_scenes,
                "content_count": content_count,
                "content_ratio": round(content_count / total_scenes, 4) if total_scenes else 0.0,
                "total_duration": round(total_duration, 3),
                "content_duration": round(content_duration, 3),
            },
        }
