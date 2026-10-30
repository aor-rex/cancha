# Cancha

TV-first sports streaming client for Linux (monitor + TV, one UI).
Python + PySide6 (QML) + libmpv.

## Quick start

```bash
# system deps (Debian/Ubuntu; Fedora: dnf install mpv qt6)
sudo apt install mpv libmpv2

# app
uv venv && uv pip install -e ".[dev]"
# or: python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

# firebase key (resolves the rotating API host; falls back to last-known without it)
export CANCHA_FIREBASE_KEY="..."
# or write {"firebase_key": "..."} to ~/.config/cancha/config.json

# run
python -m cancha.ui.main
```

## Keys

- arrows: move · OK/Enter: open/play · F: favorite team · H: help · ESC: back
- idle 10 min dims the screen; any key wakes it

## Offline

Last-good data is cached in `~/.config/cancha/cache/`. Cold offline start
renders saved rails with an `OFFLINE — LAST SAVED DATA` banner. Streams are
never cached — they need the network.

## Layout

- `cancha/api/` — config (remote host), crypto (5 reversed schemes), client,
  favorites, cache
- `cancha/ui/` — QML shell (`qml/main.qml`), bridge, data shaping
- `cancha/player/` — libmpv wrapper (fallback across dead servers)
- `docs/` — SPEC, ARCHITECTURE, IMPLEMENTATION
- Agent rules: `AGENTS.md`
