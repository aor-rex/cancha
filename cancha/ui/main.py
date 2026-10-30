"""Cancha UI entry: QML shell over the API client. Usage: python -m cancha.ui.main [--shot out.png]"""
import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QTimer, QUrl

from cancha.api import cache
from cancha.api import favorites as fav
from cancha.api.client import Client
from cancha.ui.bridge import Bridge
from cancha.ui.data import (build_filters, build_rails, event_dict, parse_m3u,
                            search_events)

REFRESH_MS = 3 * 60 * 1000


class App:
    def __init__(self, shot=False):
        self.client = Client()
        self.bridge = Bridge()
        self.shot = shot
        self.player = None
        self.favs = fav.load()
        self.reels = []
        self.bridge.on_open_match = self.open_match
        self.bridge.on_play_server = self.play_server
        self.bridge.on_filter = self.apply_filter
        self.bridge.on_nav = self.go_view
        self.bridge.on_open_provider = self.open_provider
        self.bridge.on_play_channel = self.play_channel
        self.bridge.on_play_reel = self.play_reel
        self.bridge.on_search = self.run_search
        self.bridge.on_toggle_fav = self.toggle_fav
        self._filter = "All"

    # ----- data -----
    def load(self, keep_view=True):
        try:
            self.client.refresh_events()
            self.client.refresh_categories()
            self.bridge._set("stale", False)
            self._push_events()
        except Exception as ex:
            if not self._restore_cache():
                self.bridge._set("status", f"offline and no saved data: {ex}"[:120])
            return
        try:
            self.client.refresh_providers()
        except Exception:
            pass
        try:
            self.reels = self.client.highlights_index()
        except Exception:
            self.reels = []
        self.bridge._set("providers", [
            {"name": p.name, "ref": p.ref, "playlist": p.is_playlist}
            for p in self.client.providers
        ])
        self.bridge._set("reels", [
            {"id": r.id, "title": r.title or "Untitled", "logo": r.logo}
            for r in self.reels
        ])
        self._save_cache()

    def _push_events(self):
        self.bridge._set("filters", build_filters(self.client.events))
        self.apply_filter(0)
        evs = self.client.events
        live = [e for e in evs if e.servers]
        first = live[0] if live else (evs[0] if evs else None)
        self.bridge._set("hero", event_dict(first) if first else {})
        self._push_favorites()

    def _snapshot(self):
        return {
            "filters": self.bridge._get("filters"),
            "rails": self.bridge._get("rails"),
            "hero": self.bridge._get("hero"),
            "providers": self.bridge._get("providers"),
            "reels": self.bridge._get("reels"),
            "favrail": self.bridge._get("favrail"),
        }

    def _save_cache(self):
        cache.save("home", self._snapshot())

    def _restore_cache(self):
        snap = cache.load("home")
        if not snap:
            return False
        for k, v in snap.items():
            self.bridge._set(k, v)
        self.bridge._set("stale", True)
        self.bridge._set("status", "offline — showing last saved data")
        return True

    def _push_favorites(self):
        starred = [e for e in self.client.events if fav.matches(e, self.favs)]
        self.bridge._set("favrail", [event_dict(e) for e in starred[:8]])
        m = self.bridge._get("match")
        if m:
            e = next((x for x in self.client.events if x.id == m.get("id")), None)
            if e:
                starred_now = e.team_a in self.favs["teams"] or e.team_b in self.favs["teams"]
                self.bridge._set("matchstar", "★" if starred_now else "☆")

    def apply_filter(self, index):
        cats = self.bridge._get("filters")
        self._filter = cats[index] if 0 <= index < len(cats) else "All"
        self.bridge._set("rails", build_rails(self.client.events, self._filter))

    # ----- nav -----
    def go_view(self, view):
        self.bridge._set("view", view)

    # ----- match -----
    def open_match(self, event_id):
        e = next((x for x in self.client.events if x.id == event_id), None)
        if not e:
            return
        self.bridge._set("match", event_dict(e))
        self._push_favorites()
        try:
            servers = self.client.channels_for(event_id)
        except Exception as ex:
            self.bridge._set("status", f"source unavailable: {ex}"[:120])
            servers = []
        self.bridge._set("servers", [
            {"title": s.title, "note": " · ".join(
                [p for p in [s.kind, next(iter(s.headers.values()), "")] if p])[:60]}
            for s in servers
        ])
        self.bridge._set("view", "match")

    def _play(self, servers, index=0):
        if self.shot:
            self.bridge._set("status", f"[shot mode] would play {servers[index].title if servers else '?'}")
            return
        from cancha.player.mpv import MpvPlayer
        try:
            self.player = MpvPlayer(on_state=self._on_player_state)
            self.player.play_servers(servers[index:])
            self.bridge._set("status", "")
        except Exception as ex:
            self.bridge._set("status", str(ex)[:160])

    def play_server(self, index):
        try:
            servers = self.client.channels_for(self.bridge._get("match").get("id", ""))
        except Exception as ex:
            self.bridge._set("status", f"source unavailable: {ex}"[:120])
            return
        if 0 <= index < len(servers):
            self._play(servers, index)

    def _on_player_state(self, state, info):
        if state == "error" and self.player:
            title = self.player.next_server()
            if not title:
                self.bridge._set("status", "all servers failed — pick another match")

    # ----- providers / live tv -----
    def open_provider(self, ref):
        try:
            if ref.lower().endswith(".m3u"):
                text = self.client.fetch_playlist(ref)
                items = parse_m3u(text)
                self.bridge._set("channels", [
                    {"id": it["url"], "title": it["title"], "image": it["logo"],
                     "m3u": True, "url": it["url"]}
                    for it in items[:200]
                ])
            else:
                chans = self.client.provider_channels(ref)
                self.bridge._set("channels", [
                    {"id": c.id, "title": c.title, "image": c.image, "m3u": False}
                    for c in chans[:200]
                ])
            self.bridge._set("status", "")
        except Exception as ex:
            self.bridge._set("channels", [])
            self.bridge._set("status", f"source unavailable: {ex}"[:120])
        self.bridge._set("view", "channels")

    def play_channel(self, cid, m3u_url=""):
        if m3u_url:
            from cancha.api.client import Server
            self._play([Server(title=cid, url=m3u_url)])
            return
        try:
            servers = self.client.channels_for(cid)
        except Exception as ex:
            self.bridge._set("status", f"source unavailable: {ex}"[:120])
            return
        if servers:
            self._play(servers)

    # ----- highlights -----
    def play_reel(self, reel_id):
        try:
            servers = self.client.reel_servers(reel_id)
        except Exception as ex:
            self.bridge._set("status", f"source unavailable: {ex}"[:120])
            return
        if servers:
            self._play(servers)
        else:
            self.bridge._set("status", "no playable links for this reel")

    # ----- search -----
    def run_search(self, query):
        hits = search_events(self.client.events, query)
        self.bridge._set("results", [event_dict(e) for e in hits[:24]])
        self.bridge._set("view", "search")

    # ----- favorites -----
    def toggle_fav(self):
        m = self.bridge._get("match")
        if not m:
            return
        e = next((x for x in self.client.events if x.id == m.get("id")), None)
        if not e:
            return
        team = e.team_a or e.title
        self.favs = fav.toggle_team(self.favs, team)
        self._push_favorites()


def main():
    shot = None
    if "--shot" in sys.argv:
        shot = sys.argv[sys.argv.index("--shot") + 1]
    app = QGuiApplication(sys.argv)
    core = App(shot=bool(shot))
    try:
        core.load()
    except Exception as ex:
        print("load failed:", ex)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("bridge", core.bridge)
    engine.load(QUrl.fromLocalFile("cancha/ui/qml/main.qml"))
    if not engine.rootObjects():
        print("qml errors — aborting")
        return 1
    timer = QTimer()
    timer.timeout.connect(lambda: core.load())
    timer.start(REFRESH_MS)
    if shot:
        def grab():
            win = engine.rootObjects()[0]
            img = app.primaryScreen().grabWindow(win.winId())
            img.save(shot)
            print("saved", shot)
            app.quit()
        QTimer.singleShot(9000, grab)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
