"""
subtitle.py - 字幕处理模块

Subtitle transcription and generation:
  - transcribe()            Transcribe audio to text with timestamps
  - generate_srt()          Generate SRT subtitle file
  - format_subtitle_style() Format subtitle style for FFmpeg
"""

import os

from .utils import require_file
from .audio import extract_audio


class SubtitleError(Exception):
    pass


# Whisper model cache
_whisper_models: dict[str, any] = {}


def _get_whisper_model(model: str):
    """Get or load Whisper model (cached)."""
    if model not in _whisper_models:
        try:
            import whisper
        except ImportError:
            raise SubtitleError("Whisper not installed. Run: pip install openai-whisper")
        
        try:
            _whisper_models[model] = whisper.load_model(model)
        except Exception as e:
            raise SubtitleError(f"Failed to load Whisper model '{model}': {e}")
    
    return _whisper_models[model]


def transcribe(
    input_video: str,
    language: str = None,
    model: str = None,
    config: dict = None,
) -> list[dict]:
    """Transcribe audio to text with timestamps using Whisper.

    Args:
        input_video: Path to the source video.
        language: Language code (e.g., 'zh', 'en'). Auto-detect if None.
        model: Whisper model size (tiny/base/small/medium/large).

    Returns:
        List of segments with start, end, text.
    """
    require_file(input_video)

    # Get config values
    subtitle_config = (config or {}).get("subtitle", {})
    language = language or subtitle_config.get("language", "zh")
    model = model or subtitle_config.get("model", "base")

    # Load model (cached)
    model_obj = _get_whisper_model(model)

    # Transcribe
    result = model_obj.transcribe(input_video, language=language)

    # Format output
    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": round(seg["start"], 3),
            "end": round(seg["end"], 3),
            "text": seg["text"].strip(),
        })

    return segments


def generate_srt(
    transcription: list[dict],
    output_path: str,
    config: dict = None,
) -> str:
    """Generate SRT subtitle file from transcription.

    Args:
        transcription: Output from transcribe().
        output_path: Path for the SRT file.

    Returns:
        Path to the generated SRT file.
    """
    def format_time(seconds: float) -> str:
        """Convert seconds to SRT time format: HH:MM:SS,mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    # Get config for line length
    subtitle_config = (config or {}).get("subtitle", {})
    max_line_length = subtitle_config.get("max_line_length", 20)

    srt_lines = []
    for i, seg in enumerate(transcription, 1):
        text = seg["text"]

        # Auto-wrap long lines at word boundaries
        if len(text) > max_line_length:
            words = text
            lines = []
            while len(words) > max_line_length:
                # Find a space to break at, but don't go beyond max_line_length
                break_point = min(max_line_length, len(words) - 1)
                while break_point > 0 and words[break_point] != ' ':
                    break_point -= 1
                if break_point == 0:
                    # No space found, force break at max_line_length
                    break_point = min(max_line_length, len(words))
                lines.append(words[:break_point].strip())
                words = words[break_point:].strip()
            if words:
                lines.append(words)
            text = '\n'.join(lines)

        srt_lines.append(str(i))
        srt_lines.append(f"{format_time(seg['start'])} --> {format_time(seg['end'])}")
        srt_lines.append(text)
        srt_lines.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_lines))

    return output_path


def format_subtitle_style(style_config: dict = None, config: dict = None) -> str:
    """Format subtitle style for FFmpeg subtitles filter.

    Args:
        style_config: Style configuration dict.

    Returns:
        FFmpeg subtitles filter style string (force_style parameter).
    """
    subtitle_config = (config or {}).get("subtitle", {})

    if style_config is None:
        style_config = {}

    # Get style values
    font = style_config.get("font") or subtitle_config.get("font", "Microsoft YaHei")
    size = style_config.get("size") or subtitle_config.get("size", 24)
    color = style_config.get("color") or subtitle_config.get("color", "white")
    position = style_config.get("position") or subtitle_config.get("position", "bottom")
    background = style_config.get("background") or subtitle_config.get("background", False)

    # Map color names to ASS color codes
    color_map = {
        "white": "&HFFFFFF",
        "black": "&H000000",
        "yellow": "&H00FFFF",
        "red": "&H0000FF",
        "blue": "&HFF0000",
        "green": "&H00FF00",
    }
    ass_color = color_map.get(color.lower(), "&HFFFFFF")

    # Build force_style string for subtitles filter
    style_parts = [f"FontName={font}", f"FontSize={size}", f"PrimaryColour={ass_color}"]

    if position == "bottom":
        style_parts.append("MarginV=30")
    elif position == "top":
        style_parts.append("MarginV=30")
    elif position == "center":
        pass  # Default center

    if background:
        style_parts.append("BackColour=&H80000000")
        style_parts.append("BorderStyle=4")

    return "force_style='" + ",".join(style_parts) + "'"