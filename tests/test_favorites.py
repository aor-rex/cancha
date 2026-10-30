"""Favorites store tests — uses a temp HOME so nothing touches real config."""
import os
import tempfile

os.environ["HOME"] = tempfile.mkdtemp()

from cancha.api.client import Event
from cancha.api import favorites as fav


def _e(**kw):
    d = dict(id="1", title="T", team_a="Team A", team_b="Team B", category="F1")
    d.update(kw)
    return Event(**d)


def test_toggle_team_roundtrip():
    f = fav.load()
    assert f == {"teams": set(), "categories": set()}
    fav.toggle_team(f, "Team A")
    assert fav.load()["teams"] == {"Team A"}
    fav.toggle_team(f, "Team A")
    assert fav.load()["teams"] == set()


def test_toggle_category_roundtrip():
    f = fav.load()
    fav.toggle_category(f, "F1")
    assert fav.load()["categories"] == {"F1"}


def test_matches_team_and_category():
    f = {"teams": {"Team A"}, "categories": {"NBA"}}
    assert fav.matches(_e(), f)
    assert fav.matches(_e(team_a="X", team_b="Y", category="NBA"), f)
    assert not fav.matches(_e(team_a="X", team_b="Y", category="NFL"), f)
