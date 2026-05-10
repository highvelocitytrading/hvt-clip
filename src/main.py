"""
main.py — HVT Clip v1.5 entry point.

═══════════════════════════════════════════════════════════════════════════════
SYSTEM MISSION (read every time you change this file):

This system drives sales of HVT trading indicators. Every video must:
  1. Visually emphasize the colored signal bars (Momentum/Correlation/Volume)
  2. Be polished enough to perform on Shorts/Reels/TikTok
  3. End with a CTA pointing to highvelocitytrading.com
═══════════════════════════════════════════════════════════════════════════════

Usage:
    # Default — long trade, default brand template
    python -m src.main input/clip.mp4 --hook "GREEN MEANS BUY."

    # Short trade — entry colors flip to red, SHORT badge appears
    python -m src.main input/clip.mp4 --direction short --hook "TRIPLE RED. CLEAN SHORT."

    # Adjust how much the bar zone is emphasized
    python -m src.main input/clip.mp4 --chart-ratio 0.50

    # Branding level
    python -m src.main input/clip.mp4 --branding loud
"""

import argparse
import sys
from pathlib import Path

from .markers import read_markers
from .templates import load_template, list_templates
from .render import render_short


def find_markers_csv(video_path: Path) -> Path | None:
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
        description=(
            "HVT Clip v1.5 — split-stack render engine. "
            "Polishes a hand-cut trading clip into a brand-aligned vertical short "
            "with the signal bars emphasized as the visual hero."
        )
    )
    parser.add_argument("video", help="Path to input video (.mp4)")
    parser.add_argument(
        "--template", default="hvt",
        help=f"Style template. Default: hvt. Available: {', '.join(list_templates())}",
    )
    parser.add_argument(
        "--hook", default=None,
        help="Hook text shown at start (e.g. 'GREEN MEANS BUY.', '+$840 IN 12 MIN')",
    )
    parser.add_argument(
        "--direction", choices=["long", "short"], default=None,
        help=(
            "Trade direction. Affects entry-label color and adds a corner badge. "
            "long → green accent. short → red accent."
        ),
    )
    parser.add_argument(
        "--chart-ratio", type=float, default=0.55,
        help=(
            "How much of the source frame is the chart vs. signal bars. "
            "0.55 = top 55%% chart, bottom 45%% bars. Default: 0.55. "
            "Lower this if your bars panel is taller in the source."
        ),
    )
    parser.add_argument(
        "--branding", choices=["subtle", "balanced", "loud"], default="subtle",
        help=(
            "Branding intensity. subtle = small watermark, brief CTA (best for virality). "
            "loud = bigger watermark, longer CTA (more sales-pitch-y). Default: subtle."
        ),
    )
    parser.add_argument("--markers", default=None, help="Path to markers CSV (auto-detected)")
    parser.add_argument("--framerate", type=float, default=30.0, help="Source framerate (default 30)")
    parser.add_argument("--output", default=None, help="Output path")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    video_path = Path(args.video).resolve()

    if not video_path.exists():
        print(f"❌ Input video not found: {video_path}", file=sys.stderr)
        return 1

    markers_csv = Path(args.markers).resolve() if args.markers else find_markers_csv(video_path)
    if markers_csv and markers_csv.exists():
        markers = read_markers(markers_csv, framerate=args.framerate)
        print(f"📍 Found {len(markers)} markers in {markers_csv.name}")
        for m in markers:
            print(f"     {m.name:12s} at {m.time_sec:6.2f}s")
    else:
        markers = []
        print("ℹ️  No markers — running without timed sound effects/labels.")

    try:
        template = load_template(args.template)
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1

    print(f"🎨 Template: {template.name}")
    if args.direction:
        print(f"🎯 Direction: {args.direction.upper()}")
    if args.hook:
        print(f"🪝 Hook: {args.hook}")
    print(f"🎚  Branding: {args.branding}")
    print(f"📐 Chart ratio: {args.chart_ratio} (top {int(args.chart_ratio*100)}% = chart)")

    if args.output:
        output_path = Path(args.output).resolve()
    else:
        output_dir = project_root / "output"
        output_dir.mkdir(exist_ok=True)
        suffix = f"_{args.direction}" if args.direction else ""
        output_path = output_dir / f"{video_path.stem}_{template.name}{suffix}.mp4"

    try:
        render_short(
            input_video=video_path,
            output_video=output_path,
            template=template,
            markers=markers,
            hook_text=args.hook,
            project_root=project_root,
            direction=args.direction,
            chart_ratio=args.chart_ratio,
            branding_level=args.branding,
        )
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
