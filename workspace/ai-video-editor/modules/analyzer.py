"""
analyzer.py - 视频分析统一入口

Unified entry point for video analysis.
Delegates to specialized modules:
  - audio.py    Audio extraction and analysis
  - scene.py    Scene detection and processing
  - content.py  Content analysis and scoring
  - subtitle.py Subtitle transcription and generation
"""

import os
import yaml
from typing import Optional

from .audio import extract_audio, analyze_audio_energy, AudioError
from .scene import (
    detect_scenes,
    detect_static_segments,
    extract_thumbnail,
    extract_scene_thumbnails,
    SceneError,
)
from .content import (
    analyze_content_density,
    detect_video_type,
    score_scene,
    find_safe_cut_points,
    check_splice_compatibility,
    select_scenes,
    load_config,
    ContentError,
)
from .subtitle import (
    transcribe,
    generate_srt,
    format_subtitle_style,
    SubtitleError,
)


class AnalyzerError(Exception):
    """Unified error for analyzer module."""
    pass


# Default config path
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")


class Analyzer:
    """
    Video analyzer - unified entry point.
    
    Delegates to specialized modules while maintaining API compatibility.
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg", config_path: str = None):
        self.ffmpeg_path = ffmpeg_path
        self.config = load_config(config_path)
    
    # ------------------------------------------------------------------
    # Audio methods (delegate to audio.py)
    # ------------------------------------------------------------------
    
    def extract_audio(
        self,
        input_video: str,
        output_audio: Optional[str] = None,
        sample_rate: int = 16000,
        channels: int = 1,
    ) -> str:
        """Extract audio track from video."""
        try:
            return extract_audio(
                input_video, output_audio, sample_rate, channels, self.ffmpeg_path
            )
        except AudioError as e:
            raise AnalyzerError(str(e)) from e
    
    def analyze_audio_energy(
        self,
        input_video: str,
        window_size: float = 1.0,
        sample_rate: int = 16000,
    ) -> list[dict]:
        """Compute RMS audio energy per time window."""
        try:
            return analyze_audio_energy(
                input_video, window_size, sample_rate, self.ffmpeg_path
            )
        except AudioError as e:
            raise AnalyzerError(str(e)) from e
    
    # ------------------------------------------------------------------
    # Scene methods (delegate to scene.py)
    # ------------------------------------------------------------------
    
    def detect_scenes(
        self,
        input_video: str,
        threshold: float = 0.4,
        min_scene_duration: float = 1.0,
        _return_diffs: bool = False,
    ):
        """Detect scene cuts using frame-difference analysis."""
        try:
            return detect_scenes(
                input_video, threshold, min_scene_duration, _return_diffs
            )
        except SceneError as e:
            raise AnalyzerError(str(e)) from e
    
    def detect_static_segments(
        self,
        input_video: str,
        threshold: float = 0.01,
        min_static_duration: float = 1.0,
    ) -> list[tuple[float, float]]:
        """Detect static (frozen-frame) segments."""
        try:
            return detect_static_segments(
                input_video, threshold, min_static_duration
            )
        except SceneError as e:
            raise AnalyzerError(str(e)) from e
    
    def extract_thumbnail(
        self,
        input_video: str,
        timestamp: float,
        output_image: Optional[str] = None,
        width: int = 320,
    ) -> str:
        """Extract a single frame as thumbnail."""
        try:
            return extract_thumbnail(
                input_video, timestamp, output_image, width, self.ffmpeg_path
            )
        except SceneError as e:
            raise AnalyzerError(str(e)) from e
    
    def extract_scene_thumbnails(
        self,
        input_video: str,
        scenes: list[dict],
        output_dir: Optional[str] = None,
        width: int = 320,
    ) -> list[str]:
        """Extract one thumbnail per scene."""
        try:
            return extract_scene_thumbnails(
                input_video, scenes, output_dir, width, self.ffmpeg_path
            )
        except SceneError as e:
            raise AnalyzerError(str(e)) from e
    
    # ------------------------------------------------------------------
    # Content methods (delegate to content.py)
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
        """Joint scene + audio analysis."""
        try:
            return analyze_content_density(
                input_video, scene_threshold, min_scene_duration,
                energy_window_size, audio_weight, visual_weight, content_threshold
            )
        except ContentError as e:
            raise AnalyzerError(str(e)) from e
    
    def detect_video_type(
        self,
        input_video: str,
        sample_duration: float = 60.0,
    ) -> dict:
        """Detect video type."""
        return detect_video_type(input_video, sample_duration, self.config)
    
    def score_scene(
        self,
        input_video: str,
        scene: dict,
        video_type: str = "default",
    ) -> dict:
        """Score a single scene."""
        return score_scene(input_video, scene, video_type, self.config)
    
    def find_safe_cut_points(
        self,
        input_video: str,
        start: float,
        end: float,
        min_silence_duration: float = 0.3,
    ) -> list:
        """Detect safe cut points."""
        return find_safe_cut_points(input_video, start, end, min_silence_duration)
    
    def check_splice_compatibility(
        self,
        input_video: str,
        scene1: dict,
        scene2: dict,
    ) -> dict:
        """Check scene compatibility."""
        return check_splice_compatibility(input_video, scene1, scene2)
    
    def select_scenes(
        self,
        input_video: str,
        top_n: int = 5,
        min_score: float = 0.3,
        video_type: str = "auto",
        with_cut_points: bool = True,
    ) -> dict:
        """Select best scenes."""
        return select_scenes(
            input_video, top_n, min_score, video_type, with_cut_points, self.config
        )
    
    # ------------------------------------------------------------------
    # Subtitle methods (delegate to subtitle.py)
    # ------------------------------------------------------------------
    
    def transcribe(
        self,
        input_video: str,
        language: str = None,
        model: str = None,
    ) -> list[dict]:
        """Transcribe audio to text."""
        try:
            return transcribe(input_video, language, model, self.config)
        except SubtitleError as e:
            raise AnalyzerError(str(e)) from e
    
    def generate_srt(
        self,
        transcription: list[dict],
        output_path: str,
    ) -> str:
        """Generate SRT file."""
        try:
            return generate_srt(transcription, output_path, self.config)
        except SubtitleError as e:
            raise AnalyzerError(str(e)) from e
    
    def format_subtitle_style(self, style_config: dict = None) -> str:
        """Format subtitle style."""
        return format_subtitle_style(style_config, self.config)
    
    # ------------------------------------------------------------------
    # Audio separation methods
    # ------------------------------------------------------------------
    
    def separate_vocals(
        self,
        input_video: str,
        output_audio: str,
    ) -> str:
        """Extract vocals from video using FFmpeg audio filters.
        
        Uses FFmpeg's highpass filter to isolate vocals (removes low-frequency music).
        
        Args:
            input_video: Path to source video.
            output_audio: Path to output audio file (WAV or MP3).
        
        Returns:
            Path to extracted vocals audio file.
        
        Raises:
            AnalyzerError: If extraction fails.
        """
        from .utils import require_file
        import subprocess
        
        require_file(input_video)
        
        # Use FFmpeg highpass filter to isolate vocals
        # Removes frequencies below 200Hz (where music bass typically is)
        cmd = [
            self.ffmpeg_path, "-y",
            "-i", input_video,
            "-af", "highpass=f=200:poles=2",  # Highpass filter at 200Hz
            "-q:a", "9",  # Quality setting for MP3
            output_audio,
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise AnalyzerError(f"FFmpeg vocal extraction failed: {result.stderr}")
            return output_audio
        except subprocess.TimeoutExpired:
            raise AnalyzerError("Vocal extraction timeout")
        except Exception as e:
            raise AnalyzerError(f"Vocal extraction error: {e}")