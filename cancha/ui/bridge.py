"""Python<->QML bridge: plain dict/list properties, one refresh signal."""
from PySide6.QtCore import QObject, Signal, Property, Slot


class Bridge(QObject):
    refreshed = Signal()

    def __init__(self):
        super().__init__()
        self._view = "home"
        self._hero = {}
        self._filters = ["All"]
        self._rails = []
        self._match = {}
        self._servers = []
        self._status = ""

    def _get(self, name):
        return getattr(self, "_" + name)

    def _set(self, name, value):
        setattr(self, "_" + name, value)
        self.refreshed.emit()

    view = Property(str, lambda s: s._get("view"), lambda s, v: s._set("view", v), notify=refreshed)
    hero = Property("QVariant", lambda s: s._get("hero"), notify=refreshed)
    filters = Property("QVariant", lambda s: s._get("filters"), notify=refreshed)
    rails = Property("QVariant", lambda s: s._get("rails"), notify=refreshed)
    match = Property("QVariant", lambda s: s._get("match"), notify=refreshed)
    servers = Property("QVariant", lambda s: s._get("servers"), notify=refreshed)
    status = Property(str, lambda s: s._get("status"), lambda s, v: s._set("status", v), notify=refreshed)

    # slots wired by main.py
    on_open_match = None
    on_play_server = None
    on_filter = None

    @Slot(str)
    def openMatch(self, event_id):
        if self.on_open_match:
            self.on_open_match(event_id)

    @Slot(int)
    def playServer(self, index):
        if self.on_play_server:
            self.on_play_server(index)

    @Slot(int)
    def setFilter(self, index):
        if self.on_filter:
            self.on_filter(index)

    @Slot()
    def goHome(self):
        self._set("view", "home")
