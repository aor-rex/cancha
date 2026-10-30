"""Player tests with a fake mpv module (no libmpv needed)."""
import sys
import types


class FakeTrack:
    def __init__(self, id, type, title, h=None):
        self.id = id
        self.type = type
        self.title = title
        self.demux_h = h


class FakeMPV:
    last = None

    def __init__(self, **kwargs):
        FakeMPV.last = self
        self.opts = kwargs
        self.played = []
        self.props = {"vid": "auto", "pause": False}
        self.track_list = [
            FakeTrack(1, "video", "720p", 720),
            FakeTrack(2, "video", "1080p", 1080),
            FakeTrack(3, "audio", "eng"),
        ]
        self._keys = {}

    def __setitem__(self, k, v):
        self.props[k] = v

    def __getattr__(self, name):
        if name in ("pause", "vid"):
            return self.props[name]
        if name in ("play", "stop", "terminate", "seek"):
            return lambda *a, **k: self.played.append((name, a, k))
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in ("pause", "vid"):
            self.__dict__.setdefault("props", {})[name] = value
        else:
            super().__setattr__(name, value)

    def bind_key_press(self, *a, **k):
        pass

    def event_callback(self, *a, **k):
        def deco(fn):
            return fn
        return deco


class FakeServer:
    def __init__(self, title, url, headers=None):
        self.title = title
        self.url = url
        self.headers = headers or {}


def _install_fake():
    mod = types.ModuleType("mpv")
    mod.MPV = FakeMPV
    sys.modules["mpv"] = mod


_install_fake()

from cancha.player.mpv import MpvPlayer


def test_play_servers_plays_first_and_sets_headers():
    states = []
    p = MpvPlayer(on_state=states.append)
    title = p.play_servers([
        FakeServer("A", "http://a/x.mpd", {"user-agent": "UA1"}),
        FakeServer("B", "http://b/x.mpd"),
    ])
    assert title == "A"
    assert FakeMPV.last.played[0][0] == "play"
    assert FakeMPV.last.props["http-header-fields"] == "user-agent: UA1"


def test_next_server_advances_and_exhausts():
    p = MpvPlayer()
    p.play_servers([FakeServer("A", "http://a"), FakeServer("B", "http://b")])
    assert p.next_server() == "B"
    assert p.next_server() == ""


def test_quality_picks_closest_track():
    p = MpvPlayer()
    p.play_servers([FakeServer("A", "http://a")])
    p.set_quality(720)
    assert FakeMPV.last.props["vid"] == 1
    p.set_quality(1080)
    assert FakeMPV.last.props["vid"] == 2


def test_watch_from_start_seeks_zero():
    p = MpvPlayer()
    p.play_servers([FakeServer("A", "http://a")])
    p.watch_from_start()
    assert ("seek", (0,), {"reference": "absolute"}) in FakeMPV.last.played
