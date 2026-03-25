# Progress

## Status
V1 complete. Shared Analyzer module built. Ready for V2.

## What Works
- `trim_start` — remove beginning of video
- `trim_end` — remove end of video
- `trim_range` — keep a single time range
- `trim_range` multi-segment — keep multiple segments, auto-merge
- `concat` — merge multiple video files
- `convert` — change resolution
- `remove_silence` — detect and remove silent segments (FFmpeg 7.x compatible)
- `remove_static` — detect and remove frozen-frame segments (OpenCV frame-diff)
- `info` — get video metadata
- `edit_video.py` — AI-callable structured CLI for all above operations
- `Analyzer` module — `extract_audio`, `detect_scenes`, `extract_thumbnail`, `analyze_audio_energy`, `detect_static_segments`
- `Validator` — output file validation after every operation

## In Progress
- `memory-bank/` initialization (this session)

## Not Started

**V2 — Scene Detection**
- `split_by_scenes()` in Executor
- Per-scene thumbnail extraction
- Scene list output with timestamps

**V3 — Auto Subtitles**
- `transcribe()` via Whisper
- SRT file generation
- Subtitle burn-in via FFmpeg

**V4 — Intelligent Editing**
- `score_segments()` — combine audio energy + scene change frequency
- `select_highlights()` — pick best segments
- Short video assembly
- Background music addition

## Known Issues
- `concat` uses a temp file in cwd — low risk now, fix before concurrent use
- `Parser` module still exists but is deprecated — can be removed in a future cleanup

## Milestones

| Milestone | Status | Date |
|---|---|---|
| V1 basic editing (trim/concat/convert) | ✅ Done | 2026-03-24 |
| remove_silence (FFmpeg 7.x) | ✅ Done | 2026-03-24 |
| remove_static (OpenCV) | ✅ Done | 2026-03-25 |
| Analyzer shared module | ✅ Done | 2026-03-25 |
| edit_video.py AI entry point | ✅ Done | 2026-03-25 |
| memory-bank initialized | ✅ Done | 2026-03-25 |
| V2 scene detection | ⏳ Planned | — |
| V3 auto subtitles | ⏳ Planned | — |
| V4 intelligent editing | ⏳ Planned | — |
