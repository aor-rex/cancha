"""Favorites: starred teams/competitions in ~/.config/cancha/favorites.json."""
import json
from pathlib import Path


def path():
    p = Path.home() / ".config" / "cancha"
    p.mkdir(parents=True, exist_ok=True)
    return p / "favorites.json"


def load():
    try:
        d = json.loads(path().read_text())
        teams = set(d.get("teams", []))
        cats = set(d.get("categories", []))
        return {"teams": teams, "categories": cats}
    except Exception:
        return {"teams": set(), "categories": set()}


def save(favs):
    path().write_text(json.dumps({
        "teams": sorted(favs["teams"]),
        "categories": sorted(favs["categories"]),
    }))


def toggle_team(favs, team):
    if team in favs["teams"]:
        favs["teams"].discard(team)
    else:
        favs["teams"].add(team)
    save(favs)
    return favs


def toggle_category(favs, cat):
    if cat in favs["categories"]:
        favs["categories"].discard(cat)
    else:
        favs["categories"].add(cat)
    save(favs)
    return favs


def matches(event, favs):
    """True if an event matches starred teams/categories."""
    if event.category and event.category in favs["categories"]:
        return True
    return bool(
        (event.team_a and event.team_a in favs["teams"]) or
        (event.team_b and event.team_b in favs["teams"])
    )
