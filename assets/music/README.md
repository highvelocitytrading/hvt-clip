# Background Music

Drop your music files in this folder with the EXACT names below.

## Required files (one per template)

- `hype.mp3` — high-energy trap / electronic, 130+ BPM
- `cinematic.mp3` — orchestral build, 90-110 BPM
- `clean.mp3` — minimal tech / Apple-style, 100-120 BPM
- `lofi.mp3` — chill lo-fi beat, 70-90 BPM

## Where to get them (free)

1. **YouTube Audio Library** — https://www.youtube.com/audiolibrary
   - **Best option.** Filter by mood, BPM, attribution-not-required.
2. **Pixabay Music** — https://pixabay.com/music/
   - Free for commercial use including monetization.
3. **Free Music Archive** — https://freemusicarchive.org/
   - Larger, mixed licenses.

## Important about volume

The templates expect mastered, balanced music tracks. If your track is too quiet or too loud, edit the `volume_db` value in `config/templates.json`:

```json
"music": {
  "file": "assets/music/hype.mp3",
  "volume_db": -18,    ← lower this number to make music quieter
}
```

## Important about length

If your music track is shorter than your video clip, the system loops it automatically. So a 60-second music track works fine for a 60-second clip.

## Tip

You don't need all 4 right away. Start with `hype.mp3` (the template most trading content uses), get one short produced end-to-end, then expand.
