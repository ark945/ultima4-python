"""Data-file loading, ported from U4_FILE.C and the load calls in U4_INIT.C.

`Load`/`Save` in the original are thin DOS file reads of fixed-size structs. Here they
become Python helpers that resolve a file out of the game-data directory (case-insensitively,
since the original DOS names are upper-case but installs vary) and read/write bytes.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .state import Party

# The game-data directory. Overridable via env. Holds the editable plain-text sources
# (maps/, dialogue/, intro/, party_start.json) plus any runtime save the player writes.
DATA_DIR = Path(os.environ.get("U4_DATA", Path(__file__).resolve().parent.parent / "data"))

# The committed, editable party seeds — plain JSON that replaces the original binary
# PARTY.SAV / PARTY.NEW dumps (same single-source rule as .ULT->maps, .TLK->dialogue).
STARTING_PARTY_JSON = DATA_DIR / "party_start.json"      # fresh-game seed (was PARTY.SAV)
TEMPLATE_PARTY_JSON = DATA_DIR / "party_template.json"   # class companions (was PARTY.NEW)


def resolve(name: str) -> Path:
    """Find `name` in DATA_DIR, case-insensitively (DOS filenames vs. unix installs)."""
    direct = DATA_DIR / name
    if direct.exists():
        return direct
    lname = name.lower()
    for p in DATA_DIR.glob("*"):
        if p.name.lower() == lname:
            return p
    raise FileNotFoundError(f"{name} not found in {DATA_DIR} (drop U4 data files there)")


def load_bytes(name: str, expected_size: int | None = None) -> bytes:
    """C: Load() — read a whole data file; optionally assert its size."""
    data = resolve(name).read_bytes()
    if expected_size is not None and len(data) != expected_size:
        raise ValueError(f"{name}: expected {expected_size} bytes, got {len(data)}")
    return data


def load_starting_party() -> Party:
    """The committed fresh-game seed (was `PARTY.SAV`; now editable `party_start.json`).
    C: U4_INIT.C Load("PARTY.SAV", &Party) — but read from plain JSON, not a struct dump."""
    return Party.from_json(json.loads(STARTING_PARTY_JSON.read_text(encoding="utf-8")))


def load_template_party() -> Party:
    """The eight class-companion template (was `PARTY.NEW`; now `party_template.json`)."""
    return Party.from_json(json.loads(TEMPLATE_PARTY_JSON.read_text(encoding="utf-8")))


def load_party(name: str = "PARTY.SAV") -> Party:
    """Read a binary runtime save the player wrote with Quit&Save (Journey Onward reloads it).
    C: U4_INIT.C  Load("PARTY.SAV", sizeof(struct tParty), &Party)."""
    return Party.from_bytes(load_bytes(name))


def save_party(party: Party, name: str = "PARTY.SAV") -> None:
    """C: Save("PARTY.SAV", ...). Writes back the byte-accurate 502-byte image (runtime save)."""
    resolve_or_new = DATA_DIR / name
    resolve_or_new.write_bytes(party.to_bytes())
