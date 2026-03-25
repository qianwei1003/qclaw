# Product Context

## Problem
Manual video editing is time-consuming and requires technical skill. Existing tools require users to learn complex interfaces. AI can understand editing intent from natural language, but needs reliable, structured tools to execute — not fragile keyword-matching parsers.

## Target Users
- Developers and technical users who want to automate video editing workflows
- AI agents (Claude, GPT, etc.) that need a reliable video editing tool interface
- Content creators who want to script repetitive editing tasks

## How It Works (User Perspective)
1. User (or AI) describes what they want: "remove the first 5 seconds", "delete silent parts"
2. AI maps intent to a structured operation + params
3. AI calls `edit_video.py --operation trim_start --input video.mp4 --output out.mp4 --params '{"start_time": 5}'`
4. Tool executes via FFmpeg, validates output, returns JSON result
5. AI reports success or handles error

## Design Goals
- **AI-first interface** — `edit_video.py` is designed for AI callers, not humans typing commands
- **Structured over natural language** — AI handles NLP; tools handle execution; no keyword matching in code
- **Reliable JSON output** — every operation returns `{success, message, data}` so AI can parse deterministically
- **Composable** — shared Analyzer module reused across V1/V2/V3/V4, no duplication
- **Fail loudly** — clear error messages with examples so AI can self-correct
