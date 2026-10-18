"""Venue metadata and shared path helpers."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
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

DISPLAY_NAMES: dict[str, str] = {
    "cvpr": "CVPR",
    "iccv": "ICCV",
    "neurips": "NeurIPS",
    "iclr": "ICLR",
    "icml": "ICML",
    "acl": "ACL",
    "aaai": "AAAI",
    "acmmm": "ACM MM",
    "ccs": "CCS",
    "sp": "S&P",
    "usenixsec": "USENIX Security",
    "ndss": "NDSS",
    "tifs": "TIFS",
    "tpami": "TPAMI",
    "ijcv": "IJCV",
    "tmm": "TMM",
}

FONT_NAMES: dict[str, str] = {
    "times": "Times New Roman",
    "libertine": "Linux Libertine O",
    "cm": "Latin Modern Roman",
}

MATHTEXT_FONTSETS: dict[str, str] = {
    "times": "stix",
    "cm": "cm",
    "libertine": "custom",
}

MIN_FONT_PT = 6.0

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


def normalize_layout(layout: str) -> str:
    key = layout.strip().casefold()
    if key in ("single", "single-column", "单栏"):
        return "single"
    if key in ("double", "double-column", "双栏"):
        return "double"
    raise ValueError(f"unknown layout {layout!r}; expected single or double")


@dataclass(frozen=True)
class FigureSpec:
    venue: str
    venue_name: str
    layout: str
    twocolumn: bool
    width_pt: float
    family: str
    font_name: str
    body_pt: float
    small_pt: float
    footnotesize_pt: float
    scriptsize_pt: float

    @property
    def width_in(self) -> float:
        return self.width_pt / 72.27

    @property
    def width_cm(self) -> float:
        return self.width_in * 2.54

    @property
    def label_pt(self) -> float:
        return self.footnotesize_pt

    @property
    def tick_pt(self) -> float:
        return self.scriptsize_pt

    @property
    def panel_title_pt(self) -> float:
        return self.small_pt


def _require_number(record: dict[str, Any], key: str, source: Path) -> float:
    try:
        value = float(record[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{source}: invalid or missing {key!r}") from exc
    if value <= 0:
        raise ValueError(f"{source}: {key!r} must be positive")
    return value


def get_spec(venue: str, layout: str, start: Path | None = None) -> FigureSpec:
    canonical = resolve_venue(venue)
    layout_id = normalize_layout(layout)
    record, source = load_effective_venue(canonical, start)

    twocolumn = bool(record.get("twocolumn", False))
    textwidth_pt = _require_number(record, "textwidth_pt", source)
    columnwidth_pt = _require_number(record, "columnwidth_pt", source)
    body_pt = _require_number(record, "body_pt", source)
    small_pt = _require_number(record, "small_pt", source)
    footnotesize_pt = _require_number(record, "footnotesize_pt", source)
    scriptsize_pt = _require_number(record, "scriptsize_pt", source)

    if twocolumn:
        width_pt = columnwidth_pt if layout_id == "single" else textwidth_pt
    else:
        width_pt = 0.48 * textwidth_pt if layout_id == "single" else textwidth_pt

    family = str(record.get("family", ""))
    if family not in FONT_NAMES:
        raise ValueError(f"{source}: unsupported font family {family!r}")

    return FigureSpec(
        venue=canonical,
        venue_name=DISPLAY_NAMES[canonical],
        layout=layout_id,
        twocolumn=twocolumn,
        width_pt=width_pt,
        family=family,
        font_name=FONT_NAMES[family],
        body_pt=max(MIN_FONT_PT, body_pt),
        small_pt=max(MIN_FONT_PT, small_pt),
        footnotesize_pt=max(MIN_FONT_PT, footnotesize_pt),
        scriptsize_pt=max(MIN_FONT_PT, scriptsize_pt),
    )


def setup(venue: str, layout: str) -> FigureSpec:
    """Configure matplotlib for a venue/layout and return its FigureSpec."""
    spec = get_spec(venue, layout)
    import matplotlib as mpl

    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": [spec.font_name],
            "font.size": spec.label_pt,
            "axes.labelsize": spec.label_pt,
            "axes.titlesize": spec.panel_title_pt,
            "xtick.labelsize": spec.tick_pt,
            "ytick.labelsize": spec.tick_pt,
            "legend.fontsize": spec.label_pt,
            "legend.title_fontsize": spec.label_pt,
            "figure.titlesize": spec.panel_title_pt,
            "mathtext.fontset": MATHTEXT_FONTSETS[spec.family],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.bbox": None,
        }
    )
    if spec.family == "libertine":
        mpl.rcParams.update(
            {
                "mathtext.rm": spec.font_name,
                "mathtext.it": f"{spec.font_name}:italic",
                "mathtext.bf": f"{spec.font_name}:bold",
            }
        )
    return spec


def _fmt_pt(value: float) -> str:
    return f"{value:g}"


def format_spec_line(spec: FigureSpec) -> str:
    layout_cn = "单栏" if spec.layout == "single" else "双栏"
    return (
        f"{spec.venue_name} · {layout_cn} → "
        f"{spec.width_in:.2f} in / {spec.width_pt:.1f} pt / {spec.width_cm:.2f} cm · "
        f"{spec.font_name} · 标签/图例 {_fmt_pt(spec.label_pt)} · "
        f"刻度 {_fmt_pt(spec.tick_pt)} · 子图标题 {_fmt_pt(spec.panel_title_pt)} (pt)"
    )


def load_drawio_config() -> dict[str, Any] | None:
    config = load_venue_data().get("drawio")
    if not isinstance(config, dict):
        return None
    try:
        units_per_pt = float(config["drawio_units_per_pt"])
    except (KeyError, TypeError, ValueError):
        return None
    if units_per_pt <= 0:
        return None
    return config


def format_drawio_line(spec: FigureSpec, config: dict[str, Any] | None = None) -> str | None:
    config = config or load_drawio_config()
    if not config:
        return None
    try:
        units_per_pt = float(config["drawio_units_per_pt"])
    except (KeyError, TypeError, ValueError):
        return None
    return (
        f"draw.io: 页面宽度 {spec.width_pt * units_per_pt:.1f} px · "
        f"标签/图例 {spec.label_pt * units_per_pt:.1f} · "
        f"刻度 {spec.tick_pt * units_per_pt:.1f} · "
        f"子图标题 {spec.panel_title_pt * units_per_pt:.1f}"
    )
