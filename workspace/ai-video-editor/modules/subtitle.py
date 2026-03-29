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
    initial_prompt: str = None,
    temperature: float = None,
) -> list[dict]:
    """Transcribe audio to text with timestamps using Whisper.

    Args:
        input_video: Path to the source video.
        language: Language code (e.g., 'zh', 'en'). Auto-detect if None.
        model: Whisper model size (tiny/base/small/medium/large).
        initial_prompt: Context prompt to help recognition (e.g., video topic).
        temperature: Sampling temperature (0-1). Lower = more deterministic.

    Returns:
        List of segments with start, end, text.
    """
    require_file(input_video)

    # Get config values
    subtitle_config = (config or {}).get("subtitle", {})
    language = language or subtitle_config.get("language", "zh")
    model = model or subtitle_config.get("model", "medium")  # Default to medium for better accuracy
    initial_prompt = initial_prompt or subtitle_config.get("initial_prompt", "")
    temperature = temperature if temperature is not None else subtitle_config.get("temperature", 0.0)

    # Load model (cached)
    model_obj = _get_whisper_model(model)

    # Transcribe with optimized parameters
    transcribe_params = {
        "language": language,
        "task": "transcribe",  # Only transcribe, not translate
        "temperature": temperature,  # 0.0 = most deterministic
        "word_timestamps": True,  # Word-level timestamps for better alignment
    }
    
    # Add initial_prompt if provided (helps with proper nouns, context)
    if initial_prompt:
        transcribe_params["initial_prompt"] = initial_prompt
    
    result = model_obj.transcribe(input_video, **transcribe_params)

    # Format output
    segments = []
    for seg in result["segments"]:
        text = seg["text"].strip()
        
        # Post-processing: fix common recognition errors
        text = _fix_common_errors(text, language)
        
        segments.append({
            "start": round(seg["start"], 3),
            "end": round(seg["end"], 3),
            "text": text,
        })

    return segments


def _fix_common_errors(text: str, language: str) -> str:
    """Fix common Whisper recognition errors.
    
    Args:
        text: Recognized text.
        language: Language code.
    
    Returns:
        Corrected text.
    """
    if language == "zh":
        # Common Chinese recognition errors
        fixes = {
            "？": "吗",  # Question mark confusion
            "！": "啊",  # Exclamation confusion
        }
        for wrong, correct in fixes.items():
            text = text.replace(wrong, correct)
    
    return text


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
        style_config: Style configuration dict with keys:
            - font: Font name (default: "Microsoft YaHei")
            - size: Font size in pixels (default: 24)
            - color: Text color name or hex (default: "white")
            - outline: Outline width (default: 1)
            - shadow: Shadow depth (default: 1)
            - margin_v: Vertical margin in pixels (default: 80)
            - margin_h: Horizontal margin in pixels (default: 10)
            - bold: Bold text (default: False)
            - italic: Italic text (default: False)
        config: Global config dict.

    Returns:
        FFmpeg subtitles filter style string (force_style parameter).
    """
    subtitle_config = (config or {}).get("subtitle", {})

    if style_config is None:
        style_config = {}

    # Get style values with defaults
    font = style_config.get("font") or subtitle_config.get("font", "Microsoft YaHei")
    size = style_config.get("size") or subtitle_config.get("size", 24)
    color = style_config.get("color") or subtitle_config.get("color", "white")
    outline = style_config.get("outline", subtitle_config.get("outline", 1))
    shadow = style_config.get("shadow", subtitle_config.get("shadow", 1))
    margin_v = style_config.get("margin_v", subtitle_config.get("margin_v", 80))
    margin_h = style_config.get("margin_h", subtitle_config.get("margin_h", 10))
    bold = style_config.get("bold", subtitle_config.get("bold", False))
    italic = style_config.get("italic", subtitle_config.get("italic", False))

    # Map color names to ASS color codes (BGR format)
    color_map = {
        "white": "&HFFFFFF",
        "black": "&H000000",
        "yellow": "&H00FFFF",
        "red": "&H0000FF",
        "blue": "&HFF0000",
        "green": "&H00FF00",
        "cyan": "&HFFFF00",
        "magenta": "&HFF00FF",
    }
    
    # Handle hex colors
    if isinstance(color, str) and color.startswith("#"):
        # Convert #RRGGBB to &HBBGGRR
        hex_color = color.lstrip("#")
        if len(hex_color) == 6:
            ass_color = f"&H{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"
        else:
            ass_color = "&HFFFFFF"
    else:
        ass_color = color_map.get(color.lower(), "&HFFFFFF")

    # Build force_style string for subtitles filter
    style_parts = [
        f"FontName={font}",
        f"FontSize={size}",
        f"PrimaryColour={ass_color}",
        f"Outline={outline}",
        f"Shadow={shadow}",
        f"MarginV={margin_v}",
        f"MarginL={margin_h}",
        f"MarginR={margin_h}",
    ]
    
    # Add bold/italic
    if bold:
        style_parts.append("Bold=1")
    if italic:
        style_parts.append("Italic=1")

    return ",".join(style_parts)