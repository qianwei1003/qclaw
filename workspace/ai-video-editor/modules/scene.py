"""
scene.py - 场景检测与处理

Scene detection and processing:
  - detect_scenes()            Detect scene cuts
  - detect_static_segments()   Detect frozen-frame segments
  - extract_thumbnail()        Extract a frame as thumbnail
  - extract_scene_thumbnails() Extract one thumbnail per scene
"""

import os
import tempfile
from typing import Optional

import cv2

from .utils import run_cmd, require_file, iter_frame_diffs


class SceneError(Exception):
    pass


def detect_scenes(
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

    Returns:
        List of scene dicts, or (scenes, fps, frame_diffs) if _return_diffs.
    """
    require_file(input_video)

    fps, frame_diffs = iter_frame_diffs(input_video)
    if not frame_diffs:
        if _return_diffs:
            return [], fps, frame_diffs
        return []

    # Use last frame timestamp as total duration (more reliable than +1/fps)
    total_duration = frame_diffs[-1][1]
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


def detect_static_segments(
    input_video: str,
    threshold: float = 0.01,
    min_static_duration: float = 1.0,
    frame_diffs: list[tuple[int, float, float]] = None,
    fps: float = None,
) -> list[tuple[float, float]]:
    """Detect static (frozen-frame) segments using frame-difference analysis.

    Args:
        input_video:          Path to the source video.
        threshold:            Diff score threshold (0–1). Below = static.
        min_static_duration:  Minimum consecutive static seconds to report.
        frame_diffs:          Pre-computed frame diffs (optional, for reuse).
        fps:                  Video fps (required if frame_diffs provided).

    Returns:
        List of (start, end) tuples for static segments (seconds).
    """
    require_file(input_video)

    if frame_diffs is None or fps is None:
        fps, frame_diffs = iter_frame_diffs(input_video)
    
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

    if static_start is not None and frame_diffs:
        end_time = frame_diffs[-1][1]
        duration = end_time - static_start
        if duration >= min_static_duration:
            static_segments.append((round(static_start, 3), round(end_time, 3)))

    return static_segments


def extract_thumbnail(
    input_video: str,
    timestamp: float,
    output_image: Optional[str] = None,
    width: int = 320,
    ffmpeg_path: str = "ffmpeg",
    accurate_seek: bool = False,
) -> str:
    """Extract a single frame as a thumbnail image.

    Args:
        input_video:  Path to the source video.
        timestamp:    Time in seconds to capture.
        output_image: Destination path (.jpg/.png). Defaults to a temp .jpg.
        width:        Output image width in pixels (height auto-scaled).
        accurate_seek: If True, use accurate but slower seek (input option).

    Returns:
        Absolute path to the thumbnail image.

    Raises:
        SceneError: If timestamp is negative or extraction fails.
    """
    require_file(input_video)

    if timestamp < 0:
        raise SceneError(f"Timestamp must be non-negative: {timestamp}")

    if output_image is None:
        fd, output_image = tempfile.mkstemp(suffix=".jpg", prefix="thumb_")
        os.close(fd)

    if accurate_seek:
        # Accurate but slower: -ss after -i
        cmd = [
            ffmpeg_path,
            "-y",
            "-i", input_video,
            "-ss", str(timestamp),
            "-vframes", "1",
            "-vf", f"scale={width}:-1",
            output_image,
        ]
    else:
        # Fast but slightly imprecise: -ss before -i
        cmd = [
            ffmpeg_path,
            "-y",
            "-ss", str(timestamp),
            "-i", input_video,
            "-vframes", "1",
            "-vf", f"scale={width}:-1",
            output_image,
        ]

    result = run_cmd(cmd, timeout=30)
    if result.returncode != 0 or not os.path.exists(output_image):
        raise SceneError(
            f"Thumbnail extraction failed at {timestamp}s.\n"
            f"FFmpeg stderr:\n{result.stderr[-300:]}"
        )

    return os.path.abspath(output_image)


def extract_scene_thumbnails(
    input_video: str,
    scenes: list[dict],
    output_dir: Optional[str] = None,
    width: int = 320,
    ffmpeg_path: str = "ffmpeg",
    accurate_seek: bool = False,
) -> list[str]:
    """Extract one thumbnail per detected scene.

    Args:
        input_video:     Path to the source video.
        scenes:          List of scene dicts from detect_scenes().
        output_dir:      Directory to save thumbnails. Defaults to a temp dir.
        width:           Output image width in pixels (height auto-scaled).
        accurate_seek:   If True, use accurate but slower seek.

    Returns:
        List of absolute paths to the saved thumbnail images.
    """
    require_file(input_video)

    if not scenes:
        return []

    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="thumbs_")
    else:
        os.makedirs(output_dir, exist_ok=True)

    paths: list[str] = []
    for scene in scenes:
        mid_time = (scene["start"] + scene["end"]) / 2.0
        filename = f"scene_{scene['index']:03d}.jpg"
        output_path = os.path.join(output_dir, filename)
        saved = extract_thumbnail(input_video, mid_time, output_path, width, ffmpeg_path, accurate_seek)
        paths.append(saved)

    return paths