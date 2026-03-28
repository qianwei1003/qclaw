"""
content.py - 内容分析模块

Content analysis and scene scoring:
  - analyze_content_density()  Scene + audio joint analysis
  - detect_video_type()        Video type classification
  - score_scene()              Score a single scene
  - find_safe_cut_points()     Detect safe cut points
  - check_splice_compatibility() Check scene compatibility
  - select_scenes()            Select best scenes
"""

import os
from typing import Optional

import cv2
import yaml

from .utils import require_file, iter_frame_diffs, get_duration
from .audio import analyze_audio_energy
from .scene import detect_scenes


class ContentError(Exception):
    pass


# Default config path
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")

# Config cache
_config_cache: dict | None = None


def load_config(config_path: str = None, use_cache: bool = True) -> dict:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to config file. Defaults to config.yaml in project root.
        use_cache: If True, return cached config if available.
    
    Returns:
        Configuration dict.
    """
    global _config_cache
    
    if use_cache and _config_cache is not None:
        return _config_cache
    
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}
    
    if use_cache:
        _config_cache = config
    
    return config


def analyze_content_density(
    input_video: str,
    scene_threshold: float = 0.4,
    min_scene_duration: float = 1.0,
    energy_window_size: float = 1.0,
    audio_weight: float = 0.6,
    visual_weight: float = 0.4,
    content_threshold: float = 0.3,
) -> dict:
    """Joint scene + audio analysis to identify "content-rich" scenes."""
    require_file(input_video)

    # Validate & normalise weights
    weight_sum = audio_weight + visual_weight
    if weight_sum <= 0:
        raise ContentError("audio_weight + visual_weight must be > 0")
    a_w = audio_weight / weight_sum
    v_w = visual_weight / weight_sum

    # Single-pass scene detection + frame diffs
    scenes, fps, frame_diffs = detect_scenes(
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

    energy_windows = analyze_audio_energy(input_video, window_size=energy_window_size)

    # Global max frame diff for visual normalisation
    # Note: If video is all-black, max_diff will be 0.0, then we use 1.0 to avoid division by zero.
    # In that case, all visual scores will be 0.0 (since all frame diffs are 0).
    max_diff = max((score for _, _, score in frame_diffs), default=0.0) or 1.0

    # Downsample frame_diffs for visual scoring
    # Note: Sampling reduces precision at scene boundaries, but for visual scoring
    # (averaging over scene duration) this is acceptable.
    total_frames = len(frame_diffs)
    sample_step = max(1, total_frames // 2000)
    sampled_diffs = frame_diffs[::sample_step]

    # Score each scene
    enriched: list[dict] = []
    content_indices: list[int] = []
    content_duration = 0.0
    total_duration = 0.0

    for scene in scenes:
        s_start = scene["start"]
        s_end = scene["end"]

        audio_scores = [
            w["energy"]
            for w in energy_windows
            if w["end"] > s_start and w["start"] < s_end
        ]
        a_score = (sum(audio_scores) / len(audio_scores)) if audio_scores else 0.0

        # Use sampled diffs for visual scoring (faster, slightly less precise)
        v_scores = [
            score / max_diff
            for _, timestamp, score in sampled_diffs
            if s_start <= timestamp <= s_end
        ]
        # If no sampled points in scene, fall back to original frame_diffs
        if not v_scores:
            v_scores = [
                score / max_diff
                for _, timestamp, score in frame_diffs
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


# Placeholder for remaining methods - will be implemented in next step
def detect_video_type(input_video: str, sample_duration: float = 60.0, config: dict = None) -> dict:
    """Detect video type based on visual and audio features."""
    # TODO: Implement
    return {"type": "unknown", "confidence": 0.0, "features": {}}


def score_scene(input_video: str, scene: dict, video_type: str = "default", config: dict = None) -> dict:
    """Score a single scene based on multiple metrics."""
    # TODO: Implement
    return {"score": 0.0, "metrics": {}, "reason": "Not implemented"}


def find_safe_cut_points(input_video: str, start: float, end: float, min_silence_duration: float = 0.3) -> list:
    """Detect safe cut points within a time range."""
    # TODO: Implement
    return []


def check_splice_compatibility(input_video: str, scene1: dict, scene2: dict) -> dict:
    """Check if two scenes can be spliced together."""
    # TODO: Implement
    return {"compatible": True, "score": 0.0, "issues": [], "warnings": []}


def select_scenes(input_video: str, top_n: int = 5, min_score: float = 0.3, video_type: str = "auto", with_cut_points: bool = True, config: dict = None) -> dict:
    """Select and recommend best scenes from video."""
    # TODO: Implement
    return {"video_type": "unknown", "total_scenes": 0, "recommended": []}