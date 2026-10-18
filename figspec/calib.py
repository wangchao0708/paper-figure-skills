"""Generate draw.io calibration assets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fitz
import yaml

from .spec import load_venue_data, repo_root, venues_path


class CalibError(RuntimeError):
    """Calibration generation failed."""


CALIB_WIDTH_IN = 3.28
CALIB_HEIGHT_IN = 1.2
CALIB_TEXT_PT = 8.0
CALIB_LINE_IN = 1.0


@dataclass(frozen=True)
class CalibAssets:
    svg: Path
    pdf: Path
    width_in: float
    height_in: float
    width_tex_pt: float
    line_in: float
    text_pt: float


@dataclass(frozen=True)
class CalibrationMeasurement:
    out_pdf: Path
    page_width_pt: float
    page_height_pt: float
    source_width_pt: float
    source_width_tex_pt: float
    page_scale: float
    reference_line_pt: float
    svg_import_scale: float
    svg_import_compensation_percent: float
    calib_8pt_rendered_pt: float
    drawio_10_rendered_pt: float
    drawio_pt_per_unit: float
    drawio_units_per_pt: float
    svg_is_1to1: bool


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def generate_calibration() -> CalibAssets:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    output_dir = repo_root() / "calib"
    output_dir.mkdir(parents=True, exist_ok=True)
    width_in = CALIB_WIDTH_IN
    height_in = CALIB_HEIGHT_IN
    text_pt = CALIB_TEXT_PT
    line_in = CALIB_LINE_IN

    with mpl.rc_context(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.bbox": None,
        }
    ):
        fig = plt.figure(figsize=(width_in, height_in))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, width_in)
        ax.set_ylim(0, height_in)
        ax.axis("off")

        # Corner marks keep the full page width/height when draw.io exports
        # with Crop enabled.
        mark = 0.02
        for x, y in (
            (0, 0),
            (width_in - mark, 0),
            (0, height_in - mark),
            (width_in - mark, height_in - mark),
        ):
            ax.add_patch(
                Rectangle(
                    (x, y),
                    mark,
                    mark,
                    facecolor="black",
                    edgecolor="none",
                    transform=ax.transData,
                )
            )

        ax.text(
            0.2,
            0.92,
            "Calib-8pt",
            fontsize=text_pt,
            family="Times New Roman",
            va="center",
            ha="left",
        )
        ax.plot(
            [0.2, 1.2],
            [0.6, 0.6],
            color="black",
            linewidth=0.8,
            solid_capstyle="butt",
        )
        for x in (0.2, 1.2):
            ax.plot(
                [x, x],
                [0.55, 0.65],
                color="black",
                linewidth=0.8,
                solid_capstyle="butt",
            )

        svg_path = output_dir / "calib.svg"
        pdf_path = output_dir / "calib.pdf"
        fig.savefig(svg_path)
        fig.savefig(pdf_path)
        plt.close(fig)

    return CalibAssets(
        svg=svg_path,
        pdf=pdf_path,
        width_in=width_in,
        height_in=height_in,
        width_tex_pt=width_in * 72.27,
        line_in=line_in,
        text_pt=text_pt,
    )


def _find_text_size(doc: fitz.Document, needle: str) -> float | None:
    for page in doc:
        for block in page.get_text("dict").get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if needle in span.get("text", ""):
                        return float(span["size"])
    return None


def _find_reference_line(doc: fitz.Document) -> float | None:
    best: float | None = None
    for page in doc:
        page_width = page.rect.width
        for drawing in page.get_drawings():
            for item in drawing["items"]:
                if item[0] == "l":
                    first, second = item[1], item[2]
                    if abs(first.y - second.y) < 0.5:
                        length = abs(first.x - second.x)
                        if length > 20 and length < page_width * 0.8:
                            if best is None or length > best:
                                best = length
                elif item[0] == "re":
                    rect = item[1]
                    if rect.height < 2 and 20 < rect.width < page_width * 0.8:
                        if best is None or rect.width > best:
                            best = rect.width
    return best


def _save_drawio_doc(measurement: CalibrationMeasurement) -> Path:
    path = repo_root() / "skills" / "paper-figure-spec" / "references" / "drawio.md"
    text = f"""# draw.io calibration

Generated by `figspec calib --measure`. Do not edit the measured values by hand.

## Calibration asset

- Source: `calib/calib.svg` and `calib/calib.pdf`
- Source width: {CALIB_WIDTH_IN:.2f} in = {measurement.source_width_pt:.2f} PDF pt = {measurement.source_width_tex_pt:.2f} TeX pt
- Source calibration text: `Calib-8pt`, {CALIB_TEXT_PT:g} pt
- Source reference line: {CALIB_LINE_IN:g} in
- draw.io export: `calib/out.pdf` (Crop enabled)

