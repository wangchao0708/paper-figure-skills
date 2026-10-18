"""Check an exported figure PDF against a venue specification."""

from __future__ import annotations

import re
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import fitz

from .probe import classify_family
from .spec import FigureSpec, get_spec


class CheckError(RuntimeError):
    """The PDF could not be inspected."""


@dataclass(frozen=True)
class FontInfo:
    name: str
    font_type: str
    encoding: str
    embedded: bool

    @property
    def type3(self) -> bool:
        return self.font_type.startswith("Type 3")


@dataclass
class CheckReport:
    pdf: Path
    spec: FigureSpec
    pages: int
    actual_width_pt: float
    actual_width_in: float
    width_deviation_pct: float
    width_ok: bool
    size_counts: dict[float, int]
    min_size: float | None
    max_size: float | None
    size_ok: bool | None
    fonts: list[FontInfo]
    fonts_ok: bool
    observed_family: str | None
    family_ok: bool
    warnings: list[str]
    failures: list[str]

    @property
    def ok(self) -> bool:
        return not self.failures


def _read_fonts(pdf: Path) -> list[FontInfo]:
    pdffonts = shutil.which("pdffonts")
    if not pdffonts:
        raise CheckError("pdffonts not found in PATH")
    proc = subprocess.run(
        [pdffonts, str(pdf)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise CheckError(f"pdffonts failed for {pdf}:\n{proc.stdout[-2000:]}")
    lines = proc.stdout.splitlines()
    try:
        separator = next(i for i, line in enumerate(lines) if line.startswith("---"))
    except StopIteration as exc:
        raise CheckError(f"unexpected pdffonts output for {pdf}:\n{proc.stdout[-2000:]}") from exc

    fonts: list[FontInfo] = []
    for line in lines[separator + 1 :]:
        tokens = line.split()
        if not tokens:
            continue
        # Columns: name, type (may contain spaces), encoding, emb, sub, uni,
        # object ID, ID. Locate the three consecutive yes/no flags from the
        # right, then split the name/type/encoding prefix.
        flag_index = None
        for index in range(len(tokens) - 3, 0, -1):
            if (
                tokens[index] in ("yes", "no")
                and tokens[index + 1] in ("yes", "no")
                and tokens[index + 2] in ("yes", "no")
            ):
                flag_index = index
                break
        if flag_index is None or flag_index < 2:
            continue
        name = tokens[0]
        font_type = " ".join(tokens[1 : flag_index - 1]) or "unknown"
        encoding = tokens[flag_index - 1]
        fonts.append(
            FontInfo(
                name=name,
                font_type=font_type,
                encoding=encoding,
                embedded=tokens[flag_index] == "yes",
            )
        )
    if not fonts:
        raise CheckError(f"pdffonts found no fonts in {pdf}")
    return fonts


def _strip_subset_prefix(name: str) -> str:
    return re.sub(r"^[A-Z]{6}\+", "", name)


def _fmt_size(value: float) -> str:
    if abs(value - round(value)) < 0.005:
        return f"{value:.1f}"
    return f"{value:g}"


def _extract_text(pdf: Path) -> tuple[int, list[tuple[float, str, str]], float]:
    with fitz.open(pdf) as doc:
        if doc.page_count == 0:
            raise CheckError(f"{pdf} has no pages")
        width_pdf_pt = doc[0].rect.width
        spans: list[tuple[float, str, str]] = []
        for page in doc:
            for block in page.get_text("dict").get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if not text.strip():
                            continue
                        spans.append((float(span.get("size", 0)), text, span.get("font", "")))
        return doc.page_count, spans, width_pdf_pt


def check_pdf(pdf: str | Path, venue: str, layout: str) -> CheckReport:
    path = Path(pdf).expanduser().resolve()
    if not path.is_file():
        raise CheckError(f"PDF not found: {path}")
    spec = get_spec(venue, layout)

    pages, spans, width_pdf_pt = _extract_text(path)
    actual_width_in = width_pdf_pt / 72.0
    actual_width_pt = actual_width_in * 72.27
    width_deviation_pct = (actual_width_pt - spec.width_pt) / spec.width_pt * 100.0
    width_ok = abs(width_deviation_pct) <= 1.0

    size_counts = Counter(round(size, 2) for size, _, _ in spans)
    min_size = min(size_counts) if size_counts else None
    max_size = max(size_counts) if size_counts else None
    if min_size is None or max_size is None:
        size_ok = None
    else:
        size_ok = min_size >= 6.0 - 0.01 and max_size <= spec.small_pt + 0.01

    fonts = _read_fonts(path)
    fonts_ok = all(font.embedded and not font.type3 for font in fonts)

    family_chars: Counter[str] = Counter()
    for _, text, font in spans:
        family_chars[classify_family(font)] += len(text.strip())
    observed_family = family_chars.most_common(1)[0][0] if family_chars else None
    pdf_families = {
        classify_family(_strip_subset_prefix(font.name)) for font in fonts
    }
    family_ok = observed_family == spec.family and spec.family in pdf_families

    warnings: list[str] = []
    failures: list[str] = []
    if not width_ok:
        failures.append(
            f"width deviation {width_deviation_pct:+.2f}% exceeds ±1%"
        )
    if size_ok is False:
        if min_size is not None and min_size < 6.0 - 0.01:
            failures.append(f"minimum text size {_fmt_size(min_size)} pt is below 6 pt")
        if max_size is not None and max_size > spec.small_pt + 0.01:
            failures.append(
                f"maximum text size {_fmt_size(max_size)} pt exceeds "
                f"small_pt {spec.small_pt:g} pt"
            )
    if not fonts_ok:
        for font in fonts:
            if not font.embedded:
                failures.append(f"font is not embedded: {font.name}")
            if font.type3:
                failures.append(f"Type 3 font found: {font.name}")
    if not family_ok:
        warnings.append(
            f"font family {observed_family or 'unknown'} does not match "
            f"expected {spec.family}"
        )
    if pages > 1:
        warnings.append(f"PDF has {pages} pages; width was measured on page 1")
    if size_ok is None:
        warnings.append("no non-empty text spans found")

    return CheckReport(
        pdf=path,
        spec=spec,
        pages=pages,
        actual_width_pt=actual_width_pt,
        actual_width_in=actual_width_in,
        width_deviation_pct=width_deviation_pct,
        width_ok=width_ok,
        size_counts={size: size_counts[size] for size in sorted(size_counts)},
        min_size=min_size,
        max_size=max_size,
        size_ok=size_ok,
        fonts=fonts,
        fonts_ok=fonts_ok,
        observed_family=observed_family,
        family_ok=family_ok,
        warnings=warnings,
        failures=failures,
    )


def _status(ok: bool | None, *, warn: bool = False) -> str:
    if ok is None:
        return "N/A"
    if ok:
        return "PASS"
    return "WARN" if warn else "FAIL"


def format_report(report: CheckReport) -> str:
    layout_cn = "单栏" if report.spec.layout == "single" else "双栏"
    lines = [
        f"File: {report.pdf}",
        f"Venue: {report.spec.venue_name} · {layout_cn}",
        f"Pages: {report.pages}",
        "",
        (
            f"Width: {report.actual_width_pt:.1f} pt / {report.actual_width_in:.2f} in "
            f"vs target {report.spec.width_pt:.1f} pt / {report.spec.width_in:.2f} in · "
            f"{report.width_deviation_pct:+.2f}% · {_status(report.width_ok)}"
        ),
    ]

    if report.size_counts:
        distribution = ", ".join(
            f"{_fmt_size(size)} pt: {count}" for size, count in report.size_counts.items()
        )
        lines.append(f"Font sizes: {distribution}")
        lines.append(
            f"Font size range: {_fmt_size(report.min_size)}–{_fmt_size(report.max_size)} pt "
            f"(limit 6.0–{report.spec.small_pt:g}) · {_status(report.size_ok)}"
        )
    else:
        lines.append("Font sizes: no text spans")
        lines.append(f"Font size range: n/a · {_status(report.size_ok)}")

    lines.append("Fonts:")
    for font in report.fonts:
        lines.append(
            f"  {font.name} · {font.font_type} · {font.encoding} · "
            f"embedded={'yes' if font.embedded else 'no'} · "
            f"Type3={'yes' if font.type3 else 'no'}"
        )
    lines.append(f"Font embedding / Type 3: {_status(report.fonts_ok)}")
    lines.append(
        f"Font family: {report.observed_family or 'unknown'} "
        f"(expected {report.spec.family}) · {_status(report.family_ok, warn=True)}"
    )

    if report.warnings:
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"  WARN: {warning}" for warning in report.warnings)
    if report.failures:
        lines.append("")
        lines.append("Failures:")
        lines.extend(f"  FAIL: {failure}" for failure in report.failures)

    lines.append("")
    result = "PASS" if report.ok else "FAIL"
    if report.ok and report.warnings:
        result = "PASS (with warnings)"
    lines.append(f"Result: {result}")
    return "\n".join(lines)
