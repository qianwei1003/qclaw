# Active Context

## Current Focus
V1 complete. Analyzer module built as shared foundation for V2/V3/V4.
Next: decide which V2 feature to start — scene detection split or thumbnail extraction.

## Recent Changes
- `modules/analyzer.py` added — 5 methods: `extract_audio`, `detect_scenes`, `extract_thumbnail`, `analyze_audio_energy`, `detect_static_segments`
- `_remove_static` in executor.py replaced — was a stub, now calls `Analyzer.detect_static_segments()`
- `edit_video.py` added — structured CLI entry point for AI callers, bypasses Parser entirely
- `memory-bank/` initialized (this session)
- Code quality refactor on analyzer.py: removed unused import, extracted `_iter_frame_diffs()`, fixed `cap.release()` in try/finally

## Next Steps
1. Initialize memory-bank docs (in progress)
2. Implement V2: scene detection → `split_by_scenes()` in executor, `extract_thumbnail()` per scene
3. Add `detect_scenes` and `split_by_scenes` operations to `edit_video.py`
4. Update `video-editor` skill with new V2 operations

## Active Decisions
- Parser (`modules/parser.py`) is kept but deprecated — AI uses `edit_video.py` directly
- Old `docs/` files retained as reference, not actively maintained
- memory-bank/ is the new source of truth for project context

## Known Blockers
None.
