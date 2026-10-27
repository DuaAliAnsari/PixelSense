"""PixelSense: information architecture + consent-based, on-device analytics.

The five kinds of data an app holds, and where PixelSense keeps each one (shown to the user in Settings > Your data):

  1. SYSTEM data      what the app needs to work and the user did not create (photo list, text read from images,
                      face boxes, sorting rules). Lives in manifest.csv / faces.csv. Read-only.
  2. USER data        what the user creates or decides (names, favourites, collections, edits, 'done' ticks, removals).
                      Lives in this browser session only. Can be exported or erased.
  3. REFERENCES       pointers instead of copies. An edited photo, a collection and a 'Remove' are all *references* to the
                      untouched original, which is why every change is undoable and originals are never altered.
  4. SESSION / COOKIES  PixelSense sets NO cookies. Streamlit keeps a temporary session id in memory while the tab is open.
  5. ANALYTICS        how the app is used (which screens, which searches). OFF by default, opt-in, stored on this device
                      only, visible to the user line by line, exportable, erasable. No third party (no Google Analytics).

Why analytics exists at all: to answer 'is the problem actually being solved?' (do people act on a deadline before
it passes?). The log is built to answer that question and nothing else: event names and counts, never photo content.
"""
from __future__ import annotations

import json
from datetime import datetime

# Events we are allowed to record. Anything else is dropped, so a developer cannot quietly log more later.
ALLOWED = {
    "screen_open": "A screen was opened",
    "search": "A question was asked (only the word count is kept, not the words)",
    "attention_done": "A deadline or bill was ticked off",
    "attention_added": "A deadline was added by hand or from pasted text",
    "attention_undo": "A tick was undone",
    "cleanup_review": "A clean-up group was kept or removed",
    "ai_paused": "AI was paused for a collection",
}

DATA_MAP = [
    # (key, title, plain-language description, where it lives, who controls it)
    ("system", "System data", "Photo list, text read from images, face boxes and sorting rules. The app needs these to work.",
     "manifest.csv, faces.csv", "Read-only. You cannot change it, and it never leaves the device."),
    ("user", "User data", "Names you give people, favourites, collections you make, edited copies, items you tick off or remove.",
     "This browser session", "Yours. Export it or erase it any time."),
    ("refs", "References", "Edits, collections and removals point at your original photo instead of copying or changing it.",
     "Pointers (ids) only", "Originals are never modified, so every change can be undone."),
    ("cookies", "Cookies & session", "PixelSense sets no cookies and no tracking ids. A temporary session lives in memory while the tab is open.",
     "Memory only", "Closing the tab ends it."),
    ("analytics", "Analytics", "Which screens you open and how often you tick things off, to learn whether the app helps. Never photo content or search words.",
     "On this device only", "Off by default. You can read, export and erase every line."),
]


def new_event(name: str, **detail):
    """Build one log line, or None if this event type is not on the allow-list."""
    if name not in ALLOWED:
        return None
    clean = {k: v for k, v in detail.items() if isinstance(v, (int, float, str, bool)) and len(str(v)) <= 40}
    return {"t": datetime.now().strftime("%H:%M:%S"), "event": name, **clean}


def summarise(events):
    """Counts per event type: the only thing a researcher needs."""
    out: dict[str, int] = {}
    for e in events:
        out[e["event"]] = out.get(e["event"], 0) + 1
    return out


def export_json(user_data: dict, events: list, analytics_on: bool) -> str:
    return json.dumps({"exported": datetime.now().isoformat(timespec="seconds"), "note": "Everything PixelSense holds about you in this session.",
                       "user_data": user_data, "analytics_enabled": analytics_on, "analytics_log": events}, indent=2, default=str)
