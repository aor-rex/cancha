"""UI data shaping tests — no display or network needed."""
from cancha.api.client import Event
from cancha.ui.data import build_filters, build_rails, event_dict, fmt_start


def _e(id="1", cat="F1", title="Formula 1", n_servers=3):
    return Event(id=id, title=title, team_a="A", team_b="B",
                 flag_a="http://x/a.png", flag_b="http://x/b.png",
                 category=cat, start="2026/10/30 18:30:00 +0000",
                 servers=[f"s{i}" for i in range(n_servers)])


def test_fmt_start_today():
    assert fmt_start("2099/10/30 18:30:00 +0000").endswith("18:30") or "18:30" in fmt_start("2099/10/30 18:30:00 +0000")


def test_fmt_start_garbage_passthrough():
    assert fmt_start("soon") == "soon"
    assert fmt_start("") == ""


def test_event_dict_shape():
    d = event_dict(_e())
    assert d["id"] == "1" and d["title"] == "Formula 1"
    assert d["count"] == "3 servers"
    assert d["flagA"] == "http://x/a.png"


def test_rails_group_by_category_and_filter():
    evs = [_e("1", "F1"), _e("2", "F1"), _e("3", "NBA")]
    rails = build_rails(evs)
    assert {r["title"] for r in rails} == {"F1", "NBA"}
    assert len(build_rails(evs, "F1")) == 1
    assert build_rails(evs, "F1")[0]["events"][0]["id"] == "1"


def test_filters_sorted_with_all_first():
    assert build_filters([_e("1", "NBA"), _e("2", "F1")]) == ["All", "F1", "NBA"]
