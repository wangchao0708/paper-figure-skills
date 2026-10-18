"""Install and verify the fonts used by paper figures."""

from __future__ import annotations

import filecmp
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .spec import FONT_NAMES


class FontError(RuntimeError):
    """Font installation or lookup failed."""


FONT_FILES: tuple[str, ...] = (
    # Linux Libertine O: regular, bold, italic, bold italic.
    "LinLibertine_R.otf",
    "LinLibertine_RB.otf",
    "LinLibertine_RI.otf",
    "LinLibertine_RBI.otf",
    # Latin Modern Roman: regular, bold, italic, bold italic.
    "lmroman10-regular.otf",
    "lmroman10-bold.otf",
    "lmroman10-italic.otf",
    "lmroman10-bolditalic.otf",
)


@dataclass(frozen=True)
class FontStatus:
    family: str
    path: Path | None


def user_font_dir() -> Path:
    return Path.home() / "Library" / "Fonts"


def _kpsewhich(filename: str) -> Path:
    executable = shutil.which("kpsewhich")
    if not executable:
        raise FontError("kpsewhich not found in PATH (MacTeX is required)")
    proc = subprocess.run(
        [executable, filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
    )
    result = proc.stdout.strip()
    if proc.returncode != 0 or not result:
        raise FontError(f"kpsewhich could not find {filename}")
    path = Path(result).expanduser()
    if not path.is_file():
        raise FontError(f"kpsewhich returned a missing file for {filename}: {path}")
    return path


def rebuild_cache() -> None:
    from matplotlib import font_manager

    # _load_fontmanager is the supported way to rescan all font directories;
    # assigning the result makes the fresh manager visible to findfont().
    font_manager.fontManager = font_manager._load_fontmanager(try_read_cache=False)


def install_fonts() -> list[tuple[Path, Path, str]]:
    target_dir = user_font_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    results: list[tuple[Path, Path, str]] = []

    for filename in FONT_FILES:
        source = _kpsewhich(filename)
        destination = target_dir / filename
        if destination.exists() and filecmp.cmp(source, destination, shallow=False):
            action = "unchanged"
        else:
            shutil.copy2(source, destination)
            action = "installed"
        results.append((source, destination, action))

    rebuild_cache()
    return results


def check_fonts() -> list[FontStatus]:
    from matplotlib import font_manager

    # On macOS a freshly copied font can be present on disk but absent from
    # the process's existing font manager. Registering the installed files is
    # idempotent from the caller's point of view and makes --install followed
    # immediately by a check reliable.
    for filename in FONT_FILES:
        path = user_font_dir() / filename
        if path.is_file():
            try:
                font_manager.fontManager.addfont(str(path))
            except Exception:
                pass

    statuses: list[FontStatus] = []
    for family in FONT_NAMES.values():
        try:
            path = Path(
                font_manager.findfont(
                    font_manager.FontProperties(family=family),
                    fallback_to_default=False,
                )
            )
            statuses.append(FontStatus(family=family, path=path))
        except ValueError:
            statuses.append(FontStatus(family=family, path=None))
    return statuses
