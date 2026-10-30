# Cancha — Architecture

## Stack

- **Python 3.12+**, **PySide6 (QML)** for UI, **libmpv via python-mpv** for playback.
- Packaging later: PyInstaller one-dir build. No Electron, no browser runtime.

## Modules

```
sportzx/
  api/
    config.py    # firebase remote-config fetch (api_url + fallback api_url_tv)
    crypto.py    # SportzxCryptoUtils reimplementation (ported, tested)
    client.py    # events, channels, highlights, providers, search, favorites store
    refresh.py   # polling loop (~3 min) + host rotation + retry
  ui/
    main.qml     # shell: hero + rails + focus engine
    screens/     # Home, Match, Player, Sports, LiveTV, Highlights, Search, Favorites
    components/  # Tile, Rail, Hero, ServerRow, OSD, Pills
  player/
    mpv.py       # libmpv wrapper: headers, quality tracks, watch-from-start, fallback
```

## Data flow

Launch → remote config → base host → parallel fetch (live-events, cats, highlights index).
Home renders from in-memory store. Poller refreshes events + live-now counts, UI diffs rails.
OK on match → fetch `channels/{slug}.txt` → decrypt → probe servers (HEAD, timeout 5s) → sorted list.
Watch → mpv with URL + headers; on error auto-advance to next working server.

## API map (reversed 2026-10-29, verified live)

- Base: firebase remote config `api_url`, fallback `api_url_tv` (rotates, never hardcode).
- `GET {base}/categories/live-events.txt` → v3-encrypted JSON: 27 events/day.
  Fields per event: slug, title, eventInfo {teamA/B, teamAFlag/BFlag (sofascore CDN), eventCat, startTime, eventType}.
- `GET {base}/channels/{slug}.txt` → fallback2-encrypted JSON: servers [{api (key:iv), link, logo, title, type}].
- `GET {base}/cats/highlights.json` (v3) → 14 reels; `GET {base}/highlights/{id}.json` (v3) → playable DASH/`stream.php` links.
- `GET {base}/cats.txt` → 74 providers with m3u playlist links.
- Crests/flags: `teamAFlag/teamBFlag` hotlinked from `img.sofascore.com` (verified 200).

## Crypto (all static keys, port from scratch/spzx_crypto.py)

- v3: custom SXR sponge KDF (SXR3/kdf, CTX_HASH, V3_PEPPER) + HMAC tag, XOR stream. Used by events, cats, highlights.
- fallback2: AES-128-CBC with FNV-derived key/iv from seed `oAR80SGuX3EEjUGFRwLFKBTiris=`. Used by per-match channel files.
- primary (DEADBEEF magic + HKDF), v2 (0x02 + cert-bound HMAC): implemented, kept for coverage.

## Failure model

- Host dead → re-resolve remote config, retry once, else error card with Retry.
- Server dead → skip to next, show offline state. All dead → Retry row.
- Decrypt fail → log scheme + blob version byte, surface "source unavailable".
- No network → cached last-good events with stale banner (events only, never streams).
