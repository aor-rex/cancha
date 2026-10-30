"""m3u + search tests."""
from cancha.api.client import Event
from cancha.ui.data import parse_m3u, search_events

M3U = """#EXTM3U
#EXTINF:-1 tvg-logo="http://x/a.png" group-title="Sports",Sky Main
http://cdn.example.com/sky.m3u8
#EXTINF:-1,Bare Channel
http://cdn.example.com/bare.ts
"""


def test_parse_m3u_entries():
    items = parse_m3u(M3U)
    assert len(items) == 2
    assert items[0]["title"] == "Sky Main"
    assert items[0]["logo"] == "http://x/a.png"
    assert items[0]["group"] == "Sports"
    assert items[0]["url"] == "http://cdn.example.com/sky.m3u8"
    assert items[1]["title"] == "Bare Channel"


def test_parse_m3u_empty():
    assert parse_m3u("") == []
    assert parse_m3u(None) == []


def test_search_matches_teams_title_category():
    evs = [Event(id="1", title="Derby", team_a="Arsenal", team_b="Chelsea", category="EPL"),
           Event(id="2", title="Race", team_a="X", team_b="Y", category="F1")]
    assert [e.id for e in search_events(evs, "arsenal")] == ["1"]
    assert [e.id for e in search_events(evs, "f1")] == ["2"]
    assert search_events(evs, "") == []
    assert search_events(evs, "zzz") == []