## Raw measurement

| item | measured | scale |
| --- | ---: | ---: |
| page width | {measurement.page_width_pt:.2f} PDF pt | {measurement.page_scale:.6f} vs source |
| reference line | {measurement.reference_line_pt:.2f} PDF pt | {measurement.svg_import_scale:.6f} vs 1 in |
| `Calib-8pt` text | {measurement.calib_8pt_rendered_pt:.4f} pt | {measurement.calib_8pt_rendered_pt / 8.0:.6f} |
| `Drawio-10pt` text | {measurement.drawio_10_rendered_pt:.4f} pt | {measurement.drawio_10_rendered_pt / 10.0:.6f} pt/unit raw |

Page height: {measurement.page_height_pt:.2f} PDF pt. The page-width scale includes Crop
margins; the reference line and the imported SVG text are the reliable 1:1
indicators.

## Conclusions

- **SVG import is not 1:1.** The reference line and imported SVG text scale by
  about {measurement.svg_import_scale:.4f}. To preserve 1:1 when importing this
  SVG, scale the imported drawing to **{measurement.svg_import_compensation_percent:.2f}%**
  after import (or use a 1:1 draw.io canvas and do not import a pre-scaled SVG).
- **draw.io font unit conversion.** The 10-unit draw.io text rendered at
  {measurement.drawio_10_rendered_pt:.4f} pt in the uncorrected export. Dividing
  out the SVG import scale gives **1 draw.io unit = {measurement.drawio_pt_per_unit:.6f} pt**
  (**1 pt = {measurement.drawio_units_per_pt:.6f} draw.io units**).

## Values used by `figspec spec`

The draw.io line assumes a 1:1 canvas. It converts the target TeX width and
font sizes with the native factor:

- page width = target pt × {measurement.drawio_units_per_pt:.6f}
- label/legend = footnotesize_pt × {measurement.drawio_units_per_pt:.6f}
- tick = scriptsize_pt × {measurement.drawio_units_per_pt:.6f}
- panel title = small_pt × {measurement.drawio_units_per_pt:.6f}

Example: the CVPR single-column target 237.14 pt becomes
{237.14 * measurement.drawio_units_per_pt:.1f} px; 8/7/9 pt become
{8 * measurement.drawio_units_per_pt:.1f}/{7 * measurement.drawio_units_per_pt:.1f}/{9 * measurement.drawio_units_per_pt:.1f}.

## Manual procedure

1. Open draw.io.
2. Import `calib/calib.svg` without additional resizing.
3. Add a text box containing `Drawio-10pt` at font size 10.
4. Keep it inside the corner marks.
5. Export as PDF with Crop to `calib/out.pdf`.
6. Run `figspec calib --measure`.

