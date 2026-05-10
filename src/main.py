"""
main.py — The entry point you run from the command line.

Usage:
    python -m src.main input/clip.mp4 --template hype
    python -m src.main input/clip.mp4 --template cinematic --hook "+$2,400 IN 22 MIN"

Looks for a markers CSV next to the video (clip.csv or clip_markers.csv).
"""

import argparse
import sys
from pathlib import Path

from .markers import read_markers
from .templates import load_template, list_templates
from .render import render_short


def find_markers_csv(video_path: Path) -> Path | None:
    """Look for an adjacent markers CSV file with common naming patterns."""
    candidates = [
        video_path.with_suffix(".csv"),
        video_path.parent / f"{video_path.stem}_markers.csv",
        video_path.parent / "markers.csv",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="HVT Clip — polish a hand-cut trading clip into a viral-ready Short."
    )
    parser.add_argument("video", help="Path to input video (mp4)")
    parser.add_argument(
        "--template",
        default="hype",
        help=f"Style template. Available: {', '.join(list_templates())}",
    )
    parser.add_argument(
        "--hook",
        default=None,
        help="Optional hook text overlay shown at the start (e.g. '+$2,400 IN 22 MIN')",
    )
    parser.add_argument(
        "--markers",
        default=None,
        help="Path to markers CSV (optional — will auto-detect if not given)",
    )
    parser.add_argument(
        "--framerate",
        type=float,
        default=30.0,
        help="Source video framerate (used to convert timecodes). Default 30.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path (default: output/<input_name>_<template>.mp4)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    video_path = Path(args.video).resolve()

    if not video_path.exists():
        print(f"❌ Input video not found: {video_path}", file=sys.stderr)
        return 1

    # Markers
    markers_csv = Path(args.markers).resolve() if args.markers else find_markers_csv(video_path)
    if markers_csv and markers_csv.exists():
        markers = read_markers(markers_csv, framerate=args.framerate)
        print(f"📍 Found {len(markers)} markers in {markers_csv.name}")
        for m in markers:
            print(f"     {m.name:12s} at {m.time_sec:6.2f}s")
    else:
        markers = []
        print("⚠️  No markers CSV found. Running without timed sound effects/labels.")
        print("   (The video will still get music + watermark + hook.)")

    # Template
    try:
        template = load_template(args.template)
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1

    print(f"🎨 Template: {template.name} — {template.description}")

    # Output path
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        output_dir = project_root / "output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{video_path.stem}_{template.name}.mp4"

    if args.hook:
        print(f"🪝 Hook: {args.hook}")

    # Render
    try:
        render_short(
            input_video=video_path,
            output_video=output_path,
            template=template,
            markers=markers,
            hook_text=args.hook,
            project_root=project_root,
        )
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
