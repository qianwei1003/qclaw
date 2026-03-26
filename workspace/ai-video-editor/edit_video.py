#!/usr/bin/env python3
"""
edit_video.py - AI Video Editor Entry Point

Direct execution script for the video editor. Accepts structured JSON input,
bypasses the natural language parser entirely.

Usage:
    python edit_video.py --operation trim_start --input video.mp4 --output out.mp4 --params '{"start_time": 5}'
    python edit_video.py --operation trim_end   --input video.mp4 --output out.mp4 --params '{"end_time": 10}'
    python edit_video.py --operation trim_range --input video.mp4 --output out.mp4 --params '{"start_time": 10, "end_time": 60}'
    python edit_video.py --operation concat     --input video1.mp4 --output out.mp4 --params '{"files": ["video2.mp4"]}'
    python edit_video.py --operation convert    --input video.mp4 --output out.mp4 --params '{"width": 1920, "height": 1080}'
    python edit_video.py --operation remove_silence --input video.mp4 --output out.mp4
    python edit_video.py --operation info       --input video.mp4
"""

import argparse
import json
import os
import sys

# Resolve project root so this script can be run from any working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = SCRIPT_DIR
sys.path.insert(0, PROJECT_ROOT)

from modules.executor import Executor, ExecutionError
from modules.validator import Validator, ValidationError


# ---------------------------------------------------------------------------
# Supported operations and their required / optional params
# ---------------------------------------------------------------------------

