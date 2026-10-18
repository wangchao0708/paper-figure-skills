"""Venue metadata and shared path helpers."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

VENUES: tuple[str, ...] = (
    "cvpr",
    "iccv",
    "neurips",
    "iclr",
    "icml",
    "acl",
    "aaai",
    "acmmm",
    "ccs",
    "sp",
    "usenixsec",
    "ndss",
    "tifs",
    "tpami",
    "ijcv",
    "tmm",
)

ALIASES: dict[str, tuple[str, ...]] = {
    "cvpr": ("CVPR",),
    "iccv": ("ICCV",),
    "neurips": ("NeurIPS", "NIPS"),
    "iclr": ("ICLR",),
    "icml": ("ICML",),
    "acl": ("ACL",),
    "aaai": ("AAAI",),
    "acmmm": ("MM", "ACM MM", "ACM-MM", "ACM Multimedia"),
    "ccs": ("CCS", "ACM CCS"),
    "sp": ("S&P", "IEEE S&P", "Oakland", "IEEE Symposium on Security and Privacy"),
    "usenixsec": ("USENIX Security", "USENIX Sec", "USENIX-Security"),
    "ndss": ("NDSS",),
    "tifs": ("TIFS", "IEEE TIFS", "IEEE Transactions on Information Forensics and Security"),
    "tpami": ("TPAMI", "IEEE TPAMI", "PAMI", "IEEE Transactions on Pattern Analysis and Machine Intelligence"),
    "ijcv": ("IJCV", "International Journal of Computer Vision"),
    "tmm": ("TMM", "IEEE TMM", "IEEE Transactions on Multimedia"),
}


def repo_root() -> Path:
    """Repository root, overridable with FIGSPEC_HOME."""
    override = os.environ.get("FIGSPEC_HOME")
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def venues_path() -> Path:
    return repo_root() / "figspec" / "data" / "venues.yaml"


def normalize_venue_name(name: str) -> str:
    name = name.replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", name.strip()).casefold()


def _alias_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for venue in VENUES:
        index[normalize_venue_name(venue)] = venue
        for alias in ALIASES[venue]:
            index[normalize_venue_name(alias)] = venue
    return index


_ALIAS_INDEX = _alias_index()


def resolve_venue(name: str) -> str:
    """Resolve a venue ID or alias to its canonical lowercase ID.

    Unknown names raise ValueError with the supported venue list.
    """
    key = normalize_venue_name(name)
    try:
        return _ALIAS_INDEX[key]
    except KeyError as exc:
        supported = ", ".join(VENUES)
        raise ValueError(f"unknown venue {name!r}; supported: {supported}") from exc


def empty_venue_data() -> dict[str, Any]:
    return {"schema_version": 1, "venues": {}}


def load_venue_data() -> dict[str, Any]:
    path = venues_path()
    if not path.exists():
        return empty_venue_data()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        return empty_venue_data()
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    if "venues" in raw:
        if not isinstance(raw["venues"], dict):
            raise ValueError(f"{path}: 'venues' must be a mapping")
        raw.setdefault("schema_version", 1)
        return raw
    # Accept a legacy flat venue mapping.
    if all(key in VENUES for key in raw):
        return {"schema_version": 1, "venues": raw}
    raise ValueError(f"{path}: expected a 'venues' mapping")


def find_paper_spec(start: Path | None = None) -> tuple[Path, dict[str, Any]] | None:
    """Find the nearest .figspec.yaml from start (inclusive) upward."""
    current = (start or Path.cwd()).expanduser().resolve()
    if current.is_file():
        current = current.parent
    for directory in (current, *current.parents):
        candidate = directory / ".figspec.yaml"
        if not candidate.is_file():
            continue
        raw = yaml.safe_load(candidate.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"{candidate} must contain a YAML mapping")
        return candidate, raw
    return None


def load_effective_venue(venue: str, start: Path | None = None) -> tuple[dict[str, Any], Path]:
    """Load a venue record from the nearest paper override or venues.yaml."""
    canonical = resolve_venue(venue)
    found = find_paper_spec(start)
    if found is not None:
        path, raw = found
        if "venues" in raw:
            venues = raw.get("venues")
            if not isinstance(venues, dict):
                raise ValueError(f"{path}: 'venues' must be a mapping")
            record = venues.get(canonical)
        else:
            record = raw
            if "venue" in raw:
                try:
                    declared = resolve_venue(str(raw["venue"]))
                except ValueError as exc:
                    raise ValueError(f"{path}: {exc}") from exc
                if declared != canonical:
                    raise ValueError(
                        f"{path} was probed for {declared}, not {canonical}"
                    )
        if isinstance(record, dict):
            return record, path
        raise ValueError(f"{path} has no specification for {canonical}")

    data = load_venue_data()
    record = data.get("venues", {}).get(canonical)
    if not isinstance(record, dict):
        raise ValueError(f"{venues_path()} has no specification for {canonical}")
    return record, venues_path()
