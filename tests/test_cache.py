"""Cache tests — temp HOME, no network."""
import os
import tempfile

os.environ["HOME"] = tempfile.mkdtemp()

from cancha.api import cache


def test_save_load_roundtrip():
    assert cache.load("home") is None
    cache.save("home", {"events": 71, "hero": {"id": "1"}})
    assert cache.load("home") == {"events": 71, "hero": {"id": "1"}}


def test_load_missing_is_none():
    assert cache.load("nope") is None
