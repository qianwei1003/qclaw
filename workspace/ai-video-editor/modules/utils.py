"""
utils.py - 公共工具方法

Shared utilities for all modules:
  - _run()              Run subprocess with timeout
  - _require_file()     Check file exists
  - _iter_frame_diffs() Iterate frames and compute diff scores
  - _get_duration()     Get video duration via ffprobe
"""

import os
import subprocess
from typing import Optional

import cv2
import numpy as np


class UtilsError(Exception):
    pass


def run_cmd(
    cmd: list[str],
    timeout: int = 300,
) -> subprocess.CompletedProcess:
    """Run command with timeout."""
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        raise UtilsError(f"Command timed out after {timeout}s: {' '.join(cmd[:3])}...") from e


def require_file(path: str) -> None:
    """Raise if file not found."""
    if not os.path.exists(path):
        raise UtilsError(f"File not found: {path}")


def get_duration(
    input_video: str,
    ffmpeg_path: str = "ffmpeg",
) -> float:
    """Get video duration using ffprobe."""
    require_file(input_video)
    
    ffprobe_path = ffmpeg_path.replace("ffmpeg", "ffprobe")
    cmd = [
        ffprobe_path,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_video,
    ]
    result = run_cmd(cmd, timeout=30)
    if result.returncode == 0 and result.stdout.strip():
        try:
            return float(result.stdout.strip())
        except ValueError:
            pass
    raise UtilsError(f"Failed to get duration: {input_video}")


def iter_frame_diffs(
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
        UtilsError: If the video cannot be opened.
    """
    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        raise UtilsError(f"Cannot open video: {input_video}")

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