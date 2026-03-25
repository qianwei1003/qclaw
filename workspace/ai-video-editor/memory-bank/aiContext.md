# AI Context

## How AI Uses This Tool
AI receives a user's natural language editing request, maps it to a structured operation and params, calls `edit_video.py`, parses the JSON result, and reports back to the user.

## Tool Interface

| Script | Location | Input | Output |
|---|---|---|---|
| `edit_video.py` | project root | `--operation`, `--input`, `--output`, `--params JSON` | `{"success": bool, "message": str, "data": dict}` |

## Supported Operations

| Operation | Required params | Optional params |
|---|---|---|
| `trim_start` | `start_time` (float, seconds) | — |
| `trim_end` | `end_time` (float, seconds) | — |
| `trim_range` | `start_time`, `end_time` (float) | — |
| `concat` | `files` (list of paths) | — |
| `convert` | `width`, `height` (int, pixels) | — |
| `remove_silence` | — | `threshold` (dB, default -40) |
| `remove_static` | — | `threshold` (0–1, default 0.01), `min_static_duration` (seconds, default 1.0) |
| `info` | — (no `--output` needed) | — |

## Calling Conventions
- All paths must be **absolute**
- `--params` value must be valid JSON with **double quotes**
- Time values always in **float seconds** (convert "1:30" → 90.0 before calling)
- Always check `success` field first before reading `data`
- On missing params error, response includes `data.example` — use it to self-correct

## AI Decision Responsibilities

| AI decides | Tool handles |
|---|---|
| Which operation matches user intent | FFmpeg command construction |
| Parameter values from natural language | Path normalization |
| Output file naming (if not specified) | Temp file management |
| Error recovery strategy | Output validation |

## Output File Naming Convention
If user does not specify output path:
```
<input_stem>_<operation>.<ext>
e.g. interview_trim_start.mp4
```

## Error Self-Correction Pattern
```json
// AI receives:
{"success": false, "message": "Missing required params for 'trim_start': ['start_time']",
 "data": {"example": {"start_time": 5.0}}}

// AI should: add start_time and retry
```

## Anti-Patterns
- ❌ Do NOT pass natural language to `--params` — always structured JSON
- ❌ Do NOT use relative paths — always resolve to absolute before calling
- ❌ Do NOT call Analyzer directly — use `edit_video.py` as the single entry point
