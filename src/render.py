"""
render.py — HVT Clip v1.5 render engine.

═══════════════════════════════════════════════════════════════════════════════
SYSTEM MISSION
═══════════════════════════════════════════════════════════════════════════════
This system exists to drive sales of HVT trading indicators.
Every video produced must:

  1. Visually emphasize the colored signal bars (Momentum / Correlation /
     Volume Profile) — they are the product being sold.
  2. Make videos that perform on Shorts/Reels/TikTok.
  3. End with a CTA pointing to highvelocitytrading.com.

The "split-stack" mode crops the source frame into two zones:
  - TOP    = price chart (the trade)
  - BOTTOM = signal bars (the IP)
and stacks them. Bars get ~42% of output frame — MORE than their share of
source. This is intentional: the bars take more space in output than they
did in source, because they ARE the product.
═══════════════════════════════════════════════════════════════════════════════
"""

import shlex
import subprocess
from pathlib import Path

from .markers import Marker
from .templates import Template


OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920
OUTPUT_FPS = 30

DEFAULT_CHART_RATIO = 0.55           # top 55% of source = chart
DEFAULT_OUTPUT_BARS_RATIO = 0.42     # bottom 42% of output = bar zone (emphasized)
TOP_CHROME_HEIGHT = 200
BOTTOM_CHROME_HEIGHT = 180


def _escape_drawtext(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace(",", "\\,")
    )


def _build_drawtext(
    text: str,
    *,
    font_size: int,
    font_color: str,
    bg_color: str | None,
    x: str = "(w-text_w)/2",
    y: str | int = 200,
    enable_from: float = 0.0,
    enable_to: float | None = None,
    fade_in_sec: float = 0.0,
) -> str:
    safe = _escape_drawtext(text)
    parts = [
        f"text='{safe}'",
        f"fontsize={font_size}",
        f"fontcolor={font_color}",
        f"x={x}",
        f"y={y}",
        "borderw=2",
        "bordercolor=black@0.7",
    ]
    if bg_color:
        parts.append("box=1")
        parts.append(f"boxcolor={bg_color}")
        parts.append("boxborderw=18")
    if enable_to is not None:
        parts.append(f"enable='between(t,{enable_from:.3f},{enable_to:.3f})'")
    else:
        parts.append(f"enable='gte(t,{enable_from:.3f})'")
    if fade_in_sec > 0:
        parts.append(
            f"alpha='if(lt(t,{enable_from:.3f}),0,"
            f"if(lt(t,{enable_from + fade_in_sec:.3f}),"
            f"(t-{enable_from:.3f})/{fade_in_sec:.3f},1))'"
        )
    return "drawtext=" + ":".join(parts)


def _probe_dimensions(path: Path) -> tuple[int, int, float]:
    out = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height:format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    lines = [l.strip() for l in out.stdout.strip().split("\n") if l.strip()]
    return int(lines[0]), int(lines[1]), float(lines[2])