OPERATIONS: dict[str, dict] = {
    "trim_start": {
        "description": "Remove the beginning of a video.",
        "required_params": ["start_time"],
        "example_params": {"start_time": 5.0},
    },
    "trim_end": {
        "description": "Remove N seconds from the end of a video.",
        "required_params": ["trim_seconds"],
        "example_params": {"trim_seconds": 10.0},
    },
    "trim_range": {
        "description": "Keep only a specific time range (single or multiple segments).",
        "required_params": ["start_time", "end_time"],
        "example_params": {"start_time": 10.0, "end_time": 60.0},
    },
    "concat": {
        "description": "Merge multiple video files into one.",
        "required_params": ["files"],
        "example_params": {"files": ["video2.mp4", "video3.mp4"]},
    },
    "convert": {
        "description": "Change video resolution.",
        "required_params": ["width", "height"],
        "example_params": {"width": 1920, "height": 1080},
    },
    "remove_silence": {
        "description": "Remove silent segments from a video.",
        "required_params": [],
        "example_params": {"threshold": -30},
    },
    "remove_static": {
        "description": "Remove static (frozen-frame) segments from a video using OpenCV frame-diff analysis.",
        "required_params": [],
        "example_params": {"threshold": 0.01, "min_static_duration": 1.0},
    },
    "detect_scenes": {
        "description": "Detect scene cuts and return scene list. Does NOT cut video — use split_by_scenes to cut.",
        "required_params": [],
        "example_params": {"threshold": 0.4, "min_scene_duration": 1.0},
    },
    "split_by_scenes": {
        "description": "Detect scenes and split video into separate files, one per scene.",
        "required_params": [],
        "example_params": {"threshold": 0.4, "min_scene_duration": 1.0},
    },
    "info": {
        "description": "Get video metadata (duration, resolution, fps, codec).",
        "required_params": [],
        "example_params": {},
    },
    "analyze_content": {
        "description": "Joint scene + audio analysis. Scores each scene by audio energy and visual activity to identify 'content-rich' scenes.",
        "required_params": [],
        "example_params": {
            "scene_threshold": 0.4,
            "min_scene_duration": 1.0,
            "audio_weight": 0.6,
            "visual_weight": 0.4,
            "content_threshold": 0.3,
        },
    },
    "detect_type": {
        "description": "Detect video type (interview/sports/movie/speech/tutorial/vlog/funny) based on visual and audio features.",
        "required_params": [],
        "example_params": {"sample_duration": 60.0},
    },
    "select_scenes": {
        "description": "Select and recommend best scenes from video based on multi-dimensional scoring.",
        "required_params": [],
        "example_params": {
            "top_n": 5,
            "min_score": 0.3,
            "video_type": "auto",
            "with_cut_points": True,
        },
    },
    "find_cuts": {
        "description": "Find safe cut points within a time range (avoiding speech mid-sentence).",
        "required_params": [],
        "example_params": {"start": 0.0, "end": 60.0, "min_silence_duration": 0.3},
    },
    "check_splice": {
        "description": "Check if two scenes can be spliced together smoothly.",
        "required_params": [],
        "example_params": {
            "scene1": {"start": 0.0, "end": 30.0},
            "scene2": {"start": 60.0, "end": 90.0},
        },
    },
    "export_scenes": {
        "description": "Export selected scenes to separate files or merge into one.",
        "required_params": ["scenes"],
        "example_params": {
            "scenes": [{"start": 0.0, "end": 30.0}, {"start": 60.0, "end": 90.0}],
            "merge": False,
        },
    },
    "transcribe": {
        "description": "Transcribe audio to text using Whisper.",
        "required_params": [],
        "example_params": {"language": "zh", "model": "base"},
    },
    "generate_srt": {
        "description": "Generate SRT subtitle file from video.",
        "required_params": [],
        "example_params": {},
    },
    "burn_subtitle": {
        "description": "Burn subtitles into video using FFmpeg.",
        "required_params": [],
        "example_params": {"srt_file": "video.srt"},
    },
    "auto_subtitle": {
        "description": "One-click auto subtitle: transcribe + generate SRT + burn into video.",
        "required_params": [],
        "example_params": {"language": "zh", "model": "base"},
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_path(path: str) -> str:
    """Resolve a path relative to cwd; return absolute path."""
    return os.path.abspath(path)


def validate_params(operation: str, params: dict) -> list[str]:
    """Return a list of missing required param names."""
    required = OPERATIONS[operation]["required_params"]
    return [p for p in required if p not in params]


def get_video_info(executor: Executor, input_video: str) -> dict:
    """Return basic video metadata as a dict."""
    duration = executor.get_video_duration(input_video)
    return {
        "file": input_video,
        "duration_seconds": duration,
    }


def print_result(success: bool, message: str, data: dict | None = None) -> None:
    """Print a structured JSON result to stdout."""
    result = {"success": success, "message": message}
    if data:
        result["data"] = data
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="AI Video Editor — structured command interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--operation", required=True, choices=list(OPERATIONS.keys()),
                        help="Operation to perform")
    parser.add_argument("--input", required=True, help="Input video file path")
    parser.add_argument("--output", default=None, help="Output video file path (not needed for 'info')")
    parser.add_argument("--params", default="{}", help="JSON string of operation parameters")
    parser.add_argument("--validate", action="store_true", default=True,
                        help="Validate output after execution (default: true)")
    parser.add_argument("--list-operations", action="store_true",
                        help="List all supported operations and exit")

    args = parser.parse_args()

    # --list-operations: print catalogue and exit
    if args.list_operations:
        catalogue = {
            op: {
                "description": meta["description"],
                "required_params": meta["required_params"],
                "example_params": meta["example_params"],
            }
            for op, meta in OPERATIONS.items()
        }
        print(json.dumps(catalogue, ensure_ascii=False, indent=2))
        return 0

    # Resolve paths
    input_video = resolve_path(args.input)
    output_video = resolve_path(args.output) if args.output else None

    # Validate input file exists
    if not os.path.exists(input_video):
        print_result(False, f"Input file not found: {input_video}")
        return 1

    # Parse params
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print_result(False, f"Invalid JSON in --params: {e}")
        return 1

    # Check required params
    missing = validate_params(args.operation, params)
    if missing:
        print_result(False, f"Missing required params for '{args.operation}': {missing}",
                     {"example": OPERATIONS[args.operation]["example_params"]})
        return 1

    # info operation — no output needed
    if args.operation == "info":
        executor = Executor()
        info = get_video_info(executor, input_video)
        print_result(True, "Video info retrieved", info)
        return 0

    # detect_scenes operation — no output needed, returns scene list
    if args.operation == "detect_scenes":
        from modules.analyzer import Analyzer, AnalyzerError
        analyzer = Analyzer()
        try:
            threshold = params.get("threshold", 0.4)
            min_scene_duration = params.get("min_scene_duration", 1.0)
            scenes = analyzer.detect_scenes(
                input_video,
                threshold=threshold,
                min_scene_duration=min_scene_duration,
            )
            print_result(True, f"Detected {len(scenes)} scenes", {
                "scenes": scenes,
                "count": len(scenes),
            })
            return 0
        except AnalyzerError as e:
            print_result(False, f"Scene detection failed: {e}")
            return 1

    # analyze_content operation — no output needed, returns scored scenes
    if args.operation == "analyze_content":
        from modules.analyzer import Analyzer, AnalyzerError
        analyzer = Analyzer()
        try:
            result = analyzer.analyze_content_density(
                input_video,
                scene_threshold=params.get("scene_threshold", 0.4),
                min_scene_duration=params.get("min_scene_duration", 1.0),
                energy_window_size=params.get("energy_window_size", 1.0),
                audio_weight=params.get("audio_weight", 0.6),
                visual_weight=params.get("visual_weight", 0.4),
                content_threshold=params.get("content_threshold", 0.3),
            )
            summary = result["summary"]
            print_result(
                True,
                f"Analyzed {summary['total_scenes']} scenes, "
                f"{summary['content_count']} have content "
                f"({summary['content_ratio']:.0%})",
                result,
            )
            return 0
        except AnalyzerError as e:
            print_result(False, f"Content analysis failed: {e}")
            return 1

    # detect_type operation — detect video type
    if args.operation == "detect_type":
        from modules.analyzer import Analyzer, AnalyzerError
        analyzer = Analyzer()
        try:
            result = analyzer.detect_video_type(
                input_video,
                sample_duration=params.get("sample_duration", 60.0),
            )
            print_result(
                True,
                f"Video type: {result['type']} (confidence: {result['confidence']:.0%})",
                result,
            )
            return 0
        except AnalyzerError as e:
            print_result(False, f"Video type detection failed: {e}")
            return 1

    # select_scenes operation — recommend best scenes
    if args.operation == "select_scenes":
        from modules.analyzer import Analyzer, AnalyzerError
        analyzer = Analyzer()
        try:
            result = analyzer.select_scenes(
                input_video,
                top_n=params.get("top_n", 5),
                min_score=params.get("min_score", 0.3),
                video_type=params.get("video_type", "auto"),
                with_cut_points=params.get("with_cut_points", True),
            )
            count = len(result["recommended"])
            print_result(
                True,
                f"Recommended {count} scenes from {result['total_scenes']} (type: {result['video_type']})",
                result,
            )
            return 0
        except AnalyzerError as e:
            print_result(False, f"Scene selection failed: {e}")
            return 1

    # find_cuts operation — find safe cut points
    if args.operation == "find_cuts":
        from modules.analyzer import Analyzer, AnalyzerError
        analyzer = Analyzer()
        try:
            result = analyzer.find_safe_cut_points(
                input_video,
                start=params.get("start", 0.0),
                end=params.get("end", 60.0),
                min_silence_duration=params.get("min_silence_duration", 0.3),
            )
            safe_count = len([p for p in result if p["safe"]])
            print_result(
                True,
                f"Found {len(result)} cut points ({safe_count} safe)",
                {"cut_points": result, "count": len(result)},
            )
            return 0
        except AnalyzerError as e:
            print_result(False, f"Cut point detection failed: {e}")
            return 1

    # check_splice operation — check splice compatibility
    if args.operation == "check_splice":
        from modules.analyzer import Analyzer, AnalyzerError
        analyzer = Analyzer()
        try:
            scene1 = params.get("scene1", {"start": 0.0, "end": 30.0})
            scene2 = params.get("scene2", {"start": 60.0, "end": 90.0})
            result = analyzer.check_splice_compatibility(input_video, scene1, scene2)
            status = "compatible" if result["compatible"] else "incompatible"
            print_result(
                True,
                f"Scenes are {status} (score: {result['score']:.2f})",
                result,
            )
            return 0
        except AnalyzerError as e:
            print_result(False, f"Splice check failed: {e}")
            return 1

    # export_scenes operation — export selected scenes
    if args.operation == "export_scenes":
        if not output_video:
            print_result(False, "Missing --output for export_scenes")
            return 1
        
        from modules.executor import Executor, ExecutionError
        executor = Executor()
        try:
            scenes = params.get("scenes", [])
            merge = params.get("merge", False)
            
            # Export each scene
            output_dir = os.path.dirname(output_video) if not merge else output_video
            if merge:
                os.makedirs(os.path.dirname(output_video), exist_ok=True)
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            exported_files = []
            for i, scene in enumerate(scenes):
                if merge and i == 0:
                    # First scene: use output_video directly
                    scene_output = output_video
                else:
                    scene_output = os.path.join(output_dir, f"scene_{i:03d}.mp4")
                
                success = executor.execute(
                    {"operation": "trim_range", "params": scene},
                    input_video,
                    scene_output,
                )
                if success:
                    exported_files.append(scene_output)
            
            print_result(
                True,
                f"Exported {len(exported_files)} scenes",
                {"exported_files": exported_files, "count": len(exported_files)},
            )
            return 0
        except ExecutionError as e:
            print_result(False, f"Scene export failed: {e}")
            return 1

    # transcribe operation — speech to text
    if args.operation == "transcribe":
        from modules.analyzer import Analyzer, AnalyzerError
        analyzer = Analyzer()
        try:
            segments = analyzer.transcribe(
                input_video,
                language=params.get("language"),
                model=params.get("model"),
            )
            print_result(
                True,
                f"Transcribed {len(segments)} segments",
                {
                    "segments": segments,
                    "count": len(segments),
                    "language": params.get("language", "auto"),
                },
            )
            return 0
        except AnalyzerError as e:
            print_result(False, f"Transcription failed: {e}")
            return 1

    # generate_srt operation — generate subtitle file
    if args.operation == "generate_srt":
        from modules.analyzer import Analyzer, AnalyzerError
        analyzer = Analyzer()
        try:
            # Auto-generate output filename if not specified
            if not output_video:
                base_name = os.path.splitext(input_video)[0]
                output_video = base_name + ".srt"
            
            # Transcribe
            segments = analyzer.transcribe(input_video)
            
            # Generate SRT
            srt_path = analyzer.generate_srt(segments, output_video)
            
            print_result(
                True,
                f"SRT file generated: {os.path.basename(srt_path)}",
                {"srt_file": srt_path, "segment_count": len(segments)},
            )
            return 0
        except AnalyzerError as e:
            print_result(False, f"SRT generation failed: {e}")
            return 1

    # burn_subtitle operation — burn subtitles into video
    if args.operation == "burn_subtitle":
        if not output_video:
            # Auto-generate output filename
            base_name = os.path.splitext(input_video)[0]
            output_video = base_name + "_subtitled.mp4"
        
        from modules.executor import Executor, ExecutionError
        executor = Executor()
        try:
            srt_file = params.get("srt_file")
            if not srt_file:
                # Auto-generate SRT filename
                base_name = os.path.splitext(input_video)[0]
                srt_file = base_name + ".srt"
            
            success = executor.burn_subtitle(
                {"srt_file": srt_file, "style": params.get("style", {})},
                input_video,
                output_video,
            )
            if success:
                print_result(
                    True,
                    f"Subtitles burned: {os.path.basename(output_video)}",
                    {"output_video": output_video, "srt_file": srt_file},
                )
            return 0 if success else 1
        except ExecutionError as e:
            print_result(False, f"Subtitle burn failed: {e}")
            return 1

    # auto_subtitle operation — one-click subtitle
    if args.operation == "auto_subtitle":
        if not output_video:
            # Auto-generate output filename
            base_name = os.path.splitext(input_video)[0]
            output_video = base_name + "_subtitled.mp4"
        
        from modules.analyzer import Analyzer, AnalyzerError
        from modules.executor import Executor, ExecutionError
        
        try:
            # Step 1: Transcribe
            analyzer = Analyzer()
            segments = analyzer.transcribe(
                input_video,
                language=params.get("language"),
                model=params.get("model"),
            )
            
            # Step 2: Generate SRT
            base_name = os.path.splitext(input_video)[0]
            srt_file = base_name + ".srt"
            srt_path = analyzer.generate_srt(segments, srt_file)
            
            # Step 3: Burn subtitle
            executor = Executor()
            success = executor.burn_subtitle(
                {"srt_file": srt_path, "style": params.get("style", {})},
                input_video,
                output_video,
            )
            
            if success:
                print_result(
                    True,
                    f"Auto subtitle complete: {os.path.basename(output_video)}",
                    {
                        "srt_file": srt_path,
                        "output_video": output_video,
                        "segment_count": len(segments),
                    },
                )
            return 0 if success else 1
        except (AnalyzerError, ExecutionError) as e:
            print_result(False, f"Auto subtitle failed: {e}")
            return 1

    # All other operations require --output
    if not output_video:
        print_result(False, "Missing --output for operation: " + args.operation)
        return 1

    # split_by_scenes: output_video is a directory, skip validation
    if args.operation == "split_by_scenes":
        executor = Executor()
        instruction = {"operation": "split_by_scenes", "params": params}
        try:
            success = executor.execute(instruction, input_video, output_video)
        except ExecutionError as e:
            print_result(False, f"Split by scenes failed: {e}")
            return 1
        if success:
            print_result(True, f"Video split into scenes in: {output_video}")
        else:
            print_result(False, "Split by scenes returned failure")
        return 0 if success else 1

    # Ensure output directory exists
    output_dir = os.path.dirname(output_video)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Build structured instruction (matches Executor.execute() contract)
    instruction = {
        "operation": args.operation,
        "params": params,
    }

    # Execute
    executor = Executor()
    try:
        success = executor.execute(instruction, input_video, output_video)
    except ExecutionError as e:
        print_result(False, f"Execution failed: {e}")
        return 1

    if not success:
        print_result(False, "Execution returned failure; check ffmpeg logs")
        return 1

    # Validate output
    if args.validate:
        validator = Validator()
        try:
            validator.validate(output_video)
        except ValidationError as e:
            print_result(False, f"Output validation failed: {e}",
                         {"output_file": output_video})
            return 1

    print_result(True, "Done", {"output_file": output_video})
    return 0


if __name__ == "__main__":
    sys.exit(main())
