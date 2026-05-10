"""
markers.py — Reads Premiere Pro's markers CSV export.

Premiere exports markers as CSV with columns like:
    Marker Name,Description,In,Out,Duration,Marker Type
    entry,,00:00:08:14,00:00:08:14,00:00:00:00,Comment

We care about: Marker Name and In (the timestamp).

Example output:
    [
        Marker(name="entry", time_sec=8.58),
        Marker(name="target", time_sec=42.12),
    ]
"""

import csv
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Marker:
    """A single marker from Premiere — what it is and when it happens."""
    name: str
    time_sec: float


def _timecode_to_seconds(timecode: str, framerate: float = 30.0) -> float:
    """
    Convert Premiere's timecode (HH:MM:SS:FF) to seconds.

    Example: '00:00:08:14' at 30fps → 8 + 14/30 → 8.467 seconds
    """
    parts = timecode.strip().split(":")
    if len(parts) != 4:
        raise ValueError(f"Bad timecode: {timecode!r}")
    h, m, s, f = (int(p) for p in parts)
    return h * 3600 + m * 60 + s + f / framerate


def read_markers(csv_path: Path, framerate: float = 30.0) -> list[Marker]:
    """
    Read a Premiere markers CSV file and return a list of Marker objects.

    Marker names are normalized to lowercase to make matching forgiving
    ("Entry", "ENTRY", "entry" all become "entry").

    Markers without a name are skipped silently.
    """
    markers: list[Marker] = []

    if not csv_path.exists():
        # No markers file? That's fine — return empty list.
        # The pipeline will still run, just without sound effects at marker times.
        return markers

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")  # Premiere exports as TSV by default

        # Some Premiere exports use commas instead. Detect and reparse.
        first_row = next(reader, None)
        if first_row and len(first_row) <= 1:
            f.seek(0)
            reader = csv.DictReader(f, delimiter=",")
            first_row = next(reader, None)

        # Process the first row we already pulled, then continue
        rows = []
        if first_row:
            rows.append(first_row)
        rows.extend(reader)

        for row in rows:
            name = (row.get("Marker Name") or "").strip().lower()
            in_tc = (row.get("In") or "").strip()

            if not name or not in_tc:
                continue  # skip empty rows

            # Strip non-allowed characters from name (just letters/numbers)
            name = re.sub(r"[^a-z0-9_]", "", name)
            if not name:
                continue

            try:
                t = _timecode_to_seconds(in_tc, framerate=framerate)
            except ValueError:
                continue  # skip rows we can't parse

            markers.append(Marker(name=name, time_sec=t))

    return markers


def find_marker(markers: list[Marker], name: str) -> Marker | None:
    """Find the first marker matching name (case-insensitive). Returns None if not found."""
    target = name.lower()
    for m in markers:
        if m.name == target:
            return m
    return None


# Quick self-test if you run this file directly
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
