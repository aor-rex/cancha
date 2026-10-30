"""API client: events, channels, highlights over the rotating base host."""
import json
import time
from dataclasses import dataclass

import requests

from . import config
from .crypto import decrypt_payload

UA = {"User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7)"}


@dataclass
class Event:
    id: str
    title: str
    team_a: str = ""
    team_b: str = ""
    flag_a: str = ""
    flag_b: str = ""
    category: str = ""
    start: str = ""
    end: str = ""
    servers: list = None

    def __post_init__(self):
        if self.servers is None:
            self.servers = []


@dataclass
class Server:
    title: str
    url: str
    headers: dict = None
    logo: str = ""
    kind: str = ""

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


@dataclass
class Reel:
    id: str
    title: str
    logo: str = ""
    url: str = ""


def _split_link(link):
    """'url|header1=a|header2=b' -> (url, {headers})."""
    parts = (link or "").split("|")
    url = parts[0].strip()
    headers = {}
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            headers[k.strip()] = v.strip()
    return url, headers


def _payload(text):
    try:
        data = json.loads(text).get("data", "")
    except Exception:
        return None
    if not data:
        return None
    try:
        _, plain = decrypt_payload(data)
        return json.loads(plain)
    except Exception:
        return None


class Client:
    def __init__(self):
        self.session = requests.Session()
        self.hosts = config.resolve_hosts()
        self.host = self.hosts[0]
        self.events = []
        self.categories = []
        self.fetched_at = 0.0

    def _foreach_host(self, path):
        last = None
        for h in self.hosts:
            try:
                r = self.session.get(h + path, headers=UA, timeout=20)
                r.raise_for_status()
                payload = _payload(r.text)
                if payload is not None:
                    self.host = h
                    return payload
                last = ValueError("undecryptable payload")
            except Exception as e:
                last = e
        raise RuntimeError(f"all hosts failed for {path}: {last}")

    def _as_list(self, data, *keys):
        if isinstance(data, list):
            return data
        for k in keys:
            v = data.get(k) if isinstance(data, dict) else None
            if isinstance(v, list):
                return v
        return []

    def refresh_events(self):
        items = self._as_list(self._foreach_host("events.json"), "events", "data")
        out = []
        for e in items:
            info = e.get("eventInfo", {}) or {}
            fmts = e.get("formatsNew", []) or []
            servers = [s.get("title", "") for s in fmts if isinstance(s, dict)]
            out.append(Event(
                id=str(e.get("id", "")),
                title=e.get("title", ""),
                team_a=info.get("teamA", ""),
                team_b=info.get("teamB", ""),
                flag_a=info.get("teamAFlag", ""),
                flag_b=info.get("teamBFlag", ""),
                category=e.get("cat", ""),
                start=str(info.get("startTime", "")),
                end=str(info.get("endTime", "")),
                servers=servers,
            ))
        self.events = out
        self.fetched_at = time.time()
        return out

    def refresh_categories(self):
        items = self._as_list(self._foreach_host("eventcats.json"), "cats", "data")
        self.categories = [
            {"id": str(c.get("id", "")), "title": c.get("title", ""),
             "image": c.get("image", ""), "link": c.get("catLink", "")}
            for c in items if isinstance(c, dict)
        ]
        return self.categories

    def channels_for(self, event_id):
        items = self._as_list(
            self._foreach_host(f"channels/{event_id}.json"), "channels", "data")
        out = []
        for c in items:
            url, headers = _split_link(c.get("link", ""))
            out.append(Server(
                title=c.get("title", "server"),
                url=url,
                headers=headers,
                logo=c.get("logo", ""),
                kind=c.get("type", ""),
            ))
        return [s for s in out if s.url]

    def highlights_index(self):
        items = self._as_list(
            self._foreach_host("cats/highlights.json"), "highlights", "data")
        out = []
        for h in items:
            if not isinstance(h, dict):
                continue
            fmts = h.get("formatsNew", h.get("formats", [])) or []
            first = fmts[0] if fmts else {}
            url, _ = _split_link(first.get("link", "") if isinstance(first, dict) else "")
            out.append(Reel(
                id=str(h.get("id", "")),
                title=h.get("title", ""),
                logo=h.get("logo", first.get("logo", "") if isinstance(first, dict) else ""),
                url=url,
            ))
        return out


if __name__ == "__main__":
    c = Client()
    print("host:", c.host)
    events = c.refresh_events()
    cats = c.refresh_categories()
    print(f"events: {len(events)}  categories: {len(cats)}")
    for e in events[:30]:
        name = e.title or f"{e.team_a} vs {e.team_b}"
        print(f"- [{e.category}] {name} :: {e.start} ({len(e.servers)} servers)")