def render_short(
    *,
    input_video: Path,
    output_video: Path,
    template: Template,
    markers: list[Marker],
    hook_text: str | None = None,
    project_root: Path,
    direction: str | None = None,
    chart_ratio: float = DEFAULT_CHART_RATIO,
    branding_level: str = "subtle",
) -> None:
    """v1.5 split-stack render. Bars get emphasis = product showcase."""

    src_w, src_h, source_duration = _probe_dimensions(input_video)

    chart_height_src = int(src_h * chart_ratio)
    bars_height_src = src_h - chart_height_src

    available_height = OUTPUT_HEIGHT - TOP_CHROME_HEIGHT - BOTTOM_CHROME_HEIGHT
    bars_zone_height = int(available_height * DEFAULT_OUTPUT_BARS_RATIO)
    chart_zone_height = available_height - bars_zone_height

    chart_zone_y = TOP_CHROME_HEIGHT
    bars_zone_y = TOP_CHROME_HEIGHT + chart_zone_height

    # Direction-aware accent
    if direction == "short":
        direction_accent = "#FF3344"
        direction_label = "SHORT"
    elif direction == "long":
        direction_accent = "#00FF88"
        direction_label = "LONG"
    else:
        direction_accent = "#00FF88"
        direction_label = None

    # Branding intensity
    branding_levels = {
        "subtle":   {"watermark_opacity": 0.75, "cta_duration": 2.0},
        "balanced": {"watermark_opacity": 0.85, "cta_duration": 2.5},
        "loud":     {"watermark_opacity": 1.0,  "cta_duration": 3.5},
    }
    bcfg = branding_levels.get(branding_level, branding_levels["balanced"])

    # Resolve assets
    music_rel = template.music.get("file", "")
    music_path = (project_root / music_rel) if music_rel else None
    music_volume_db = template.music.get("volume_db", -22)

    watermark_cfg = template.overlays.get("watermark_image", {})
    watermark_path = (
        project_root / watermark_cfg["file"]
        if watermark_cfg.get("file") and (project_root / watermark_cfg["file"]).exists()
        else None
    )

    cta_cfg = template.overlays.get("cta_card", {})
    cta_path = (
        project_root / cta_cfg["file"]
        if cta_cfg.get("file") and (project_root / cta_cfg["file"]).exists()
        else None
    )
    cta_duration = bcfg["cta_duration"]

    # Build inputs
    inputs: list[str] = ["-i", str(input_video)]
    next_idx = 1

    watermark_input_idx: int | None = None
    if watermark_path:
        inputs.extend(["-i", str(watermark_path)])
        watermark_input_idx = next_idx
        next_idx += 1

    cta_input_idx: int | None = None
    if cta_path:
        inputs.extend(["-loop", "1", "-t", str(cta_duration), "-i", str(cta_path)])
        cta_input_idx = next_idx
        next_idx += 1

    music_input_idx: int | None = None
    if music_path and music_path.exists():
        inputs.extend(["-stream_loop", "-1", "-i", str(music_path)])
        music_input_idx = next_idx
        next_idx += 1

    sfx_inputs: list[tuple[int, float, dict]] = []
    intro = template.sounds.get("intro_whoosh_at_t0")
    if intro and (project_root / intro["file"]).exists():
        inputs.extend(["-i", str(project_root / intro["file"])])
        sfx_inputs.append((next_idx, 0.0, intro))
        next_idx += 1

    for m in markers:
        sfx = template.sound_for(m.name)
        if not sfx:
            continue
        sfx_path = project_root / sfx["file"]
        if not sfx_path.exists():
            continue
        inputs.extend(["-i", str(sfx_path)])
        sfx_inputs.append((next_idx, m.time_sec, sfx))
        next_idx += 1

    # Filter graph
    filter_parts: list[str] = []

    # Crop source into TWO zones (split needs to be from a copied stream)
    filter_parts.append(f"[0:v]split=2[v_src1][v_src2]")
    filter_parts.append(
        f"[v_src1]crop={src_w}:{chart_height_src}:0:0,"
        f"scale={OUTPUT_WIDTH}:{chart_zone_height}:force_original_aspect_ratio=decrease,"
        f"pad={OUTPUT_WIDTH}:{chart_zone_height}:(ow-iw)/2:(oh-ih)/2:black,"
        f"setsar=1[v_chart_zone]"
    )
    filter_parts.append(
        f"[v_src2]crop={src_w}:{bars_height_src}:0:{chart_height_src},"
        f"scale={OUTPUT_WIDTH}:{bars_zone_height}:force_original_aspect_ratio=decrease,"
        f"pad={OUTPUT_WIDTH}:{bars_zone_height}:(ow-iw)/2:(oh-ih)/2:black,"
        f"setsar=1[v_bars_zone]"
    )

    # Black canvas
    filter_parts.append(
        f"color=c=black:s={OUTPUT_WIDTH}x{OUTPUT_HEIGHT}:d={source_duration}:r={OUTPUT_FPS}[v_canvas]"
    )
    filter_parts.append(f"[v_canvas][v_chart_zone]overlay=0:{chart_zone_y}[v_with_chart]")
    filter_parts.append(f"[v_with_chart][v_bars_zone]overlay=0:{bars_zone_y}[v_with_zones]")

    # Accent strip + label between zones
    accent_y = bars_zone_y - 4
    accent_strip = (
        f"drawbox=x=40:y={accent_y}:w={OUTPUT_WIDTH - 80}:h=2:"
        f"color={direction_accent}@0.9:t=fill"
    )
    label_drawtext = _build_drawtext(
        "HVT SIGNALS",
        font_size=22,
        font_color=direction_accent,
        bg_color="black@0.85",
        x="(w-text_w)/2",
        y=bars_zone_y - 36,
        enable_from=0.0,
    )
    filter_parts.append(f"[v_with_zones]{accent_strip},{label_drawtext}[v_with_separator]")

    # Other overlays
    overlay_parts: list[str] = []

    if hook_text:
        h = template.overlays.get("hook", {})
        overlay_parts.append(_build_drawtext(
            hook_text,
            font_size=h.get("font_size", 64),
            font_color=h.get("font_color", "white"),
            bg_color=h.get("bg_color", "black@0.85"),
            y=80,
            enable_from=0.0,
            enable_to=h.get("duration_sec", 2.5),
            fade_in_sec=h.get("fade_in_sec", 0.3),
        ))

    if direction_label:
        overlay_parts.append(_build_drawtext(
            direction_label,
            font_size=32,
            font_color=direction_accent,
            bg_color="black@0.85",
            x="w-text_w-30",
            y=chart_zone_y + 24,
            enable_from=0.0,
        ))

    for m in markers:
        ovr = template.overlay_for(m.name)
        if not ovr:
            continue
        label_color = ovr.get("font_color", "white")
        if m.name == "entry" and direction:
            label_color = direction_accent
        overlay_parts.append(_build_drawtext(
            ovr.get("text", m.name.upper()),
            font_size=ovr.get("font_size", 42),
            font_color=label_color,
            bg_color=ovr.get("bg_color", "black@0.85"),
            y=chart_zone_y + 60,
            enable_from=m.time_sec,
            enable_to=m.time_sec + ovr.get("duration_sec", 1.2),
            fade_in_sec=0.15,
        ))

    url_cfg = template.overlays.get("url_text", {})
    if url_cfg:
        overlay_parts.append(_build_drawtext(
            url_cfg.get("text", "highvelocitytrading.com"),
            font_size=url_cfg.get("font_size", 24),
            font_color=url_cfg.get("font_color", direction_accent),
            bg_color=None,
            x=url_cfg.get("x", "(w-text_w)/2"),
            y=OUTPUT_HEIGHT - 40,
            enable_from=0.0,
        ))

    if overlay_parts:
        filter_parts.append(f"[v_with_separator]{','.join(overlay_parts)}[v_pre_wm]")
    else:
        filter_parts.append("[v_with_separator]copy[v_pre_wm]")

    # Watermark
    if watermark_input_idx is not None:
        opacity = bcfg["watermark_opacity"]
        wm_x = watermark_cfg.get("x", "(W-w)/2")
        wm_y = OUTPUT_HEIGHT - 105
        filter_parts.append(
            f"[{watermark_input_idx}:v]format=rgba,colorchannelmixer=aa={opacity}[v_wm]"
        )
        filter_parts.append(f"[v_pre_wm][v_wm]overlay={wm_x}:{wm_y}[v_main]")
    else:
        filter_parts.append("[v_pre_wm]copy[v_main]")

    # CTA card concat
    if cta_input_idx is not None:
        filter_parts.append(
            f"[{cta_input_idx}:v]scale={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}:"
            f"force_original_aspect_ratio=decrease,"
            f"pad={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}:(ow-iw)/2:(oh-ih)/2:black,"
            f"setsar=1,fps={OUTPUT_FPS},format=yuv420p[v_cta]"
        )
        filter_parts.append("[v_main]format=yuv420p,fps=30[v_main_norm]")
        filter_parts.append("[v_main_norm][v_cta]concat=n=2:v=1:a=0[vout]")
        total_duration = source_duration + cta_duration
    else:
        filter_parts.append("[v_main]format=yuv420p,fps=30[vout]")
        total_duration = source_duration

    # Audio
    audio_streams: list[str] = []
    filter_parts.append(f"[0:a]volume=1.0,apad=whole_dur={total_duration}[a_src]")
    audio_streams.append("[a_src]")

    if music_input_idx is not None:
        filter_parts.append(
            f"[{music_input_idx}:a]atrim=duration={total_duration},"
            f"volume={music_volume_db}dB[a_music]"
        )
        audio_streams.append("[a_music]")

    for idx, (input_idx, t_sec, cfg) in enumerate(sfx_inputs):
        delay_ms = int(t_sec * 1000)
        gain_db = cfg.get("volume_db", -8)
        filter_parts.append(
            f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},"
            f"volume={gain_db}dB[a_sfx{idx}]"
        )
        audio_streams.append(f"[a_sfx{idx}]")

    if len(audio_streams) > 1:
        joined = "".join(audio_streams)
        filter_parts.append(
            f"{joined}amix=inputs={len(audio_streams)}:"
            f"duration=first:dropout_transition=0:normalize=0[aout]"
        )
        audio_out = "[aout]"
    else:
        audio_out = audio_streams[0]

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", audio_out,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{total_duration:.3f}",
        "-movflags", "+faststart",
        str(output_video),
    ]

    print(f"\n[render] HVT Clip v1.5 — split-stack")
    print(f"[render] Source: {src_w}x{src_h}, {source_duration:.2f}s")
    print(f"[render] Chart zone: {chart_zone_height}px (top)")
    print(f"[render] Bars zone:  {bars_zone_height}px (bottom — emphasized)")
    if direction_label:
        print(f"[render] Direction: {direction_label}")
    print(f"[render] Branding: {branding_level}")
    print(f"[render] Output: {total_duration:.2f}s\n")

    subprocess.run(cmd, check=True)
    print(f"\n✅ Wrote {output_video}")
