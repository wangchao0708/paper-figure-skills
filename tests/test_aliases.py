from __future__ import annotations

import pytest

from figspec.spec import ALIASES, VENUES, normalize_layout, resolve_venue


@pytest.mark.parametrize(
    ("alias", "canonical"),
    [(alias, venue) for venue in VENUES for alias in ALIASES[venue]],
)
def test_all_aliases(alias: str, canonical: str):
    assert resolve_venue(alias) == canonical
    assert resolve_venue(alias.swapcase()) == canonical


def test_special_aliases():
    assert resolve_venue("S&P") == "sp"
    assert resolve_venue("Oakland") == "sp"
    assert resolve_venue("USENIX-Security") == "usenixsec"
    assert resolve_venue("MM") == "acmmm"
    assert resolve_venue("PAMI") == "tpami"


def test_unknown_venue():
    with pytest.raises(ValueError, match="unknown venue"):
        resolve_venue("not-a-venue")


def test_layout_aliases():
    assert normalize_layout("single") == "single"
    assert normalize_layout("单栏") == "single"
    assert normalize_layout("double") == "double"
    assert normalize_layout("双栏") == "double"
    with pytest.raises(ValueError, match="unknown layout"):
        normalize_layout("three-column")
