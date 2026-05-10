"""
templates.py — Loads the templates config and exposes the active template.

A "template" is your reusable formula: which music, which sounds, which overlays,
which colors, which timing.

To tweak how everything looks/sounds, you edit config/templates.json — NOT this code.
That separation is the point: the code stays stable while you iterate the formula.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Template:
    """A loaded style template (hype, cinematic, clean, lofi)."""
    name: str
    description: str
    music: dict[str, Any]
    sounds: dict[str, dict[str, Any]]
    overlays: dict[str, dict[str, Any]]
    raw: dict[str, Any] = field(repr=False)

    def sound_for(self, marker_name: str) -> dict[str, Any] | None:
        """
        Return the sound config for a given marker name (entry/target/stop).
        Returns None if no sound is configured for that marker.
        """
        return self.sounds.get(marker_name)

    def overlay_for(self, marker_name: str) -> dict[str, Any] | None:
        """
        Return the overlay config for a given marker (entry_label, target_label, etc.)
        Note: marker name 'entry' maps to overlay key 'entry_label'.
        """
        key = f"{marker_name}_label"
        return self.overlays.get(key)


def load_template(template_name: str, config_path: Path | None = None) -> Template:
    """
    Load a template by name from config/templates.json.

    Raises ValueError if the template name doesn't exist.
    """
    if config_path is None:
        # default location relative to project root
        config_path = Path(__file__).resolve().parent.parent / "config" / "templates.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Template config not found at {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        all_templates = json.load(f)

    if template_name not in all_templates:
        available = ", ".join(all_templates.keys())
        raise ValueError(
            f"Template {template_name!r} not found. Available: {available}"
        )

    cfg = all_templates[template_name]
    return Template(
        name=template_name,
        description=cfg.get("description", ""),
        music=cfg.get("music", {}),
        sounds=cfg.get("sounds", {}),
        overlays=cfg.get("overlays", {}),
        raw=cfg,
    )


def list_templates(config_path: Path | None = None) -> list[str]:
    """Return all available template names."""
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / "config" / "templates.json"
    with config_path.open("r", encoding="utf-8") as f:
        return list(json.load(f).keys())


if __name__ == "__main__":
    print("Available templates:")
    for name in list_templates():
        t = load_template(name)
        print(f"  {name:12s} — {t.description}")
