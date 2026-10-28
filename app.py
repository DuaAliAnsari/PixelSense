"""PixelSense - a chat-first photo assistant that rescues deadlines and bills trapped inside photos (HCI prototype).

Core features: Needs attention (the core problem), Why PixelSense (problem + loopholes), Your data (information architecture,
consent-based analytics) and a flat, light visual system. See PROBLEM_AND_DESIGN.md.

Screens: Ask PixelSense (chat), Photos (timeline), People (face groups), Collections, Photo details, Settings.
Navigation lives in the top-left corner menu; the prompt bar sits at the bottom with a "+" for new collections.

Journeys:
  A. Find / ask       type a request or question in the bottom bar -> answer with the photos and how it was found
  B. People           People -> tap a face -> every photo of that person (name them, hide them, fix mistakes)
  C. Stay in control  Move to..., Stop AI, Pause AI per collection, face groups on/off, Undo for every change
"""
import base64
import copy
import html
import io
import re
import time
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps

import analytics as AN
import editor as ED
import study as ST
import engine as E
from engine import AUTO, CAT_ORDER, HELD, R, df
from styles import CSS

ROOT = Path(__file__).parent
st.set_page_config(page_title="PixelSense", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

TYPE_FILTERS = ["All", "Photo", "Screenshot", "Receipt", "Bill", "Ticket", "Document"]
TILE_COLORS = [("#EEEBFF", "#5B4FD6"), ("#FFE9EC", "#D6455D"), ("#E3F6EC", "#18936A"),
               ("#FFF1D6", "#C27A00"), ("#E1F1FF", "#2A7DD1"), ("#F3E8FF", "#9333EA")]
HOME_CHIPS = {
    "What needs my attention?": "What needs my attention?",
    "HCI deadline": "When is my HCI assignment due?",
    "Electricity bill": "How much is the electricity bill?",
    "Who’s at dinner?": "Who is in the dinner photo?",
    "Photos of Person 1": "Show photos of Person 1",
    "Make a collection": "Create a collection called Eid with family dinner photos",
    "Edit by chat": "Make the wedding photos black and white and save to Eid",
    "My receipts": "Show my receipts",
}
ATTENTION_CHIP = "What needs my attention?"
ATTENTION_RE = re.compile(r"needs?\s+(my\s+)?attention|what('s| is| are)\s+(due|overdue|coming up)|upcoming|deadlines|overdue|anything due", re.I)
UNDO_KEYS = ["override", "extra_cats", "excluded_cats", "excluded_imgs", "removed", "names", "hidden_people", "notp", "fav", "kept", "copies", "done", "manual"]

ICONS = {
    "home": '<path d="M3 11.5 12 4l9 7.5"/><path d="M5 10.5V20h14v-9.5"/><path d="M10 20v-5h4v5"/>',
    "grid": '<rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/>'
            '<rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4-4"/>',
    "check": '<circle cx="12" cy="12" r="8.5"/><path d="m8.5 12.3 2.4 2.4 4.6-5"/>',
    "shield": '<path d="M12 3 5 6v5.5c0 4.3 2.9 7.6 7 9.5 4.1-1.9 7-5.2 7-9.5V6z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
    "tick": '<path d="m6 12.5 4 4 8-9"/>',
    "sparkle": '<path d="M12 3c.6 4.2 2.8 6.4 7 7-4.2.6-6.4 2.8-7 7-.6-4.2-2.8-6.4-7-7 4.2-.6 6.4-2.8 7-7z"/>',
    "folder": '<path d="M3.5 7.5a2 2 0 0 1 2-2H9l2 2.2h7.5a2 2 0 0 1 2 2V17a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/>',
    "eyeoff": '<path d="M3 3l18 18"/><path d="M10.6 6.2A9.8 9.8 0 0 1 12 6c5 0 8.5 4 9.5 6a12.6 12.6 0 0 1-2.7 3.3M6.4 7.6C4.3 9 2.9 11 2.5 12c1 2 4.5 6 9.5 6 1.3 0 2.5-.3 3.6-.8"/><path d="M9.9 10a3 3 0 0 0 4.1 4.1"/>',
    "chev": '<path d="m9 6 6 6-6 6"/>',
    "doc": '<rect x="5" y="3.5" width="14" height="17" rx="2.5"/><path d="M8.5 9h7M8.5 12.5h7M8.5 16h4"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "edit": '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "send": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "user": '<circle cx="12" cy="8.5" r="3.5"/><path d="M5 20c.7-3.6 3.4-5.5 7-5.5s6.3 1.9 7 5.5"/>',
    "users": '<circle cx="9" cy="9" r="3"/><path d="M3.5 19c.5-3 2.7-4.7 5.5-4.7s5 1.7 5.5 4.7"/><circle cx="17" cy="8.5" r="2.4"/><path d="M16 14.2c2.6-.2 4.5 1.3 5 4"/>',
    "heart": '<path d="M12 20s-7-4.4-9-9.2C1.8 7.6 3.9 4.5 7 4.5c2 0 3.6 1.1 5 3 1.4-1.9 3-3 5-3 3.1 0 5.2 3.1 4 6.3-2 4.8-9 9.2-9 9.2z"/>',
    "trash": '<path d="M4 7h16M9 7V4.5h6V7M6.5 7l1 13h9l1-13M10 11v6M14 11v6"/>',
    "image": '<rect x="3.5" y="4.5" width="17" height="15" rx="3"/><circle cx="9" cy="10" r="1.8"/><path d="m4 17 5-4.5 4 3.5 3-2.5 4.5 3.5"/>',
}


def svg(name, size=22, color="currentColor", sw=1.8, fill="none"):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{fill}" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'{ICONS[name]}</svg>')


esc = html.escape


def md(s):
    """Render an HTML snippet. Newlines are collapsed so Markdown never treats it as a code block."""
    st.markdown(re.sub(r"\s*\n\s*", " ", s.strip()), unsafe_allow_html=True)


def fmt(t):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(t))


def slug(s):
    return re.sub(r"\W+", "_", s).strip("_")


# --------------------------------------------------------------------------- state
S = st.session_state


def fresh_state():
    return dict(
        view="welcome", back="chat", query="", rfilter="All", hfilter="All", sel=None, cur_coll=None, cur_person=None,
        override={}, extra_cats=[], excluded_cats={"Sensitive"}, excluded_imgs=set(), removed=set(), arrived=set(),
        names={}, hidden_people=set(), notp=set(), faces_on=None, fav=set(), kept=set(), cur_mem=None, copies=[], copy_seq=0, llm_on=False,
        history=[], searches=[], done=set(), study=None, opened=set(), manual=[], manual_seq=0, analytics_on=False, events=[], snack=None, scroll=False, menu=False, plus=False, chat=[], res=None,
    )


if "boot" not in S:
    S.update(fresh_state())
    S.boot = True
E.sync_copies(S.copies)
E.sync_opened(S.opened)   # keep the library tables in step with this session (edited copies, undo, reset)


