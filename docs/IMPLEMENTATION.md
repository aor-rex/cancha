# Cancha — Implementation Plan

## Phase 0 — Scaffold (done when: imports run)
- Repo layout per ARCHITECTURE.md, `pyproject.toml` (PySide6, python-mpv, requests, pycryptodome).
- Port `spzx_crypto.py` → `sportzx/api/crypto.py` with unit tests (vectors: highlights.json, ch1.json, bandspx-cats.json).

## Phase 1 — API client (done when: live data prints)
- Remote config + fallback, events/channels/highlights/providers fetch + decrypt.
- Dataclasses: Event, Server, Reel, Provider. Refresh loop with backoff.
- CLI probe `python -m sportzx.api.client` prints today's events.

## Phase 2 — Player core (done when: a match plays fullscreen)
- python-mpv wrapper: play URL + headers, track/quality list, auto-fallback.
- Keyboard: space/esc/arrows. Watch-from-start = restart stream.

## Phase 3 — UI shell (done when: home renders live data)
- QML: focus engine, Hero, Rail, Tile, Pills per SPEC.md.
- Home + Match + Player wired to client. Mock parity with `mock/tv-*.png`.

## Phase 4 — Full catalogue (done when: all 8 screens live)
- Sports hub, Live TV, Highlights, Search, Favorites (local JSON store + bells via polling).

## Phase 5 — Polish + package
- Idle behavior, error cards, stale banner, key maps, README, PyInstaller build.
- Acceptance: cold launch → hero in <5s on broadband; dead server auto-skips; host rotation needs no update.

## Out of scope (v1)
Windows build (same codebase, later), phone-as-remote, downloads, accounts, EPG.
