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

    # ------------------------------------------------------------------
    # detect_video_type
    # ------------------------------------------------------------------

    def detect_video_type(
        self,
        input_video: str,
        sample_duration: float = 60.0,
    ) -> dict:
        """Detect video type based on visual and audio features.

        Args:
            input_video: Path to the source video.
            sample_duration: Duration (seconds) to sample for analysis.

        Returns:
            {
                "type": "interview" | "speech" | "sports" | "movie" | "funny" | "tutorial" | "vlog" | "unknown",
                "confidence": float (0-1),
                "features": {
                    "scene_change_rate": float,    # Scene changes per second
                    "face_count": int,              # Number of faces detected (sampled)
                    "speech_ratio": float,          # Ratio of time with audio energy
                    "avg_audio_energy": float,      # Average audio energy
                }
            }
        """
        self._require_file(input_video)

        # Get video duration
        duration = self._get_duration(input_video)
        sample_end = min(sample_duration, duration)

        # 1. Scene change rate
        scenes = self.detect_scenes(input_video, threshold=0.4, min_scene_duration=1.0)
        sample_scenes = [s for s in scenes if s["start"] < sample_end]
        scene_change_rate = len(sample_scenes) / sample_end if sample_end > 0 else 0.0

        # 2. Audio analysis
        audio_energy = self.analyze_audio_energy(input_video, window_size=1.0)
        sample_energy = [e for e in audio_energy if e["start"] < sample_end]
        
        if sample_energy:
            avg_energy = sum(e["energy"] for e in sample_energy) / len(sample_energy)
            # Speech ratio: windows with energy > 0.2
            speech_ratio = len([e for e in sample_energy if e["energy"] > 0.2]) / len(sample_energy)
        else:
            avg_energy = 0.0
            speech_ratio = 0.0

        # 3. Face detection (sample a few frames)
        face_count = self._detect_face_count(input_video, sample_end)

        # Build features
        features = {
            "scene_change_rate": round(scene_change_rate, 4),
            "face_count": face_count,
            "speech_ratio": round(speech_ratio, 4),
            "avg_audio_energy": round(avg_energy, 4),
        }

        # Determine video type
        video_type, confidence = self._classify_video_type(features)

        return {
            "type": video_type,
            "confidence": confidence,
            "features": features,
        }

    def _get_duration(self, input_video: str) -> float:
        """Get video duration using ffprobe."""
        cmd = [
            self.ffmpeg_path.replace("ffmpeg", "ffprobe"),
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_video,
        ]
        result = self._run(cmd, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
        return 0.0

    def _detect_face_count(self, input_video: str, sample_duration: float) -> int:
        """Detect number of faces in sampled frames."""
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            return 0

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(sample_duration * fps)
        
        # Sample 5 frames evenly
        sample_frames = [
            int(i * total_frames / 6) for i in range(1, 6)
        ]

        face_counts = []
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        for frame_idx in sample_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            face_counts.append(len(faces))

        cap.release()

        # Return max face count detected
        return max(face_counts) if face_counts else 0

    def _classify_video_type(self, features: dict) -> tuple[str, float]:
        """Classify video type based on features."""
        scene_rate = features["scene_change_rate"]
        face_count = features["face_count"]
        speech_ratio = features["speech_ratio"]
        audio_energy = features["avg_audio_energy"]

        # Interview: 2+ faces, high speech ratio, low scene change
        if face_count >= 2 and speech_ratio > 0.7 and scene_rate < 0.15:
            return "interview", 0.85

        # Speech: 1 face, high speech ratio, very low scene change
        if face_count == 1 and speech_ratio > 0.8 and scene_rate < 0.1:
            return "speech", 0.85

        # Sports: high scene change rate, high audio energy
        if scene_rate > 0.25 and audio_energy > 0.5:
            return "sports", 0.75

        # Movie: moderate scene change
        if 0.1 < scene_rate < 0.25:
            return "movie", 0.65

        # Tutorial: 1 face, moderate speech
        if face_count == 1 and 0.5 < speech_ratio < 0.9 and scene_rate < 0.15:
            return "tutorial", 0.70

        # Funny: high scene change + high audio energy
        if scene_rate > 0.2 and audio_energy > 0.6:
            return "funny", 0.60

        # Default to vlog
        return "vlog", 0.50

    # ------------------------------------------------------------------
    # score_scene
    # ------------------------------------------------------------------

    # Scoring profiles for different video types
    SCORING_PROFILES = {
        "interview": {
            "audio_energy": 0.3,
            "speech_density": 0.4,
            "face_change": 0.2,
            "scene_change": 0.1,
        },
        "sports": {
            "audio_energy": 0.3,
            "visual_intensity": 0.5,
            "scene_change": 0.2,
        },
        "movie": {
            "audio_energy": 0.2,
            "visual_intensity": 0.3,
            "scene_change": 0.3,
            "emotion_score": 0.2,
        },
        "funny": {
            "audio_energy": 0.4,
            "visual_intensity": 0.4,
            "scene_change": 0.2,
        },
        "tutorial": {
            "speech_density": 0.4,
            "visual_intensity": 0.3,
            "face_presence": 0.3,
        },
        "speech": {
            "audio_energy": 0.3,
            "speech_density": 0.4,
            "face_presence": 0.3,
        },
        "vlog": {
            "scene_change": 0.4,
            "visual_intensity": 0.3,
            "audio_energy": 0.3,
        },
        "default": {
            "audio_energy": 0.4,
            "visual_intensity": 0.4,
            "scene_change": 0.2,
        },
    }

    def score_scene(
        self,
        input_video: str,
        scene: dict,
        video_type: str = "default",
    ) -> dict:
        """Score a single scene based on multiple metrics.

        Args:
            input_video: Path to the source video.
            scene: Scene dict with start, end, duration.
            video_type: Video type for scoring profile.

        Returns:
            {
                "score": float (0-1),
                "metrics": {...},
                "reason": str,
            }
        """
        start = scene["start"]
        end = scene["end"]

        # Calculate metrics
        metrics = {}

        # 1. Audio energy
        audio_energy = self.analyze_audio_energy(input_video, window_size=0.5)
        scene_energy = [e["energy"] for e in audio_energy if e["start"] >= start and e["end"] <= end]
        metrics["audio_energy"] = sum(scene_energy) / len(scene_energy) if scene_energy else 0.0

        # 2. Visual intensity (frame diff)
        fps, frame_diffs = self._iter_frame_diffs(input_video)
        scene_diffs = [score for _, timestamp, score in frame_diffs if start <= timestamp <= end]
        metrics["visual_intensity"] = sum(scene_diffs) / len(scene_diffs) if scene_diffs else 0.0

        # 3. Speech density (ratio of high-energy audio)
        metrics["speech_density"] = len([e for e in scene_energy if e > 0.3]) / len(scene_energy) if scene_energy else 0.0

        # 4. Scene change (already have this from detect_scenes)
        metrics["scene_change"] = 1.0 / max(scene["duration"], 1.0)  # Normalized

        # Get scoring profile
        profile = self.SCORING_PROFILES.get(video_type, self.SCORING_PROFILES["default"])

        # Calculate weighted score
        score = 0.0
        for key, weight in profile.items():
            score += metrics.get(key, 0.0) * weight

        # Generate reason
        top_metrics = sorted(
            [(k, v) for k, v in metrics.items() if v > 0.5],
            key=lambda x: x[1],
            reverse=True
        )[:2]
        
        if top_metrics:
            reason = "、".join([self._metric_name(k) for k, v in top_metrics])
            reason = f"{reason}表现突出"
        else:
            reason = "综合评分较高"

        return {
            "score": round(score, 2),
            "metrics": {k: round(v, 2) for k, v in metrics.items()},
            "reason": reason,
        }

    def _metric_name(self, key: str) -> str:
        """Get Chinese name for metric."""
        names = {
            "audio_energy": "音频能量",
            "visual_intensity": "画面变化",
            "speech_density": "说话密度",
            "scene_change": "场景切换",
            "face_presence": "人脸出现",
            "face_change": "人脸切换",
            "emotion_score": "情感强度",
        }
        return names.get(key, key)

    # ------------------------------------------------------------------
    # find_safe_cut_points
    # ------------------------------------------------------------------

    def find_safe_cut_points(
        self,
        input_video: str,
        start: float,
        end: float,
        min_silence_duration: float = 0.3,
    ) -> list:
        """Detect safe cut points within a time range.

        Args:
            input_video: Path to the source video.
            start: Start time in seconds.
            end: End time in seconds.
            min_silence_duration: Minimum silence duration (seconds).

        Returns:
            List of cut points with safety scores.
        """
        cut_points = []

        # 1. Scene boundaries (safest)
        cut_points.append({
            "time": round(start, 2),
            "type": "scene_start",
            "safe": True,
            "score": 1.0,
        })
        cut_points.append({
            "time": round(end, 2),
            "type": "scene_end",
            "safe": True,
            "score": 1.0,
        })

        # 2. Detect silence points
        audio_energy = self.analyze_audio_energy(input_video, window_size=0.2)
        
        # Find silence regions
        silence_threshold = 0.1
        silence_start = None
        
        for e in audio_energy:
            if e["start"] < start or e["end"] > end:
                continue
            
            if e["energy"] < silence_threshold:
                if silence_start is None:
                    silence_start = e["start"]
            else:
                if silence_start is not None:
                    silence_duration = e["start"] - silence_start
                    if silence_duration >= min_silence_duration:
                        # Add middle point of silence
                        cut_time = silence_start + silence_duration / 2
                        cut_points.append({
                            "time": round(cut_time, 2),
                            "type": "silence",
                            "safe": True,
                            "score": 0.9,
                        })
                    silence_start = None

        # Sort by time
        cut_points.sort(key=lambda x: x["time"])
        
        return cut_points

    # ------------------------------------------------------------------
    # check_splice_compatibility
    # ------------------------------------------------------------------

    def check_splice_compatibility(
        self,
        input_video: str,
        scene1: dict,
        scene2: dict,
    ) -> dict:
        """Check if two scenes can be spliced together.

        Args:
            input_video: Path to the source video.
            scene1: First scene dict.
            scene2: Second scene dict.

        Returns:
            Compatibility result with issues and suggestions.
        """
        issues = []
        warnings = []

        # 1. Check audio energy difference
        audio_energy = self.analyze_audio_energy(input_video, window_size=0.5)
        
        e1_list = [e["energy"] for e in audio_energy 
                   if e["start"] >= scene1["start"] and e["end"] <= scene1["end"]]
        e2_list = [e["energy"] for e in audio_energy 
                   if e["start"] >= scene2["start"] and e["end"] <= scene2["end"]]
        
        avg_e1 = sum(e1_list) / len(e1_list) if e1_list else 0.0
        avg_e2 = sum(e2_list) / len(e2_list) if e2_list else 0.0
        
        energy_diff = abs(avg_e1 - avg_e2) * 100  # Scale to ~dB
        
        if energy_diff > 15:
            issues.append({
                "type": "volume_jump",
                "detail": f"音量差异约 {energy_diff:.1f}dB",
                "severity": "error",
                "suggestion": "建议进行音量均衡处理",
            })
        elif energy_diff > 10:
            warnings.append(f"音量差异约 {energy_diff:.1f}dB，建议音量均衡")

        # 2. Check visual difference (frame similarity)
        # Sample last frame of scene1 and first frame of scene2
        fps, frame_diffs = self._iter_frame_diffs(input_video)
        
        # Get visual intensity around splice point
        splice_time = scene1["end"]
        near_splice = [score for _, timestamp, score in frame_diffs 
                       if abs(timestamp - splice_time) < 1.0]
        
        if near_splice and max(near_splice) > 0.3:
            warnings.append("拼接点附近画面变化较大，建议添加过渡效果")

        # Calculate compatibility score
        if issues:
            compatible = False
            score = 0.3
        elif warnings:
            compatible = True
            score = 0.7
        else:
            compatible = True
            score = 0.9

        return {
            "compatible": compatible,
            "score": round(score, 2),
            "issues": issues,
            "warnings": warnings,
        }

    # ------------------------------------------------------------------
    # select_scenes
    # ------------------------------------------------------------------

    def select_scenes(
        self,
        input_video: str,
        top_n: int = 5,
        min_score: float = 0.3,
        video_type: str = "auto",
        with_cut_points: bool = True,
    ) -> dict:
        """Select and recommend best scenes from video.

        Args:
            input_video: Path to the source video.
            top_n: Number of scenes to return.
            min_score: Minimum score threshold.
            video_type: Video type ("auto" for auto-detect).
            with_cut_points: Include safe cut points.

        Returns:
            {
                "video_type": str,
                "total_scenes": int,
                "recommended": [...],
            }
        """
        # 1. Detect video type
        if video_type == "auto":
            type_result = self.detect_video_type(input_video)
            video_type = type_result["type"]

        # 2. Detect scenes
        scenes = self.detect_scenes(input_video)
        if not scenes:
            return {
                "video_type": video_type,
                "total_scenes": 0,
                "recommended": [],
            }

        # 3. Score each scene
        scored_scenes = []
        for scene in scenes:
            score_result = self.score_scene(input_video, scene, video_type)
            scored_scene = {
                **scene,
                "score": score_result["score"],
                "metrics": score_result["metrics"],
                "reason": score_result["reason"],
            }

            # Add cut points if requested
            if with_cut_points and score_result["score"] >= min_score:
                cut_points = self.find_safe_cut_points(
                    input_video, scene["start"], scene["end"]
                )
                scored_scene["cut_points"] = cut_points

            scored_scenes.append(scored_scene)

        # 4. Filter by min_score
        filtered = [s for s in scored_scenes if s["score"] >= min_score]

        # 5. Sort by score
        filtered.sort(key=lambda x: x["score"], reverse=True)

        # 6. Return top N
        recommended = filtered[:top_n]

        return {
            "video_type": video_type,
            "total_scenes": len(scenes),
            "recommended": recommended,
        }
