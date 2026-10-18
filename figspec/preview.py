"""Compile a LaTeX preview of figure PDFs in a venue template."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .spec import FigureSpec, get_spec, normalize_layout, repo_root, resolve_venue


class PreviewError(RuntimeError):
    """The preview could not be generated or compiled."""


@dataclass(frozen=True)
class PreviewResult:
    pdf: Path
    output_dir: Path
    overfull_hbox: int
    warnings: list[str]
    opened: bool


BEGIN_DOC_RE = re.compile(r"\\begin\s*\{document\}")


def _insert_packages(text: str) -> str:
    match = BEGIN_DOC_RE.search(text)
    if not match:
        raise PreviewError("min.tex has no \\begin{document}")
    packages = "\\usepackage{graphicx}\n\\usepackage{lipsum}\n"
    return text[: match.start()] + packages + text[match.start() :]


def _replace_body(text: str, body: str) -> str:
    if "%%BODY%%" not in text:
        raise PreviewError("min.tex does not contain the %%BODY%% placeholder")
    return text.replace("%%BODY%%", body, 1)


def _figure_block(environment: str, image: str) -> str:
    return (
        f"\\begin{{{environment}}}[htbp]\n"
        "\\centering\n"
        f"\\includegraphics{{{image}}}\n"
        f"\\end{{{environment}}}\n"
    )


def _minipage_block(first: str, second: str) -> str:
    return (
        "\\begin{figure}[htbp]\n"
        "\\centering\n"
        "\\noindent\n"
        "\\begin{minipage}[t]{0.48\\textwidth}\n"
        "\\centering\n"
        f"\\includegraphics{{{first}}}\n"
        "\\end{minipage}\\hfill\n"
        "\\begin{minipage}[t]{0.48\\textwidth}\n"
        "\\centering\n"
        f"\\includegraphics{{{second}}}\n"
        "\\end{minipage}\n"
        "\\end{figure}\n"
    )


def _resolve_inputs(pdfs: list[str | Path]) -> list[Path]:
    if not 1 <= len(pdfs) <= 2:
        raise PreviewError("preview expects one or two figure PDFs")
    resolved: list[Path] = []
    for value in pdfs:
        path = Path(value).expanduser().resolve()
        if not path.is_file():
            raise PreviewError(f"figure PDF not found: {path}")
        resolved.append(path)
    return resolved


def _figure_body(spec: FigureSpec, inputs: list[Path]) -> tuple[str, list[Path]]:
    if not spec.twocolumn and spec.layout == "single":
        # Single-column template with a single-column figure: show two
        # 0.48\textwidth panels. If only one figure is supplied, duplicate it.
        used = inputs if len(inputs) == 2 else [inputs[0], inputs[0]]
        block = _minipage_block("fig1.pdf", "fig2.pdf")
    else:
        if spec.twocolumn:
            environment = "figure" if spec.layout == "single" else "figure*"
        else:
            environment = "figure"
        used = inputs
        block = "\n".join(
            _figure_block(environment, f"fig{index}.pdf")
            for index in range(1, len(inputs) + 1)
        )
    return block, used


def _copy_inputs(inputs: list[Path], output_dir: Path) -> None:
    for index, source in enumerate(inputs, start=1):
        destination = output_dir / f"fig{index}.pdf"
        if source == destination:
            continue
        shutil.copy2(source, destination)


def _compile(output_dir: Path, template_dir: Path) -> tuple[Path, int]:
    latexmk = shutil.which("latexmk")
    if not latexmk:
        raise PreviewError("latexmk not found in PATH")

    env = os.environ.copy()
    old_texinputs = env.get("TEXINPUTS", "")
    env["TEXINPUTS"] = f"{template_dir}:{old_texinputs}" if old_texinputs else f"{template_dir}:"
    command = [
        latexmk,
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        "preview.tex",
    ]
    try:
        proc = subprocess.run(
            command,
            cwd=output_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired as exc:
        raise PreviewError("latexmk timed out while compiling preview.tex") from exc

    log_path = output_dir / "preview.log"
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    pdf_path = output_dir / "preview.pdf"
    if proc.returncode != 0 or not pdf_path.exists():
        tail = "\n".join((log or proc.stdout).splitlines()[-30:])
        raise PreviewError(f"latexmk failed for preview.tex\n{tail}")
    overfull = log.count("Overfull \\hbox")
    return pdf_path, overfull


def preview_figures(
    venue: str,
    layout: str,
    pdfs: list[str | Path],
    *,
    open_pdf: bool = True,
) -> PreviewResult:
    canonical = resolve_venue(venue)
    layout_id = normalize_layout(layout)
    spec = get_spec(canonical, layout_id)
    inputs = _resolve_inputs(pdfs)

    template_dir = repo_root() / "templates" / canonical
    min_tex = template_dir / "min.tex"
    if not min_tex.is_file():
        raise PreviewError(f"template not found: {min_tex}")

    output_dir = repo_root() / "build" / "preview" / f"{canonical}-{layout_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    block, used = _figure_body(spec, inputs)
    body = f"\\lipsum[1]\n\n{block}\n\\lipsum[2]\n"
    text = min_tex.read_text(encoding="utf-8")
    text = _insert_packages(text)
    text = _replace_body(text, body)
    (output_dir / "preview.tex").write_text(text, encoding="utf-8")

    _copy_inputs(used, output_dir)
    old_pdf = output_dir / "preview.pdf"
    if old_pdf.exists():
        old_pdf.unlink()

    pdf_path, overfull = _compile(output_dir, template_dir)
    warnings: list[str] = []
    if overfull:
        warnings.append(f"{overfull} Overfull \\hbox warning(s); see {output_dir / 'preview.log'}")

    opened = False
    if open_pdf:
        opener = shutil.which("open")
        if opener:
            proc = subprocess.run([opener, str(pdf_path)], check=False)
            opened = proc.returncode == 0
            if not opened:
                warnings.append("could not open the preview PDF with `open`")
        else:
            warnings.append("`open` not found; preview PDF was not opened")

    return PreviewResult(
        pdf=pdf_path,
        output_dir=output_dir,
        overfull_hbox=overfull,
        warnings=warnings,
        opened=opened,
    )
