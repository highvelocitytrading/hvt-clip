"""
templates.py — Loads style templates from config/templates.json.

To tweak how everything looks/sounds, edit config/templates.json — NOT this code.
The code stays stable while you iterate the formula.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Template:
    name: str
    description: str
    music: dict[str, Any]
    sounds: dict[str, dict[str, Any]]
    overlays: dict[str, dict[str, Any]]
    raw: dict[str, Any] = field(repr=False)

    def sound_for(self, marker_name: str) -> dict[str, Any] | None:
        return self.sounds.get(marker_name)

    def overlay_for(self, marker_name: str) -> dict[str, Any] | None:
        return self.overlays.get(f"{marker_name}_label")


def _config_path(p: Path | None) -> Path:
    if p is not None:
        return p
    return Path(__file__).resolve().parent.parent / "config" / "templates.json"


def load_template(template_name: str, config_path: Path | None = None) -> Template:
    cp = _config_path(config_path)
    if not cp.exists():
        raise FileNotFoundError(f"Template config not found at {cp}")
    with cp.open("r", encoding="utf-8") as f:
        all_templates = json.load(f)

    # Skip metadata keys (keys starting with underscore)
    available_templates = {
        k: v for k, v in all_templates.items() if not k.startswith("_")
    }

    if template_name not in available_templates:
        avail = ", ".join(available_templates.keys())
        raise ValueError(f"Template {template_name!r} not found. Available: {avail}")

    cfg = available_templates[template_name]
    return Template(
        name=template_name,
        description=cfg.get("description", ""),
        music=cfg.get("music", {}),
        sounds=cfg.get("sounds", {}),
        overlays=cfg.get("overlays", {}),
        raw=cfg,
    )


def list_templates(config_path: Path | None = None) -> list[str]:
    cp = _config_path(config_path)
    with cp.open("r", encoding="utf-8") as f:
        all_templates = json.load(f)
    return [k for k in all_templates.keys() if not k.startswith("_")]


if __name__ == "__main__":
    print("Available templates:")
    for name in list_templates():
        t = load_template(name)
        print(f"  {name:14s} — {t.description}")
