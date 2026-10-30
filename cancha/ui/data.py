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


def parse_m3u(text):
    """Parse an m3u playlist -> [{'title', 'logo', 'group', 'url'}]."""
    out = []
    title, logo, group = "", "", ""
    for line in (text or "").splitlines():
        line = line.strip()
        if line.startswith("#EXTINF"):
            title = line.rsplit(",", 1)[-1].strip() if "," in line else ""
            logo, group = "", ""
            for key in ('tvg-logo="', 'group-title="'):
                if key in line:
                    val = line.split(key, 1)[1].split('"', 1)[0]
                    if "logo" in key:
                        logo = val
                    else:
                        group = val
        elif line and not line.startswith("#"):
            if title or True:
                out.append({"title": title or line.rsplit("/", 1)[-1],
                            "logo": logo, "group": group, "url": line})
            title, logo, group = "", "", ""
    return out


def search_events(events, query):
    q = (query or "").strip().lower()
    if not q:
        return []
    return [e for e in events
            if q in (e.title or "").lower()
            or q in (e.team_a or "").lower()
            or q in (e.team_b or "").lower()
            or q in (e.category or "").lower()]


def quality_tag(title, kind=""):
    """Short clean badge for a server row: FHD/HD/SD/4K from the title,
    else the stream kind. Never leaks headers or user-agents."""
    t = (title or "").upper()
    for q in ("4K", "UHD", "FULLHD", "FHD", " HD", "HD", "SD"):
        if q.strip() and q in t:
            return "FHD" if q == "FULLHD" else q.strip()
    k = (kind or "").upper()[:12]
    return "" if k.isdigit() else k
