"""
markers.py — Reads Premiere Pro's markers CSV export.

Premiere exports markers as TSV (tab-separated) with columns:
    Marker Name | Description | In | Out | Duration | Marker Type
"""

import csv
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Marker:
    name: str
    time_sec: float


def _timecode_to_seconds(timecode: str, framerate: float = 30.0) -> float:
    parts = timecode.strip().split(":")
    if len(parts) != 4:
        raise ValueError(f"Bad timecode: {timecode!r}")
    h, m, s, f = (int(p) for p in parts)
    return h * 3600 + m * 60 + s + f / framerate


def read_markers(csv_path: Path, framerate: float = 30.0) -> list[Marker]:
    markers: list[Marker] = []
    if not csv_path.exists():
        return markers

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        first_row = next(reader, None)

        if first_row and len(first_row) <= 1:
            f.seek(0)
            reader = csv.DictReader(f, delimiter=",")
            first_row = next(reader, None)

        rows = []
        if first_row:
            rows.append(first_row)
        rows.extend(reader)

        for row in rows:
            name = (row.get("Marker Name") or "").strip().lower()
            in_tc = (row.get("In") or "").strip()
            if not name or not in_tc:
                continue
            name = re.sub(r"[^a-z0-9_]", "", name)
            if not name:
                continue
            try:
                t = _timecode_to_seconds(in_tc, framerate=framerate)
            except ValueError:
                continue
            markers.append(Marker(name=name, time_sec=t))

    return markers


def find_marker(markers: list[Marker], name: str) -> Marker | None:
    target = name.lower()
    for m in markers:
        if m.name == target:
            return m
    return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m src.markers <path/to/markers.csv>")
        sys.exit(1)
    found = read_markers(Path(sys.argv[1]))
    if not found:
        print("No markers found.")
    for m in found:
        print(f"  {m.name:20s} at {m.time_sec:.2f}s")
