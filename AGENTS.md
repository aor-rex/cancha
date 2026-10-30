# AGENTS.md — cancha

## What this is
TV-first Linux sports streaming client (Python + PySide6 QML + libmpv).
Backend is a reversed third-party template API; keys are static and committed in `api/crypto.py` by design.

## Docs (read before coding)
- `docs/SPEC.md` — screens, nav model, design language. UI changes must match it.
- `docs/ARCHITECTURE.md` — modules, API map, crypto, failure model.
- `docs/IMPLEMENTATION.md` — phases and done-criteria. Work in phase order.

## Rules
- One UI, monitor + TV. No separate skins. Focus ring (`#f5c518`, 4px) always visible; mouse hover mirrors focus.
- No gradients, no glass, no card borders except focus. Black `#000` base, one yellow accent.
- Never hardcode the API host — always resolve via remote config with fallback.
- Never bundle data files — everything is fetched per session; tests use checked-in vectors.
- Server failure is normal: skip-and-advance, never a blocking error.
- Crypto changes: add test vectors from live blobs before merging.
- Mock parity: `mock/tv-*.png` in scratch are the visual reference until QML screenshots replace them.
- Commit messages: lowercase, short (`api: add refresh loop`, `ui: home rail focus`).
