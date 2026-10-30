"""Qt-free UI data shaping: event dicts, rails, filters. Tested without a display."""
from datetime import datetime, timezone


def fmt_start(s):
    try:
        dt = datetime.strptime(s[:19], "%Y/%m/%d %H:%M:%S").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc).astimezone()
        t = dt.astimezone().strftime("%H:%M")
        if dt.astimezone().date() == now.date():
            return "Today " + t
        return dt.astimezone().strftime("%a %H:%M").upper()
    except Exception:
        return s or ""


def event_dict(e):
    return {
        "id": e.id, "title": e.title or f"{e.team_a} vs {e.team_b}",
        "sub": f"{e.category}",
        "flagA": e.flag_a, "flagB": e.flag_b,
        "badge": fmt_start(e.start),
        "count": f"{len(e.servers)} servers",
    }


def build_rails(events, filt="All"):
    evs = [e for e in events if filt == "All" or e.category == filt]
    groups = {}
    for e in evs:
        groups.setdefault(e.category or "Other", []).append(e)
    return [{"title": k, "events": [event_dict(e) for e in v[:8]]}
            for k, v in groups.items()]


def build_filters(events):
    return ["All"] + sorted({e.category for e in events if e.category})
