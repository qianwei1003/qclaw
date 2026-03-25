# System Patterns

## Architecture Overview

```
User / AI
    ↓
edit_video.py          ← AI entry point (structured CLI, JSON output)
    ↓
Executor               ← Maps operation → FFmpeg command
    ↓
FFmpeg                 ← Actual video processing

Analyzer               ← Shared analysis layer (used by Executor + future stages)
    ├── extract_audio
    ├── detect_scenes
    ├── extract_thumbnail
    ├── analyze_audio_energy
    └── detect_static_segments

Validator              ← Output verification after every operation
```

## Module Responsibilities

| Module | File | Responsibility |
|---|---|---|
| `edit_video.py` | root | AI-facing CLI; validates params; routes to Executor |
| `Executor` | `modules/executor.py` | Translates structured instruction → FFmpeg command; handles retries |
| `Analyzer` | `modules/analyzer.py` | Video/audio analysis; shared across V1–V4 |
| `Validator` | `modules/validator.py` | Post-execution output validation |
| `Parser` | `modules/parser.py` | **Deprecated** — natural language parser, no longer used in AI flow |

## Key Design Patterns

- **Structured instruction contract**: all operations use `{"operation": str, "params": dict}` — Executor never receives raw text
- **JSON-only output**: `edit_video.py` always returns `{success, message, data}` — AI parses deterministically
- **Fail loudly with examples**: on missing params, return example params so AI can self-correct without human intervention
- **Shared analysis layer**: `Analyzer` is instantiated by Executor internally — callers never call Analyzer directly
- **Auto-fallback in FFmpeg**: `-c copy` attempted first; re-encodes on failure

## Data Flow

```
AI call → edit_video.py
  → validate params
  → build instruction dict
  → Executor.execute(instruction, input, output)
      → Analyzer (if needed, e.g. remove_static, remove_silence)
      → FFmpeg command
      → _run_ffmpeg()
  → Validator.validate(output)
  → return JSON result to AI
```

## Critical Constraints
- All paths passed to FFmpeg must use forward slashes (Windows compat — `_normalize_path()`)
- Temp files must use `tempfile.mkstemp()` — never hardcoded paths (concurrent safety)
- `cap.release()` must always be in `try/finally` when using OpenCV VideoCapture