@st.cache_data(show_spinner=False)
def img_uri(file, w, h):
    im = Image.open(ROOT / file).convert("RGB")
    im = ImageOps.fit(im, (w, h), method=Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


@st.cache_data(show_spinner=False)
def face_uri(file, x, y, w, h, size=128):
    im = Image.open(ROOT / file).convert("RGB")
    W, H = im.size
    cx, cy, side = x + w / 2, y + h / 2, max(w, h) * 1.8
    box = (max(0, cx - side / 2), max(0, cy - side / 2), min(W, cx + side / 2), min(H, cy + side / 2))
    im = ImageOps.fit(im.crop(tuple(int(v) for v in box)), (size, size), method=Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


# --------------------------------------------------------------------------- what the AI may use
def cat_of(r):
    return S.override.get(r.id) or AUTO[r.id][0]


def arrived_ok(r):
    return r.id not in HELD or r.id in S.arrived


def visible(r):
    """Only images the AI is allowed to use show up anywhere."""
    return (arrived_ok(r) and r.id not in S.removed and r.id not in S.excluded_imgs and cat_of(r) not in S.excluded_cats)


def visible_rows():
    return [r for r in df.itertuples() if visible(r)]


def all_cats():
    base = [c for c in CAT_ORDER if any(a[0] == c for a in AUTO.values())]
    extra = [c for c in S.extra_cats if c not in base]
    sens = ["Sensitive"] if any(a[0] == "Sensitive" for a in AUTO.values()) else []
    return base + extra + sens


def cat_total(c):
    return sum(1 for r in df.itertuples() if arrived_ok(r) and r.id not in S.removed and cat_of(r) == c)


def coll_items(name):
    return [r.id for r in visible_rows() if cat_of(r) == name]


def deadline_items(include_done=False):
    """All dated obligations found in photos the AI may use (see engine.deadlines), minus ones already ticked off."""
    items = sorted(E.deadlines(visible_rows(), date.today()) + E.manual_deadlines(S.manual, date.today()), key=lambda d: d["days"])
    return [d for d in items if include_done or d["id"] not in S.done]


def done_items():
    every = E.deadlines([r for r in df.itertuples() if arrived_ok(r) and r.id not in S.removed], date.today()) + E.manual_deadlines(S.manual, date.today())
    return [d for d in every if d["id"] in S.done]


def title_of(i):
    return next((m["title"] for m in S.manual if m["id"] == i), None) or R[i].description


def library_health():
    """Progress, not a grade. Counts things you have *reviewed*: deadlines handled + clutter groups decided.
    Keeping a photo and removing a photo count the same, so there is no reward for deleting blindly."""
    pool = [r for r in df.itertuples() if arrived_ok(r) and r.id not in S.excluded_imgs and cat_of(r) not in S.excluded_cats]
    all_dl = [d["id"] for d in E.deadlines([r for r in pool if r.id not in S.removed], date.today())]
    flagged = [r.id for v in E.cleanup_groups(pool, ()).values() for r in v]
    total = len(all_dl) + len(flagged)
    handled = len([i for i in all_dl if i in S.done]) + len([i for i in flagged if i in S.kept or i in S.removed])
    return handled, total


# ---- people ---------------------------------------------------------------------------------------
def pname(pid):
    return S.names.get(pid) or f"Person {E.PNUM[pid]}"


def person_images(pid, strict=True):
    ids = [i for i in E.PERSON_IMAGES.get(pid, []) if (pid, i) not in S.notp]
    return [i for i in ids if visible(R[i])] if strict else ids


def shown_people():
    if not S.faces_on:
        return []
    out = [p for p in E.PERSON_IMAGES if p not in S.hidden_people and person_images(p)]
    out.sort(key=lambda p: (p not in S.names, -len(person_images(p)), E.PNUM[p]))
    return out


def avatar(pid, px=84):
    ids = person_images(pid) or person_images(pid, strict=False)
    best = max(ids, key=lambda i: E.FACE_OF[(i, pid)][2] * E.FACE_OF[(i, pid)][3], default=None)
    if best is None:
        return f'<div class="pav" style="width:{px}px;height:{px}px"></div>'
    x, y, w, h = E.FACE_OF[(best, pid)]
    return f'<img class="pav" src="{face_uri(R[best].file, x, y, w, h)}" style="width:{px}px;height:{px}px" alt="{esc(pname(pid))}">'


def make_ctx():
    names = {p: pname(p) for p in shown_people()}
    return E.Ctx(rows=visible_rows(), cat_of=cat_of, names=names, people_ids={p: person_images(p) for p in names},
                 fav=set(S.fav), faces_on=bool(S.faces_on), collections=all_cats(),
                 last_ids=next((m["reply"].ids for m in reversed(S.chat) if m["role"] == "ai" and m["reply"].ids), []))


# --------------------------------------------------------------------------- navigation, undo, chat
def track(name, **detail):
    """Record a usage event, but only if the person opted in. Event names are allow-listed in analytics.py."""
    if S.analytics_on:
        ev = AN.new_event(name, **detail)
        if ev:
            S.events.append(ev)


def study_tick(key):
    """Count screens visited and undo taps while a study task is running (objective effort measures)."""
    if S.study and S.study.get("running"):
        S.study[key] = S.study.get(key, 0) + 1


def go(view):
    study_tick("nav")
    track("screen_open", screen=view)
    S.view, S.snack, S.menu, S.plus, S.scroll = ("home" if view == "attention" else view), None, False, False, True
    st.rerun()


def open_image(i):
    S.opened.add(i)
    S.back = S.view if S.view != "detail" else S.back
    S.sel = i
    go("detail")


def open_from_msg(i, query):
    S.query = query
    open_image(i)


def open_collection(name):
    S.cur_coll = name
    go("collection")


def open_person(pid):
    S.cur_person = pid
    go("person")


def open_menu():
    S.menu, S.plus = True, False
    st.rerun()


def new_chat():
    """Clear the current search and return to Home (the one place searches start)."""
    S.chat, S.query, S.menu, S.plus = [], "", False, False
    go("home")


def home_button(key):
    """Labelled way back to Home, shown on the search-results and photo-details screens."""
    with st.container(key=f"homebtn_{key}"):
        if st.button("Home", key=f"homebtn_btn_{key}", icon=":material/home:"):
            new_chat()
            st.rerun()


def notify(msg, can_undo=True):
    S.snack = (msg, can_undo)
    S.scroll = True


def snap():
    S.history.append(copy.deepcopy({k: S[k] for k in UNDO_KEYS}))


def undo():
    if S.history:
        S.update(S.history.pop())
        study_tick("undos")
        notify("Last change undone.", False)


def remember_search(q):
    S.searches = [q] + [x for x in S.searches if x.lower() != q.lower()]
    S.searches = S.searches[:8]


def new_copy_record(src, ops):
    S.copy_seq += 1
    rec = {"id": f"ed{S.copy_seq}", "src": src, "ops": ops}
    S.copies.append(rec)
    E.register_copy(rec)
    return rec


def place_copy(i, name):
    if name not in all_cats():
        S.extra_cats.append(name)
    if AUTO[i][0] == name:
        S.override.pop(i, None)
    else:
        S.override[i] = name


def open_editor(i):
    for k in [k for k in S.keys() if str(k).startswith("ed_")]:
        del S[k]
    S.sel = i
    go("edit")


def execute(rp):
    """Apply a command the assistant understood (create a collection, rename a person). Always undoable."""
    c = rp.cmd
    if not c or getattr(rp, "executed", False):
        return
    if c["type"] == "create_collection":
        name = c["name"].strip()
        if name in S.excluded_cats:
            rp.text, rp.cmd = f"AI is paused for **{name}**. Allow it in Settings first.", None
            return
        ids = [i for i in c["ids"] if i in R and visible(R[i])]
        snap()
        if name not in all_cats():
            S.extra_cats.append(name)
        for i in ids:
            if AUTO[i][0] == name:
                S.override.pop(i, None)
            else:
                S.override[i] = name
        rp.executed = True
    elif c["type"] == "undo":
        if S.history:
            undo()
            rp.text = "Undone. I reverted your last change."
        else:
            rp.text = "There is nothing to undo yet."
        S.snack = None
    elif c["type"] == "edit_photos":
        name = c["collection"]
        if name in S.excluded_cats:
            rp.text, rp.cmd = f"AI is paused for **{name}**. Allow it in Settings first.", None
            return
        snap()
        new = []
        for i in c["ids"]:
            if i in R:
                rec = new_copy_record(i, c["ops"])
                place_copy(rec["id"], name)
                new.append(rec["id"])
        n = len(new)
        rp.ids, rp.sources = new, []
        rp.text = (f"Done: {', '.join(ED.describe(c['ops']))}. Saved {n} edited cop{'y' if n == 1 else 'ies'} to **{name}**. "
                   "Your original" + (" is" if n == 1 else "s are") + " untouched.")
        rp.executed = True
    elif c["type"] == "rename_person":
        snap()
        S.names[c["pid"]] = c["name"]
        rp.executed = True


def ask(q):
    q = (q or "").strip()
    if not q:
        return
    if ATTENTION_RE.search(q) and not re.search(r"\bhci\b|assignment|bill|electricity|internet", q, re.I):
        track("search", words=len(q.split()))
        S.view, S.snack, S.menu, S.plus, S.scroll = "home", None, False, False, True
        return
    track("search", words=len(q.split()))
    remember_search(q)
    S.chat.append({"role": "user", "text": q})
    ctx = make_ctx()
    rp = E.answer(ctx, q)
    if S.llm_on and E.llm_available() and rp.kind == "none" and rp.text.startswith("I couldn’t find"):
        hist = [("user", m["text"]) if m["role"] == "user" else ("assistant", m["reply"].text) for m in S.chat[:-1]]
        rp = E.llm_reply(ctx, hist, q) or rp
    execute(rp)
    S.chat.append({"role": "ai", "reply": rp})
    S.view, S.snack, S.menu, S.plus, S.scroll = "chat", None, False, False, "bottom"


def send():
    """text_input on_change callback (Enter): runs before the script, so it only sets state."""
    q = (S.get("composer_q") or "").strip()
    S["composer_q"] = ""
    ask(q)


def send_click():
    send()
    st.rerun()


def ask_chip(label):
    ask(HOME_CHIPS.get(label, label))
    st.rerun()


# --------------------------------------------------------------------------- reusable UI
def tappable(key, markup, fn, *args, label="Open"):
    """A card that is itself the button: no 'View details' button under every image."""
    with st.container(key=f"tap_{key}"):
        md(markup)
        if st.button(label, key=f"tapbtn_{key}"):
            fn(*args)


def chips(key, options, current, on_pick):
    with st.container(key=f"chips_{key}"):
        cols = st.columns(len(options))
        for c, o in zip(cols, options):
            with c:
                if st.button(o, key=f"chip_{key}_{o}", type="primary" if o == current else "secondary"):
                    on_pick(o)


def topbar(title, back_view, key, home=False):
    with st.container(key=f"topbar_{key}"):
        c1, c2, *c3 = st.columns([1, 4, 2] if home else [1, 6])
        with c1:
            if st.button("←", key=f"back_{key}", help="Back"):
                go(back_view)
        with c2:
            md(f'<div class="tb-title">{esc(title)}</div>')
        if home:
            with c3[0]:
                home_button(key)


USER_NAME = "Ayesha Khan"   # dummy account name shown in the Home greeting; change to any name
USER_PIC = "images/selfie_closeup.jpg"   # dummy account picture; point to any file in images/


def greeting():
    h = datetime.now().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"


def appbar(title="PixelSense", chat_btn=False, greet=False):
    with st.container(key="appbar"):
        c1, c2, c3 = st.columns([1, 4, 2] if chat_btn else [1, 5, 1])
        with c1:
            tappable("menu", f'<div class="ibtn pressable">{svg("menu", 22)}</div>', open_menu, label="Open menu")
        with c2:
            if greet:
                md(f'<div class="ab-title two"><small>{greeting()},</small><b>{esc(USER_NAME)}</b></div>')
            else:
                md(f'<div class="ab-title">{esc(title)}</div>')
        with c3:
            if greet:
                md(f'<img class="me" src="{img_uri(USER_PIC, 96, 96)}" alt="{esc(USER_NAME)} account picture">')
            if chat_btn:
                home_button("chat")


def snack_ui():
    if not S.snack:
        return
    msg, can_undo = S.snack
    with st.container(key="snack"):
        c1, c2 = st.columns([4, 1.4])
        with c1:
            md(f'<div class="snack-t">{esc(msg)}</div>')
        with c2:
            if can_undo and S.history and st.button("Undo", key="snack_undo"):
                undo()
                st.rerun()


def pill(text, kind=""):
    return f'<span class="pill {kind}">{esc(text)}</span>'


def tile_html(r):
    heart = f'<span class="heart">{svg("heart", 13, "#D6455D", 2, "#D6455D")}</span>' if r.id in S.fav else ""
    return f'<div class="tile pressable"><img src="{img_uri(r.file, 320, 240)}" alt="{esc(r.description)}">{heart}</div>'


def image_grid(rows, prefix, opener=open_image, extra=(), n=6):
    """n photos per row on a computer (the CSS folds 6 into 3 per row on a phone)."""
    with st.container(key=f"grid{n}_{prefix}"):
        for k in range(0, len(rows), n):
            cols = st.columns(n)
            for c, r in zip(cols, rows[k:k + n]):
                with c:
                    tappable(f"{prefix}_{r.id}", tile_html(r), opener, r.id, *extra, label=f"Open {r.description}")


def empty_state(icon, title, text):
    md(f'<div class="empty"><div class="ic">{svg(icon, 40, "#5B4FD6", 1.6)}</div><h3>{esc(title)}</h3><p>{esc(text)}</p></div>')


def highlight(raw, terms):
    if not terms:
        return esc(raw)
    pat = re.compile("(" + "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True)) + ")", re.I)
    return "".join(f"<mark>{esc(p)}</mark>" if n % 2 else esc(p) for n, p in enumerate(pat.split(raw)))


def thumb_head(r, extra):
    return (f'<div style="display:flex;gap:12px;align-items:center;margin-bottom:10px">'
            f'<img src="{img_uri(r.file, 160, 120)}" style="width:80px;height:60px;border-radius:12px;object-fit:cover" alt="">'
            f'<div><div style="font-weight:800;font-size:14.5px">{esc(r.description)}</div>'
            f'<div style="font-size:12.5px;color:#6B6F8C">{extra}</div></div></div>')


# --------------------------------------------------------------------------- dialogs
def create_collection(name, ids):
    """Shared by the dialog. Moves the photos into the collection (undoable)."""
    snap()
    if name not in all_cats():
        S.extra_cats.append(name)
    for i in ids:
        if AUTO[i][0] == name:
            S.override.pop(i, None)
        else:
            S.override[i] = name


@st.dialog("New collection")
def new_collection_dialog():
    name = st.text_input("Collection name", placeholder="e.g. Semester 7, Eid 2026", key="nc_name")
    sub = st.text_input("Fill it with photos that match (optional)", placeholder="e.g. family dinner, or Person 1", key="nc_new")
    st.caption("Photos you add move out of the collection AI put them in. Undo is always available.")
    if st.button("Create collection", type="primary", key="nc_ok"):
        n = name.strip()
        if not n:
            st.warning("Give your collection a name first.")
        elif n in all_cats():
            st.warning("You already have a collection with that name.")
        elif n in S.excluded_cats:
            st.warning("AI is paused for that collection name.")
        else:
            ids = E.answer_find(make_ctx(), sub, allow_count=False).ids if sub.strip() else []
            create_collection(n, [i for i in ids if visible(R[i])])
            notify(f"Collection “{n}” created" + (f" with {len(ids)} photo{'s' if len(ids) != 1 else ''}." if sub.strip() else "."))
            S.view = "collections"
            st.rerun()


@st.dialog("Move to another collection")
def move_dialog(i):
    r = R[i]
    cur = cat_of(r)
    md(thumb_head(r, f"Now in {esc(cur)}"))
    opts = [c for c in all_cats() if c not in S.excluded_cats]
    choice = st.radio("Collection", opts, index=opts.index(cur) if cur in opts else 0, key=f"mv_{i}")
    new = st.text_input("Or create a new collection", placeholder="e.g. Semester 7", key="nc_new_mv")
    if st.button("Save", type="primary", key=f"mv_save_{i}"):
        target = new.strip() or choice
        if target in S.excluded_cats:
            st.warning("AI is paused for that collection. Allow it in Settings first.")
            return
        snap()
        if target not in all_cats():
            S.extra_cats.append(target)
        if target == AUTO[i][0]:
            S.override.pop(i, None)
        else:
            S.override[i] = target
        notify(f"Moved to “{target}”.")
        st.rerun()


@st.dialog("Remove from PixelSense?")
def remove_dialog(i):
    r = R[i]
    md(thumb_head(r, "") + '<div class="info"><p>It leaves your library, search, People and collections.</p>'
       '<p><b>Your original file is not touched.</b> You can restore it from the Undo message or from Settings, Recently removed.</p></div>')
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel", key=f"rm_cancel_{i}"):
            st.rerun()
    with c2:
        if st.button("Remove", type="primary", key=f"rm_ok_{i}"):
            snap()
            S.removed.add(i)
            notify("Photo removed from PixelSense. Your original is untouched.")
            S.view = S.back if S.back in ("home", "chat", "photos", "results", "collection", "collections", "person", "people", "cleanup", "memory") else "home"
            st.rerun()


@st.dialog("Stop AI using this photo?")
def stop_ai_dialog(i):
    r = R[i]
    md(thumb_head(r, "") + '<div class="info"><p><b>What changes:</b> this photo leaves search, People and collections, and AI stops reading it.</p>'
       '<p>Nothing is deleted and the original is never changed. Allow it again any time in Settings.</p></div>')
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel", key=f"sa_cancel_{i}"):
            st.rerun()
    with c2:
        if st.button("Stop AI", type="primary", key=f"sa_ok_{i}"):
            snap()
            S.excluded_imgs.add(i)
            S.view = "chat"
            notify("AI will no longer use that photo.")
            st.rerun()


@st.dialog("Pause AI for this collection?")
def pause_cat_dialog(name):
    n = cat_total(name)
    md(f'<div class="info"><p><b>“{esc(name)}”</b> has {n} photo{"s" if n != 1 else ""}.</p>'
       '<p><b>What changes:</b> they leave search, People and the timeline, and AI stops reading them. '
       'They stay on your device and nothing is deleted.</p><p>Allow AI again any time in Settings.</p></div>')
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel", key=f"pc_cancel_{slug(name)}"):
            st.rerun()
    with c2:
        if st.button("Pause AI", type="primary", key=f"pc_ok_{slug(name)}"):
            snap()
            S.excluded_cats.add(name)
            if S.view in ("collection", "detail"):
                S.view = "collections" if S.view == "collection" else "chat"
            notify(f"AI is paused for “{name}”.")
            st.rerun()


@st.dialog("Name this person")
def rename_dialog(pid):
    md(f'<div style="display:flex;justify-content:center;margin-bottom:8px">{avatar(pid, 88)}</div>')
    new = st.text_input("Name", value=S.names.get(pid, ""), placeholder="e.g. Ayesha", key=f"rn_{pid}")
    st.caption("Only you can name people. The name is used for search, like “photos of Ayesha”.")
    if st.button("Save name", type="primary", key=f"rn_ok_{pid}"):
        n = new.strip()
        snap()
        if n:
            S.names[pid] = n
            notify(f"Named “{n}”.")
        else:
            S.names.pop(pid, None)
            notify("Name removed.")
        st.rerun()


@st.dialog("Hide this person?")
def hide_person_dialog(pid):
    md(f'<div style="display:flex;justify-content:center;margin-bottom:8px">{avatar(pid, 88)}</div>'
       f'<div class="info"><p><b>{esc(pname(pid))}</b> will disappear from People and from search by name. '
       'The photos themselves stay in your library. You can show this person again in Settings.</p></div>')
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel", key=f"hp_cancel_{pid}"):
            st.rerun()
    with c2:
        if st.button("Hide", type="primary", key=f"hp_ok_{pid}"):
            snap()
            S.hidden_people.add(pid)
            notify(f"{pname(pid)} is hidden.")
            S.view = "people"
            st.rerun()


@st.dialog("People in this photo")
def fix_faces_dialog(i):
    md('<div class="sub" style="margin-top:0">If PixelSense grouped someone wrongly, take this photo out of their group.</div>')
    for pid in [p for p in E.FACES_IN.get(i, []) if (p, i) not in S.notp]:
        c1, c2 = st.columns([1, 3])
        with c1:
            md(avatar(pid, 52))
        with c2:
            if st.button(f"Not {pname(pid)}", key=f"nf_{i}_{pid}"):
                snap()
                S.notp.add((pid, i))
                notify(f"Removed this photo from {pname(pid)}.")
                st.rerun()


# --------------------------------------------------------------------------- views
def view_welcome():
    t = lambda f, w, h: img_uri(f, w, h)
    with st.container(key="stack_wel"):
        left, right = st.columns([1, 1])
        with left:
            md(f'''<div class="wel-brand"><span class="wel-logo2">{svg("sparkle", 22, "#fff", 1.2, "#fff")}</span>PixelSense</div>
              <div class="wel-h">Your photo library, organised the way you ask.</div>
              <div class="wel-p">Find any photo in your own words, clear out blurry and duplicate shots, and keep what matters. You decide what the AI can read, and everything stays on your device.</div>''')
            if st.button("Get started", type="primary", key="start"):
                go("analysing")
            md('<div class="wel-note">HCI prototype · sample photos only · no tracking, no cookies</div>')
        with right:
            md(f'''<div class="mos">
              <div class="m a"><img src="{t("images/images (1).jpg", 600, 360)}" alt=""></div>
              <div class="m b"><img src="{t("images/images.jpg", 300, 380)}" alt=""></div>
              <div class="m c"><img src="{t("images/photo1.jpg", 300, 180)}" alt=""></div>
              <div class="m d"><img src="{t("images/images (3).jpg", 300, 180)}" alt=""></div></div>''')
    md(f'''<div class="feats"><div class="feat"><div class="fi">{svg("clock", 24)}</div><div><b>Needs attention</b><small>Due dates and amounts are read from your photos, with the exact words shown as proof.</small></div></div>
      <div class="feat"><div class="fi">{svg("sparkle", 24)}</div><div><b>Ask in plain words</b><small>“When is my assignment due?” is answered from the text inside your photos.</small></div></div>
      <div class="feat"><div class="fi">{svg("shield", 24)}</div><div><b>You stay in control</b><small>Pause AI on any collection, move any photo, and undo every change.</small></div></div></div>''')


def view_analysing():
    steps = ["Photos", "Screenshots", "Receipts & bills", "Tickets & documents"]
    ph = st.empty()

    def render(k):
        rows = ""
        for n, s in enumerate(steps):
            state, label = ("done", "Ready") if n < k else (("run", "Analysing…") if n == k else ("", "Waiting"))
            ic = svg("check", 22, "#18936A") if state == "done" else (svg("clock", 22, "#5B4FD6") if state == "run" else svg("clock", 22, "#B3B6CC"))
            rows += f'<div class="stepi {state}">{ic}<span>{s}</span><em>{label}</em></div>'
        done = k >= len(steps)
        head = "You’re all set" if done else "Analysing your photos…"
        sub = "Ask me anything about your library." if done else "This may take a few moments."
        spin = (f'<div class="empty" style="box-shadow:none;background:none;padding:34px 0 0"><div class="ic" style="background:#E3F6EC">{svg("check", 44, "#18936A", 2)}</div></div>'
                if done else '<div class="spin"></div>')
        ph.markdown(re.sub(r"\s*\n\s*", " ", f'''{spin}<div style="text-align:center"><div class="h1" style="margin-top:0">{head}</div><div class="sub">{sub}</div></div>
          <div class="card" style="margin-top:18px">{rows}</div>
          <div style="text-align:center;font-size:12px;color:#8A8EA8;margin-top:14px">Prototype note: analysis is simulated with a prepared sample dataset.</div>'''), unsafe_allow_html=True)

    for k in range(len(steps) + 1):
        render(k)
        time.sleep(0.75)
    n = len(visible_rows())
    k = len({cat_of(r) for r in visible_rows()})
    paused = sum(1 for r in df.itertuples() if r.id not in HELD and cat_of(r) in S.excluded_cats)
    S.view, S.scroll = "home", True
    S.snack = (f"Sorted {n} photos into {k} collections." + (f" {paused} that look private were paused for AI." if paused else ""), False)
    st.rerun()


# ---- chat -------------------------------------------------------------------------------------------
def view_chat():
    if not S.chat:                       # nothing searched yet: searching starts on Home
        S.view = "home"
        st.rerun()
    appbar("Search results", chat_btn=True)
    snack_ui()
    last = len(S.chat) - 1
    for idx, m in enumerate(S.chat):
        render_msg(idx, m, idx == last)


def coming_up_ui():
    soon = deadline_items()
    if not soon and not S.done:
        return
    section("Needs attention", "read from your photos", "attention", key="ca")
    if not soon:
        md('<div class="card pad calm"><b>You’re clear.</b><small>Every bill and deadline found in your photos is ticked off.</small></div>')
        return
    with st.container(key="cards3_upc"):
        cols = st.columns(3)
        for c, d in zip(cols, soon[:3]):
            urgent = " urgent" if d["urgency"] in ("overdue", "soon") else ""
            extra = f" · Rs {d['money']:,}" if d["money"] else ""
            with c:
                tappable(f"upc_{d['id']}",
                         f'<div class="card upc pressable glass"><div class="dbadge{urgent}"><b>{d["date"].day}</b><span>{d["date"].strftime("%b").upper()}</span></div>'
                         f'<div style="flex:1;min-width:0"><div class="rtitle">{esc(d["title"])}</div>'
                         f'<div class="ccount">{d["kind"]} {E.when_words(d["days"])}{extra}</div></div><div class="chev">{svg("chev", 20)}</div></div>',
                         go, "attention", label=f"Open {d['title']} in Needs attention")


def intro():
    md('<div class="greet"><h2>What are you looking for?</h2><p>Ask in your own words. I can find photos, answer questions from the text inside them, '
       'group them by person, and make collections. I only use photos the AI is allowed to read.</p></div>')
    chips("ask", list(HOME_CHIPS), None, ask_chip)


def open_results(rp):
    S.res = {"title": rp.text, "ids": list(rp.ids), "query": rp.query}
    go("results")


def chat_chip(idx, rp, label):
    if label == "Save these as a collection":
        if rp.person:
            name = f"{pname(rp.person)} photos"
        else:
            words = [t for t, o in E.search_terms(rp.query).items() if o is None and t not in E.TYPE_WORDS][:3]
            name = " ".join(w.title() for w in words) or "My collection"
        base, n = name, 2
        while name in all_cats():
            name, n = f"{base} {n}", n + 1
        ask(f"Create a collection called {name} with {rp.query}")
        st.rerun()
    elif label == "Open in editor" and rp.ids:
        S.back = "chat"
        open_editor(rp.ids[0])
    elif label == "Open People":
        go("people")
    elif label == "Open the photo" and rp.ids:
        open_from_msg(rp.ids[0], rp.query)
    elif label == "Show my latest photos":
        go("photos")


def src_line(r, snip, terms):
    """Show the matched text; for photos with no text, show type and date instead of repeating the title."""
    if snip and snip != r.description:
        return highlight(snip, terms)
    d = E.taken_date(r)
    return esc(r.type.title() + (f" · taken {d.strftime('%d %b %Y')}" if d else ""))


def render_msg(idx, m, is_last):
    if m["role"] == "user":
        md(f'<div class="msg-u"><div class="bub-u">{esc(m["text"])}</div></div>')
        return
    rp = m["reply"]
    md(f'<div class="msg-a"><div class="av-ai">{svg("sparkle", 18, "#fff", 1, "#fff")}</div><div class="bub-a">{fmt(rp.text)}</div></div>')
    rows = [R[i] for i in rp.ids if visible(R[i])]
    terms = list(E.search_terms(rp.query))
    shown_src = set()
    for sid, snip in rp.sources:
        if sid in R and visible(R[sid]):
            r = R[sid]
            shown_src.add(sid)
            tappable(f"m{idx}_src_{sid}",
                     f'<div class="card src pressable"><img class="rthumb" src="{img_uri(r.file, 240, 180)}" alt="">'
                     f'<div class="rbody"><div class="rtitle">{esc(r.description)}</div><div class="rsnip">{src_line(r, snip, terms)}</div></div>'
                     f'<div class="chev">{svg("chev", 20)}</div></div>', open_from_msg, sid, rp.query, label=f"Open {r.description}")
    grid = [r for r in rows if r.id not in shown_src]
    if grid:
        image_grid(grid[:6], f"m{idx}", open_from_msg, (rp.query,), n=3)
        if len(grid) > 6:
            tappable(f"m{idx}_all", f'<div class="more pressable" style="color:#5B4FD6;font-weight:800">See all {len(grid)} photos →</div>',
                     open_results, rp, label="See all photos")
    if rp.steps:
        items = "".join(f"<li>{esc(s)}</li>" for s in rp.steps)
        md(f'<details class="how"><summary>How I found this</summary><ol>{items}</ol>'
           '<div style="color:#8A8EA8">Answers come from prepared text and descriptions in this prototype, not a live model.</div></details>')
    if rp.chips:
        chips(f"mc{idx}", rp.chips, None, lambda lab: chat_chip(idx, rp, lab))
    if is_last and getattr(rp, "executed", False) and S.history:
        with st.container(key="plain_mundo"):
            if st.button("↶ Undo", key=f"mundo_{idx}"):
                undo()
                rp.executed = False
                rp.text += " (Undone.)"
                S.snack = None
                st.rerun()


# ---- home dashboard, clean-up, memories -------------------------------------------------------------
def section(title, sub="", target=None, label="See all", key=""):
    if target:
        c1, c2 = st.columns([4, 1])
        with c1:
            md(f'<div class="sect"><b>{esc(title)}</b>' + (f'<span style="margin-left:10px">{esc(sub)}</span>' if sub else "") + '</div>')
        with c2:
            with st.container(key=f"link_{key}"):
                if st.button(label, key=f"link_btn_{key}"):
                    go(target)
    else:
        md(f'<div class="sect"><b>{esc(title)}</b>' + (f'<span>{esc(sub)}</span>' if sub else "") + '</div>')


def open_memory(iso):
    S.cur_mem = iso
    go("memory")


def cover_card(img_file, title, sub):
    return (f'<div class="cov pressable"><img src="{img_uri(img_file, 480, 300)}" alt="">'
            f'<div class="cb"><div class="rtitle">{esc(title)}</div><div class="ccount">{esc(sub)}</div></div></div>')


def health_card():
    handled, total = library_health()
    if not total:
        return
    pct = round(100 * handled / total)
    circ = 2 * 3.14159 * 34
    ring = (f'<svg width="84" height="84" viewBox="0 0 84 84"><circle cx="42" cy="42" r="34" fill="none" stroke="rgba(91,79,214,.15)" stroke-width="9"/>'
            f'<circle cx="42" cy="42" r="34" fill="none" stroke="url(#hg)" stroke-width="9" stroke-linecap="round" stroke-dasharray="{circ * pct / 100:.1f} {circ:.1f}" transform="rotate(-90 42 42)"/>'
            f'<defs><linearGradient id="hg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7A6CF0"/><stop offset="1" stop-color="#3FA9F5"/></linearGradient></defs>'
            f'<text x="42" y="48" text-anchor="middle" font-size="19" font-weight="700" fill="#1F2140">{pct}%</text></svg>')
    msg = "All reviewed. Nice and tidy." if handled == total else f"{total - handled} left to review"
    md(f'<div class="card glass health"><div>{ring}</div><div style="flex:1"><div class="rtitle">Library progress</div>'
       f'<div class="ccount">{handled} of {total} reviewed · {msg}</div>'
       '<div class="att-proof">Counts bills and deadlines you handled, plus clutter you decided on. Keep and Remove count the same, so deleting is never rewarded.</div></div></div>')


def home_send():
    """Home search bar (Enter): same behaviour as the Ask prompt bar."""
    q = (S.get("home_q") or "").strip()
    S["home_q"] = ""
    ask(q)


def view_home():
    appbar("Home", greet=True)
    st.text_input("Search your library", key="home_q", placeholder="Search your library…", label_visibility="collapsed", on_change=home_send)
    chips("home", list(HOME_CHIPS), None, ask_chip)
    snack_ui()
    rows = visible_rows()
    groups = E.cleanup_groups(rows, S.kept)
    n_clean = sum(len(v) for v in groups.values())
    cats = [c for c in all_cats() if c not in S.excluded_cats]
    n_att = len(deadline_items())
    stats = [("coll", "Collections", len(cats), "folder", "collections"), ("photos", "Photos", len(rows), "image", "photos"),
             ("clean", "To review", n_clean, "trash", "cleanup"),
             ("ppl", "People", len(shown_people()), "users", "people")]
    with st.container(key="stats4_home"):
        cols = st.columns(4)
        for c, (k, lab, n, ic, target) in zip(cols, stats):
            with c:
                tappable(f"st_{k}", f'<div class="stat pressable"><span class="sic">{svg(ic, 22)}</span><div><div class="sn">{n}</div><div class="sl">{lab}</div></div></div>',
                         go, target, label=f"Open {lab}")

    if S.faces_on is None:
        tappable("faces_cta", f'<div class="banner pressable"><div class="bic">{svg("users", 26, "#C27A00")}</div><div style="flex:1"><b>Group photos by person?</b>'
                              f'<small>Turn on face groups to ask “photos of Person 1”.</small></div>{svg("chev", 22, "#C27A00")}</div>',
                 go, "people", label="Open People")

    attention_ui()
    health_card()

    if n_clean:
        thumbs = "".join(f'<img src="{img_uri(r.file, 120, 90)}" alt="">' for r in [x for v in groups.values() for x in v][:3])
        tappable("home_clean", f'<div class="banner pressable"><div class="bic">{svg("trash", 26, "#C27A00")}</div><div style="flex:1"><b>{n_clean} photos you may not need</b>'
                               f'<small>Blurry, low-resolution and screenshot photos, grouped for a quick review. Nothing is removed without your consent.</small></div>'
                               f'<div class="bthumbs">{thumbs}</div>{svg("chev", 22, "#C27A00")}</div>', go, "cleanup", label="Review clean-up")

    if cats:
        section("Collections", "sorted for you", "collections", key="hc")
        with st.container(key="cards3_hcov"):
            for k in range(0, min(len(cats), 6), 3):
                cols = st.columns(3)
                for c, name in zip(cols, cats[k:k + 3]):
                    items = coll_items(name)
                    with c:
                        if items:
                            tappable(f"hcl_{slug(name)}", cover_card(R[items[0]].file, name, f"{len(items)} item{'s' if len(items) != 1 else ''}"),
                                     open_collection, name, label=f"Open {name}")

    mem = E.moments(rows, cat_of)[:3]
    if mem:
        section("Memories", "days worth looking back on")
        with st.container(key="cards3_hmem"):
            cols = st.columns(3)
            for c, m in zip(cols, mem):
                with c:
                    tappable(f"hm_{m['iso']}", cover_card(m["cover"].file, m["title"], f"{len(m['items'])} photos"), open_memory, m["iso"], label=f"Open {m['title']}")

    recent = sorted(rows, key=lambda r: (r.taken, r.id), reverse=True)[:6]
    if recent:
        section("Recent photos", "", "photos", key="hr")
        image_grid(recent, "hrec")

    ppl = shown_people()[:6]
    if ppl:
        section("People", "", "people", key="hp")
        with st.container(key="grid6_hpeople"):
            cols = st.columns(6)
            for c, pid in zip(cols, ppl):
                with c:
                    tappable(f"hpp_{pid}", f'<div class="ptile pressable">{avatar(pid, 84)}<div class="pname {"" if pid in S.names else "un"}">{esc(pname(pid))}</div></div>',
                             open_person, pid, label=f"Open {pname(pid)}")


@st.dialog("Remove these photos?")
def clean_dialog(key="all"):
    ids = [r.id for v in E.cleanup_groups(visible_rows(), S.kept).values() for r in v]
    md(f'<div class="info"><p><b>{len(ids)} photo{"s" if len(ids) != 1 else ""}</b> will leave your library, search, People and collections.</p>'
       '<p><b>Your original files are not touched.</b> You can restore them from the Undo message or from Settings, Recently removed.</p></div>')
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel", key=f"cd_cancel_{key}"):
            st.rerun()
    with c2:
        if st.button(f"Remove {len(ids)}", type="primary", key=f"cd_ok_{key}"):
            snap()
            S.removed.update(ids)
            notify(f"Removed {len(ids)} photos. Your originals are untouched.")
            st.rerun()


def view_cleanup():
    appbar("Clean up")
    snack_ui()
    groups = E.cleanup_groups(visible_rows(), S.kept)
    items = [r for v in groups.values() for r in v]
    if not items:
        empty_state("check", "All tidy", "No blurry, duplicate, unopened or leftover photos to review.")
        return
    md(f'<div class="sect"><b>Photos you may not need</b><span>{len(items)} photo{"s" if len(items) != 1 else ""}</span></div>'
       '<div class="sub" style="margin-top:0;padding-bottom:0">Blurry, low-resolution, near-duplicate, old screenshots and photos not opened in a year. '
       'Measured on this device. Tap a photo to look closer. Nothing is removed without your consent.</div>')
    image_grid(items, "cu_all")
    with st.container(key="cuact_all"):
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Keep these", key="cu_keep_all"):
                snap()
                S.kept.update(r.id for r in items)
                notify(f"Kept {len(items)} photos. I will not suggest them again.")
                st.rerun()
        with c2:
            if st.button(f"Remove {len(items)}…", type="primary", key="cu_rm_all"):
                clean_dialog()


def view_memory():
    m = next((x for x in E.moments(visible_rows(), cat_of) if x["iso"] == S.cur_mem), None)
    if not m:
        go("home")
    topbar(m["title"], "home", "mem")
    snack_ui()
    md(f'<div class="sub" style="margin-top:0">{len(m["items"])} photos from {m["date"].strftime("%A, %d %B %Y")}</div>')
    image_grid(sorted(m["items"], key=lambda r: r.id), "mm")


# ---- needs attention (the core problem) -------------------------------------------------------------
def mark_done(i, days_left):
    snap()
    S.done.add(i)
    track("attention_done", days_left=days_left)
    notify(f"Ticked off “{title_of(i)}”.")
    st.rerun()


def unmark_done(i):
    snap()
    S.done.discard(i)
    track("attention_undo")
    notify("Moved back to Needs attention.", False)
    st.rerun()


@st.dialog("Did you pay this?")
def paid_dialog(i, days_left, money):
    md(f'<div class="info"><p><b>Rs {money:,}</b> · {esc(title_of(i))}</p>'
       '<p>PixelSense can’t check your bank, so it asks once before ticking a bill off. '
       'If you tick it by mistake, tap Undo and it comes straight back.</p></div>')
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Not yet", key=f"pd_no_{i}"):
            st.rerun()
    with c2:
        if st.button("Yes, I paid", type="primary", key=f"pd_yes_{i}"):
            mark_done(i, days_left)


def add_manual(title, d, money, kind, source, evidence=""):
    snap()
    S.manual_seq += 1
    S.manual.append({"id": f"m{S.manual_seq}", "title": title.strip() or "Untitled deadline", "date": d.isoformat(), "money": money,
                     "kind": kind, "source": source, "evidence": evidence})
    track("attention_added", source=source)
    notify(f"Added “{title.strip() or 'Untitled deadline'}”.")
    st.rerun()


@st.dialog("Add a deadline")
def add_deadline_dialog():
    md('<div class="sub" style="margin-top:0">Not everything starts as a photo. Type a deadline, or paste a message and PixelSense will find the date and amount.</div>')
    tab1, tab2 = st.tabs(["Type it", "Paste a message"])
    with tab1:
        title = st.text_input("What is it?", key="md_title", placeholder="e.g. Rent, Viva, Visa renewal")
        d = st.date_input("Date", value=date.today() + timedelta(days=7), key="md_date")
        money = st.number_input("Amount in Rs (leave 0 if none)", min_value=0, step=500, key="md_money")
        kind = st.selectbox("Type", ["Bill due", "Deadline", "Event"], key="md_kind")
        if st.button("Add", type="primary", key="md_add"):
            add_manual(title, d, int(money), kind, "typed")
    with tab2:
        txt = st.text_area("Paste an SMS, email or chat message", key="md_text", height=120, placeholder="Reminder: your rent of Rs 45,000 is due 1 Nov")
        t2 = st.text_input("Name it (optional)", key="md_title2", placeholder="e.g. Rent")
        if st.button("Find the date", type="primary", key="md_find"):
            hit = E.parse_pasted(txt, date.today())
            if not hit:
                st.warning("I couldn’t find a date in that text, so I added nothing. Try the Type it tab.")
            else:
                token = re.search(r"\d{1,2}\s*(?:st|nd|rd|th)?\s+[A-Za-z]{3,}|[A-Za-z]{3,}\s+\d{1,2}", txt)
                add_manual(t2 or txt.strip()[:40], hit["date"], hit["money"], hit["kind"], "pasted", E.snippet_of(txt, token.group(0)) if token else "")


URG = {"overdue": ("Overdue", "bad"), "soon": ("This week", "warn"), "later": ("Later", "")}


def attention_card(d):
    r, i = d["row"], d["id"]
    kind = URG[d["urgency"]][1]
    thumb = f'<img class="att-thumb" src="{img_uri(r.file, 160, 120)}" alt="{esc(d["title"])}">' if r is not None else ""
    proof = (f'Read from your photo: <i>{esc(d["evidence"])}</i>' if r is not None
             else (f'Read from your pasted message: <i>{esc(d["evidence"])}</i>' if d["source"] == "pasted" else "Added by you"))
    extra = f" · Rs {d['money']:,}" if d["money"] else ""
    with st.container(key=f"att_{i}"):
        md(f'<div class="att-row"><div class="dbadge{" urgent" if d["urgency"] != "later" else ""}"><b>{d["date"].day}</b><span>{d["date"].strftime("%b").upper()}</span></div>'
           f'{thumb}'
           f'<div class="att-body"><div class="rtitle">{esc(d["title"])}</div>'
           f'<div class="ccount">{d["kind"]} {E.when_words(d["days"])}{extra}</div>'
           f'<div class="att-proof">{proof}</div>'
           f'<div class="pills">{pill(d["stakes"], "warn" if d["urgency"] != "later" and d["stakes"] != "Optional" else "gray")}'
           f'{pill("You confirm it", "gray")}</div></div></div>')
        with st.container(key=f"sm_att_{i}"):
            c1, c2 = st.columns(2)
            with c1:
                if r is not None:
                    if st.button("Open photo", key=f"att_open_{i}"):
                        open_image(i)
                elif st.button("Remove", key=f"att_rm_{i}"):
                    snap()
                    S.manual = [m for m in S.manual if m["id"] != i]
                    notify("Deadline removed.")
                    st.rerun()
            with c2:
                if st.button("Mark done", key=f"att_done_{i}", type="primary"):
                    if d["money"]:
                        paid_dialog(i, d["days"], d["money"])
                    else:
                        mark_done(i, d["days"])


def attention_ui():
    """Needs attention, shown on Home under Coming up (it is not a separate page)."""
    live = deadline_items()
    done = done_items()
    money_soon = sum(d["money"] for d in live if d["money"] and d["days"] <= 14)
    nxt = live[0] if live else None
    md('<div class="sect" style="margin-top:6px"><b>Coming up</b></div>')
    if live:
        hero = (f'<div class="att-hero glass"><div><div class="ah-n">{len(live)}</div><div class="ah-l">need{"s" if len(live) == 1 else ""} you</div></div>'
                f'<div class="ah-sep"></div><div><div class="ah-n">Rs {money_soon:,}</div><div class="ah-l">due in the next 14 days</div></div>'
                f'<div class="ah-sep"></div><div><div class="ah-n">{nxt["date"].day} {nxt["date"].strftime("%b")}</div><div class="ah-l">next: {esc(nxt["title"])}</div></div></div>')
        md(hero)
    else:
        empty_state("check", "You’re clear", "Nothing due. Every bill and deadline found in your photos is ticked off.")
    for key in ("overdue", "soon", "later"):
        grp = [d for d in live if d["urgency"] == key]
        if grp:
            md(f'<div class="sect"><b>{URG[key][0]}</b><span>{len(grp)} item{"s" if len(grp) != 1 else ""}</span></div>')
            for d in grp:
                attention_card(d)
    if done:
        md(f'<div class="sect"><b>Done</b><span>{len(done)}</span></div>')
        for d in done:
            with st.container(key=f"att_done_row_{d['id']}"):
                c1, c2 = st.columns([4, 2])
                with c1:
                    md(f'<div class="crow" style="padding:2px 0">{svg("check", 22, "#18936A")}<div class="rtitle" style="font-size:14px">{esc(d["title"])}</div></div>')
                with c2:
                    with st.container(key=f"sm_undo_{d['id']}"):
                        if st.button("Undo", key=f"att_undo_{d['id']}"):
                            unmark_done(d["id"])
    md('<div class="sub" style="margin-top:14px;max-width:720px">Why “Done” is your word: PixelSense can’t see your bank or your university portal, and it never pretends to. '
       'It asks once before ticking off a payment, and every tick can be undone.</div>')


# ---- why PixelSense: the problem and the loopholes -------------------------------------------------
LOOPHOLES = [
    ("Ask people to type their own reminders", "Nobody keeps it up. Entering a date by hand is the very effort that made them take a photo instead.",
     "PixelSense reads the date and amount from the photo and shows the exact words it used as proof."),
    ("Reward people for staying on top (scores, streaks)", "People game it: tick everything without doing it, or delete photos just to look tidy.",
     "Progress counts things you have <b>reviewed</b>. Keep and Remove count the same, removal is undoable, and bills ask “Did you pay?” once."),
    ("Make identity checks stronger (face scan, biometrics)", "Strongest proof, highest cost: expensive, and a photo library is the most private place there is.",
     "The weakest check that works. Face groups are opt-in, on this device, named by you, with no biometric template. Private-looking photos start with AI paused."),
    ("Let cloud AI read everything", "Works well, but your bills and private messages leave your device.",
     "Everything runs on this device. You can pause AI per collection or per photo. Nothing is sent anywhere."),
    ("Track usage to improve the app", "Hidden tracking and third-party analytics break trust.",
     "Analytics is off by default, stored on this device, readable line by line, and has no third party."),
]


def view_about():
    if S.get("about_from") == "welcome":
        topbar("Why PixelSense", "welcome", "about")
    else:
        appbar("Why PixelSense")
    md('<div class="about-hero glass"><div class="lbl">The problem</div>'
       '<div class="about-h">Important information gets trapped inside photos.</div>'
       '<p>People screenshot a bill, a deadline notice or a poster “to deal with later”, then lose it among thousands of images. '
       'The cost is real: late fees, missed submissions, and minutes of scrolling to find one date.</p>'
       f'<div class="pills" style="margin-top:12px">{pill("Who: students and busy households", "")}{pill("Success: deadlines acted on before they pass", "good")}</div></div>')
    md('<div class="sect" style="margin-top:20px"><b>Every fix has a loophole</b><span>how each choice was made</span></div>'
       '<div class="sub" style="margin-top:0;max-width:720px">A design is only finished when you have asked how someone could misuse it, and what the stronger fix would cost. '
       'This is that thinking, one row per idea.</div>')
    for fix, hole, ans in LOOPHOLES:
        md(f'<div class="card pad glass loop"><div class="lp-a"><span>Idea</span><b>{fix}</b></div>'
           f'<div class="lp-b"><span>Loophole or cost</span><p>{hole}</p></div>'
           f'<div class="lp-c"><span>What PixelSense does</span><p>{ans}</p></div></div>')
    md('<div class="sect" style="margin-top:20px"><b>How it is built</b></div>'
       '<div class="card pad glass info"><p><b>Information architecture.</b> Home (what needs me now) · Ask (find anything) · Photos, People, Collections (browse) · Clean up (maintain) · Settings and Your data (control). '
       'Frequent tasks sit one tap from Home, and rare or risky ones sit in Settings.</p>'
       '<p><b>Visual language.</b> A Liquid Glass style: translucent layers that let content show through, large rounded shapes that nest, one type family on a clear scale, and an 8-point spacing grid. '
       'Navigation floats above content and the prompt bar floats below it, so photos stay the hero.</p>'
       '<p><b>Data.</b> System data, user data, references, cookies and analytics are each shown in Settings, Your data, with what they are and who controls them.</p>'
       '<p><b>What it does not cover.</b> A deadline that never became a photo is only caught if you add it (type it, or paste the message). “Done” is your word. In this prototype the AI is simulated with prepared data.</p></div>')


# ---- study mode (evaluation kit, researcher-facing) ----------------------------------------------------
def study_tasks():
    return [t for t in ST.TASKS if S.study["cond"] in t[5]]


@st.dialog("Task finished")
def finish_dialog():
    sd = S.study
    t = study_tasks()[sd["i"]]
    md(f'<div class="info"><p><b>{esc(t[0])} · {esc(t[2])}</b></p><p>Success looks like: {esc(t[4])}</p></div>')
    success = st.radio("Did the participant succeed?", ["Yes", "Partly", "No or gave up"], key="fd_success", horizontal=True)
    errors = st.number_input("Errors you observed (wrong taps, wrong results used, going back)", min_value=0, step=1, key="fd_errors")
    notes = st.text_area("Quotes or observations (think-aloud)", key="fd_notes", height=90)
    if st.button("Save and continue", type="primary", key="fd_save"):
        ST.log_task(participant=sd["pid"], condition=sd["cond"], task_id=t[0], rq=t[1], seconds=round(time.time() - sd["t0"], 1), success=success,
                    errors=int(errors), undos=sd.get("undos", 0), screens_visited=sd.get("nav", 0), notes=notes.replace("\n", " "))
        sd["logs"].append({"task": t[0], "seconds": round(time.time() - sd["t0"], 1), "success": success})
        sd["i"] += 1
        sd["running"] = False
        S.view = "study"
        st.rerun()


def study_bar():
    sd = S.study
    n = len(study_tasks())
    t = study_tasks()[sd["i"]]
    md("<style>[data-testid='stMainBlockContainer']{padding-top:92px!important}</style>")
    with st.container(key="studybar"):
        md(f'<div class="sb-t"><span>Task {sd["i"] + 1} of {n}</span><b>{esc(t[3])}</b></div>')
        if st.button("I’m finished", key="sb_done", type="primary"):
            finish_dialog()


@st.dialog("Photo", width="large")
def baseline_open(i):
    st.image(str(ROOT / R[i].file), caption=f"Taken {R[i].taken}")


def view_baseline():
    """The comparison condition: an ordinary gallery. A date-sorted grid, open a photo, select and delete. No search, no suggestions, no assistant."""
    md('<div class="h1" style="font-size:28px;font-weight:700;margin-bottom:8px">Gallery</div>')
    rows = sorted([r for r in df.itertuples() if arrived_ok(r) and r.id not in S.removed], key=lambda r: r.taken, reverse=True)
    picked = [r.id for r in rows if S.get(f"bl_sel_{r.id}")]
    with st.container(key="sm_bl"):
        if st.button(f"Delete selected ({len(picked)})", key="bl_del", disabled=not picked, type="primary"):
            S.removed.update(picked)
            for i in picked:
                S.pop(f"bl_sel_{i}", None)
            st.rerun()
    with st.container(key="grid4_bl"):
        for k in range(0, len(rows), 4):
            cols = st.columns(4)
            for c, r in zip(cols, rows[k:k + 4]):
                with c:
                    md(f'<img class="att-thumb" style="width:100%;height:auto;aspect-ratio:4/3;flex:none" src="{img_uri(r.file, 360, 270)}" alt="Photo from {r.taken}">'
                       f'<div class="ccount" style="margin:2px 0 4px">{r.taken}</div>')
                    st.checkbox("Select", key=f"bl_sel_{r.id}")
                    if st.button("Open", key=f"bl_open_{r.id}"):
                        baseline_open(r.id)


def view_study():
    appbar("Study mode")
    snack_ui()
    sd = S.study
    md('<div class="sub" style="margin-top:0;max-width:720px"><b>Researcher screen.</b> One session is one participant in one condition. Run the app twice per participant '
       '(PixelSense and Gallery baseline) in counterbalanced order. Data is saved to <b>study_data/</b> as you go.</div>')
    if not sd:
        study_setup()
    elif sd["step"] == "tasks":
        study_tasks_ui()
    elif sd["step"] == "survey":
        study_survey()
    else:
        study_done()


def study_setup():
    md(f'<div class="card pad glass info"><p><b>Information and consent</b></p><p>{esc(ST.CONSENT)}</p></div>')
    pid = st.text_input("Participant number", key="st_pid", placeholder="P01")
    if pid.strip():
        st.caption(f"Counterbalanced order: {pid.strip()} starts with {ST.counterbalance(pid.strip())}.")
    cond = st.radio("Condition for this session", ST.CONDITIONS, key="st_cond", horizontal=True)
    ok = st.checkbox("The participant has read the information above and agrees to take part.", key="st_consent")
    with st.container(key="sm_stb"):
        if st.button("Begin session", type="primary", key="st_begin", disabled=not (pid.strip() and ok)):
            S.study = dict(step="tasks", pid=pid.strip(), cond=cond, i=0, running=False, logs=[], nav=0, undos=0)
            st.rerun()


def study_tasks_ui():
    sd = S.study
    tasks = study_tasks()
    md(f'<div class="sect"><b>{esc(sd["pid"])} · {esc(sd["cond"])}</b><span>{sd["i"]} of {len(tasks)} tasks done</span></div>')
    done = {l["task"]: l for l in sd["logs"]}
    for n, t in enumerate(tasks):
        d = done.get(t[0])
        state = f'{d["success"]} · {d["seconds"]} s' if d else ("Next" if n == sd["i"] else "Waiting")
        md(f'<div class="card pad glass crow" style="margin-bottom:8px"><div style="flex:1"><div class="rtitle">{esc(t[0])} · {esc(t[2])} <span class="pill gray">{esc(t[1])}</span></div>'
           f'<div class="ccount">Read aloud: “{esc(t[3])}”</div><div class="att-proof">Success: {esc(t[4])}</div></div>{pill(state, "good" if d else "")}</div>')
    with st.container(key="sm_stb"):
        if sd["i"] < len(tasks):
            if st.button(f"Start task {sd['i'] + 1}", type="primary", key="st_start"):
                sd.update(running=True, t0=time.time(), nav=0, undos=0)
                S.view = "home" if sd["cond"] == "PixelSense" else "baseline"
                st.rerun()
        elif st.button("Continue to questionnaires", type="primary", key="st_to_survey"):
            sd["step"] = "survey"
            st.rerun()
        if st.button("Abort session (keeps data already saved)", key="st_abort"):
            S.update(fresh_state())
            S.view = "study"
            st.rerun()


def study_survey():
    sd = S.study
    lab = {1: "1 · Strongly disagree", 5: "5 · Strongly agree"}
    md('<div class="sub" style="margin-top:0">Hand the screen to the participant. All questions are required.</div>')
    with st.form("survey_form"):
        md('<div class="sect"><b>System Usability Scale</b></div>')
        sus = [st.radio(f"{i + 1}. {q}", [1, 2, 3, 4, 5], index=None, horizontal=True, format_func=lambda v: lab.get(v, str(v)), key=f"sus_{i}") for i, q in enumerate(ST.SUS_ITEMS)]
        md('<div class="sect"><b>Workload (NASA-TLX)</b></div>')
        tlx = {k: st.slider(f"{name}. {q}", 0, 100, 50, 5, key=f"tlx_{k}") for k, name, q in ST.TLX_ITEMS}
        ueq, trust = [None] * 8, [None] * 3
        if sd["cond"] == "PixelSense":
            md('<div class="sect"><b>Experience (UEQ-S)</b></div><div class="sub" style="margin-top:0">Pick the point between the two words that matches your impression.</div>')
            ueq = [st.radio(f"{a}  ←→  {b}", [1, 2, 3, 4, 5, 6, 7], index=None, horizontal=True, key=f"ueq_{i}") for i, (a, b) in enumerate(ST.UEQ_S)]
            md('<div class="sect"><b>Trust and control</b></div><div class="sub" style="margin-top:0">1 = strongly disagree, 7 = strongly agree.</div>')
            trust = [st.radio(q, [1, 2, 3, 4, 5, 6, 7], index=None, horizontal=True, key=f"trust_{i}") for i, q in enumerate(ST.TRUST_ITEMS)]
        md('<div class="sect"><b>Interview</b></div>')
        notes = st.text_area("Researcher notes and quotes: what worked, what confused them, would they use it?", key="iv_notes", height=120)
        submitted = st.form_submit_button("Save answers", type="primary")
    if submitted:
        if None in sus or None in ueq or None in trust:
            st.warning("Please answer every question.")
            return
        row = dict(participant=sd["pid"], condition=sd["cond"], sus_score=ST.sus_score(sus), tlx_raw=ST.tlx_raw(tlx), interview_notes=notes.replace("\n", " "))
        row.update({f"sus_{i + 1}": v for i, v in enumerate(sus)})
        row.update({f"tlx_{k}": v for k, v in tlx.items()})
        if sd["cond"] == "PixelSense":
            row.update({f"ueq_{i + 1}": v for i, v in enumerate(ueq)})
            row["ueq_pragmatic"], row["ueq_hedonic"] = ST.ueq_scores(ueq)
            row.update({f"trust_{i + 1}": v for i, v in enumerate(trust)})
        ST.log_questionnaire(**row)
        sd["scores"] = row
        sd["step"] = "done"
        st.rerun()


def study_done():
    sd = S.study
    sc = sd["scores"]
    md(f'<div class="card pad glass info"><p><b>Session saved for {esc(sd["pid"])} · {esc(sd["cond"])}.</b></p>'
       f'<p>SUS {sc["sus_score"]} (about 68 is average) · NASA-TLX raw {sc["tlx_raw"]}'
       + (f' · UEQ-S pragmatic {sc["ueq_pragmatic"]}, hedonic {sc["ueq_hedonic"]}' if "ueq_pragmatic" in sc else "") + '</p></div>')
    with st.container(key="sm_dl"):
        c1, c2, _sp = st.columns([1, 1, 1])
        with c1:
            st.download_button("Download tasks.csv", ST.read_csv_bytes("tasks.csv"), file_name="tasks.csv", mime="text/csv", key="dl_tasks")
        with c2:
            st.download_button("Download questionnaires.csv", ST.read_csv_bytes("questionnaires.csv"), file_name="questionnaires.csv", mime="text/csv", key="dl_q")
    with st.container(key="sm_stb"):
        if st.button("Start next session", type="primary", key="st_next"):
            S.update(fresh_state())
            S.view = "study"
            st.rerun()


# ---- photos timeline ----------------------------------------------------------------------------------
def view_photos():
    appbar("Photos")
    snack_ui()

    def pick(o):
        S.hfilter = o
        st.rerun()

    chips("lib", ["All", "Favorites"] + TYPE_FILTERS[1:], S.hfilter, pick)
    rows = visible_rows()
    if S.hfilter == "Favorites":
        rows = [r for r in rows if r.id in S.fav]
    elif S.hfilter != "All":
        rows = [r for r in rows if r.type.title() == S.hfilter]
    if not rows:
        empty_state("heart" if S.hfilter == "Favorites" else "image", "Nothing here yet",
                    "Tap the heart on a photo to add it here." if S.hfilter == "Favorites" else f"No {S.hfilter.lower()} photos that AI is allowed to use.")
        return
    groups = {}
    for r in sorted(rows, key=lambda r: (r.taken, r.id), reverse=True):
        d = E.taken_date(r)
        groups.setdefault((d.year, d.month) if d else (0, 0), []).append(r)
    for (y, mo), items in groups.items():
        label = date(y, mo, 1).strftime("%B %Y") if y else "Undated"
        md(f'<div class="monthh"><b>{label}</b><span>{len(items)} photo{"s" if len(items) != 1 else ""}</span></div>')
        image_grid(items, f"t{y}{mo}")


def view_results():
    res = S.res or {"title": "", "ids": [], "query": ""}
    topbar("All results", "chat", "res")
    rows = [R[i] for i in res["ids"] if visible(R[i])]
    md(f'<div class="sub" style="margin-top:0">{fmt(res["title"])}</div>')
    if rows:
        image_grid(rows, "rs", open_from_msg, (res["query"],))
    else:
        empty_state("search", "Nothing to show", "These photos are no longer available to the AI.")


# ---- people -------------------------------------------------------------------------------------------
def view_people():
    appbar("People")
    snack_ui()
    if not S.faces_on:
        off = S.faces_on is False
        md(f'<div class="card consent"><h3>{"Face groups are off" if off else "Group photos by the people in them?"}</h3>'
           '<p>PixelSense finds faces and puts the same person together, so you can open one face and see every photo of them.</p>'
           '<p><b>You stay in control:</b> you name people, you can hide anyone, and you can turn this off and forget names at any time in Settings.</p>'
           '<p style="color:#8A8EA8;font-size:12.5px">In this prototype faces are prepared in advance. Nothing is recognised live and nothing leaves this device.</p></div>')
        with st.container(key="consent_btns"):
            if st.button("Turn on face groups", type="primary", key="btn_faces_on"):
                S.faces_on = True
                notify("Face groups are on. Tap a face to see every photo of that person.", False)
                st.rerun()
            if not off:
                if st.button("Not now", key="faces_notnow"):
                    S.faces_on = False
                    st.rerun()
        return
    ppl = shown_people()
    md(f'<div class="sub" style="margin-top:0">{len(ppl)} people. Tap a face to see every photo of that person. Name people to search by name.</div>')
    if not ppl:
        empty_state("users", "No people yet", "Faces appear here once AI can read photos that have people in them.")
    with st.container(key="grid6_people"):
        for k in range(0, len(ppl), 6):
            cols = st.columns(6)
            for c, pid in zip(cols, ppl[k:k + 6]):
                n = len(person_images(pid))
                with c:
                    tappable(f"p_{pid}", f'<div class="ptile pressable">{avatar(pid, 84)}<div class="pname {"" if pid in S.names else "un"}">{esc(pname(pid))}</div>'
                                         f'<div class="pcount">{n} photo{"s" if n != 1 else ""}</div></div>',
                             open_person, pid, label=f"Open {pname(pid)}")


def view_person():
    pid = S.cur_person
    if not S.faces_on or pid not in E.PERSON_IMAGES or pid in S.hidden_people or not person_images(pid):
        go("people")
    topbar(pname(pid), "people", "per")
    snack_ui()
    ids = person_images(pid)
    md(f'<div class="phero">{avatar(pid, 112)}<div class="pn">{esc(pname(pid))}</div>'
       f'<div class="ccount">{len(ids)} photo{"s" if len(ids) != 1 else ""}</div></div>')
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Rename" if pid in S.names else "Add name", type="primary", key="per_rename"):
            rename_dialog(pid)
    with c2:
        if st.button("Hide person", key="per_hide"):
            hide_person_dialog(pid)
    shown = shown_people()
    together = Counter(p for i in ids for p in E.FACES_IN.get(i, []) if p != pid and (p, i) not in S.notp and p in shown)
    if together:
        md('<div class="lbl" style="margin-top:6px">Often with</div>')
        top = [p for p, _ in together.most_common(4)]
        cols = st.columns(4)
        for c, p in zip(cols, top):
            with c:
                tappable(f"pw_{p}", f'<div class="ptile sm pressable">{avatar(p, 60)}<div class="pname {"" if p in S.names else "un"}" style="font-size:11.5px">{esc(pname(p))}</div></div>',
                         open_person, p, label=f"Open {pname(p)}")
    md('<div class="sect" style="margin-top:6px"><b>Photos</b><span>newest first</span></div>')
    rows = sorted((R[i] for i in ids), key=lambda r: (r.taken, r.id), reverse=True)
    image_grid(rows, "pp")


# ---- details --------------------------------------------------------------------------------------------
def view_detail():
    if S.sel is None or S.sel not in R or not visible(R[S.sel]):
        go("chat")
    r = R[S.sel]
    topbar("Photo details", S.back, "det", home=True)
    snack_ui()
    cur, (auto, reason) = cat_of(r), AUTO[r.id]
    moved = r.id in S.override
    d = E.taken_date(r)
    heart = f'<span class="heart">{svg("heart", 20, "#D6455D", 2, "#D6455D")}</span>' if r.id in S.fav else ""
    with st.container(key="stack_detail"):
        left, right = st.columns([5, 4])
        with left:
            md(f'<div class="hero-img"><img src="{img_uri(r.file, 720, 540)}" alt="{esc(r.description)}">{heart}'
               f'<div class="pills">{pill(r.type.title())}{pill(cur, "good")}</div></div>')
            md(f'<div class="dtitle">{esc(r.description)}</div>'
               + (f'<div class="ccount" style="margin-top:4px">Taken {d.strftime("%d %b %Y")}</div>' if d else ""))

        with right:
            faces = [p for p in E.FACES_IN.get(r.id, []) if (p, r.id) not in S.notp]
            if faces and S.faces_on:
                shown = [p for p in faces if p not in S.hidden_people]
                if shown:
                    md(f'<div class="sect" style="margin-top:4px"><b style="font-size:16px">People in this photo</b><span>{len(shown)}</span></div>')
                    for k in range(0, len(shown), 4):
                        cols = st.columns(4)
                        for c, p in zip(cols, shown[k:k + 4]):
                            with c:
                                tappable(f"df_{p}", f'<div class="ptile sm pressable">{avatar(p, 60)}<div class="pname {"" if p in S.names else "un"}" style="font-size:11.5px">{esc(pname(p))}</div></div>',
                                         open_person, p, label=f"Open {pname(p)}")
                    with st.container(key="link_fix"):
                        if st.button("Wrong person?", key="d_fix"):
                            fix_faces_dialog(r.id)
            elif faces:
                tappable("d_facecta", f'<div class="banner pressable"><div class="bic">{svg("users", 26, "#C27A00")}</div><div style="flex:1"><b>{len(faces)} face{"s" if len(faces) != 1 else ""} found</b>'
                                      f'<small>Turn on face groups to see who is in this photo.</small></div>{svg("chev", 22, "#C27A00")}</div>', go, "people", label="Open People")

            ev = []
            if S.query:
                ev = next((e for _, rr, e in E.search(make_ctx(), S.query) if rr.id == r.id), [])
            if ev:
                items = "".join(f'<div class="ev"><i>{svg("tick", 13, "#18936A", 3)}</i><span>{esc(E.ev_sentence(e))}</span></div>' for e in ev)
                md(f'<div class="card pad"><div class="sect" style="margin:0 0 4px"><b style="font-size:16px">Why this result?</b>'
                   f'<span>for “{esc(S.query)}”</span></div>{items}</div>')
            if r.visible_text:
                md(f'<div class="found"><small>Text found in image</small><div>{highlight(r.visible_text, list(E.search_terms(S.query)) if S.query else [])}</div></div>')

            why = (f"You moved it here. AI would have chosen “{esc(auto)}”." if moved else f"AI put it here because {esc(reason)}.")
            md(f'<div class="lcard good">{pill("Moved by you", "warn") if moved else pill("Sorted by AI")}'
               f'<div class="big">{esc(cur)}</div><p>{why} You can change it any time.</p></div>')
            if moved:
                with st.container(key="plain_reset"):
                    if st.button("Back to AI’s choice", key="d_reset"):
                        snap()
                        S.override.pop(r.id, None)
                        notify(f"Back in “{auto}”.")
                        st.rerun()
            with st.container(key="danger_rm"):
                if st.button("Remove photo from PixelSense", key="d_remove"):
                    remove_dialog(r.id)
    md('<div style="height:70px"></div>')
    with st.container(key="actionbar"):
        c0, ce, c1, c2 = st.columns([1, 2, 2, 2])
        with ce:
            if st.button("✎ Edit", key="d_edit"):
                open_editor(r.id)
        with c0:
            with st.container(key="favbtn"):
                if st.button("♥" if r.id in S.fav else "♡", key="d_fav", help="Favorite"):
                    snap()
                    S.fav.symmetric_difference_update({r.id})
                    notify("Added to Favorites." if r.id in S.fav else "Removed from Favorites.")
                    st.rerun()
        with c1:
            if st.button("Move to…", type="primary", key="d_move"):
                move_dialog(r.id)
        with c2:
            if st.button("Stop AI", key="d_stopai"):
                stop_ai_dialog(r.id)


# ---- photo editor ------------------------------------------------------------------------------------------
def pil_uri(im, q=88):
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def view_edit():
    if S.sel is None or S.sel not in R or not visible(R[S.sel]):
        go("home")
    r = R[S.sel]
    topbar("Edit photo", "detail", "edit")
    snack_ui()
    src = Image.open(ROOT / r.file)
    with st.container(key="stack_edit"):
        left, right = st.columns([5, 4])
        with right:
            t_adj, t_crop, t_look, t_res = st.tabs(["Adjust", "Crop & rotate", "Filters", "Resolution"])
            with t_adj:
                auto = st.toggle("Auto-enhance", key="ed_auto")
                b = st.slider("Brightness", -50, 50, 0, key="ed_b")
                c = st.slider("Contrast", -50, 50, 0, key="ed_c")
                sat = st.slider("Colour", -60, 60, 0, key="ed_sat")
                warm = st.slider("Warmth", -50, 50, 0, key="ed_warm")
                sharp = st.slider("Sharpness", -50, 100, 0, key="ed_sharp")
            with t_crop:
                asp = st.selectbox("Aspect ratio", list(ED.ASPECTS), key="ed_asp")
                st.caption("Trim the edges (%)")
                k1, k2 = st.columns(2)
                with k1:
                    tl = st.slider("Left", 0, 40, 0, key="ed_tl")
                    tt = st.slider("Top", 0, 40, 0, key="ed_tt")
                with k2:
                    tr = st.slider("Right", 0, 40, 0, key="ed_tr")
                    tb = st.slider("Bottom", 0, 40, 0, key="ed_tb")
                rot = st.radio("Rotate", [0, 90, 180, 270], horizontal=True, format_func=lambda d: f"{d}°", key="ed_rot")
                flip = st.toggle("Flip horizontally", key="ed_flip")
            with t_look:
                look = st.radio("Look", ED.FILTERS, horizontal=True, key="ed_look")
            with t_res:
                sc = st.radio("Output size", [1, 2, 4], horizontal=True, format_func=lambda x: "Original" if x == 1 else f"{x}x larger", key="ed_sc")
                st.caption("Resizes with high-quality resampling and gentle sharpening. It cannot invent detail the way a generative AI would.")
        ops = ED.new_ops(brightness=b, contrast=c, saturation=sat, warmth=warm, sharpness=sharp, auto=auto, aspect=asp,
                         crop=(tl, tt, tr, tb), rotate=rot, flip=flip, filter=look, scale=sc)
        with left:
            show_orig = st.toggle("Show original", key="ed_orig")
            small = ImageOps.exif_transpose(src).convert("RGB")
            small.thumbnail((1100, 1100))
            shown = small if show_orig else ED.apply(small, {**ops, "scale": 1})
            md(f'<div class="edprev"><img src="{pil_uri(shown)}" alt="Preview"></div>')
            done = ED.describe(ops)
            md(f'<div class="ccount" style="margin-top:2px">{esc(", ".join(done).capitalize()) if done else "No changes yet"} · original {src.size[0]}×{src.size[1]} px'
               + (f' · saved copy will be {min(sc, 4096 / max(src.size)) * max(src.size):.0f}px on the long side' if sc > 1 else "") + '</div>')
        with right:
            opts = ["Edited"] + [x for x in all_cats() if x not in S.excluded_cats and x != "Edited"]
            dest = st.selectbox("Save copy to collection", opts, key="ed_dest")
            with st.container(key="edact"):
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Reset", key="ed_reset"):
                        for k in [k for k in S.keys() if str(k).startswith("ed_") and k != "ed_dest"]:
                            del S[k]
                        st.rerun()
                with c2:
                    if st.button("Save as copy", type="primary", key="ed_save", disabled=ED.is_default(ops)):
                        snap()
                        rec = new_copy_record(r.id, ops)
                        place_copy(rec["id"], dest)
                        notify(f"Saved a copy to “{dest}”. Your original is untouched.")
                        S.sel, S.back, S.view, S.scroll = rec["id"], "photos", "detail", True
                        st.rerun()
                if not ED.is_default(ops):
                    buf = io.BytesIO()
                    ED.apply(src, ops).save(buf, "JPEG", quality=92)
                    st.download_button("Download edited photo", buf.getvalue(), file_name=f"{r.id}_edited.jpg", mime="image/jpeg", key="ed_dl")
            md('<div class="ccount">Edits never change your original. Saving makes a new copy you can undo.</div>')


# ---- collections ----------------------------------------------------------------------------------------
def view_collections():
    appbar("Collections")
    c1, c2 = st.columns([3, 1.6])
    with c1:
        md('<div class="sub" style="margin-top:6px">Sorted for you. Create your own, or move any photo.</div>')
    with c2:
        with st.container(key="sm_new"):
            if st.button("+ New", key="coll_new"):
                new_collection_dialog()
    snack_ui()
    cats = [c for c in all_cats() if c not in S.excluded_cats]
    cards = []
    for n, name in enumerate(cats):
        items = coll_items(name)
        bg, fg = TILE_COLORS[n % len(TILE_COLORS)]
        thumb = (f'<div class="cthumb"><img src="{img_uri(R[items[0]].file, 160, 120)}" alt=""></div>' if items
                 else f'<div class="cthumb" style="background:{bg};color:{fg}">{svg("folder", 24)}</div>')
        cards.append((f"cl_{slug(name)}",
                      f'<div class="card crow pressable">{thumb}<div style="flex:1;min-width:0"><div class="rtitle" style="font-size:15.5px">{esc(name)}</div>'
                      f'<div class="ccount">{len(items)} item{"s" if len(items) != 1 else ""}</div></div><div class="chev">{svg("chev", 20)}</div></div>',
                      open_collection, name, f"Open {name}"))
    paused = [c for c in all_cats() if c in S.excluded_cats]
    if paused:
        cards.append(("paused", f'<div class="card crow pressable"><div class="cthumb" style="background:#EEF0F6;color:#6B6F8C">{svg("eyeoff", 24)}</div>'
                                f'<div style="flex:1;min-width:0"><div class="rtitle" style="font-size:15.5px">{len(paused)} paused for AI</div>'
                                f'<div class="ccount">Manage in Settings</div></div><div class="chev">{svg("chev", 20)}</div></div>',
                      go, "settings", "Open Settings"))
    with st.container(key="cards3_coll"):
        for k in range(0, len(cards), 3):
            cols = st.columns(3)
            for c, (key, markup, fn, arg, label) in zip(cols, cards[k:k + 3]):
                with c:
                    tappable(key, markup, fn, arg, label=label)


def view_collection():
    name = S.cur_coll
    if name not in all_cats() or name in S.excluded_cats:
        go("collections")
    topbar(name, "collections", "coll")
    snack_ui()
    items = [R[i] for i in coll_items(name)]
    md(f'<div class="sub" style="margin-top:0">{len(items)} item{"s" if len(items) != 1 else ""}</div>')
    if items:
        image_grid(items, "cg")
    else:
        empty_state("folder", "This collection is empty", "Open any photo and choose “Move to…”, or ask me to fill it.")
    md('<div style="height:8px"></div>')
    if name in S.extra_cats:
        with st.container(key="danger_delcoll"):
            if st.button("Delete collection", key="coll_del"):
                snap()
                S.extra_cats.remove(name)
                S.override = {k: v for k, v in S.override.items() if v != name}
                notify(f"Collection “{name}” deleted. Its photos went back to AI’s choice.")
                S.view = "collections"
                st.rerun()
    else:
        with st.container(key="danger_pause"):
            if st.button("Pause AI for this collection", key="coll_pause"):
                pause_cat_dialog(name)


# ---- settings ---------------------------------------------------------------------------------------------
def thumb_row(r, key, btn, on_click, kind="secondary"):
    with st.container(key=f"row_{key}_{r.id}"):
        c1, c2 = st.columns([4, 2])
        with c1:
            md(f'<div class="crow" style="padding:2px 0"><div class="cthumb"><img src="{img_uri(r.file, 160, 120)}" alt=""></div>'
               f'<div class="rtitle" style="font-size:14px">{esc(r.description)}</div></div>')
        with c2:
            with st.container(key=f"sm_{key}_{r.id}"):
                if st.button(btn, key=f"{key}_{r.id}", type=kind):
                    on_click(r.id)


def allow_image(i):
    snap()
    S.excluded_imgs.discard(i)
    notify("AI can use that photo again.")
    st.rerun()


def restore_image(i):
    S.removed.discard(i)
    notify("Photo restored.", False)
    st.rerun()


def user_data_snapshot():
    """Everything the person has created or decided in this session (what 'Download my data' exports)."""
    return {"names": S.names, "hidden_people": sorted(S.hidden_people), "favourites": sorted(S.fav), "collections_made": S.extra_cats,
            "moved_photos": S.override, "removed": sorted(S.removed), "ai_paused_collections": sorted(S.excluded_cats),
            "ai_paused_photos": sorted(S.excluded_imgs), "ticked_off": sorted(S.done), "edited_copies": [{"id": c["id"], "original": c["src"]} for c in S.copies],
            "recent_searches": S.searches}


def acted_early():
    """The one number that says whether the app solves its problem: ticked off with days to spare."""
    ticks = [e for e in S.events if e["event"] == "attention_done"]
    return (sum(1 for e in ticks if e.get("days_left", 0) >= 0), len(ticks))


def your_data_ui():
    md('<div class="sect" style="margin-top:16px"><b>Your data</b></div>'
       '<div class="sub" style="margin-top:0;max-width:720px">Every app holds five kinds of data. Here is what PixelSense keeps in each, where it lives, and who is in control.</div>')
    ud = user_data_snapshot()
    n_user = sum(len(v) for v in ud.values())
    live = {"system": f"{len(df)} items · {len(E.FACES)} face boxes", "user": f"{n_user} saved choice{'' if n_user == 1 else 's'}",
            "refs": f"{len(S.copies)} edited copies · {len(S.removed)} removed, originals untouched", "cookies": "0 cookies · 0 tracking ids",
            "analytics": f"{'ON' if S.analytics_on else 'OFF'} · {len(S.events)} events logged"}
    icons = {"system": "folder", "user": "user", "refs": "image", "cookies": "shield", "analytics": "clock"}
    for key, title, what, where, control in AN.DATA_MAP:
        md(f'<div class="card pad glass dmap"><span class="si">{svg(icons[key], 20)}</span><div style="flex:1;min-width:0">'
           f'<div class="dm-t"><b>{title}</b><em>{live[key]}</em></div><p>{what}</p>'
           f'<div class="dm-m"><span>Where</span> {where}<span style="margin-left:14px">Control</span> {control}</div></div></div>')
    with st.container(key="sm_dl"):
        c1, c2, _sp = st.columns([1, 1, 2])
        with c1:
            st.download_button("Download my data", AN.export_json(ud, S.events, S.analytics_on), file_name="pixelsense_my_data.json",
                               mime="application/json", key="dl_data")
        with c2:
            with st.container(key="danger_erase"):
                if st.button("Erase my data", key="erase_data"):
                    S.update(fresh_state())
                    S.view = "settings"
                    st.rerun()
    md('<div class="sect" style="margin-top:12px"><b>Help improve PixelSense</b></div>'
       '<div class="sub" style="margin-top:0;max-width:720px">Optional. Records <b>which screens you open and how often you tick things off</b>, so we can tell whether the app really helps people act before a deadline. '
       'It never records photos, search words or names. It stays on this device, and you can read and erase every line.</div>')
    with st.container(key="sm_ana"):
        if S.analytics_on:
            if st.button("Turn off analytics", key="ana_off"):
                S.analytics_on = False
                notify("Analytics is off. Nothing more is recorded.", False)
                st.rerun()
        elif st.button("Turn on analytics", key="ana_on", type="primary"):
            S.analytics_on = True
            track("screen_open", screen="settings")
            notify("Analytics is on. You can read every line below.", False)
            st.rerun()
    if S.analytics_on:
        early, tot = acted_early()
        summ = AN.summarise(S.events)
        md(f'<div class="card pad glass info"><p><b>Is it solving the problem?</b> {early} of {tot} ticked-off items were handled before their date.</p>'
           + "".join(f'<p style="margin:2px 0"><span class="pill gray">{n}</span> {esc(AN.ALLOWED[k])}</p>' for k, n in summ.items())
           + '</div>')
        if S.events:
            with st.expander("Read the raw log (last 15 lines)"):
                st.code("\n".join(" · ".join(f"{k}={v}" for k, v in e.items()) for e in S.events[-15:]), language=None)
            with st.container(key="sm_anaclr"):
                if st.button("Erase analytics log", key="ana_clear"):
                    S.events = []
                    notify("Analytics log erased.", False)
                    st.rerun()


def view_settings():
    appbar("Settings")
    md('<div class="sub" style="margin-top:6px">Privacy, face groups and what AI is allowed to see.</div>')
    snack_ui()

    md('<div class="sect" style="margin-top:6px"><b>Face groups</b></div>')
    on = bool(S.faces_on)
    nm = len(S.names) + len(S.hidden_people)
    with st.container(key="row_faces"):
        c1, c2 = st.columns([3, 2])
        with c1:
            md(f'<div class="setrow" style="padding:4px 0;border:none"><span class="si {"" if on else "off"}">{svg("users", 20)}</span>'
               f'<div><b>People</b><small>{"On" if on else "Off"}{f" · {nm} named or hidden" if nm else ""}</small></div></div>')
        with c2:
            with st.container(key="sm_faces"):
                if on:
                    if st.button("Turn off", key="faces_off"):
                        snap()
                        S.faces_on = False
                        notify("Face groups are off. Names are kept until you forget them.")
                        st.rerun()
                elif st.button("Turn on", key="faces_on2", type="primary"):
                    S.faces_on = True
                    notify("Face groups are on.", False)
                    st.rerun()
    if nm:
        with st.container(key="sm_forget"):
            if st.button("Forget names and hidden people", key="faces_forget"):
                snap()
                S.names, S.hidden_people, S.notp = {}, set(), set()
                notify("Names, hidden people and corrections were cleared.")
                st.rerun()
    for pid in sorted(S.hidden_people, key=lambda p: E.PNUM[p]):
        with st.container(key=f"row_hp_{pid}"):
            c1, c2 = st.columns([4, 2])
            with c1:
                md(f'<div class="crow" style="padding:2px 0">{avatar(pid, 44)}<div class="rtitle" style="font-size:14px">{esc(pname(pid))} (hidden)</div></div>')
            with c2:
                with st.container(key=f"sm_hp_{pid}"):
                    if st.button("Show", key=f"hp_{pid}"):
                        snap()
                        S.hidden_people.discard(pid)
                        notify(f"{pname(pid)} is shown again.")
                        st.rerun()

    md('<div class="sect" style="margin-top:16px"><b>AI access by collection</b></div>'
       '<div class="sub" style="margin-top:0">Paused collections disappear from search, People and the timeline. Nothing is deleted.</div>')
    for cat in all_cats():
        off, n, k = cat in S.excluded_cats, cat_total(cat), slug(cat)
        with st.container(key=f"row_{k}"):
            c1, c2 = st.columns([3, 2])
            with c1:
                md(f'<div class="setrow" style="padding:4px 0;border:none"><span class="si {"off" if off else ""}">{svg("eyeoff" if off else "folder", 20)}</span>'
                   f'<div><b>{esc(cat)}</b><small>{n} item{"s" if n != 1 else ""} · {"AI paused" if off else "AI allowed"}</small></div></div>')
            with c2:
                with st.container(key=f"sm_{k}"):
                    if off:
                        if st.button("Allow AI", key=f"on_{k}", type="primary"):
                            snap()
                            S.excluded_cats.discard(cat)
                            notify(f"AI can use “{cat}” again.")
                            st.rerun()
                    elif st.button("Pause AI", key=f"off_{k}"):
                        pause_cat_dialog(cat)
    if "Sensitive" in all_cats():
        md('<div class="sub" style="margin-top:0">“Sensitive” was paused automatically because those photos look private. You decide whether to allow it.</div>')

    stopped = [R[i] for i in sorted(S.excluded_imgs, key=lambda x: int(x[3:]))]
    if stopped:
        md('<div class="sect" style="margin-top:16px"><b>Photos AI can’t use</b></div>')
        for r in stopped:
            thumb_row(r, "si", "Allow AI", allow_image)

    md('<div class="sect" style="margin-top:16px"><b>Recently removed</b></div>')
    gone = [R[i] for i in sorted(S.removed, key=lambda x: int(x[3:]))]
    if gone:
        for r in gone:
            thumb_row(r, "rs", "Restore", restore_image)
    else:
        md('<div class="sub" style="margin-top:0">Nothing removed. Use Remove photo on a photo’s details.</div>')

    md('<div class="sect" style="margin-top:16px"><b>Plain-language promises</b></div>'
       '<div class="card pad glass info"><p><b>Answers.</b> The assistant answers from descriptions and text prepared for each photo. It does not generate facts, and every answer shows the photo it came from and how it was found.</p>'
       '<p><b>Faces.</b> Face groups are prepared in advance for this prototype. Nothing is recognised live. You name people, hide anyone, and can turn the feature off. No biometric template is stored.</p>'
       '<p><b>Sorting.</b> Collections are made by simple rules, not a live image model, and nothing is sent to outside services.</p>'
       '<p><b>Originals.</b> PixelSense never edits, moves, deletes or shares your original photos.</p></div>')

    md('<div class="sect" style="margin-top:16px"><b>Chat history</b></div>')
    if S.searches:
        md(f'<div class="pills">{"".join(pill(s, "gray") for s in S.searches)}</div>')
        with st.container(key="sm_hist"):
            if st.button("Clear history and chat", key="hist_clear"):
                S.searches, S.chat = [], []
                notify("History cleared.", False)
                st.rerun()
    else:
        md('<div class="sub" style="margin-top:0">Nothing yet.</div>')

    md('<div class="sect" style="margin-top:16px"><b>Smart chat (optional)</b></div>')
    if E.llm_available():
        md('<div class="sub" style="margin-top:0">Lets the assistant hold a free conversation using an AI model. It sends your message and the <b>text descriptions</b> of photos the AI may use, never the photos themselves. Off by default.</div>')
        with st.container(key="sm_llm"):
            if S.llm_on:
                if st.button("Turn off", key="llm_off"):
                    S.llm_on = False
                    notify("Smart chat is off.", False)
                    st.rerun()
            elif st.button("Turn on", key="llm_on_btn", type="primary"):
                S.llm_on = True
                notify("Smart chat is on.", False)
                st.rerun()
    else:
        md('<div class="sub" style="margin-top:0">Chat works offline with built-in replies and editing commands. For free conversation, set the ANTHROPIC_API_KEY environment variable, run <b>pip install anthropic</b>, then restart the app.</div>')

    md('<div class="sect" style="margin-top:16px"><b>Researcher tools</b></div>'
       '<div class="sub" style="margin-top:0">Open study mode to run an evaluation session, simulate new photos arriving, or reset everything so the next participant starts fresh.</div>')
    with st.container(key="sm_arrive"):
        if st.button("Simulate 3 new photos arriving", key="arrive", disabled=len(S.arrived) == len(HELD)):
            S.arrived = set(HELD)
            live = [i for i in sorted(HELD) if visible(R[i])]
            cats = sorted({cat_of(R[i]) for i in live})
            notify(f"{len(HELD)} new photos arrived. " + (f"{len(live)} sorted into {', '.join(cats)}." if live else "AI is paused for them."), False)
            st.rerun()
    with st.container(key="sm_study"):
        if st.button("Open study mode", key="open_study"):
            go("study")
    with st.container(key="danger_reset"):
        if st.button("Reset prototype", key="reset"):
            for k in list(S.keys()):
                del S[k]
            st.rerun()


# --------------------------------------------------------------------------- composer + corner menu
def toggle_plus():
    S.plus = not S.plus
    st.rerun()


def plus_new_collection():
    S.plus = False
    new_collection_dialog()


def composer():
    if S.plus:
        with st.container(key="plus_scrim"):
            if st.button("Close", key="plus_scrim_btn"):
                S.plus = False
                st.rerun()
        with st.container(key="plussheet"):
            tappable("pl_new", f'<div class="pl-row pressable"><i>{svg("folder", 18)}</i><div>New collection<small>Name it, optionally fill it from a search</small></div></div>',
                     plus_new_collection, label="New collection")
            tappable("pl_chat", f'<div class="pl-row pressable"><i>{svg("edit", 18)}</i><div>New search<small>Clear this and go back to Home</small></div></div>',
                     new_chat, label="New search")
            tappable("pl_ppl", f'<div class="pl-row pressable"><i>{svg("users", 18)}</i><div>People<small>Open face groups</small></div></div>',
                     go, "people", label="People")
    with st.container(key="composer"):
        c1, c2, c3 = st.columns([1, 6, 1])
        with c1:
            tappable("plus", f'<div class="cbtn pressable">{svg("plus", 22, sw=2.2)}</div>', toggle_plus, label="More actions")
        with c2:
            st.text_input("Ask PixelSense", key="composer_q", placeholder="Ask about your photos…",
                          label_visibility="collapsed", on_change=send)
        with c3:
            tappable("send", f'<div class="cbtn send pressable">{svg("send", 22, "#fff", 2.2)}</div>', send_click, label="Send")


def nav_to(key):
    S.menu, S.about_from = False, None
    if key == "favorites":
        S.hfilter = "Favorites"
        go("photos")
    else:
        if key == "photos" and S.hfilter == "Favorites":
            S.hfilter = "All"
        go(key)


def drawer():
    """Phones: slide-out drawer opened from the corner menu. Computers: the same list is a permanent sidebar (CSS decides)."""
    if S.view in ("welcome", "analysing"):
        return
    if S.menu:
        with st.container(key="scrim"):
            if st.button("Close menu", key="scrim_btn"):
                S.menu = False
                st.rerun()
    cur = {"home": "home", "memory": "home", "cleanup": "cleanup", "chat": "home", "results": "home", "photos": "photos", "people": "people", "person": "people",
           "collections": "collections", "collection": "collections", "settings": "settings"}.get(S.view, "")
    if cur == "photos" and S.hfilter == "Favorites":
        cur = "favorites"
    n_clean = sum(len(v) for v in E.cleanup_groups(visible_rows(), S.kept).values())
    n_att = len(deadline_items())
    items = [("home", "Home", "home", ""), ("photos", "Photos", "image", ""), ("people", "People", "users", ""),
             ("collections", "Collections", "folder", ""), ("cleanup", "Clean up", "trash", f"{n_clean}" if n_clean else ""), ("favorites", "Favorites", "heart", f"{len(S.fav)}" if S.fav else ""),
             ("settings", "Settings", "shield", "")]
    with st.container(key="drawer" if S.menu else "sidebar"):
        md(f'<div class="dr-head"><span class="logo-sm">{svg("sparkle", 18, "#fff", 1, "#fff")}</span>PixelSense</div>')
        for key, label, icon, extra in items:
            on = "on" if cur == key else ""
            tappable(f"dr_{key}", f'<div class="dr-row {on} pressable">{svg(icon, 22)}<span>{label}</span><small>{extra}</small></div>',
                     nav_to, key, label=label)
        md('<div class="dr-note">Everything here is sample data. Your original photos are never changed.</div>')


# --------------------------------------------------------------------------- router
VIEWS = {"study": view_study, "baseline": view_baseline, "edit": view_edit, "home": view_home, "cleanup": view_cleanup, "memory": view_memory, "welcome": view_welcome, "analysing": view_analysing, "chat": view_chat, "photos": view_photos,
         "results": view_results, "people": view_people, "person": view_person, "detail": view_detail,
         "collections": view_collections, "collection": view_collection, "settings": view_settings}
if S.study and S.study.get("running") and S.study["cond"] != "PixelSense":
    S.view = "baseline"                  # the baseline condition is a plain gallery with no assistant and no navigation
with st.container(key=f"v_{S.view}"):
    VIEWS.get(S.view, view_chat)()
if S.study and S.study.get("running"):
    study_bar()

if S.view in ("chat", "results"):      # prompt bar lives on the Ask screen only
    composer()
if S.view != "baseline":
    drawer()

if S.scroll:
    mode, S.scroll = S.scroll, False
    target = "m.scrollHeight" if mode == "bottom" else "0"
    try:
        import streamlit.components.v1 as components
        components.html("<script>setTimeout(function(){try{const d=window.parent.document;"
                        "const m=d.querySelector('[data-testid=\"stMain\"]')||d.querySelector('section.main');"
                        f"m.scrollTo(0,{target});}}catch(e){{}}}},140);</script>", height=0)
    except Exception:
        pass
