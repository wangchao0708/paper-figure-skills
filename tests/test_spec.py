from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from figspec.spec import (
    MIN_FONT_PT,
    VENUES,
    format_spec_line,
    get_spec,
    load_venue_data,
)


def test_width_rules_and_font_levels_for_all_venues():
    records = load_venue_data()["venues"]
    for venue in VENUES:
        record = records[venue]
        single = get_spec(venue, "single")
        double = get_spec(venue, "double")

        if record["twocolumn"]:
            assert single.width_pt == pytest.approx(record["columnwidth_pt"])
            assert single.twocolumn is True
        else:
            assert single.width_pt == pytest.approx(0.48 * record["textwidth_pt"])
            assert single.twocolumn is False

        assert double.width_pt == pytest.approx(record["textwidth_pt"])
        assert single.width_in == pytest.approx(single.width_pt / 72.27)
        assert double.width_in == pytest.approx(double.width_pt / 72.27)

        for value in (
            single.body_pt,
            single.small_pt,
            single.footnotesize_pt,
            single.scriptsize_pt,
            single.label_pt,
            single.tick_pt,
            single.panel_title_pt,
        ):
            assert value >= MIN_FONT_PT


def test_expected_cvpr_spec_line():
    line = format_spec_line(get_spec("CVPR", "single"))
    assert line == (
        "CVPR · 单栏 → 3.28 in / 237.1 pt / 8.33 cm · Times New Roman · "
        "标签/图例 8 · 刻度 7 · 子图标题 9 (pt)"
    )


def test_local_figspec_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    record = dict(load_venue_data()["venues"]["cvpr"])
    record["columnwidth_pt"] = 300.0
    record["venue"] = "cvpr"
    (tmp_path / ".figspec.yaml").write_text(
        yaml.safe_dump(record, sort_keys=False),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    spec = get_spec("CVPR", "single")
    assert spec.width_pt == 300.0
    assert spec.venue == "cvpr"
