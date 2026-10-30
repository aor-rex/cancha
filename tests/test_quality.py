"""quality_tag tests — server rows must never leak headers/user-agents."""
from cancha.ui.data import quality_tag


def test_picks_quality_from_title():
    assert quality_tag("TSN SPORTS FHD", "1") == "FHD"
    assert quality_tag("Sky Sports F1 HD", "0") == "HD"
    assert quality_tag("bein 4k feed", "") == "4K"


def test_falls_back_to_kind_not_headers():
    assert quality_tag("RUSSIA FEED", "0") == ""
    assert "Mozilla" not in quality_tag("X", "Mozilla/5.0")
    assert quality_tag("", "") == ""
