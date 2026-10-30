"""Remote-config resolution: base API host, refreshed every launch (it rotates).

Public-repo safe: the firebase key is NEVER committed. Provide it via:
  1. env var CANCHA_FIREBASE_KEY, or
  2. {"firebase_key": "..."} in ~/.config/cancha/config.json, or
  3. bundled at build time from the CANCHA_FIREBASE_KEY repo secret
     (CI writes cancha/api/_build_key.py, gitignored, before bundling).
Without it, remote config is skipped and last-known hosts are used."""

import json
import os
import uuid
from pathlib import Path

import requests


def _bundled_key():
    try:
        from cancha.api._build_key import FIREBASE_KEY
        return (FIREBASE_KEY or "").strip()
    except Exception:
        return ""


def _firebase_key():
    key = os.environ.get("CANCHA_FIREBASE_KEY", "").strip()
    if key:
        return key
    cfg = Path.home() / ".config" / "cancha" / "config.json"
    if cfg.exists():
        try:
            return json.loads(cfg.read_text()).get("firebase_key", "").strip()
        except Exception:
            return ""
    return _bundled_key()

FIREBASE_API_KEY = _firebase_key()
PROJECT_NUMBER = "234785582029"
APP_ID = "1:234785582029:android:f5f9299eaa7a0d73c93284"
PACKAGE_NAME = "com.sportzx.live"

# Last-known-good hosts. Never primary — remote config wins when reachable.
KNOWN_HOSTS = [
    "https://es.bandspx.com/",
    "https://anshulajoy10.github.io/mygaja/",
]

FETCH_URL = (
    f"https://firebaseremoteconfig.googleapis.com/v1/projects/"
    f"{PROJECT_NUMBER}/namespaces/firebase:fetch"
)


def fetch_remote_entries(timeout=15):
    """Return remote-config entries dict, or None on any failure."""
    if not FIREBASE_API_KEY:
        return None
    try:
        r = requests.post(
            FETCH_URL,
            json={
                "appInstanceId": uuid.uuid4().hex,
                "appInstanceIdToken": "",
                "appId": APP_ID,
                "countryCode": "US",
                "languageCode": "en-US",
                "platformVersion": "30",
                "timeZone": "UTC",
                "appVersion": "3.2",
                "appBuild": "32",
                "packageName": PACKAGE_NAME,
                "sdkVersion": "22.1.0",
                "analyticsUserProperties": {},
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Android-Package": PACKAGE_NAME,
                "X-Goog-Api-Key": FIREBASE_API_KEY,
                "X-Google-GFE-Can-Retry": "yes",
            },
            timeout=timeout,
        )
        if r.ok:
            return (r.json().get("entries") or None) or None
        return None
    except Exception:
        return None


def resolve_hosts():
    """Ordered candidate base hosts: remote config first, known-good fallback."""
    entries = fetch_remote_entries()
    hosts = []
    if entries:
        for k in ("api_url", "api_url_tv"):
            v = entries.get(k)
            if v and v not in hosts:
                hosts.append(v if v.endswith("/") else v + "/")
    for h in KNOWN_HOSTS:
        if h not in hosts:
            hosts.append(h)
    return hosts
