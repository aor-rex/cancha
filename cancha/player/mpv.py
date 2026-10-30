"""libmpv wrapper: play URL + headers, quality tracks, auto-fallback, fullscreen.

Requires libmpv on the playback machine (`apt install mpv` / `dnf install mpv`,
plus `pip install python-mpv`). Import is lazy so the rest of the app
imports cleanly without it.
"""

STATE_OK = "ok"
STATE_ERROR = "error"


class MpvError(RuntimeError):
    pass


def _load_mpv():
    try:
        import mpv  # type: ignore
        return mpv
    except Exception as e:
        raise MpvError(
            "python-mpv/libmpv missing: install mpv on your system and "
            "`pip install python-mpv`"
        ) from e


class MpvPlayer:
    """One video surface. on_state(state, info) fires on end/error for fallback."""

    def __init__(self, on_state=None, vo="gpu", hwdec="auto"):
        mpv = _load_mpv()
        self._mpv = mpv
        self.on_state = on_state
        self.servers = []
        self.index = 0
        self.player = mpv.MPV(
            vo=vo, hwdec=hwdec, fullscreen=True,
            input_default_bindings=True, input_vo_keyboard=True,
            osd_level=1,
        )
        self.player.bind_key_press("q", lambda: self.stop())

        @self.player.event_callback("end-file")
        def _end(event):
            reason = (event or {}).get("reason", "")
            if reason == "error" and self.on_state:
                self.on_state(STATE_ERROR, {"at": self.index})
            elif self.on_state:
                self.on_state(STATE_OK, {"at": self.index})

    def play_servers(self, servers):
        """Play first working server; auto-advance on error. Returns title or ''."""
        self.servers = [s for s in servers if getattr(s, "url", "")]
        self.index = 0
        return self._play_at(0)

    def _play_at(self, i):
        if i >= len(self.servers):
            return ""
        self.index = i
        s = self.servers[i]
        headers = "".join(f"{k}: {v}\r\n" for k, v in (s.headers or {}).items())
        if headers:
            self.player["http-header-fields"] = headers.strip()
        self.player.play(s.url)
        return s.title

    def next_server(self):
        """Advance to next server (dead-link skip). Returns title or ''."""
        return self._play_at(self.index + 1)

    def retry(self):
        return self._play_at(self.index)

    def watch_from_start(self):
        self.player.seek(0, reference="absolute")

    def toggle_pause(self):
        self.player.pause = not self.player.pause

    @property
    def tracks(self):
        try:
            return [
                {"id": t.id, "type": t.type, "title": t.title,
                 "height": getattr(t, "demux_h", None)}
                for t in self.player.track_list or []
            ]
        except Exception:
            return []

    def set_quality(self, height):
        """Pick video track closest to height (720/1080), '' clears to auto."""
        if not height:
            self.player.vid = "auto"
            return
        best, best_d = None, None
        for t in self.tracks:
            if t["type"] != "video" or not t["height"]:
                continue
            d = abs(t["height"] - height)
            if best_d is None or d < best_d:
                best, best_d = t["id"], d
        if best is not None:
            self.player.vid = best

    def stop(self):
        try:
            self.player.stop()
        except Exception:
            pass

    def terminate(self):
        try:
            self.player.terminate()
        except Exception:
            pass
