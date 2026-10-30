"""Cancha UI entry: QML shell over the API client. Usage: python -m cancha.ui.main [--shot out.png]"""
import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QTimer, QUrl

from cancha.api.client import Client
from cancha.ui.bridge import Bridge
from cancha.ui.data import build_filters, build_rails, event_dict


class App:
    def __init__(self, shot=False):
        self.client = Client()
        self.bridge = Bridge()
        self.shot = shot
        self.player = None
        self.bridge.on_open_match = self.open_match
        self.bridge.on_play_server = self.play_server
        self.bridge.on_filter = self.apply_filter
        self._filter = "All"

    def load(self):
        self.client.refresh_events()
        self.client.refresh_categories()
        self.bridge._set("filters", build_filters(self.client.events))
        self.apply_filter(0)
        first = self.client.events[0] if self.client.events else None
        self.bridge._set("hero", event_dict(first) if first else {})

    def _rails(self):
        return build_rails(self.client.events, self._filter)

    def apply_filter(self, index):
        cats = self.bridge._get("filters")
        self._filter = cats[index] if 0 <= index < len(cats) else "All"
        self.bridge._set("rails", self._rails())

    def open_match(self, event_id):
        e = next((x for x in self.client.events if x.id == event_id), None)
        if not e:
            return
        self.bridge._set("match", event_dict(e))
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

    def play_server(self, index):
        if self.shot:
            self.bridge._set("status", f"[shot mode] would play server {index}")
            return
        try:
            servers = self.client.channels_for(self.bridge._get("match").get("id", ""))
        except Exception as ex:
            self.bridge._set("status", f"source unavailable: {ex}"[:120])
            return
        if not (0 <= index < len(servers)):
            return
        from cancha.player.mpv import MpvPlayer
        try:
            self.player = MpvPlayer(on_state=self._on_player_state)
            self.player.play_servers(servers[index:])
        except Exception as ex:
            self.bridge._set("status", str(ex)[:160])

    def _on_player_state(self, state, info):
        if state == "error" and self.player:
            title = self.player.next_server()
            if not title:
                self.bridge._set("status", "all servers failed — pick another match")


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
    if shot:
        def grab():
            win = engine.rootObjects()[0]
            img = win.grabWindow()
            img.save(shot)
            print("saved", shot)
            app.quit()
        QTimer.singleShot(9000, grab)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
