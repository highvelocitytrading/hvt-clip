# HVT Clip — The Polish Engine

Takes a hand-cut trading clip from Premiere with markers, adds sound effects, music, and branding overlays, and outputs a polished vertical Short ready to post.

## The workflow

```
1. You cut a winning trade in Premiere (30-60 sec)
2. You drop markers (M key) at entry, target, etc.
3. You export: .mp4 + markers.csv (File → Export → Markers)
4. You drop both in input/
5. You run: python -m src.main input/your_clip.mp4 --template hype
6. Polished short appears in output/
7. You post.
```

## Project structure

```
hvt-clip/
├── src/                  # The actual code
│   ├── main.py           # Entry point — runs the pipeline
│   ├── markers.py        # Reads Premiere CSV markers
│   ├── effects.py        # Adds sound effects at marker times
│   ├── overlays.py       # Adds text/branding overlays
│   ├── render.py         # Final FFmpeg compose & export
│   └── templates.py      # The 4 style templates (hype, cinematic, clean, lofi)
├── assets/
│   ├── sounds/           # whoosh.mp3, entry.mp3, target.mp3, etc.
│   ├── music/            # hype.mp3, cinematic.mp3, clean.mp3, lofi.mp3
│   └── branding/         # logo.png, your visual identity
├── config/
│   └── templates.json    # The tunable formula — change here as you find what works
├── input/                # Drop your .mp4 + markers.csv here
└── output/               # Polished shorts appear here
```

## How to "lock in the formula" over time

This is the iteration loop:

1. **Week 1-2:** Use placeholder defaults. Post 5-10 shorts. Track which clips perform.
2. **Week 3-4:** Look at what's hitting. Was it the hook style? The music tempo? Caption color? Adjust `config/templates.json`.
3. **Week 5+:** Each tweak gets you closer to your winning formula. The pipeline never changes — only the config does.

The system is designed to be **boringly stable** so YOU can iterate the FORMULA without breaking the engine.

## Marker conventions

Use these exact marker names in Premiere for the system to know what to do:

- `entry` → places entry sound + ENTRY callout
- `target` → places target/cha-ching sound + TARGET callout
- `stop` → places impact sound + STOP callout
- `hook` → marks where the hook text starts (usually 0:00)
- `reveal` → P&L reveal moment (usually near end)

Other markers (without these names) are ignored.

## Templates

```bash
# Big winning breakout
python -m src.main input/clip.mp4 --template hype

# Patient setup that paid off
python -m src.main input/clip.mp4 --template cinematic

# Quick scalp / tech vibe
python -m src.main input/clip.mp4 --template clean

# Educational / lesson
python -m src.main input/clip.mp4 --template lofi
```

## Custom hook text

```bash
python -m src.main input/clip.mp4 --template hype --hook "+$2,400 IN 22 MIN"
```

If no `--hook` is provided, no hook overlay is added.
