"""Last-good cache: UI-ready data in ~/.config/cancha/cache/*.json.

Cold offline start still renders yesterday's rails. Never stores streams."""
import json
from pathlib import Path


def _dir():
    p = Path.home() / ".config" / "cancha" / "cache"
    p.mkdir(parents=True, exist_ok=True)
    return p


def save(name, obj):
    try:
        (_dir() / f"{name}.json").write_text(json.dumps(obj))
    except Exception:
        pass


def load(name):
    try:
        return json.loads((_dir() / f"{name}.json").read_text())
    except Exception:
        return None
