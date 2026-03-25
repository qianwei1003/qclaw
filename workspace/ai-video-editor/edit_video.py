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
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..", "..", "ai-video-editor")
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
        "description": "Remove the end of a video.",
        "required_params": ["end_time"],
        "example_params": {"end_time": 10.0},
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
    "info": {
        "description": "Get video metadata (duration, resolution, fps, codec).",
        "required_params": [],
        "example_params": {},
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

    # All other operations require --output
    if not output_video:
        print_result(False, "Missing --output for operation: " + args.operation)
        return 1

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
