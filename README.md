# HVT Clip

> Automated polish engine for High Velocity Trading shorts. Split-stack rendering puts the signal bars front and center — they're the product.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FFmpeg](https://img.shields.io/badge/ffmpeg-required-orange.svg)](https://ffmpeg.org/)
[![Version](https://img.shields.io/badge/version-1.5-green.svg)](#)

## System mission

This system exists to drive sales of HVT trading indicators. Every video produced must:

1. **Visually emphasize the colored signal bars** (Momentum / Correlation / Volume Profile) — they are the product being sold
2. **Be polished enough to perform on Shorts/Reels/TikTok** — virality and sales are co-equal goals
3. **End with a CTA** pointing to highvelocitytrading.com

## What v1.5 does that v1 didn't

- **Split-stack rendering** — source frame is cropped into two zones: chart on top, signal bars on bottom. Stacked vertically. Bar zone gets ~42% of the output frame, MORE than its share of the source. The bars take more space because they ARE the product.
- **Direction awareness** — `--direction long` or `--direction short` flag. Long trades use green accents. Short trades use red. Adds a corner badge ("LONG" or "SHORT") and color-codes the entry label accordingly.
- **Branding levels** — `--branding subtle|balanced|loud` flag. Subtle = small watermark + brief CTA card (best for virality). Loud = bigger watermark + longer CTA (more sales-pitch-y).
- **Configurable chart ratio** — `--chart-ratio 0.55` flag if your indicator panel is taller/shorter than the default.

## The workflow

```
1. Cut a winning trade in Premiere (30-60 sec)
2. (Optional) Drop markers (M key) at entry, target, etc.
3. Export: video.mp4
4. Drop in input/
5. Run: python -m src.main input/your_clip.mp4 --direction long --hook "GREEN MEANS BUY."
6. Polished short appears in output/ — ready to post
```

## Setup

### Prerequisites

- Python 3.10+
- FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### Install

```bash
git clone https://github.com/highvelocitytrading/hvt-clip.git
cd hvt-clip
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Basic usage (defaults to subtle branding, no direction)

```bash
python -m src.main input/clip.mp4 --hook "GREEN MEANS BUY."
```

### Long trade

```bash
python -m src.main input/clip.mp4 \
  --direction long \
  --hook "+\$840 IN 12 MIN"
```

### Short trade (triple red signal)

```bash
python -m src.main input/clip.mp4 \
  --direction short \
  --hook "TRIPLE RED. CLEAN SHORT."
```

### Tune the chart-vs-bars split

If your bars panel is shorter (taking only ~30% of source), use:
```bash
python -m src.main input/clip.mp4 --chart-ratio 0.70
```

If your bars panel is bigger (taking ~50% of source), use:
```bash
python -m src.main input/clip.mp4 --chart-ratio 0.50
```

### Adjust branding intensity

```bash
# Subtle (default) — small watermark, 2-second CTA. Best for virality.
python -m src.main input/clip.mp4 --branding subtle

# Balanced — medium watermark, 2.5-second CTA
python -m src.main input/clip.mp4 --branding balanced

# Loud — full opacity watermark, 3.5-second CTA. Most sales-pitch.
python -m src.main input/clip.mp4 --branding loud
```

## Hook copy patterns (matches HVT brand voice)

The brand on highvelocitytrading.com is calm/institutional, not hype. Match it:

✅ Good:
- `"GREEN MEANS BUY."`
- `"TRIPLE RED. CLEAN SHORT."`
- `"WAIT FOR ALIGNMENT."`
- `"+\$500 IN 8 MIN"` (specific numbers convert)
- `"SAME SETUP. EVERY DAY."`

❌ Avoid:
- `"INSANE WIN!!!"` (too hype)
- Hook with hype emojis
- More than 5 words

## Marker conventions (optional)

If you drop markers in Premiere with these names, the system places sound effects + text labels at those moments:

| Marker name | Effect |
|---|---|
| `entry` | ENTRY label + signal-tick sound at that timestamp |
| `target` | TARGET label + confirm sound |
| `stop` | STOP label + impact sound |

Markers are optional. The system runs without them — you just won't get timed effects.

## Project structure

```
hvt-clip/
├── src/
│   ├── main.py        # Entry point — runs the pipeline
│   ├── markers.py     # Reads Premiere CSV markers
│   ├── templates.py   # Loads style templates from config
│   └── render.py      # FFmpeg engine: split-stack + overlays + CTA card
├── config/
│   └── templates.json # The TUNABLE FORMULA — change here, not in code
├── assets/
│   ├── sounds/        # SFX files
│   ├── music/         # BGM files
│   └── branding/      # Watermark + CTA card images
├── input/             # Drop .mp4 + (optional) .csv here
├── output/            # Polished shorts appear here
└── requirements.txt
```

## How to "lock in the formula" over time

The system was designed for iteration:

1. **Weeks 1-2:** Use defaults. Post 5-10 shorts. Track which clips perform.
2. **Weeks 3-4:** Tweak `config/templates.json` based on what's hitting.
3. **Weeks 5+:** Each tweak gets you closer to your winning formula. The pipeline never changes. Only the config does.

To create a new template, copy an existing entry in `config/templates.json` and rename it.

## Output specs

- **Resolution:** 1080×1920 (9:16 vertical)
- **Framerate:** 30 fps
- **Codec:** H.264 / AAC, web-streaming optimized (`+faststart`)
- **CTA card:** Auto-appended last 2-3.5s of every video (depends on branding level)
- **Compatible with:** YouTube Shorts, Instagram Reels, TikTok, X/Twitter

## License

Proprietary — High Velocity Trading. Not for redistribution.
