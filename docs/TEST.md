# Cancha — Interactive Test Guide

Run through this on your PC after `python -m cancha.ui.main`.
Mark each `[ ]` as you go. Anything failing → paste the terminal output.

## 0. Automated suite

```bash
uv run pytest
```

- `[ ]` 20/20 green

## 1. Cold launch

- `[ ]` window opens fullscreen-black, no traceback in terminal
- `[ ]` hero shows today's top event with crests, time badge, server count
- `[ ]` rails render below hero with match tiles
- `[ ]` launch to hero takes under ~5s on broadband

## 2. Remote navigation (arrows + Enter + ESC)

- `[ ]` up/down moves between nav → pills → rails, focus ring always visible
- `[ ]` left/right moves inside pills and inside rails
- `[ ]` yellow ring never disappears or lands on two items at once
- `[ ]` mouse hover moves focus too, click equals OK

## 3. Match → servers → playback

- `[ ]` OK on a tile opens the match screen (title, badge, star row, server list)
- `[ ]` server list shows real titles (not "server 1, server 2")
- `[ ]` OK on a server goes fullscreen and video starts with sound
- `[ ]` space pauses, ESC or Q exits back to the match screen
- `[ ]` dead server auto-skips to the next one (watch the terminal line)

## 4. Top nav (1..5 or click: HOME SPORTS LIVE TV HIGHLIGHTS SEARCH)

- `[ ]` SPORTS shows pills + league rails, favorites rail on top if starred
- `[ ]` LIVE TV lists all 74 providers with M3U/HUB badges, list scrolls past 9
- `[ ]` opening a HUB provider shows its channels; OK plays one
- `[ ]` opening an M3U provider shows its channels; OK plays one
- `[ ]` HIGHLIGHTS lists reels; OK plays one
- `[ ]` SEARCH: type a team, Enter, results open matches
- `[ ]` ESC walks back: channels → livetv → home

## 5. Favorites

- `[ ]` on a match screen press F — star fills to ★
- `[ ]` back on home/sports, a ★ Favorites rail appears with that team
- `[ ]` press F again — star empties, rail drops the team
- `[ ]` restart the app — favorites persist

## 6. Help + idle

- `[ ]` H opens the key map overlay, H or ESC closes it
- `[ ]` leave the app alone 10 min — screen dims, any key wakes it

## 7. Offline

- `[ ]` kill the network, restart the app — saved rails render
- `[ ]` `OFFLINE — LAST SAVED DATA` banner shows top-right
- `[ ]` reconnect, wait ~3 min (or restart) — live data returns, banner clears

## 8. Host rotation (no-update check)

- `[ ]` with the firebase key set, cold launch resolves the host live
  (terminal shows no hardcoded-host errors)
- `[ ]` without the key, app still launches on last-known hosts
