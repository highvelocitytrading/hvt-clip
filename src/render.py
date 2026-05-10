"""
render.py — The FFmpeg-driven render engine.

Takes:
- A video clip (any aspect ratio, any length)
- A list of markers (entry, target, etc. with timestamps)
- A template (music + sound + overlay config)
- An optional hook text

Produces:
- A polished 1080x1920 vertical Short with music ducked under sound effects,
  branded overlays at marker times, and a hook at the start.

Strategy:
- Build one big FFmpeg command rather than chaining many. FFmpeg is fastest
  when it does everything in one pipeline because it avoids re-encoding.
- We use the filter_complex graph to layer audio and add drawtext overlays.
"""

import shlex
import subprocess
from pathlib import Path

from .markers import Marker, find_marker
from .templates import Template


# --- Final output dimensions ---
OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920
OUTPUT_FPS = 30


def _escape_drawtext(text: str) -> str:
    """
    Escape characters for FFmpeg's drawtext filter.
    Single quotes and colons are special; backslashes need doubling.
    """
    # The order matters here — escape backslashes first.
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace(",", "\\,")
    )


def _build_drawtext_filter(
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
    """
    Build a single drawtext filter expression.

    enable_from / enable_to: when the text appears (in seconds).
    fade_in_sec: optional fade-in duration at the start.
    """
    safe = _escape_drawtext(text)
    parts = [
        f"text='{safe}'",
        f"fontsize={font_size}",
        f"fontcolor={font_color}",
        f"x={x}",
        f"y={y}",
        "borderw=2",
        "bordercolor=black@0.6",
    ]
    if bg_color:
        parts.append("box=1")
        parts.append(f"boxcolor={bg_color}")
        parts.append("boxborderw=20")

    if enable_to is not None:
        parts.append(
            f"enable='between(t,{enable_from:.3f},{enable_to:.3f})'"
        )
    else:
        parts.append(f"enable='gte(t,{enable_from:.3f})'")

    if fade_in_sec > 0:
        # fade alpha from 0 to 1 over fade_in_sec, starting at enable_from
        parts.append(
            f"alpha='if(lt(t,{enable_from:.3f}),0,"
            f"if(lt(t,{enable_from + fade_in_sec:.3f}),"
            f"(t-{enable_from:.3f})/{fade_in_sec:.3f},1))'"
        )

    return "drawtext=" + ":".join(parts)


def render_short(
    *,
    input_video: Path,
    output_video: Path,
    template: Template,
    markers: list[Marker],
    hook_text: str | None = None,
    project_root: Path,
) -> None:
    """
    Run the full polish pipeline. Writes output_video.

    Raises subprocess.CalledProcessError if FFmpeg fails.
    """

    # Resolve asset paths relative to project root
    music_rel = template.music.get("file", "")
    music_path = (project_root / music_rel) if music_rel else None
    music_volume_db = template.music.get("volume_db", -20)

    # ---- Build the input list ----
    # input 0 = source video
    # input 1 = music (if exists)
    # input 2..N = sound effects
    inputs: list[str] = ["-i", str(input_video)]
    music_input_index: int | None = None
    sfx_inputs: list[tuple[int, float, dict]] = []  # (input_index, time_sec, sfx_cfg)

    if music_path and music_path.exists():
        inputs.extend(["-stream_loop", "-1", "-i", str(music_path)])
        music_input_index = 1
        next_idx = 2
    else:
        next_idx = 1

    # Intro whoosh at t=0
    intro = template.sounds.get("intro_whoosh_at_t0")
    if intro:
        intro_path = project_root / intro["file"]
        if intro_path.exists():
            inputs.extend(["-i", str(intro_path)])
            sfx_inputs.append((next_idx, 0.0, intro))
            next_idx += 1

    # One sfx per matching marker
    for marker in markers:
        sfx = template.sound_for(marker.name)
        if not sfx:
            continue
        sfx_path = project_root / sfx["file"]
        if not sfx_path.exists():
            continue
        inputs.extend(["-i", str(sfx_path)])
        sfx_inputs.append((next_idx, marker.time_sec, sfx))
        next_idx += 1

    # ---- Build the filter graph ----
    filter_parts: list[str] = []

    # 1. Video chain: scale + pad to 1080x1920, then add overlays
    video_chain = (
        f"[0:v]scale={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}:(ow-iw)/2:(oh-ih)/2:black,"
        f"setsar=1,fps={OUTPUT_FPS}"
    )

    drawtext_filters: list[str] = []

    # Hook overlay (starts at t=0)
    if hook_text:
        hook_cfg = template.overlays.get("hook", {})
        drawtext_filters.append(_build_drawtext_filter(
            hook_text,
            font_size=hook_cfg.get("font_size", 80),
            font_color=hook_cfg.get("font_color", "white"),
            bg_color=hook_cfg.get("bg_color", "black@0.8"),
            y=hook_cfg.get("y_position", 200),
            enable_from=0.0,
            enable_to=hook_cfg.get("duration_sec", 2.5),
            fade_in_sec=hook_cfg.get("fade_in_sec", 0.2),
        ))

    # Marker labels (entry, target, stop)
    for marker in markers:
        ovr = template.overlay_for(marker.name)
        if not ovr:
            continue
        drawtext_filters.append(_build_drawtext_filter(
            ovr.get("text", marker.name.upper()),
            font_size=ovr.get("font_size", 56),
            font_color=ovr.get("font_color", "white"),
            bg_color=ovr.get("bg_color", "black@0.75"),
            y=ovr.get("y_position", 280),
            enable_from=marker.time_sec,
            enable_to=marker.time_sec + ovr.get("duration_sec", 1.2),
            fade_in_sec=0.1,
        ))

    # Watermark (always on)
    wm = template.overlays.get("watermark")
    if wm:
        drawtext_filters.append(_build_drawtext_filter(
            wm.get("text", ""),
            font_size=wm.get("font_size", 28),
            font_color=wm.get("font_color", "white@0.85"),
            bg_color=None,
            x=wm.get("x", "(w-text_w)/2"),
            y=wm.get("y", "h-60"),
            enable_from=0.0,
        ))

    if drawtext_filters:
        video_chain += "," + ",".join(drawtext_filters)

    filter_parts.append(f"{video_chain}[vout]")

    # 2. Audio chain
    audio_chain_outputs: list[str] = []

    # Source video audio (might be silent — that's fine)
    filter_parts.append(f"[0:a]volume=1.0[a_src]")
    audio_chain_outputs.append("[a_src]")

    # Music (looped, ducked under sound effects)
    if music_input_index is not None:
        # Convert dB to linear gain (volume filter takes dB directly)
        filter_parts.append(
            f"[{music_input_index}:a]volume={music_volume_db}dB[a_music]"
        )
        audio_chain_outputs.append("[a_music]")

    # Sound effects (delayed to their marker time)
    for idx, (input_idx, t_sec, cfg) in enumerate(sfx_inputs):
        delay_ms = int(t_sec * 1000)
        gain_db = cfg.get("volume_db", -8)
        filter_parts.append(
            f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},"
            f"volume={gain_db}dB[a_sfx{idx}]"
        )
        audio_chain_outputs.append(f"[a_sfx{idx}]")

    # Mix all audio streams together
    if len(audio_chain_outputs) > 1:
        joined = "".join(audio_chain_outputs)
        filter_parts.append(
            f"{joined}amix=inputs={len(audio_chain_outputs)}:"
            f"duration=first:dropout_transition=0:normalize=0[aout]"
        )
        audio_out = "[aout]"
    else:
        audio_out = audio_chain_outputs[0]

    filter_complex = ";".join(filter_parts)

    # ---- Assemble the final ffmpeg command ----
    cmd = [
        "ffmpeg",
        "-y",  # overwrite output without asking
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
        "-shortest",
        "-movflags", "+faststart",
        str(output_video),
    ]

    print("\n[render] Running FFmpeg...")
    print("[render] Command:", " ".join(shlex.quote(c) for c in cmd[:6]), "...")
    print()

    subprocess.run(cmd, check=True)
    print(f"\n✅ Wrote {output_video}")
