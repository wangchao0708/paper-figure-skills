from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pytest

import figspec
from figspec.check import check_pdf, format_report


def _make_pdf(path: Path, *, font_size: float = 8.0, width_scale: float = 1.0) -> Path:
    spec = figspec.setup("CVPR", "single")
    fig = plt.figure(
        figsize=(spec.width_in * width_scale, 2.0),
        layout="constrained",
    )
    fig.text(0.5, 0.5, "8 pt figure text", ha="center", va="center", fontsize=font_size)
    fig.savefig(path)
    plt.close(fig)
    return path


def test_check_passes_for_8pt_figure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    pdf = _make_pdf(tmp_path / "pass.pdf")
    report = check_pdf(pdf, "CVPR", "single")

    assert report.ok
    assert report.width_ok
    assert report.size_ok is True
    assert report.min_size == pytest.approx(8.0, abs=0.1)
    assert report.max_size == pytest.approx(8.0, abs=0.1)
    assert report.fonts_ok
    assert report.family_ok
    assert "Result: PASS" in format_report(report)


def test_check_fails_small_text(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    pdf = _make_pdf(tmp_path / "small.pdf", font_size=5.0)
    report = check_pdf(pdf, "CVPR", "single")

    assert not report.ok
    assert report.size_ok is False
    assert any("below 6 pt" in failure for failure in report.failures)


def test_check_fails_wrong_width(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    pdf = _make_pdf(tmp_path / "narrow.pdf", width_scale=0.8)
    report = check_pdf(pdf, "CVPR", "single")

    assert not report.ok
    assert not report.width_ok
    assert any("width deviation" in failure for failure in report.failures)
