# Branding Assets

This folder contains the visual identity files the system burns onto every video.

## Files

- `hvt_watermark.png` — the bottom-of-frame watermark (transparent PNG, ~240×80px)
- `cta_card.png` — the full-frame outro card shown in the last 2.5 sec (1080×1920px, opaque)

## Replacing the placeholders with real HVT brand

The repo ships with placeholder versions so the system runs out of the box. To use the real HVT logo:

### Watermark

1. Export your V/HVT logo as a transparent PNG
2. Recommended size: 240×80px (keeps it small and unobtrusive at phone size)
3. Save as `hvt_watermark.png` in this folder, overwriting the placeholder

### CTA card

1. Design a 1080×1920 vertical card with:
   - Black background
   - Big HVT/V logo, centered
   - Tagline: "TRADE WITH STRUCTURE. NO EMOTION."
   - URL: `highvelocitytrading.com` (in #00FF88)
2. Export as PNG
3. Save as `cta_card.png` in this folder

That's it. The system reads from these paths directly — no code changes needed when you swap them.

## Brand colors (extracted from highvelocitytrading.com)

- Background: `#000000` (pure black)
- Text primary: `#FFFFFF` (white)
- Accent green: `#00FF88` (signal/CTA color)
- Warning red: `#FF3344` (stop/loss color)
- Neutral grey: `#9CA3AF` (subtitle text)
