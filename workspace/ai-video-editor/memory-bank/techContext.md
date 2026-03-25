# Tech Context

## Tech Stack

| Layer | Technology | Version | Notes |
|---|---|---|---|
| Language | Python | 3.12 | |
| Video processing | FFmpeg | 7.x | Must be in system PATH |
| Frame analysis | OpenCV | `opencv-python` | Used by Analyzer |
| Audio analysis | NumPy | latest | PCM processing in Analyzer |
| Video download | yt-dlp | latest | Separate tool, not in core modules |

## Development Environment
- OS: Windows 10 x64
- Shell: PowerShell
- Workspace: `C:\Users\admin\.qclaw\workspace\ai-video-editor`

## Key Dependencies

| Package | Purpose |
|---|---|
| `opencv-python` | Frame-diff analysis for scene detection and static removal |
| `numpy` | Audio PCM buffer processing in `analyze_audio_energy` |
| `ffmpeg` (system) | All video/audio operations |

## Constraints
- FFmpeg must be installed separately and available in PATH
- Windows path separators must be normalized to `/` before passing to FFmpeg (`_normalize_path()`)
- PowerShell does not support `&&` — use `;` to chain commands
- JSON params passed via CLI must use double quotes — single quotes fail on PowerShell

## Build & Run

```bash
# Install Python dependencies
pip install opencv-python numpy

# Run a video operation
python edit_video.py --operation info --input tests/1.mp4

# List all supported operations
python edit_video.py --list-operations
```

## Repo
- Remote: `github.com:qianwei1003/qclaw.git`
- Branch: `main`
- Path in repo: `workspace/ai-video-editor/`
