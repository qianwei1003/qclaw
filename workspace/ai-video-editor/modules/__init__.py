"""
AI Video Editor - AI 视频剪辑工具
"""

from .executor import Executor, ExecutionError
from .validator import Validator, ValidationError
from .analyzer import Analyzer, AnalyzerError
from .logger import get_logger, set_log_level, log

# New modules
from .utils import UtilsError, run_cmd, require_file, get_duration, iter_frame_diffs
from .audio import AudioError, extract_audio, analyze_audio_energy
from .scene import SceneError, detect_scenes, detect_static_segments, extract_thumbnail, extract_scene_thumbnails
from .content import ContentError, analyze_content_density, detect_video_type, score_scene, select_scenes
from .subtitle import SubtitleError, transcribe, generate_srt, format_subtitle_style

__all__ = [
    # Core
    'Executor',
    'ExecutionError',
    'Validator',
    'ValidationError',
    'Analyzer',
    'AnalyzerError',
    # Logger
    'get_logger',
    'set_log_level',
    'log',
    # Utils
    'UtilsError',
    'run_cmd',
    'require_file',
    'get_duration',
    'iter_frame_diffs',
    # Audio
    'AudioError',
    'extract_audio',
    'analyze_audio_energy',
    # Scene
    'SceneError',
    'detect_scenes',
    'detect_static_segments',
    'extract_thumbnail',
    'extract_scene_thumbnails',
    # Content
    'ContentError',
    'analyze_content_density',
    'detect_video_type',
    'score_scene',
    'select_scenes',
    # Subtitle
    'SubtitleError',
    'transcribe',
    'generate_srt',
    'format_subtitle_style',
]