If an imported figure is used, compensate for the measured
{measurement.svg_import_compensation_percent:.2f}% import scale before applying the
canvas and font values above.
"""
    path.write_text(text, encoding="utf-8")
    return path


def _save_drawio(measurement: CalibrationMeasurement) -> Path:
    data: dict[str, Any] = load_venue_data()
    data["drawio"] = {
        "calibrated_at": _now(),
        "out_pdf": "calib/out.pdf",
        "source_width_in": CALIB_WIDTH_IN,
        "source_width_tex_pt": round(measurement.source_width_tex_pt, 2),
        "out_pdf_width_pt": round(measurement.page_width_pt, 2),
        "out_pdf_height_pt": round(measurement.page_height_pt, 2),
        "page_width_scale": round(measurement.page_scale, 6),
        "reference_line_pt": round(measurement.reference_line_pt, 2),
        "calib_8pt_rendered_pt": round(measurement.calib_8pt_rendered_pt, 4),
        "drawio_10_rendered_pt": round(measurement.drawio_10_rendered_pt, 4),
        "svg_is_1to1": measurement.svg_is_1to1,
        "svg_import_scale": round(measurement.svg_import_scale, 6),
        "svg_import_compensation_percent": round(
            measurement.svg_import_compensation_percent, 2
        ),
        "drawio_pt_per_unit": round(measurement.drawio_pt_per_unit, 6),
        "drawio_units_per_pt": round(measurement.drawio_units_per_pt, 6),
    }
    rendered = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1000,
    )
    header = (
        "# Generated by `figspec probe` and `figspec calib`. Do not edit values by hand.\n"
        "# Template provenance: skills/paper-figure-spec/references/venue_sources.md\n"
    )
    path = venues_path()
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(header + rendered, encoding="utf-8")
    tmp.replace(path)
    return path


def measure_calibration() -> CalibrationMeasurement:
    output_dir = repo_root() / "calib"
    out_pdf = output_dir / "out.pdf"
    if not out_pdf.is_file():
        raise CalibError(
            f"{out_pdf} not found; complete the draw.io export described by "
            "`figspec calib` first"
        )

    source_width_bp = CALIB_WIDTH_IN * 72.0
    source_width_tex_pt = CALIB_WIDTH_IN * 72.27

    with fitz.open(out_pdf) as doc:
        if doc.page_count == 0:
            raise CalibError(f"{out_pdf} has no pages")
        page = doc[0]
        page_count = doc.page_count
        page_width_pt = page.rect.width
        page_height_pt = page.rect.height
        calib_size = _find_text_size(doc, "Calib-8pt")
        drawio_size = _find_text_size(doc, "Drawio-10pt")
        line_bp = _find_reference_line(doc)

    if line_bp is None:
        raise CalibError("reference line not found in calib/out.pdf")
    if calib_size is None:
        raise CalibError("text 'Calib-8pt' not found in calib/out.pdf")
    if drawio_size is None:
        raise CalibError("text 'Drawio-10pt' not found in calib/out.pdf")

    page_scale = page_width_pt / source_width_bp
    line_scale = line_bp / 72.0
    calib_scale = calib_size / 8.0
    svg_is_1to1 = abs(line_scale - 1.0) <= 0.01 and abs(calib_scale - 1.0) <= 0.01

    raw_pt_per_unit = drawio_size / 10.0
    # The whole exported canvas is affected by the SVG import scale. Remove
    # that scale to get the native draw.io font unit conversion.
    pt_per_unit = raw_pt_per_unit / line_scale
    units_per_pt = 1.0 / pt_per_unit
    measurement = CalibrationMeasurement(
        out_pdf=out_pdf,
        page_width_pt=page_width_pt,
        page_height_pt=page_height_pt,
        source_width_pt=source_width_bp,
        source_width_tex_pt=source_width_tex_pt,
        page_scale=page_scale,
        reference_line_pt=line_bp,
        svg_import_scale=line_scale,
        svg_import_compensation_percent=100.0 / line_scale,
        calib_8pt_rendered_pt=calib_size,
        drawio_10_rendered_pt=drawio_size,
        drawio_pt_per_unit=pt_per_unit,
        drawio_units_per_pt=units_per_pt,
        svg_is_1to1=svg_is_1to1,
    )

    print(f"out.pdf: {out_pdf}")
    print(f"Pages: {page_count}")
    print(f"Page width: {page_width_pt:.2f} PDF pt ({page_width_pt / 72:.4f} in)")
    print(
        f"Source width: {source_width_bp:.2f} PDF pt "
        f"({source_width_tex_pt:.2f} TeX pt); page scale={page_scale:.6f}"
    )
    print(
        f"Reference line: {line_bp:.2f} PDF pt; "
        f"SVG import scale={line_scale:.6f} (1:1={svg_is_1to1})"
    )
    print(
        f"Calib-8pt text: {calib_size:.2f} pt; "
        f"SVG text scale={calib_scale:.6f}"
    )
    print(
        f"Drawio-10pt text: {drawio_size:.2f} pt; raw pt/unit={raw_pt_per_unit:.6f}"
    )
    print(
        f"Native draw.io conversion: 1 unit = {pt_per_unit:.6f} pt "
        f"({units_per_pt:.6f} units/pt)"
    )
    path = _save_drawio(measurement)
    doc_path = _save_drawio_doc(measurement)
    print(f"Saved draw.io calibration fields to {path}")
    print(f"Wrote calibration notes to {doc_path}")
    return measurement


def print_instructions(assets: CalibAssets) -> None:
    print(f"Generated: {assets.svg}")
    print(f"Generated: {assets.pdf}")
    print(
        f"Source width: {assets.width_in:.2f} in "
        f"({assets.width_tex_pt:.1f} TeX pt), "
        f"calibration text: {assets.text_pt:g} pt, reference line: {assets.line_in:g} in"
    )
    print()
    print("Next: complete the draw.io export manually:")
    print("  1. Open https://app.diagrams.net/ (or the draw.io desktop app).")
    print(f"  2. Import {assets.svg}; do not scale or resize the imported SVG.")
    print("  3. Add a text box containing \"Drawio-10pt\" and set its font size to 10.")
    print("  4. Keep the text box inside the canvas (inside the corner marks).")
    print("  5. File -> Export as -> PDF, enable Crop, save as:")
    print(f"     {repo_root() / 'calib' / 'out.pdf'}")
    print()
    print("Then run: figspec calib --measure")
