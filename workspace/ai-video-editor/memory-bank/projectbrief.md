# Project Brief

## Goal
An AI-driven video editing tool that lets users edit videos through natural language instructions, with AI handling intent understanding and structured tools handling execution.

## Core Requirements
- Accept natural language editing instructions (via AI, not hardcoded NLP)
- Execute video operations via FFmpeg: trim, concat, convert, remove silence, remove static
- Analyze video content: scene detection, audio energy, thumbnails
- Validate output correctness after every operation
- Expose a structured CLI (`edit_video.py`) that AI can call directly

## Scope
**In scope:**
- V1: Basic editing — trim, concat, convert, remove silence, remove static frames
- V2: Scene detection and splitting
- V3: Auto subtitles via Whisper
- V4: Intelligent highlight extraction and short video generation
- Shared analysis layer (Analyzer module) reused across all stages

**Out of scope:**
- GUI / web interface
- Real-time / live video processing
- Video recording or capture
- Cloud storage or upload

## Success Criteria
- AI can call `edit_video.py` with structured params and get reliable JSON output
- All V1 operations work correctly on real video files
- Each stage (V2/V3/V4) builds on shared Analyzer without duplication
