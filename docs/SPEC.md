# Cancha — Product Specification

TV-first sports streaming client for Linux (monitor + TV, one UI).
Backend: shared sportzx/playfy/cricfy template API (reversed, see ARCHITECTURE.md).

## Screens

1. **Home** — hero (top live event) + `Live & coming up` rail + `Highlights` rail + provider strip.
   Filter pills: All, Football, Cricket, Fighting, Racing, Baseball.
2. **Match** — hero (teams, score state, competition) + server list (working/offline, quality, language). OK = play instantly.
3. **Player** — fullscreen video, auto-hiding OSD: title/server top, progress + quality pills + server switcher + Watch from start bottom.
4. **Sports hub** — sport filter row with live counts + league rails (Football tonight, UFC/WWE this week, ...).
5. **Live TV** — genre filter row (Sports, Entertainment, Movies, News, Kids) + provider grids with channel counts and live-now badges. Provider → channel list → play.
6. **Highlights** — reel grid (title, competition, duration, cut type) → direct play.
7. **Search** — one box across events, channels, highlights, providers.
8. **Favorites** — starred teams/competitions; their matches pin to a Home rail + reminder bells.

## Navigation (single remote model)

- Up/down: move between sections/rails. Left/right: move inside a rail/row.
- OK: open/play. Back: return. No modes, mouse hover mirrors focus.
- Focus is always visible: 4px yellow (`#f5c518`) ring.

## Design language (DAZN TV)

- Pure black `#000` base, cards `#141821` max, white primary text, grey `#999` secondary.
- One accent: yellow `#f5c518` — live times, counts, focus ring, progress.
- Match tiles: 16:9, team-color background, both crests centered, time/live pill top-left, bell top-right, title + `league · status` below on black.
- No gradients, no glass, no card borders except focus. Uppercase bold rail headers.
- Typography: system sans (Inter/Segoe fallback), 800 weight headers.

## Content rules

- Rails render only when they have content (quiet days stay clean).
- Dead servers show offline + Retry, never block the list; player auto-falls to next working server.
- Everything refreshes per session: events feed every ~3 min while open, base host re-resolved every launch.
- No bundled/frozen data. No EPG: entertainment shows channels, not schedules (API has no guide data).
