# HVT Clip

> Automated polish engine for High Velocity Trading shorts. You cut. The system polishes. You post.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FFmpeg](https://img.shields.io/badge/ffmpeg-required-orange.svg)](https://ffmpeg.org/)

## What it does

Takes a hand-cut trading clip from Premiere with markers, applies a styled template (sound effects, music, branding overlays, hook text, vertical formatting), and outputs a polished 1080×1920 Short ready to post on YouTube Shorts, Instagram Reels, and TikTok.

The point: **you keep creative control over the cut. The system handles the production.** Sound design, captions, music ducking, branding — all automated. No more hours in Premiere per video.

## The workflow

```
1. Cut a winning trade in Premiere (30-60 sec)
2. Drop markers (M key) at entry, target, etc.
3. Export: video.mp4 + markers.csv (File → Export → Markers)
4. Drop both in input/
5. Run: python -m src.main input/your_clip.mp4 --template hype --hook "+$2,400 IN 22 MIN"
6. Polished short appears in output/
7. Post.
```

## Setup

### Prerequisites

- Python 3.10 or higher
- FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows: https://ffmpeg.org/download.html → add to PATH
```

### Install

```bash
git clone https://github.com/highvelocitytrading/hvt-clip.git
cd hvt-clip
python3 -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Add your assets

The system needs sound effects, music, and branding before it can produce polished output. See:
- `assets/sounds/README.md` for sound effect file list + free download sources
- `assets/music/README.md` for music file list + free download sources
- `assets/branding/` for logo placement (optional)

The system runs without these — it gracefully skips missing files — but the output won't have audio polish until you add them.

## Usage

```bash
# Big winning breakout
python -m src.main input/clip.mp4 --template hype --hook "+$2,400 IN 22 MIN"

# Patient setup that paid off
python -m src.main input/clip.mp4 --template cinematic --hook "I waited 40 minutes for this"

# Quick scalp / minimal style
python -m src.main input/clip.mp4 --template clean

# Educational / lesson trade
python -m src.main input/clip.mp4 --template lofi --hook "Lesson from this stop-out"
```

## Marker conventions

Use these EXACT marker names in Premiere for the system to recognize them:

| Marker name | Effect |
|---|---|
| `entry` | Plays entry sound + ENTRY label overlay |
| `target` | Plays cha-ching sound + TARGET label overlay |
| `stop` | Plays impact sound + STOPPED label overlay |
| `hook` | (Optional) marks where hook text should start |
| `reveal` | (Optional) marks the P&L reveal moment |

Markers without these names are ignored. The system does NOT crash if markers are missing — it just produces output without those effects.

## Project structure

```
hvt-clip/
├── src/
│   ├── main.py        # Entry point — runs the pipeline
│   ├── markers.py     # Reads Premiere CSV markers
│   ├── templates.py   # Loads style templates from config
│   └── render.py      # FFmpeg engine: composites video + audio + overlays
├── config/
│   └── templates.json # The TUNABLE FORMULA — change here, not in code
├── assets/
│   ├── sounds/        # SFX files (see README inside)
│   ├── music/         # BGM files (see README inside)
│   └── branding/      # Logo, brand assets
├── input/             # Drop .mp4 + .csv here
├── output/            # Polished shorts appear here
└── requirements.txt
```

## How to "lock in the formula" over time

This is the iteration loop the system was designed for:

1. **Weeks 1-2:** Use placeholder defaults. Post 5-10 shorts. Track which clips perform.
2. **Weeks 3-4:** Look at what's hitting. Was it the hook style? Music tempo? Caption color? Adjust `config/templates.json`.
3. **Weeks 5+:** Each tweak gets you closer to your winning formula. The pipeline never changes — only the config does.

The code is intentionally boring and stable so YOU can iterate the FORMULA without breaking the engine.

## Templates explained

| Template | When to use | Music vibe |
|---|---|---|
| `hype` | Big wins, breakouts, dollar-amount hooks | High-BPM trap/electronic |
| `cinematic` | Patient setups, slow-build trades | Orchestral, building |
| `clean` | Quick scalps, minimal style | Tech / Apple-style |
| `lofi` | Educational trades, lesson posts | Lo-fi chill |

To create a new template, copy an existing entry in `config/templates.json` and rename it.

## Output specs

- **Resolution:** 1080×1920 (9:16 vertical)
- **Framerate:** 30 fps
- **Codec:** H.264 / AAC, web-streaming optimized (`+faststart`)
- **Format:** MP4
- **Compatible with:** YouTube Shorts, Instagram Reels, TikTok, X/Twitter

## License

Proprietary — High Velocity Trading. Not for redistribution.
