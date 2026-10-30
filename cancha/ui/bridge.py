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
        self._providers = []
        self._channels = []
        self._reels = []
        self._results = []
        self._favrail = []
        self._matchstar = "☆"
        self._stale = False

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
    providers = Property("QVariant", lambda s: s._get("providers"), notify=refreshed)
    channels = Property("QVariant", lambda s: s._get("channels"), notify=refreshed)
    reels = Property("QVariant", lambda s: s._get("reels"), notify=refreshed)
    results = Property("QVariant", lambda s: s._get("results"), notify=refreshed)
    favrail = Property("QVariant", lambda s: s._get("favrail"), notify=refreshed)
    matchstar = Property(str, lambda s: s._get("matchstar"), notify=refreshed)
    status = Property(str, lambda s: s._get("status"), lambda s, v: s._set("status", v), notify=refreshed)
    stale = Property(bool, lambda s: s._get("stale"), lambda s, v: s._set("stale", v), notify=refreshed)

    # slots wired by main.py
    on_open_match = None
    on_play_server = None
    on_filter = None
    on_nav = None
    on_open_provider = None
    on_play_channel = None
    on_play_reel = None
    on_search = None
    on_toggle_fav = None

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

    @Slot(str)
    def go(self, view):
        if self.on_nav:
            self.on_nav(view)

    @Slot(str)
    def openProvider(self, ref):
        if self.on_open_provider:
            self.on_open_provider(ref)

    @Slot(str, str)
    def playChannel(self, cid, url):
        if self.on_play_channel:
            self.on_play_channel(cid, url)

    @Slot(str)
    def playReel(self, reel_id):
        if self.on_play_reel:
            self.on_play_reel(reel_id)

    @Slot(str)
    def search(self, query):
        if self.on_search:
            self.on_search(query)

    @Slot()
    def toggleFav(self):
        if self.on_toggle_fav:
            self.on_toggle_fav()
