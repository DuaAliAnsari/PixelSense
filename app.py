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
import streamlit.components.v1 as components
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

TYPE_FILTERS = ["All", "Photo", "Screenshot", "Receipt", "Bill", "Ticket", "Poster", "Document"]
TILE_COLORS = [("#EEEBFF", "#5B4FD6"), ("#FFE9EC", "#D6455D"), ("#E3F6EC", "#18936A"),
               ("#FFF1D6", "#C27A00"), ("#E1F1FF", "#2A7DD1"), ("#F3E8FF", "#9333EA")]
HOME_CHIPS = {
    "What needs my attention?": "What needs my attention?",
    "HCI deadline": "When is my HCI assignment due?",
    "Electricity bill": "How much is the electricity bill?",
    "Me in pink": "Fetch me that photo in which I am wearing pink",
    "Photos of Sara": "Fetch me all photos of Sara",
    "Event posters": "Fetch me all event posters",
    "Tech Fest poster": "Get me the photo of the poster of the Tech Fest event",
    "Who’s at dinner?": "Who is in the dinner photo?",
    "Make a collection": "Create a collection called Eid with family dinner photos",
    "Edit by chat": "Make the wedding photos black and white and save to Eid",
    "My receipts": "Show my receipts",
}
ATTENTION_CHIP = "What needs my attention?"
ATTENTION_RE = re.compile(r"needs?\s+(my\s+)?attention|what('s| is| are)\s+(due|overdue|coming up)|upcoming|deadlines|overdue|anything due", re.I)
UNDO_KEYS = ["override", "extra_cats", "excluded_cats", "excluded_imgs", "removed", "names", "hidden_people", "notp", "fav", "kept", "copies", "done", "manual", "deleted_cats"]

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
        override={}, extra_cats=[], deleted_cats=set(), excluded_cats={"Sensitive"}, excluded_imgs=set(), removed=set(), arrived=set(),
        names=dict(E.PRESET_NAMES), hidden_people=set(), notp=set(), faces_on=None, fav=set(), kept=set(), cur_mem=None, copies=[], copy_seq=0, llm_on=False,
        bl_view="photos", bl_albums={}, bl_back="photos", history=[], searches=[], done=set(), study=None, opened=set(), manual=[], manual_seq=0, analytics_on=False, events=[], snack=None, scroll=False, menu=False, plus=False, chat=[], res=None,
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


@st.cache_data(show_spinner=False)
def full_uri(file, side=1600):
    """The whole picture (never cropped), shrunk so its longest side is `side` px. Used where a photo must be seen in full."""
    im = ImageOps.exif_transpose(Image.open(ROOT / file)).convert("RGB")
    im.thumbnail((side, side), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86)
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
    gone = S.get("deleted_cats", set())
    return [c for c in base + extra + sens if c not in gone]


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
    S.view, S.snack, S.menu, S.plus, S.scroll = view, None, False, False, True
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
    study_tick("searches")
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
    S.view, S.snack, S.menu, S.plus, S.scroll = "home", None, False, False, True


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
    """The one header for every screen below a tab: a back arrow and a title, always in the same place."""
    with st.container(key=f"topbar_{key}"):
        c1, c2 = st.columns([1, 8])
        with c1:
            if st.button("←", key=f"back_{key}", help="Back"):
                go(back_view if back_view else "home")
        with c2:
            md(f'<div class="tb-title">{esc(title)}</div>')


USER_NAME = "Ayesha Khan"   # dummy account name shown in the Home greeting; change to any name
USER_PIC = "images/selfie_closeup.jpg"   # fallback account picture (used only if people.csv has no "me")


def me_pic_uri():
    """The account picture is the face of the person marked is_me in people.csv (the same face People calls "Me")."""
    ids = E.PERSON_IMAGES.get(E.ME, []) if E.ME else []
    if not ids:
        return img_uri(USER_PIC, 96, 96)
    best = max(ids, key=lambda i: E.FACE_OF[(i, E.ME)][2] * E.FACE_OF[(i, E.ME)][3])
    x, y, w, h = E.FACE_OF[(best, E.ME)]
    return face_uri(R[best].file, x, y, w, h, size=96)


def greeting():
    h = datetime.now().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"


def appbar(title="PixelSense", chat_btn=False, greet=False):
    with st.container(key="appbar"):
        c1, c2 = st.columns([6, 1])
        with c1:
            if greet:
                md(f'<div class="ab-title two"><small>{greeting()},</small><b>{esc(USER_NAME)}</b></div>')
            else:
                md(f'<div class="ab-title">{esc(title)}</div>')
        with c2:
            if greet:
                md(f'<img class="me" src="{me_pic_uri()}" alt="{esc(USER_NAME)} account picture">')


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
    S.deleted_cats.discard(name)
    if name not in all_cats():
        S.extra_cats.append(name)
    for i in ids:
        if AUTO[i][0] == name:
            S.override.pop(i, None)
        else:
            S.override[i] = name


@st.dialog("New collection")
def new_collection_dialog(default="", ids=None):
    name = st.text_input("Collection name", value=default, placeholder="e.g. Semester 7, Eid 2026", key="nc_name")
    if ids:
        sub = ""
        st.caption(f"The {len(ids)} photos from your search will go into it. Undo is always available.")
    else:
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
            found = list(ids) if ids else (E.answer_find(make_ctx(), sub, allow_count=False).ids if sub.strip() else [])
            create_collection(n, [i for i in found if i in R and visible(R[i])])
            notify(f"Collection “{n}” created" + (f" with {len(found)} photo{'s' if len(found) != 1 else ''}." if found else "."))
            S.cur_coll = n
            S.chat, S.query = [], ""
            S.view = "collection"        # land inside the new collection
            st.rerun()


# ---- photo picker: every photo can be opened big and swiped through before it is chosen (PixelSense and Gallery share it) ----------
def _pk_open(pk, i):
    S[f"{pk}_pv"] = i
    st.rerun(scope="fragment")


def _pk_close(pk):
    S[f"{pk}_pv"] = None


def _pk_toggle(pk, i):
    S[f"{pk}_sel"] = set(S.get(f"{pk}_sel", set())) ^ {i}


def _pk_check(pk, i):
    cur = set(S.get(f"{pk}_sel", set()))
    if S.get(f"{pk}_ck_{i}"):
        cur.add(i)
    else:
        cur.discard(i)
    S[f"{pk}_sel"] = cur


def _pk_step(pk, ids, d):
    cur = S.get(f"{pk}_pv")
    if cur in ids:
        k = ids.index(cur) + d
        if 0 <= k < len(ids):
            S[f"{pk}_pv"] = ids[k]


def photo_picker(pk, rows, w=200, h=200):
    """Choose photos for a collection. Grid: tap a photo to see it big, tick the square to choose it.
    Big view: swipe left / right (or use Previous / Next, or the arrow keys) to go through ALL the photos, and add the ones you want.
    Returns the chosen ids in library order. Must be called inside a dialog (it reruns only the dialog)."""
    ids = [r.id for r in rows]
    by_id = {r.id: r for r in rows}
    S[f"{pk}_sel"] = set(S.get(f"{pk}_sel", set())) & set(ids)
    cur = S.get(f"{pk}_pv")
    if cur not in by_id:
        cur = S[f"{pk}_pv"] = None
    ev = _SWIPE(key=f"{pk}_sw", default=None)
    if isinstance(ev, dict) and ev.get("n") != S.get(f"{pk}_swn"):
        S[f"{pk}_swn"] = ev.get("n")
        if cur:
            k = ids.index(cur) + (1 if ev.get("dir") == "next" else -1)
            if 0 <= k < len(ids):
                cur = S[f"{pk}_pv"] = ids[k]
    sel = S[f"{pk}_sel"]
    if cur:
        r, k = by_id[cur], ids.index(cur)
        md(f'<div class="pk-prev" data-swipe-zone><img src="{full_uri(r.file, 1100)}" alt="Photo {k + 1} of {len(ids)}"></div>'
           f'<div class="pk-count">Photo {k + 1} of {len(ids)} · <b>{len(sel)}</b> chosen · swipe left or right for the next photo</div>')
        with st.container(key=f"pkctl_{pk}"):
            c = st.columns([1, 1.6, 1])
            with c[0]:
                st.button("‹ Back", key=f"{pk}_prev", on_click=_pk_step, args=(pk, ids, -1), disabled=k == 0, use_container_width=True)
            with c[1]:
                st.button("✓ Chosen (tap to undo)" if cur in sel else "Choose this photo", key=f"{pk}_pick", type="secondary" if cur in sel else "primary",
                          on_click=_pk_toggle, args=(pk, cur), use_container_width=True)
            with c[2]:
                st.button("Next ›", key=f"{pk}_next", on_click=_pk_step, args=(pk, ids, 1), disabled=k == len(ids) - 1, use_container_width=True)
        st.button("← All photos", key=f"{pk}_all", on_click=_pk_close, args=(pk,))
        return [i for i in ids if i in sel]
    md(f'<div class="pk-count" style="margin-top:0">Tap a photo to see it big and swipe through them all. Tick the square to choose it. <b>{len(sel)}</b> chosen.</div>')
    with st.container(key=f"pkgrid_{pk}"):
        for k in range(0, len(rows), 4):
            cols = st.columns(4)
            for c, r in zip(cols, rows[k:k + 4]):
                with c:
                    with st.container(key=f"selcell_pk_{pk}_{r.id}"):
                        tappable(f"{pk}_o_{r.id}", f'<div class="tile pressable"><img src="{img_uri(r.file, w, h)}" alt="Photo"></div>', _pk_open, pk, r.id, label="See photo bigger")
                        S[f"{pk}_ck_{r.id}"] = r.id in sel
                        st.checkbox("Choose photo", key=f"{pk}_ck_{r.id}", label_visibility="collapsed", on_change=_pk_check, args=(pk, r.id))
    return [i for i in ids if i in sel]


def rename_collection(old, new):
    """Rename = the same photos under a new name (undoable). Photos AI sorted into the old name are moved by you into the new one."""
    snap()
    S.deleted_cats.discard(new)
    if old in S.extra_cats:
        S.extra_cats[S.extra_cats.index(old)] = new
    else:
        S.extra_cats.append(new)
        S.deleted_cats.add(old)
    for r in df.itertuples():
        if cat_of(r) == old:
            if AUTO[r.id][0] == new:
                S.override.pop(r.id, None)
            else:
                S.override[r.id] = new


@st.dialog("Rename collection")
def rename_collection_dialog(old):
    new = st.text_input("New name", value=old, key=f"rc_{slug(old)}")
    if st.button("Save name", type="primary", key=f"rc_ok_{slug(old)}"):
        n = new.strip()
        if not n:
            st.warning("The name cannot be empty.")
        elif n == old:
            st.rerun()
        elif n in all_cats():
            st.warning("You already have a collection with that name.")
        elif n in S.excluded_cats:
            st.warning("AI is paused for that collection name.")
        else:
            rename_collection(old, n)
            S.cur_coll = n
            notify(f"Renamed to “{n}”.")
            st.rerun()


@st.dialog("Add photos", width="large")
def add_photos_dialog(name):
    """Add photos to a collection from inside it (no need to go back and move photos one by one)."""
    rows = [r for r in visible_rows() if cat_of(r) != name]
    pk = f"ap_{slug(name)}"
    st.caption("They move out of the collection AI put them in; Undo is always available.")
    picked = photo_picker(pk, rows, 200, 150)
    if st.button(f"Add {len(picked)} photo{'s' if len(picked) != 1 else ''}", type="primary", key="ap_ok", disabled=not picked):
        create_collection(name, picked)
        for k in [k for k in S.keys() if str(k).startswith(f"{pk}_")]:
            S.pop(k, None)
        notify(f"Added {len(picked)} to “{name}”.")
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


@st.dialog("Delete this photo?")
def remove_dialog(i):
    r = R[i]
    md(thumb_head(r, "") + '<div class="info"><p>It moves to <b>Trash</b>, where you can bring it back.</p>'
       '<p><b>Your original file is not touched.</b></p></div>')
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel", key=f"rm_cancel_{i}"):
            st.rerun()
    with c2:
        if st.button("Delete", type="primary", key=f"rm_ok_{i}"):
            snap()
            S.removed.add(i)
            notify("Photo deleted. Find it in Trash.")
            S.view = S.back if S.back in ("home", "photos", "collection", "collections", "person", "people", "cleanup", "memory", "attention") else "home"
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


# ---- select & delete (Photos page and every collection) ---------------------------------------------
def sel_key(scope, i):
    return f"sel_{scope}_{i}"


def untick_later(key):
    """A tick square can only be reset before it is drawn, so the key is noted here and the router clears it at the start of the next run
    (just removing it from the session left the square ticked on screen)."""
    S.setdefault("_untick", []).append(key)


def tick_all(scope, ids):
    for i in ids:
        S[sel_key(scope, i)] = True


def untick_all(scope, ids):
    for i in ids:
        S[sel_key(scope, i)] = False


def select_grid(rows, prefix, scope, n=6, opener=None, extra=()):
    """Like image_grid, but every photo has a tick square in its top-left corner (state lives in the checkbox itself)."""
    opener = opener or open_image
    with st.container(key=f"grid{n}_{prefix}"):
        for k in range(0, len(rows), n):
            cols = st.columns(n)
            for c, r in zip(cols, rows[k:k + n]):
                with c:
                    with st.container(key=f"selcell_{scope}_{r.id}"):
                        tappable(f"{prefix}_{r.id}", tile_html(r), opener, r.id, *extra, label=f"Open {r.description}")
                        st.checkbox(f"Select {r.description}", key=sel_key(scope, r.id), label_visibility="collapsed")


def selection_bar(scope, rows, where, mode="library", all_ids=None):
    """The bar above the photos: Delete all ticks every square; Delete selected asks for confirmation.
    Buttons sit at the right end (in line with the 'N photos' label), Clear to the left of Delete all.
    mode "library" (Photos, collections): Delete selected + Move to.  mode "cleanup": Delete selected + Remove from Cleanup bin."""
    ids = [r.id for r in rows]
    every = list(all_ids) if all_ids is not None else ids       # what "Delete all" removes (search results also count the answer cards)
    picked = [i for i in ids if S.get(sel_key(scope, i))]
    second = ("selbin", None) if mode == "cleanup" else ("selmove", None)
    show = ([("seldel", None), second, ("selclear", None)] if picked else []) + [("delall", None)]
    with st.container(key=f"selbar_{scope}"):
        cols = st.columns([1] + [0.01] * len(show))
        with cols[0]:
            md(f'<div class="selinfo">{f"<b>{len(picked)}</b> of {len(ids)} selected" if picked else ("Tick a square to choose photos" if ids else f"{len(every)} photos found")}</div>')
        for col, (kind, _) in zip(cols[1:], show):
            with col:
                if kind == "seldel":
                    with st.container(key=f"danger_seldel_{scope}"):
                        if st.button(f"Delete selected ({len(picked)})", key=f"seldel_{scope}"):
                            delete_photos_dialog(picked, scope, len(picked) == len(ids), where)
                elif kind == "selmove":
                    with st.container(key=f"danger_selmove_{scope}"):
                        if st.button(f"Move to ({len(picked)})", key=f"selmove_{scope}"):
                            move_many_dialog(picked, scope)
                elif kind == "selbin":
                    with st.container(key=f"danger_selbin_{scope}"):
                        if st.button(f"Keep selected ({len(picked)})", key=f"selbin_{scope}"):
                            bin_out(picked, scope)
                elif kind == "selclear":
                    st.button("Clear", key=f"selclear_{scope}", on_click=untick_all, args=(scope, ids))
                else:
                    if st.button("Delete all", key=f"delall_{scope}", icon=":material/delete:", disabled=not every):
                        delete_photos_dialog(every, scope, True, where)


def bin_out(ids, scope):
    """Cleanup: take the ticked photos out of the Cleanup bin (same as Keep: they stay in the library and are not suggested again)."""
    n = len(ids)
    snap()
    S.kept.update(ids)
    for i in ids:
        untick_later(sel_key(scope, i))
    notify(f"Kept {n} photo{'s' if n != 1 else ''}. I will not suggest {'it' if n == 1 else 'them'} again.")
    st.rerun()


@st.dialog("Move to another collection")
def move_many_dialog(ids, scope):
    n = len(ids)
    s = "s" if n != 1 else ""
    thumbs = "".join(f'<img src="{img_uri(R[i].file, 96, 72)}" alt="" style="width:56px;height:42px;border-radius:8px;object-fit:cover">' for i in ids[:8])
    more = f'<span style="align-self:center;font-size:12.5px;color:#6B6F8C">+{n - 8} more</span>' if n > 8 else ""
    md(f'<div class="info"><p><b>Move {n} photo{s}</b></p><div style="display:flex;gap:6px;flex-wrap:wrap">{thumbs}{more}</div></div>')
    opts = [c for c in all_cats() if c not in S.excluded_cats]
    choice = st.radio("Collection", opts, index=None, key=f"mvm_{scope}")
    new = st.text_input("Or create a new collection", placeholder="e.g. Semester 7", key=f"nc_new_mvm_{scope}")
    if st.button(f"Move {n} photo{s}", type="primary", key=f"mvm_save_{scope}"):
        target = new.strip() or choice
        if not target:
            st.warning("Pick a collection or type a new name.")
            return
        if target in S.excluded_cats:
            st.warning("AI is paused for that collection. Allow it in Settings first.")
            return
        snap()
        if target not in all_cats():
            S.extra_cats.append(target)
        for i in ids:
            if target == AUTO[i][0]:
                S.override.pop(i, None)
            else:
                S.override[i] = target
            untick_later(sel_key(scope, i))
        notify(f"Moved {n} photo{s} to “{target}”.")
        st.rerun()


@st.dialog("Delete photos?")
def delete_photos_dialog(ids, scope, everything, where):
    n = len(ids)
    s = "s" if n != 1 else ""
    head = f"Delete all {n} photo{s} in {esc(where)}?" if everything else f"Delete the {n} selected photo{s}?"
    thumbs = "".join(f'<img src="{img_uri(R[i].file, 96, 72)}" alt="" style="width:56px;height:42px;border-radius:8px;object-fit:cover">' for i in ids[:8])
    more = f'<span style="align-self:center;font-size:12.5px;color:#6B6F8C">+{n - 8} more</span>' if n > 8 else ""
    md(f'<div class="info"><p><b>{head}</b></p><div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px">{thumbs}{more}</div>'
       '<p>They leave your library, search, People and collections.</p>'
       '<p>You can undo right after, or bring them back from Trash.</p></div>')
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel", key=f"dp_cancel_{scope}"):
            st.rerun()
    with c2:
        if st.button(f"Delete {n} photo{s}", type="primary", key=f"dp_ok_{scope}"):
            snap()
            S.removed.update(ids)
            for i in ids:
                untick_later(sel_key(scope, i))
            notify(f"{n} photo{s} deleted.")
            st.rerun()


@st.dialog("Delete this collection?")
def delete_collection_dialog(name):
    items = coll_items(name)
    n = len(items)
    mine = name in S.extra_cats
    back = " They return to the collection AI sorted them into." if mine else ""
    md(f'<div class="info"><p><b>“{esc(name)}”</b> has {n} photo{"s" if n != 1 else ""}.</p>'
       f'<p>The collection will be deleted. <b>By default its photos stay</b> in Photos.{back}</p>'
       '<p>You can undo right after.</p></div>')
    also = st.checkbox(f"Also delete the {n} photo{'s' if n != 1 else ''} inside it", key=f"dc_also_{slug(name)}", disabled=not n)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel", key=f"dc_cancel_{slug(name)}"):
            st.rerun()
    with c2:
        if st.button("Delete collection", type="primary", key=f"dc_ok_{slug(name)}"):
            snap()
            if mine:
                S.extra_cats.remove(name)
                S.override = {k: v for k, v in S.override.items() if v != name}
            else:
                S.deleted_cats.add(name)
            if also:
                S.removed.update(items)
            for i in items:
                untick_later(sel_key(f"c_{slug(name)}", i))
            S.cur_coll = None
            notify(f"Collection “{name}” deleted" + (f" with its {n} photo{'s' if n != 1 else ''}." if also else ". Its photos are still in Photos."))
            S.view = "collections"
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
            if pid in E.PRESET_NAMES:      # the account holder's own group is always called "Me" unless renamed
                S.names[pid] = E.PRESET_NAMES[pid]
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
    # one static screen on a phone and on a laptop: nothing scrolls, and every size is relative to the window height
    md("<style>html,body,.stApp,[data-testid='stAppViewContainer'],[data-testid='stMain'],section.main{overflow:hidden!important;height:100dvh}"
       "[data-testid='stMainBlockContainer']{padding:12px!important;height:100dvh;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center}"
       "[data-testid='stMainBlockContainer']>[data-testid='stVerticalBlock']{flex:0 1 auto}</style>")
    with st.container(key="stack_wel"):
        left, right = st.columns([1, 1])
        with left:
            md(f'''<div class="wel-brand"><span class="wel-logo2">{svg("sparkle", 22, "#fff", 1.2, "#fff")}</span>PixelSense</div>
              <div class="wel-h">Find any photo in seconds.</div>
              <div class="wel-sub">Search your library by what you remember, keep photos tidy in collections and clear out clutter, with full control over what gets deleted.</div>
              <div class="wel-pills"><span>Search</span><span>Collections</span><span>Clean up</span><span>Trash</span></div>
              <div class="mos mos-m">
                <div class="m a"><img src="{t("images/images (1).jpg", 300, 180)}" alt=""></div>
                <div class="m b"><img src="{t("images/images.jpg", 150, 190)}" alt=""></div>
                <div class="m c"><img src="{t("images/photo1.jpg", 150, 90)}" alt=""></div>
                <div class="m d"><img src="{t("images/images (3).jpg", 150, 90)}" alt=""></div></div>''')
            with st.container(key="wel_start"):
                if st.button("Get started", type="primary", key="start"):
                    go("analysing")
            md('<div class="wel-note">HCI prototype · sample photos only · no tracking, no cookies</div>')
        with right:
            md(f'''<div class="mos mos-d">
              <div class="m a"><img src="{t("images/images (1).jpg", 600, 360)}" alt=""></div>
              <div class="m b"><img src="{t("images/images.jpg", 300, 380)}" alt=""></div>
              <div class="m c"><img src="{t("images/photo1.jpg", 300, 180)}" alt=""></div>
              <div class="m d"><img src="{t("images/images (3).jpg", 300, 180)}" alt=""></div></div>''')


def view_analysing():
    steps = ["Photos", "Screenshots", "Receipts & bills", "Tickets & documents"]
    md("<style>.st-key-v_analysing [data-stale='true'],.st-key-v_analysing [data-testid='stElementContainer'].stale{display:none!important}</style>")
    ph = st.empty()
    for _ in range(40):
        st.empty()                       # overwrite what the Welcome screen left behind, so it does not show (faded) while loading

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
    S.view = "home"          # searching and its results are on Home
    st.rerun()


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
            md(f'<div class="sect sect-col"><b>{esc(title)}</b>' + (f'<span class="ssub">{esc(sub)}</span>' if sub else "") + '</div>')
        with c2:
            with st.container(key=f"link_{key}"):
                if st.button(label, key=f"link_btn_{key}"):
                    go(target)
    else:
        md(f'<div class="sect sect-col"><b>{esc(title)}</b>' + (f'<span class="ssub">{esc(sub)}</span>' if sub else "") + '</div>')


def open_memory(iso):
    S.cur_mem = iso
    go("memory")


def cover_card(img_file, title, sub):
    return (f'<div class="cov pressable"><img src="{img_uri(img_file, 480, 300)}" alt="">'
            f'<div class="cb"><div class="rtitle">{esc(title)}</div><div class="ccount">{esc(sub)}</div></div></div>')


def coll_tile(img_file, title, n):
    """Square cover with the collection's name under it (three per row on a phone)."""
    return (f'<div class="ctilesq pressable"><img src="{img_uri(img_file, 320, 320)}" alt="">'
            f'<div class="cn">{esc(title)}</div><div class="cc">{n} item{"s" if n != 1 else ""}</div></div>')


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
    q = (S.get("home_q") or "").strip()
    S["home_q"] = ""
    ask(q)


def home_clear():
    S.chat, S.query = [], ""
    for k in [k for k in S.keys() if str(k).startswith("sel_hres")]:
        del S[k]
    st.rerun()


def save_results_as_collection(rp):
    if rp.person:
        name = f"{pname(rp.person)} photos"
    else:
        words = [t for t, o in E.search_terms(rp.query).items() if o is None and t not in E.TYPE_WORDS][:3]
        name = " ".join(w.title() for w in words) or "My collection"
    new_collection_dialog(name, list(rp.ids))


def home_results():
    """Search results under the search bar: the answer, the photos (tick, delete, save as a collection) and how they were found."""
    users = [m for m in S.chat if m["role"] == "user"]
    ais = [m for m in S.chat if m["role"] == "ai"]
    if not users or not ais:
        return
    rp, q = ais[-1]["reply"], users[-1]["text"]
    hc = st.columns([5, 1.6])
    with hc[0]:
        md(f'<div class="res-head">Results for <b>“{esc(q)}”</b></div>')
    with hc[1]:
        with st.container(key="sm_clear"):
            if st.button("Clear", key="home_clear_btn", icon=":material/close:"):
                home_clear()
    snack_ui()
    md(f'<div class="ans"><div class="av-ai">{svg("sparkle", 18, "#fff", 1, "#fff")}</div><div class="ans-t">{fmt(rp.text)}</div></div>')
    rows = [R[i] for i in rp.ids if i in R and visible(R[i])]
    terms = list(E.search_terms(rp.query))
    shown_src = set()
    for sid, snip in rp.sources:
        if sid in R and visible(R[sid]):
            r = R[sid]
            shown_src.add(sid)
            tappable(f"hs_src_{sid}",
                     f'<div class="card src pressable"><img class="rthumb" src="{img_uri(r.file, 240, 180)}" alt="">'
                     f'<div class="rbody"><div class="rtitle">{esc(r.description)}</div><div class="rsnip">{src_line(r, snip, terms)}</div></div>'
                     f'<div class="chev">{svg("chev", 20)}</div></div>', open_from_msg, sid, rp.query, label=f"Open {r.description}")
    grid = [r for r in rows if r.id not in shown_src]
    if len(rows) > 1:
        selection_bar("hres", grid, "Search results", mode="library", all_ids=[r.id for r in rows])
    if grid:
        select_grid(grid, "hres", "hres", n=6, opener=open_from_msg, extra=(rp.query,))
    if len(rows) >= 2 and rp.kind in ("results", "people"):
        with st.container(key="sm_savecoll"):
            if st.button("Save these as a collection", key="hres_save", icon=":material/create_new_folder:"):
                save_results_as_collection(rp)
    extra_chips = [c for c in rp.chips if c != "Save these as a collection"]
    if extra_chips:
        chips("hres_chips", extra_chips, None, lambda lab: chat_chip(0, rp, lab))
    if rp.steps:
        items = "".join(f"<li>{esc(x)}</li>" for x in rp.steps)
        md(f'<details class="how"><summary>How I found this</summary><ol>{items}</ol></details>')
    if getattr(rp, "executed", False) and S.history:
        with st.container(key="plain_mundo"):
            if st.button("↶ Undo", key="hres_undo"):
                undo()
                rp.executed = False
                rp.text += " (Undone.)"
                S.snack = None
                st.rerun()


def coming_up_home():
    live = [d for d in deadline_items() if d["row"] is not None]
    hc = st.columns([4, 2])
    with hc[0]:
        md(f'<div class="sect" style="margin-top:6px"><b>Coming up</b><span style="margin-left:10px">{len(live)} from your photos</span></div>' if live
           else '<div class="sect" style="margin-top:6px"><b>Coming up</b></div>')
    with hc[1]:
        if len(live) > 3:
            with st.container(key="link_hcu"):
                if st.button("See all", key="link_btn_hcu"):
                    go("attention")
    if not live:
        md('<div class="card pad calm"><b>You’re clear.</b><small>Nothing due in your photos right now.</small></div>')
        return
    for d in live[:3]:
        attention_card(d)


def view_home():
    appbar("Home", greet=True)
    with st.container(key="homesearch"):
        c1, c2 = st.columns([8, 1.3])
        with c1:
            st.text_input("Search your library", key="home_q", placeholder="Search or ask, e.g. “gas bill October”", label_visibility="collapsed", on_change=home_send)
        with c2:
            with st.container(key="homesearch_btn"):
                st.button("Search", key="home_search_btn", icon=":material/search:", on_click=home_send)
    if S.chat:
        home_results()
    else:
        snack_ui()
        coming_up_home()
    if not S.study:
        tappable("home_study", f'<div class="banner pressable"><div class="bic">{svg("sparkle", 26, "#C27A00")}</div><div style="flex:1"><b>Take part in our usability study</b>'
                               f'<small>About 15 minutes. You will try two versions of a photo app.</small></div>{svg("chev", 22, "#C27A00")}</div>',
                 go, "study", label="Start the usability study")


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
    selection_bar("cleanup", items, "Clean up", mode="cleanup")
    select_grid(items, "cu_all", "cleanup")
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
    urgent = " urgent" if d["urgency"] != "later" else ""
    extra = f" · Rs {d['money']:,}" if d["money"] else ""
    thumb = f'<img class="att-thumb" src="{img_uri(r.file, 160, 120)}" alt="">' if r is not None else ""
    tappable(f"att_{i}",
             f'<div class="card upc pressable"><div class="dbadge{urgent}"><b>{d["date"].day}</b><span>{d["date"].strftime("%b").upper()}</span></div>{thumb}'
             f'<div style="flex:1;min-width:0"><div class="rtitle">{esc(d["title"])}</div>'
             f'<div class="ccount">{d["kind"]} {E.when_words(d["days"])}{extra}</div></div><div class="chev">{svg("chev", 22)}</div></div>',
             open_image, i, label=f"Open {d['title']}")


def attention_ui():
    live = [d for d in deadline_items() if d["row"] is not None]
    if not live:
        empty_state("check", "You’re clear", "Nothing due. Every bill and deadline found in your photos is ticked off.")
        return
    for key in ("overdue", "soon", "later"):
        grp = [d for d in live if d["urgency"] == key]
        if grp:
            md(f'<div class="sect"><b>{URG[key][0]}</b><span>{len(grp)} item{"s" if len(grp) != 1 else ""}</span></div>')
            for d in grp:
                attention_card(d)
    md('<div class="sub" style="margin-top:14px">Dates and amounts are read from your photos. Tap one to open the photo.</div>')


def view_attention():
    topbar("Coming up", "home", "att")
    snack_ui()
    attention_ui()


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


def install_as_app():
    """Make the page behave like an installed phone app: full-screen viewport, theme colour, home-screen icon and manifest."""
    components.html("""<script>
      var d = window.parent.document, h = d.head;
      function meta(n, c) { var m = d.querySelector('meta[name="' + n + '"]') || d.createElement("meta"); m.name = n; m.content = c; h.appendChild(m); }
      meta("viewport", "width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no");
      meta("theme-color", "#4F46C6"); meta("mobile-web-app-capable", "yes"); meta("apple-mobile-web-app-capable", "yes");
      meta("apple-mobile-web-app-title", "PixelSense"); meta("apple-mobile-web-app-status-bar-style", "default");
      if (!d.querySelector('link[rel="manifest"]')) {
        var l = d.createElement("link"); l.rel = "manifest"; l.href = "/app/static/manifest.json"; h.appendChild(l);
        var a = d.createElement("link"); a.rel = "apple-touch-icon"; a.href = "/app/static/icon-192.png"; h.appendChild(a);
      }
    </script>""", height=0)


# ---- study mode (self-guided: the participant does both versions, in counterbalanced order) ------------------------------
def study_tasks():
    sd = S.study
    return ST.tasks_for(sd["cond"], sd["sets"][sd["cond"]])


def study_check(t):
    """True once the app's own state shows the task is done. Checked on every screen update while a task runs."""
    sd, k, tg = S.study, t["kind"], t["targets"]
    new_copies = S.copies[sd.get("copies0", 0):]
    if k == "open":
        return bool(tg & (S.opened - sd.get("opened0", set())))
    if k == "fav":
        return tg <= S.fav
    if k == "clean":
        gone = S.removed - sd.get("removed0", set())
        return tg <= gone
    if k == "edit":      # a black-and-white AND cropped copy of the photo
        return any(c["src"] in tg and (c["ops"].get("aspect", "Original") != "Original" or any(c["ops"].get("crop") or []))
                   and (c["ops"].get("filter", "None") == "B&W" or c["ops"].get("saturation", 0) <= -80) for c in new_copies)
    if k == "collect":   # a collection / album with this name that holds every target photo
        name = t.get("name", "")
        if sd["cond"] == "PixelSense":
            return name in all_cats() and tg <= set(coll_items(name))
        return any(n.strip().lower() == name.lower() and tg <= set(v) for n, v in S.bl_albums.items())
    if k == "restore":      # a photo was deleted at some point and is back now
        sd.setdefault("gone", set()).update(tg & S.removed)
        return any(i not in S.removed for i in sd["gone"])
    return False


def study_wrong_actions(t):
    """Photos opened, marked or removed that were not what the task asked for."""
    sd, k, tg = S.study, t["kind"], t["targets"]
    if k == "open":
        return len((S.opened - sd.get("opened0", set())) - tg)
    if k == "fav":
        return len((S.fav - sd.get("fav0", set())) - tg)
    if k == "clean":
        return len((S.removed - sd.get("removed0", set())) - tg)
    return ""


def study_end(gave_up):
    """The task is over: stop the clock and ask the one ease question."""
    sd = S.study
    t = study_tasks()[sd["i"]]
    sd.update(running=False, secs=round(time.time() - sd["t0"], 1), outcome="gave up" if gave_up else "finished",
              success="no" if gave_up else "yes", wrong=study_wrong_actions(t), step="seq")
    S.view = "study"
    S.scroll = True
    st.rerun()


def study_autocheck():
    sd = S.study
    if sd and sd.get("running") and study_check(study_tasks()[sd["i"]]):
        study_end(False)


def study_bar():
    sd = S.study
    t = study_tasks()[sd["i"]]
    # the bar is a fixed panel 68px tall; every screen (and the sidebars) starts below it, so nothing is ever hidden behind it
    md("<style>:root{--sbh:68px;--sbo:68px}[data-testid='stMainBlockContainer']{padding-top:calc(var(--sbh) + 14px)!important}"
       ".st-key-sidebar,.st-key-drawer{top:var(--sbh)!important}"
       ".st-key-v_chat .st-key-appbar,.st-key-v_results .st-key-appbar,"
       ".st-key-v_chat [data-testid='stLayoutWrapper']:has(> .st-key-appbar),.st-key-v_results [data-testid='stLayoutWrapper']:has(> .st-key-appbar){top:var(--sbh)!important}</style>")
    with st.container(key="studybar"):
        md(f'<div class="sb-t"><span>Task {sd["i"] + 1} of {len(study_tasks())}</span><b>{esc(t["text"])}</b></div>')
        if st.button("Give up", key="sb_giveup"):
            study_end(True)


def scale_radio(label, opts, key, low="", high="", mid=""):
    """A 1-to-5 / 1-to-7 row: circles in one line with the number under each, and the end words under them.
    Everything sits in one keyed box, which is a white card on a phone."""
    with st.container(key=f"scale_{key}"):
        v = st.radio(label, opts, index=None, horizontal=True, key=key)
        if low or high:
            scale_ends(low, high, mid)
        return v


def sus_text(q):
    """Item text; some versions of study.py store (text, is_positive) pairs."""
    return q[0] if isinstance(q, (tuple, list)) else q


TLX_FALLBACK = [("mental", "Mental demand", "How mentally demanding was it? (0 = very low, 100 = very high)"),
                ("physical", "Physical demand", "How physically demanding was it? (0 = very low, 100 = very high)"),
                ("temporal", "Hurry", "How hurried or rushed was the pace? (0 = very low, 100 = very high)"),
                ("performance", "Performance", "How unsuccessful were you? (0 = perfect, 100 = failure)"),
                ("effort", "Effort", "How hard did you have to work? (0 = very low, 100 = very high)"),
                ("frustration", "Frustration", "How stressed or frustrated did you feel? (0 = very low, 100 = very high)")]


UEQ_FALLBACK = [("obstructive", "supportive"), ("complicated", "easy"), ("inefficient", "efficient"), ("confusing", "clear"),
                ("boring", "exciting"), ("not interesting", "interesting"), ("conventional", "inventive"), ("usual", "leading edge")]
TRUST_FALLBACK = ["I felt in control of what the app did with my photos.", "I understood how the app found its results.",
                  "I would trust this app with my own photo library."]


def ueq_items():
    return list(getattr(ST, "UEQ_S", None) or UEQ_FALLBACK)


def trust_items():
    return list(getattr(ST, "TRUST_ITEMS", None) or TRUST_FALLBACK)


def tlx_items():
    for name in ("TLX_ITEMS", "TLX_QUESTIONS", "TLX"):
        v = getattr(ST, name, None)
        if v and all(isinstance(x, (tuple, list)) and len(x) == 3 for x in v):
            return list(v)
    return TLX_FALLBACK                  # study.py without the workload list: use the standard six


def scale_ends(low, high, mid=""):
    """Words under the two ends (and the middle) of a row of numbered circles."""
    m = f"<span>{esc(mid)}</span>" if mid else ""
    md(f'<div class="scale-ends"><span>{esc(low)}</span>{m}<span>{esc(high)}</span></div>')


def study_seq():
    sd = S.study
    t = study_tasks()[sd["i"]]
    md(f'<div class="card pad glass info"><p><b>{"Task complete." if sd["outcome"] == "finished" else "No problem, thanks for trying."}</b></p></div>')
    with st.container(key="seqbox"):
        md('<div class="seq-q">How easy or difficult was that task?</div><div class="seq-hint">Tap one. <b>1 is very difficult</b>, <b>7 is very easy</b>.</div>')
        seq = st.radio("How easy or difficult was that task?", [1, 2, 3, 4, 5, 6, 7], index=None, key="fd_rate",
                       format_func=lambda v: ST.SEQ_LABELS[v], label_visibility="collapsed")
    with st.container(key="sm_stb"):
        if st.button("Next", type="primary", key="fd_save", disabled=seq is None):
            ST.log_task(participant=sd["pid"], order=" > ".join(sd["order"]), condition=sd["cond"], task_id=t["id"], task_set=t["task_set"], rq=t["rq"],
                        seconds=sd["secs"], outcome=sd["outcome"], success=sd["success"], wrong_actions=sd["wrong"],
                        photos_opened=len(S.opened - sd.get("opened0", set())), searches=sd.get("searches", 0), undos=sd.get("undos", 0),
                        screens_visited=sd.get("nav", 0), seq=seq)
            sd["i"] += 1
            sd["step"] = "tasks"
            S.pop("fd_rate", None)
            st.rerun()


# ---- Gallery baseline: modelled on the phone's stock Gallery app (researcher's screenshots), in a light theme ----------------------
# Photos: big title, Today / Yesterday / date groups, tight 4-column grid. Select (button or hold a photo): "N Item(s) Selected", a checkbox on each
# photo and on each day, bottom bar Copy / Move / Delete. Open photo: bottom bar Favorite / Edit / Delete / More. Albums: 3-column album grid with
# name and count, then rows for Favorites and Recently Deleted. Recently Deleted: select photos, Recover or Delete. No assistant, no
# Needs-attention, no Clean-up, no search by meaning, no faces.
BL_ICONS = {
    "heart": '<path d="M12 20.5S4.5 16 3 10.8C2.1 7.6 4.3 5 7 5c2 0 3.6 1.2 5 3 1.4-1.8 3-3 5-3 2.7 0 4.9 2.6 4 5.8-1.5 5.2-9 9.7-9 9.7z"/>',
    "edit": '<path d="M4 20h4L19.5 8.5l-4-4L4 16v4z"/><path d="M13.5 6.5l4 4"/>',
    "trash": '<path d="M5 7h14"/><path d="M9 7V4h6v3"/><path d="M7 7l1 13h8l1-13"/><path d="M10 11v6M14 11v6"/>',
    "copy": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M5 16V5a1 1 0 0 1 1-1h10"/>',
    "move": '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M10 9l4 3-4 3"/>',
    "more": '<circle cx="12" cy="5" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="12" cy="19" r="1.3"/>',
    "photos": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="M4 18l5-5 4 4 3-3 4 4"/>',
    "albums": '<path d="M5 9h14v10H5z"/><path d="M7 6h10"/><path d="M9 3h6"/>',
    "recover": '<path d="M4 12a8 8 0 1 0 2.5-5.800"/><path d="M4 4v5h5"/>',
    "auto": '<path d="M12 3l1.800 5.2L19 10l-5.2 1.800L12 17l-1.800-5.2L5 10l5.2-1.800z"/><path d="M19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z"/>',
    "crop": '<path d="M7 3v14h14"/><path d="M3 7h14v14"/>',
    "adjust": '<circle cx="12" cy="13" r="7"/><path d="M12 13l3-4"/><path d="M12 3v2"/>',
    "filters": '<circle cx="9" cy="12" r="6"/><circle cx="15" cy="12" r="6"/>',
    "close": '<path d="M6 6l12 12M18 6L6 18"/>',
    "back": '<path d="M19 12H5"/><path d="M12 5l-7 7 7 7"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "select": '<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M8 12l3 3 5-6"/>',
    "flip": '<path d="M12 4v16"/><path d="M9 7L4 17h5z"/><path d="M15 7l5 10h-5z"/>',
    "rotate": '<rect x="5" y="9" width="11" height="11" rx="2"/><path d="M9 6a6 6 0 0 1 10 3"/><path d="M19 4v5h-5"/>',
    "chev": '<path d="M9 5l7 7-7 7"/>',
}


def bl_icon(name, size=24, color="currentColor", fill=False):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{color if fill else "none"}" stroke="{color}" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{BL_ICONS[name]}</svg>')


def bl_act(key, icon, label, fn, *args, active=False, color="#2b2b2b", fill=False, disabled=False):
    col = "#1a8fd1" if active else color
    tappable(key, f'<div class="bl-act" style="color:{col};opacity:{.35 if disabled else 1}">{bl_icon(icon, 24, col, fill)}<span>{esc(label)}</span></div>',
             (lambda *a: None) if disabled else fn, *args, label=label)


def bl_go(view, **kw):
    study_tick("nav")
    prev = S.get("bl_view")
    S.bl_view = view
    S.update(kw)
    back_to_same = prev in ("viewer", "editor") and S.get("bl_leave") == (view, S.get("bl_list"))
    S.bl_restore = bool(back_to_same)       # coming back from a photo: return to the place in the list, not the top
    S.scroll = not back_to_same
    st.rerun()


def bl_scroll_memory(track=True):
    """Remembers how far the list was scrolled when a photo is tapped (a pointer-down listener on the page) and, coming back, scrolls there again.
    track=False on the photo and editor screens, so their short pages never overwrite the saved place."""
    restore = bool(S.pop("bl_restore", False)) if track else False
    js = ("(function(){try{var P=window.parent,d=P.document;"
          f"P.__blTrack={'true' if track else 'false'};"
          "function M(){return d.querySelector('[data-testid=\"stMain\"]')||d.querySelector('section.main')||d.scrollingElement;}"
          "if(!P.__blHook){P.__blHook=true;"
          "d.addEventListener('scroll',function(e){if(P.__blTrack){var t=e.target;P.__blEl=(t===d||!t.scrollTop&&t.nodeType===9)?d.scrollingElement:t;P.__blLive=(P.__blEl.scrollTop||0);}},true);"
          "d.addEventListener('pointerdown',function(){if(P.__blTrack){P.__blY=P.__blLive||0;}},true);}"
          + ("var y=P.__blY||0,n=0,t=setInterval(function(){var els=[P.__blEl,M(),d.scrollingElement];for(var k=0;k<els.length;k++){if(els[k]&&els[k].scrollTo){els[k].scrollTo(0,y);}}"
             "n+=1;var m=P.__blEl||M();if(n>70||(m&&Math.abs(m.scrollTop-y)<3&&n>2)){clearInterval(t);}},50);" if restore else "")
          + "}catch(e){}})();")
    try:
        import streamlit.components.v1 as components
        components.html(f"<script>{js}</script>", height=0)
    except Exception:
        pass


def bl_rows():
    return sorted([r for r in df.itertuples() if arrived_ok(r) and r.id not in S.removed], key=lambda r: (r.taken, r.id), reverse=True)


def bl_trash_ids():
    return [i for i in sorted(S.removed) if i in R and i not in S.get("bl_purged", set())]


def bl_open(i):
    S.opened.add(i)
    back = S.bl_view if S.bl_view not in ("viewer", "editor") else S.get("bl_back", "photos")
    S.bl_leave = (back, S.get("bl_list"))
    bl_go("viewer", bl_sel=i, bl_back=back)


def bl_tap(i):
    if S.get("bl_select"):
        S.bl_picked = set(S.get("bl_picked", set())) ^ {i}
        st.rerun()
    bl_open(i)


def bl_tile(r):
    heart = '<span style="position:absolute;left:6px;bottom:3px;color:#fff;font-size:15px;text-shadow:0 1px 3px rgba(0,0,0,.7)">♥</span>' if r.id in S.fav else ""
    return (f'<div class="tile pressable" data-pid="{r.id}" style="position:relative;-webkit-touch-callout:none;user-select:none"><img src="{img_uri(r.file, 320, 320)}" '
            f'alt="Photo from {r.taken}" style="aspect-ratio:1/1;object-fit:cover;border-radius:0;width:100%;display:block">{heart}</div>')


def bl_grid(rows, prefix, n=8):
    """Photos, n per row. Every photo has a tick square in its top-left corner (single or group select), as in PixelSense."""
    picked = set(S.get("bl_picked", set()))
    with st.container(key=f"blg_{prefix}"):
        for k in range(0, len(rows), n):
            cols = st.columns(n)
            for c, r in zip(cols, rows[k:k + n]):
                with c:
                    with st.container(key=f"selcell_bl_{prefix}_{r.id}"):
                        tappable(f"{prefix}_{r.id}", bl_tile(r), bl_tap, r.id, label=f"Photo from {r.taken}")
                        S[f"blck_{r.id}"] = r.id in picked
                        st.checkbox(f"Select photo from {r.taken}", key=f"blck_{r.id}", label_visibility="collapsed", on_change=bl_check, args=(r.id,))


BL_CSS = r"""<style>
:root{--sbh:68px}
.stApp,[data-testid='stAppViewContainer'],[data-testid='stMain']{background:#fff!important}
[data-testid='stMainBlockContainer']{background:#fff!important;max-width:none!important;width:100%!important;
  padding-left:28px!important;padding-right:28px!important;padding-bottom:160px!important}

/* photo grid: fills the screen, 8 per row on a computer */
[class*='st-key-blg_'] [data-testid='stHorizontalBlock']{gap:3px!important;flex-wrap:nowrap!important;margin-bottom:3px}
[class*='st-key-blg_'] [data-testid='stColumn']{min-width:0!important;flex:1 1 0!important}
[class*='st-key-blg_'] [data-testid='stVerticalBlock']{gap:0!important}

/* bottom navigation (Photos, Collections): the same bar on a phone and on a computer, no side menu */
.st-key-bl_side,.st-key-bl_side_sel{position:fixed!important;left:0;right:0;bottom:0;top:auto;width:100%;box-sizing:border-box;z-index:70;
  background:#fff;border-top:1px solid #e6e8eb;flex-direction:row!important;justify-content:center;padding:6px 8px calc(8px + env(safe-area-inset-bottom))!important;gap:0!important}
.st-key-bl_side>*{flex:1 1 0!important;min-width:0;max-width:260px}
.bl-side-row{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;padding:6px 0;border-radius:14px;font-size:12px;font-weight:500;color:#5f6368;text-align:center}
.bl-side-row.on{color:#1a8fd1;font-weight:600}
.bl-side-row:not(.on):hover{background:#f1f3f4}
.st-key-bl_side_sel{display:none!important}

/* bottom bars: Copy / Move / Delete, Recover / Delete, and the photo actions */
.st-key-bl_bar{position:fixed!important;left:0;bottom:0;width:100%;z-index:60;background:#f8f9fa;border-top:1px solid #e6e8eb;
  padding:6px 8px calc(8px + env(safe-area-inset-bottom))!important}
.st-key-bl_bar [data-testid='stHorizontalBlock']{flex-wrap:nowrap!important;gap:0!important;max-width:520px;margin:0 auto}
.st-key-bl_bar [data-testid='stColumn']{min-width:0!important;flex:1 1 0!important}
.bl-act{display:flex;flex-direction:column;align-items:center;gap:3px;padding:4px 0;font-size:12px;font-weight:500}

.bl-title{font-size:30px;font-weight:600;color:#1b1c1e;margin:4px 0 8px;line-height:1.2}
.bl-day{font-size:15px;color:#5f6368;font-weight:500}
.bl-pad{padding:0 16px}
.bl-row{display:flex;align-items:center;gap:14px;padding:14px 16px;color:#1b1c1e;font-size:17px;border-top:1px solid #f0f1f3}
.bl-row .n{margin-left:auto;color:#80868b;font-size:15px}
.bl-alb img,.bl-alb .ph{aspect-ratio:1/1;object-fit:cover;width:100%;border-radius:12px;display:block;background:#eceff1}
.bl-alb .nm{font-size:14px;color:#3c4043;margin-top:4px}.bl-alb .ct{font-size:12px;color:#80868b}
.st-key-bl_lpwrap{height:0;overflow:hidden;margin:0!important}.st-key-bl_lpwrap iframe{height:0}

/* the whole picture, never cropped, never scrolled: sized to the space left under the header */
.bl-fit{height:calc(100dvh - var(--sbh) - 190px);min-height:180px;display:flex;align-items:center;justify-content:center}
.bl-fit img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;border-radius:8px;display:block}
.bl-fit.ed{height:calc(100dvh - var(--sbh) - 120px)}

/* a short message that floats at the top, so it never pushes the page down */
.st-key-bl_toast{position:fixed!important;top:calc(var(--sbh) + 12px);left:50%;transform:translateX(-50%);z-index:1100;width:auto!important;max-width:90vw}
.bl-toast{background:#202124;color:#fff;padding:10px 20px;border-radius:8px;font-size:14px;font-weight:500;box-shadow:0 4px 14px rgba(0,0,0,.25)}

/* header buttons */
[class*='st-key-blh_'] button,.st-key-bl_ghost button{background:transparent!important;border:0!important;box-shadow:none!important;color:#1b1c1e!important}
[class*='st-key-blh_selall'] .stButton,[class*='st-key-blh_save'] .stButton{display:flex;justify-content:flex-end;width:100%!important}
[class*='st-key-blh_selall'] button{color:#1a8fd1!important;font-weight:600}
[class*='st-key-blh_save'] button{background:var(--b,#5B4FD6)!important;color:#fff!important;border:0!important;border-radius:14px!important;padding:0 26px!important;min-height:44px;font-weight:700}
[class*='st-key-blh_save'] button p{color:#fff!important;white-space:nowrap!important;writing-mode:horizontal-tb!important;letter-spacing:0!important}
[class*='st-key-blh_save'] button{white-space:nowrap!important;width:auto!important;min-width:88px}
[data-testid='stColumn']:has([class*='st-key-blh_save']){flex:0 0 auto!important;width:auto!important;min-width:100px!important}
/* big back arrow, close and plus: drawn as pictures (the text glyphs are tiny) */
[class*='st-key-blhback_'] .stButton,[class*='st-key-blhclose_'] .stButton,[class*='st-key-blhplus_'] .stButton{width:auto!important}
[class*='st-key-blhplus_'] .stButton{display:flex;justify-content:flex-end;width:100%!important}
[class*='st-key-blhback_'] button,[class*='st-key-blhclose_'] button,[class*='st-key-blhplus_'] button{position:relative;width:64px!important;min-width:64px!important;
  height:64px!important;min-height:64px!important;padding:0!important;border:0!important;background:#eef0f2!important;box-shadow:none!important;border-radius:50%!important}
[class*='st-key-blhback_'] button:hover,[class*='st-key-blhclose_'] button:hover,[class*='st-key-blhplus_'] button:hover{background:#e1e4e8!important}
[data-testid='stColumn']:has([class*='st-key-blhback_']),[data-testid='stColumn']:has([class*='st-key-blhclose_']),[data-testid='stColumn']:has([class*='st-key-blhplus_']){flex:0 0 72px!important;width:72px!important;min-width:72px!important}
[class*='st-key-blhback_'] button p,[class*='st-key-blhclose_'] button p,[class*='st-key-blhplus_'] button p{font-size:0!important;line-height:0!important}
[class*='st-key-blhback_'] button::after,[class*='st-key-blhclose_'] button::after,[class*='st-key-blhplus_'] button::after{content:"";position:absolute;inset:0;margin:auto;
  width:42px;height:42px;background-position:center;background-repeat:no-repeat;background-size:contain;pointer-events:none}
[class*='st-key-blhback_'] button::after{background-image:url('data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%231b1c1e%27 stroke-width=%272.4%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Cpath d=%27M19 12H5M11 5.5 4.5 12l6.5 6.5%27/%3E%3C/svg%3E')}
[class*='st-key-blhclose_'] button::after{background-image:url('data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%231b1c1e%27 stroke-width=%272.4%27 stroke-linecap=%27round%27%3E%3Cpath d=%27M6 6l12 12M18 6 6 18%27/%3E%3C/svg%3E')}
[class*='st-key-blhplus_'] button::after{background-image:url('data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%231b1c1e%27 stroke-width=%272.4%27 stroke-linecap=%27round%27%3E%3Cpath d=%27M12 4.5v15M4.5 12h15%27/%3E%3C/svg%3E')}

/* the plus for a new album is smaller than the arrows */
[class*='st-key-blhplus_'] button{width:44px!important;min-width:44px!important;height:44px!important;min-height:44px!important}
[class*='st-key-blhplus_'] button::after{width:26px!important;height:26px!important}
[data-testid='stColumn']:has([class*='st-key-blhplus_']){flex:0 0 60px!important;width:60px!important;min-width:60px!important}

/* tick square on every photo (top-left, like PixelSense), blue here */
[class*='st-key-selcell_bl'] [data-testid='stElementContainer']:has([data-testid='stCheckbox']),
[class*='st-key-selcell_bl'] .element-container:has([data-testid='stCheckbox']){top:6px!important;left:6px!important}
[class*='st-key-selcell_bl'] [data-testid='stCheckbox'] label:has(input:checked)::before{background:rgba(26,143,209,.95)!important}
[class*='st-key-selcell_bl']:has(input:checked) .tile{outline:3px solid #1a8fd1;outline-offset:-3px}

/* editor: photo on the left, tools on the right */
.st-key-bl_edit [data-testid='stHorizontalBlock']{align-items:flex-start!important;gap:32px!important;flex-wrap:nowrap!important}
.st-key-bl_editpanel{max-height:calc(100dvh - var(--sbh) - 120px);overflow-y:auto;padding-right:6px}
@media (max-width:767px){
  .st-key-bl_edit [data-testid='stHorizontalBlock']:not([data-testid='stColumn'] *){flex-wrap:wrap!important;gap:8px!important}
  .st-key-bl_edit [data-testid='stHorizontalBlock']:not([data-testid='stColumn'] *)>[data-testid='stColumn']:first-child{flex:1 1 100%!important;width:100%!important;min-width:0!important}
  .st-key-bl_edit [data-testid='stHorizontalBlock']:not([data-testid='stColumn'] *)>[data-testid='stColumn']:last-child{position:fixed!important;left:0;right:0;bottom:0;top:auto;z-index:900;
    width:100%!important;min-width:0!important;flex:none!important;height:38dvh;overflow-y:auto;box-sizing:border-box;background:#fff;border-radius:22px 22px 0 0;
    box-shadow:0 -10px 30px rgba(0,0,0,.18);padding:14px 16px calc(10px + env(safe-area-inset-bottom))!important}
  .st-key-bl_editpanel{max-height:none;overflow:visible;padding-right:0}
  .bl-fit.ed{height:calc(62dvh - var(--sbh) - 90px)}
  .st-key-bl_edit{padding-bottom:42dvh}
}
[class*='st-key-blasp_'] .stButton>button{width:100%;justify-content:flex-start;min-height:46px;border-radius:999px;background:#fff!important;color:#202124!important;border:1px solid #dadce0!important;box-shadow:none}
[class*='st-key-blasp_'] .stButton>button[data-testid='stBaseButton-primary']{background:#e3f1fb!important;color:#0b6aa8!important;border-color:#e3f1fb!important}

@media (max-width:900px){
  [class*='st-key-blg_'] [data-testid='stHorizontalBlock']{flex-wrap:wrap!important}
  [class*='st-key-blg_'] [data-testid='stColumn']{flex:0 0 calc(25% - 3px)!important;width:calc(25% - 3px)!important}
}
/* the photo, a little shorter so the Previous / Next row fits under it */
.bl-fit{height:calc(100dvh - var(--sbh) - 250px)}
/* Previous / Next stay side by side on a phone */
[class*='st-key-pkctl_'] [data-testid='stHorizontalBlock']{flex-wrap:nowrap!important;gap:8px!important;align-items:center}
[class*='st-key-pkctl_'] [data-testid='stColumn']{min-width:0!important}
.bl-hint{color:#5f6368;font-size:13px;text-align:center;margin:8px 0 0}
</style>"""
BL_NOSCROLL = "<style>html,body,.stApp,[data-testid='stAppViewContainer'],[data-testid='stMain'],section.main{overflow:hidden!important}</style>"


def bl_header(left_icon, left_key, left_fn, title, right=None):
    """Light top bar: big back arrow on the left, title, optional action on the right."""
    c = st.columns([1, 6, 1.4] if right else [1, 7])
    with c[0]:
        with st.container(key=f"blhclose_{left_key}" if left_icon == "close" else f"blhback_{left_key}"):
            if st.button("✕" if left_icon == "close" else "←", key=f"blhb_{left_key}", help="Close" if left_icon == "close" else "Back"):
                left_fn()
    with c[1]:
        md(f'<div style="font-size:21px;font-weight:600;color:#1b1c1e;margin-top:18px">{esc(title)}</div>')
    if right:
        with c[2]:
            right()


def bl_snack():
    """A one-time message that floats at the top of the screen (it never moves the page)."""
    if not S.snack:
        return
    msg = S.snack[0]
    S.snack = None
    with st.container(key="bl_toast"):
        md(f'<div class="bl-toast">{esc(msg)}</div>')


def bl_check(i):
    """The tick square on a photo was tapped (on_change): keep the picked set in step with it."""
    cur = set(S.get("bl_picked", set()))
    if S.get(f"blck_{i}"):
        cur.add(i)
    else:
        cur.discard(i)
    S.bl_picked = cur


def bl_clear_pick():
    S.bl_picked, S.bl_select = set(), False


def bl_back_to_albums():
    bl_clear_pick()
    bl_go("albums")


def bl_sel_header(picked, all_ids):
    """Shown while photos are ticked: close, how many are selected, Select all."""
    c = st.columns([1, 6, 1.6])
    with c[0]:
        with st.container(key="blhclose_sel"):
            st.button("✕", key="bl_sel_close", on_click=bl_clear_pick, help="Cancel")
    with c[1]:
        md(f'<div style="font-size:20px;font-weight:600;color:#1b1c1e;margin-top:12px">{len(picked)} Item{"s" if len(picked) != 1 else ""} Selected</div>')
    with c[2]:
        with st.container(key="blh_selall"):
            everything = bool(all_ids) and len(picked) == len(all_ids)
            st.button("Deselect all" if everything else "Select all", key="bl_sel_all", on_click=bl_toggle_ids, args=(all_ids,))


@st.dialog("Delete?")
def bl_delete_dialog(ids):
    st.write(f"{len(ids)} item{'s' if len(ids) != 1 else ''} will move to Recently Deleted. You can recover them from Collections.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel", key="bl_del_cancel"):
            st.rerun()
    with c2:
        if st.button("Delete", type="primary", key="bl_del_ok"):
            S.removed.update(ids)
            S.bl_select, S.bl_picked = False, set()
            notify(f"{len(ids)} moved to Recently Deleted.", False)
            if S.bl_view in ("viewer", "editor"):
                S.bl_view = S.get("bl_back", "photos")
                S.bl_restore, S.scroll = S.get("bl_leave") == (S.bl_view, S.get("bl_list")), S.get("bl_leave") != (S.bl_view, S.get("bl_list"))
            st.rerun()


@st.dialog("Delete permanently?")
def bl_purge_dialog(ids):
    st.write(f"{len(ids)} item{'s' if len(ids) != 1 else ''} will be deleted for good.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel", key="bl_purge_cancel"):
            st.rerun()
    with c2:
        if st.button("Delete", type="primary", key="bl_purge_ok"):
            S.bl_purged = set(S.get("bl_purged", set())) | set(ids)
            S.bl_picked = set()
            st.rerun()


def bl_picker(prefix, rows):
    """Photos to add: the shared picker (tap a photo to see it big and swipe through all of them, tick the square to choose it)."""
    return photo_picker(prefix, rows, 200, 200)


@st.dialog("New collection", width="large")
def bl_album_dialog():
    name = st.text_input("Collection name", placeholder="Collection name", key="bl_new_name")
    st.caption("Pick photos now, or create it empty and add photos from inside the collection later.")
    picked = bl_picker("blnew", bl_rows())
    if st.button(f"Create ({len(picked)} selected)", type="primary", key="bl_new_ok"):
        n = name.strip()
        if not n:
            st.warning("Enter a name first.")
        elif n in S.bl_albums:
            st.warning("You already have a collection with that name.")
        else:
            S.bl_albums[n] = list(picked)
            for k in [k for k in S.keys() if str(k).startswith("blnew_")]:
                del S[k]
            S.pop("bl_new_name", None)
            bl_go("list", bl_list=("album", n), bl_back="albums")


@st.dialog("Add photos", width="large")
def bl_add_dialog(name):
    rows = [r for r in bl_rows() if r.id not in S.bl_albums[name]]
    picked = bl_picker(f"bladd_{slug(name)}", rows)
    if st.button(f"Add ({len(picked)})", type="primary", key="bl_add_ok", disabled=not picked):
        S.bl_albums[name] += picked
        for k in [k for k in S.keys() if str(k).startswith(f"bladd_{slug(name)}_")]:
            del S[k]
        notify(f"Added {len(picked)} to “{name}”.", False)
        st.rerun()


@st.dialog("Choose collection")
def bl_to_album_dialog(ids, move=False):
    names = list(S.bl_albums)
    if names:
        pick = st.radio("Collection", names, key=f"bl_pick_{move}")
        if st.button("Move here" if move else "Copy here", type="primary", key=f"bl_pick_ok_{move}"):
            for i in ids:
                for n in names:
                    if move and n != pick and i in S.bl_albums[n]:
                        S.bl_albums[n].remove(i)
                if i not in S.bl_albums[pick]:
                    S.bl_albums[pick].append(i)
            S.bl_select, S.bl_picked = False, set()
            notify(f"{'Moved' if move else 'Copied'} to “{pick}”.", False)
            st.rerun()
    new = st.text_input("Or a new collection", placeholder="Collection name", key=f"bl_pick_new_{move}")
    if st.button("Create and add", key=f"bl_pick_newok_{move}", disabled=not new.strip() or new.strip() in S.bl_albums):
        S.bl_albums[new.strip()] = list(ids)
        S.bl_select, S.bl_picked = False, set()
        notify(f"Added to “{new.strip()}”.", False)
        st.rerun()


@st.dialog("Details")
def bl_details_dialog(r):
    st.write(f"**Date:** {r.taken}")
    st.write(f"**File:** {r.file.split('/')[-1]}")
    st.write(f"**Type:** {'Screenshot' if r.type == 'screenshot' else 'Camera photo'}")


def bl_set_tab(key):
    S.bl_select, S.bl_picked = False, set()
    bl_go(key)


def bl_active():
    """Which bottom-bar entry is current: every list (Camera, Favorites, Recently Deleted, a collection) belongs to Collections."""
    return "albums" if S.bl_view in ("albums", "list") else "photos"


def bl_side_go(key):
    bl_clear_pick()
    bl_go(key)


def bl_nav(selecting=False):
    """Bottom navigation, like a normal gallery app: Photos and Collections. No side menu."""
    md(BL_CSS)
    cur = bl_active()
    with st.container(key="bl_side_sel" if selecting else "bl_side"):
        for key, icon, label in (("photos", "photos", "Photos"), ("albums", "albums", "Collections")):
            on = key == cur
            tappable(f"blside_{key}", f'<div class="bl-side-row{" on" if on else ""} pressable">{bl_icon(icon, 26, "#1a8fd1" if on else "#5f6368")}<span>{label}</span></div>',
                     bl_side_go, key, label=label)


def bl_day_label(day):
    try:
        d = datetime.strptime(str(day), "%Y-%m-%d").date()
    except ValueError:
        return str(day)
    delta = (date.today() - d).days
    return "Today" if delta == 0 else "Yesterday" if delta == 1 else d.strftime("%b %d, %Y")


def bl_toggle_ids(ids):
    cur = set(S.get("bl_picked", set()))
    S.bl_picked = cur - set(ids) if set(ids) <= cur else cur | set(ids)


def bl_selected_bar(picked):
    with st.container(key="bl_bar"):
        c = st.columns(3)
        with c[0]:
            bl_act("sel_copy", "copy", "Copy", lambda: bl_to_album_dialog(picked, False), disabled=not picked)
        with c[1]:
            bl_act("sel_move", "move", "Move", lambda: bl_to_album_dialog(picked, True), disabled=not picked)
        with c[2]:
            bl_act("sel_del", "trash", "Delete", lambda: bl_delete_dialog(picked), disabled=not picked)


def bl_photos():
    md(BL_CSS)
    rows = bl_rows()
    all_ids = [r.id for r in rows]
    picked = sorted(S.get("bl_picked", set()) & set(all_ids))
    sel = bool(picked)                  # selecting = at least one photo is ticked
    S.bl_select = sel
    if sel:
        bl_sel_header(picked, all_ids)
    else:
        md('<div class="bl-title bl-pad" style="margin-top:6px">Photos</div>')
    bl_snack()
    with st.container(key="bl_lpwrap"):
        held = _LONGPRESS(key="bl_lp", default=None)
    if isinstance(held, dict) and held.get("n") != S.get("bl_lp_n"):
        S.bl_lp_n = held["n"]               # holding a photo ticks it, like the phone's Gallery app
        S.bl_picked = set(S.get("bl_picked", set())) | {held["pid"]}
        st.rerun()
    S.bl_order = all_ids                 # the photo screen swipes through this list
    by_day = {}
    for r in rows:
        by_day.setdefault(r.taken, []).append(r)
    for day, items in by_day.items():
        ids = [r.id for r in items]
        if sel:
            hc = st.columns([6, 1])
            with hc[0]:
                md(f'<div class="bl-day bl-pad" style="margin:14px 0 6px">{esc(bl_day_label(day))}</div>')
            with hc[1]:
                with st.container(key=f"blh_day_{slug(str(day))}"):
                    st.button("☑" if set(ids) <= set(picked) else "☐", key=f"bl_day_{slug(str(day))}", on_click=bl_toggle_ids, args=(ids,), help="Select day")
        else:
            md(f'<div class="bl-day bl-pad" style="margin:14px 0 6px">{esc(bl_day_label(day))}</div>')
        bl_grid(items, f"p_{slug(str(day))}")
    bl_nav(selecting=sel)
    if sel:
        bl_selected_bar(picked)


def bl_album_cell(key, title, items, kw):
    thumb = items[0] if items else None
    img = f'<img src="{img_uri(thumb.file, 320, 320)}" alt="">' if thumb is not None else '<div class="ph"></div>'
    tappable(f"bla_{key}", f'<div class="bl-alb pressable">{img}<div class="nm">{esc(title)}</div><div class="ct">{len(items)}</div></div>',
             lambda: bl_go("list", bl_back="albums", **kw), label=f"Open {title}")


def bl_open_list(kind):
    bl_go("list", bl_list=(kind, None), bl_back="albums")


def bl_albums_view():
    md(BL_CSS)
    c = st.columns([8, 1])
    with c[0]:
        md('<div class="bl-title bl-pad" style="margin-top:6px">Collections</div>')
    with c[1]:
        with st.container(key="blhplus_newalb"):
            if st.button("＋", key="bl_new_album", help="New collection"):
                bl_album_dialog()
    bl_snack()
    rows = bl_rows()
    cells = [("cam", "Camera", [r for r in rows if r.type != "screenshot"], dict(bl_list=("camera", None))),
             ("shots", "Screenshots", [r for r in rows if r.type == "screenshot"], dict(bl_list=("shots", None)))]
    for n, ids in S.bl_albums.items():
        cells.append((f"u_{slug(n)}", n, [R[i] for i in ids if i in R and i not in S.removed], dict(bl_list=("album", n))))
    with st.container(key="bl_albgrid"):             # 4 covers per row on a computer, 3 on a phone (CSS)
        for k in range(0, len(cells), 4):
            cols = st.columns(4)
            for col, (key, title, items, kw) in zip(cols, cells[k:k + 4]):
                with col:
                    bl_album_cell(key, title, items, kw)
    md('<div style="height:10px"></div>')
    fav_n = len([r for r in rows if r.id in S.fav])
    for key, icon, label, n in (("fav", "heart", "Favorites", fav_n), ("trash", "trash", "Recently Deleted", len(bl_trash_ids()))):
        tappable(f"blrow_{key}", f'<div class="bl-row pressable">{bl_icon(icon, 24, "#3c4043")}<span>{label}</span><span class="n">{n}</span></div>',
                 bl_open_list, key, label=f"Open {label}")
    bl_nav()


def bl_list():
    md(BL_CSS)
    kind, arg = S.get("bl_list", ("camera", None))
    rows = bl_rows()
    if kind == "fav":
        title, items = "Favorites", [r for r in rows if r.id in S.fav]
    elif kind == "shots":
        title, items = "Screenshots", [r for r in rows if r.type == "screenshot"]
    elif kind == "camera":
        title, items = "Camera", [r for r in rows if r.type != "screenshot"]
    elif kind == "album":
        title = arg
        items = [R[i] for i in S.bl_albums.get(arg, []) if i in R and i not in S.removed]
    else:
        title, items = "Recently Deleted", [R[i] for i in bl_trash_ids()]
    ids = [r.id for r in items]
    picked = sorted(S.get("bl_picked", set()) & set(ids))
    in_trash = kind == "trash"
    sel = bool(picked)
    S.bl_select = sel or in_trash           # in Recently Deleted a tap always ticks a photo
    S.bl_order = ids                        # the photo screen swipes through this list
    if sel:
        bl_sel_header(picked, ids)
    elif in_trash and ids:
        def _selall():
            with st.container(key="blh_selall"):
                st.button("Select all", key="bl_tr_selall", on_click=bl_toggle_ids, args=(ids,))
        bl_header("back", "list", bl_back_to_albums, title, right=_selall)
    else:
        bl_header("back", "list", bl_back_to_albums, title)
    bl_snack()
    md(f'<div class="bl-pad" style="color:#80868b;font-size:13px;margin-bottom:6px">{len(items)} item{"s" if len(items) != 1 else ""}</div>')
    if kind == "album" and not sel:
        with st.container(key="blh_addph"):
            if st.button("＋ Add photos", key="bl_album_add"):
                bl_add_dialog(arg)
    if not items:
        if in_trash:
            empty_state("folder", "Nothing deleted", "Photos you delete stay here so you can recover them.")
        else:
            empty_state("folder", "Nothing here yet", "Tap Add photos." if kind == "album" else "No photos.")
    bl_grid(items, f"l_{kind}")
    bl_nav(selecting=sel or in_trash)
    if in_trash:
        with st.container(key="bl_bar"):
            c = st.columns(2)
            with c[0]:
                bl_act("tr_recover", "recover", "Recover", lambda: bl_recover(picked), disabled=not picked)
            with c[1]:
                bl_act("tr_delete", "trash", "Delete", lambda: bl_purge_dialog(picked), disabled=not picked)
    elif sel:
        bl_selected_bar(picked)


def bl_recover(ids):
    S.removed -= set(ids)
    S.bl_picked = set()
    notify(f"{len(ids)} recovered.", False)
    st.rerun()


def bl_toggle_heart(i):
    S.fav.symmetric_difference_update({i})


def bl_step(d):
    order = S.get("bl_order") or []
    cur = S.get("bl_sel")
    if cur in order:
        k = order.index(cur) + d
        if 0 <= k < len(order):
            S.bl_sel = order[k]
            S.opened.add(S.bl_sel)
            S.bl_leave = (S.get("bl_back", "photos"), S.get("bl_list"))


def bl_viewer():
    md(BL_CSS)
    md(BL_NOSCROLL)                      # the whole photo fits on the screen, so there is nothing to scroll
    ev = _SWIPE(key="sw_bl", default=None)           # swipe left = next photo, swipe right = previous (arrow keys on a computer)
    if isinstance(ev, dict) and ev.get("n") != S.get("sw_bl_n"):
        S.sw_bl_n = ev.get("n")
        bl_step(1 if ev.get("dir") == "next" else -1)
    r = R.get(S.get("bl_sel"))
    if r is None or r.id in S.removed:
        S.bl_view = "photos"
        return bl_photos()
    try:
        nice = datetime.strptime(str(r.taken), "%Y-%m-%d").strftime("%b %d, %Y")
    except ValueError:
        nice = str(r.taken)
    bl_header("back", "viewer", lambda: bl_go(S.get("bl_back", "photos")), nice)
    bl_snack()
    md(f'<div class="bl-fit" data-swipe-zone><img src="{full_uri(r.file, 1600)}" alt="Photo from {r.taken}"></div>')
    order = S.get("bl_order") or []
    k = order.index(r.id) if r.id in order else 0
    with st.container(key="pkctl_bl"):
        pc = st.columns([1, 2, 1])
        with pc[0]:
            st.button("‹ Back", key="bl_v_prev", on_click=bl_step, args=(-1,), disabled=k == 0, use_container_width=True)
        with pc[1]:
            md(f'<div class="bl-hint">{k + 1} of {max(len(order), 1)} · swipe for the next photo</div>')
        with pc[2]:
            st.button("Next ›", key="bl_v_next", on_click=bl_step, args=(1,), disabled=k >= len(order) - 1, use_container_width=True)
    with st.container(key="bl_bar"):
        c = st.columns(4)
        with c[0]:
            bl_act("v_heart", "heart", "Favorite", bl_toggle_heart_rerun, r.id, active=r.id in S.fav, fill=r.id in S.fav)
        with c[1]:
            bl_act("v_edit", "edit", "Edit", bl_start_edit)
        with c[2]:
            bl_act("v_del", "trash", "Delete", lambda: bl_delete_dialog([r.id]))
        with c[3]:
            bl_act("v_more", "more", "More", lambda: bl_more_dialog(r))
    bl_after_more()


def bl_toggle_heart_rerun(i):
    bl_toggle_heart(i)
    st.rerun()


def bl_start_edit():
    for k in [k for k in S.keys() if str(k).startswith("bled_")]:
        del S[k]
    bl_go("editor")


@st.dialog("More")
def bl_more_dialog(r):
    # Streamlit cannot open a dialog from inside a dialog, so each choice is remembered and opened right after this one closes.
    for label, what in (("Copy", "copy"), ("Move", "move"), ("Details", "details")):
        if st.button(label, key=f"bl_more_{what}", use_container_width=True):
            S.bl_after = (what, r.id)
            st.rerun()


def bl_after_more():
    act = S.pop("bl_after", None)
    if act and act[1] in R:
        what, i = act
        if what == "details":
            bl_details_dialog(R[i])
        else:
            bl_to_album_dialog([i], what == "move")


def bl_reframe():
    """Put the crop frame back to the default for the current ratio and rotation, and tell the frame widget to redraw."""
    S.bled_crop = ed_default_crop(S.bl_sel, S.get("bled_asp", "Original"), S.get("bled_rot", 0))
    S.bled_nonce = S.get("bled_nonce", 0) + 1


def bl_rotate():
    S.bled_rot = (S.get("bled_rot", 0) + 90) % 360
    bl_reframe()
    st.rerun()


def bl_flip():
    S.bled_flip = not S.get("bled_flip", False)
    bl_reframe()
    st.rerun()


def bl_pick_auto(v):
    S.bled_auto = v
    st.rerun()


def bl_pick_asp(v):
    S.bled_asp = v
    bl_reframe()
    st.rerun()


def bl_pick_look(v):
    S.bled_look = v
    st.rerun()


def bl_pick_tool(v):
    S.bled_tool = v
    st.rerun()


def bl_editor():
    """Editor laid out like Google Photos on a computer: the whole photo on the left (no scrolling), and on the right the tool tabs
    (Auto, Crop, Adjust, Filters) with that tool's options under them. Light theme."""
    md(BL_CSS)
    md(BL_NOSCROLL.replace("<style>", "<style>@media (min-width:768px){").replace("</style>", "}</style>"))     # a phone can scroll the photo clear of the panel
    r = R.get(S.get("bl_sel"))
    if r is None:
        S.bl_view = "photos"
        return bl_photos()
    src = Image.open(ROOT / r.file)
    small = ImageOps.exif_transpose(src).convert("RGB")
    small.thumbnail((900, 900))
    S.setdefault("bled_crop", (0.0, 0.0, 0.0, 0.0))
    S.setdefault("bled_nonce", 0)
    for k in ("bled_b", "bled_c", "bled_w", "bled_look"):
        if k in S:
            S[k] = S[k]          # keep slider settings made under a tool that is not on screen right now
    tool = S.get("bled_tool", "Crop")
    auto, asp, rot, flip = S.get("bled_auto", "None"), S.get("bled_asp", "Original"), S.get("bled_rot", 0), S.get("bled_flip", False)
    b, c, w, look = S.get("bled_b", 0), S.get("bled_c", 0), S.get("bled_w", 0), S.get("bled_look", "None")
    dyn = auto == "Dynamic"
    look_ops = dict(brightness=b + (10 if dyn else 0), contrast=c + (20 if dyn else 0), saturation=(20 if dyn else 0), warmth=w,
                    auto=auto in ("Enhance", "Dynamic"), filter=look)
    crop = tuple(S.get("bled_crop", (0.0, 0.0, 0.0, 0.0)))
    ops = ED.new_ops(**look_ops, aspect="Original", crop=crop, rotate=rot, flip=flip)

    def save():
        rec = new_copy_record(r.id, ops)
        notify("Saved a copy. Your original is untouched.", False)
        bl_go("viewer", bl_sel=rec["id"], bl_back="photos")

    def save_btn():
        with st.container(key="blh_save"):
            if st.button("Save", key="bled_save", type="primary", help="Save a copy"):
                if ED.is_default(ops):
                    notify("Nothing to save yet. Make a change first.", False)
                    st.rerun()
                save()
    bl_header("back", "editor", lambda: bl_go("viewer"), "Edit", right=save_btn)
    bl_snack()
    with st.container(key="bl_edit"):
        left, right = st.columns([5, 2])
        with left:
            if tool == "Crop":
                base = ED.apply(small, ED.new_ops(**look_ops, rotate=rot, flip=flip))
                fw, fh = ed_size(r.id)
                if rot in (90, 270):
                    fw, fh = fh, fw
                # the frame is as wide as the photo's shape allows in the space left on screen, so the whole photo is visible without scrolling
                md(f"<style>.st-key-bl_cropwrap{{width:min(100%,calc((100dvh - var(--sbh) - 150px) * {fw / fh:.4f}))!important;margin:0 auto!important}}"
                   f"@media (max-width:767px){{.st-key-bl_cropwrap{{width:min(100%,calc((62dvh - var(--sbh) - 120px) * {fw / fh:.4f}))!important}}}}</style>")
                with st.container(key="bl_cropwrap"):
                    v = _CROP_FRAME(img=pil_uri(base, 85), crop=list(crop), ratio=ED.ASPECTS.get(asp), nonce=S.bled_nonce, full_w=fw, full_h=fh, key="bl_cropper", default=None)
                if isinstance(v, dict) and v.get("nonce") == S.bled_nonce and v.get("crop"):
                    S.bled_crop = tuple(float(x) for x in v["crop"])
            else:
                md(f'<div class="bl-fit ed"><img src="{pil_uri(ED.apply(small, ops), 85)}" alt="Preview"></div>')
        with right:
            with st.container(key="bl_editpanel"):
                cols = st.columns(4)
                for col, (name, icon) in zip(cols, (("Auto", "auto"), ("Crop", "crop"), ("Adjust", "adjust"), ("Filters", "filters"))):
                    with col:
                        bl_act(f"ed_tool_{name}", icon, name, bl_pick_tool, name, active=tool == name, color="#5f6368")
                md('<div style="border-top:1px solid #e6e8eb;margin:2px 0 6px"></div>')
                if tool == "Crop":
                    c1, c2 = st.columns(2)
                    with c1:
                        bl_act("ed_flip", "flip", "Flip", bl_flip)
                    with c2:
                        bl_act("ed_rot", "rotate", "Rotate", bl_rotate)
                    md('<div style="font-size:14px;font-weight:600;color:#3c4043;margin:6px 0 2px">Aspect ratio</div>')
                    for name in ED.ASPECTS:
                        with st.container(key=f"blasp_{slug(name)}"):
                            if st.button(name, key=f"bled_asp_{name}", type="primary" if asp == name else "secondary"):
                                bl_pick_asp(name)
                elif tool == "Auto":
                    cols = st.columns(2)
                    for col, name in zip(cols, ("Enhance", "Dynamic")):
                        with col:
                            demo = ED.apply(small.copy(), ED.new_ops(auto=True, brightness=10 if name == "Dynamic" else 0, contrast=20 if name == "Dynamic" else 0,
                                                                     saturation=20 if name == "Dynamic" else 0))
                            md(f'<img style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:10px;border:{"3px solid #1a8fd1" if auto == name else "3px solid transparent"}" src="{pil_uri(demo, 70)}" alt="{name}">')
                            bl_act(f"ed_auto_{name}", "auto", name, bl_pick_auto, "None" if auto == name else name, active=auto == name)
                elif tool == "Adjust":
                    with st.container(key="bl_ghost"):
                        st.slider("Brightness", -50, 50, 0, key="bled_b")
                        st.slider("Contrast", -50, 50, 0, key="bled_c")
                        st.slider("Warmth", -50, 50, 0, key="bled_w")
                elif tool == "Filters":
                    tiny = small.copy()
                    tiny.thumbnail((150, 150))
                    for k in range(0, len(ED.FILTERS), 3):
                        cols = st.columns(3)
                        for col, nm in zip(cols, ED.FILTERS[k:k + 3]):
                            with col:
                                tappable(f"blf_{slug(nm)}", f'<div class="bl-filt{" on" if look == nm else ""} pressable"><img src="{pil_uri(ED.apply(tiny.copy(), ED.new_ops(filter=nm)), 70)}" alt=""><span>{nm}</span></div>',
                                         bl_pick_look, nm, label=f"Filter {nm}")


def view_baseline():
    """The comparison condition: a gallery modelled on the phone's stock Gallery app (see the comment above)."""
    S.setdefault("bl_view", "photos")
    S.setdefault("bl_albums", {})
    {"photos": bl_photos, "albums": bl_albums_view, "list": bl_list, "viewer": bl_viewer, "editor": bl_editor}.get(S.bl_view, bl_photos)()
    bl_scroll_memory(S.bl_view not in ("viewer", "editor"))      # last, so the list is already on the page when the old place is restored


def study_clear_answers():
    for k in [k for k in S.keys() if str(k).split("_")[0] in ("sus", "tlx", "ueq", "trust", "iv", "fd", "fin", "cmp", "seq")]:
        del S[k]


def study_goto_part(part):
    """Start a version: fresh app state (so nothing from the other version leaks across), study position kept."""
    sd = S.study
    sd.update(part=part, cond=sd["order"][part], i=0, step="tasks", running=False)
    S.update(fresh_state())
    S.study = sd
    S.view = "study"
    S.scroll = True
    study_clear_answers()


def view_study():
    appbar("Usability study")
    snack_ui()
    sd = S.study
    if not sd:
        return study_intro()
    ST.save_progress(sd)
    {"tasks": study_tasks_ui, "seq": study_seq, "survey": study_survey, "between": study_between, "final": study_final}.get(sd["step"], study_done)()


def study_intro():
    pid = ST.next_pid()
    md(f'<div class="card pad glass info"><p><b>Information and consent</b></p><p>{esc(ST.CONSENT)}</p></div>')
    st.caption(f"Your participant number is {pid}. You will try two versions of a photo app, one after the other.")
    age = st.selectbox("Age range", ST.AGE_RANGES, index=None, key="in_age")
    kept = st.selectbox("About how many photos are on your phone?", ST.PHOTO_COUNTS, index=None, key="in_kept")
    freq = st.selectbox("How often do you search for a specific photo?", ST.SEARCH_FREQ, index=None, key="in_freq")
    ok = st.checkbox("I have read the information above and agree to take part.", key="st_consent")
    with st.container(key="sm_stb"):
        if st.button("Begin", type="primary", key="st_begin", disabled=not (ok and age and kept and freq)):
            order, sets = ST.order_for(pid), ST.sets_for(pid)
            ST.log_participant(participant=pid, order=" > ".join(order), task_sets=f"PixelSense={sets['PixelSense']}, Gallery={sets['Gallery (baseline)']}",
                               age_range=age, photos_kept=kept, search_freq=freq)
            S.study = dict(pid=pid, order=order, sets=sets, part=0, cond=order[0], i=0, step="tasks", running=False, nav=0, undos=0)
            study_goto_part(0)
            st.query_params["pid"] = pid
            st.rerun()


def study_tasks_ui():
    sd = S.study
    tasks = study_tasks()
    if sd["i"] >= len(tasks):
        sd["step"] = "between" if sd["part"] == 0 else "final"     # one survey, at the very end, comparing both versions
        st.rerun()
    t = tasks[sd["i"]]
    md(f'<div class="sect"><b>Version {sd["part"] + 1} of 2</b><span>Task {sd["i"] + 1} of {len(tasks)}</span></div>')
    if sd["i"] == 0:
        what = ("This version has an assistant that can search, tidy and edit your photos." if sd["cond"] == "PixelSense"
                else "This version is a regular photo gallery, like the ones on most phones.")
        md(f'<div class="card pad glass info"><p>{what} Try each task the way you normally would. The app notices when you are done. If it is too hard, tap <b>Give up</b>; that is useful for us.</p></div>')
    md(f'<div class="card pad glass" style="margin:10px 0"><div class="rtitle" style="font-size:17px">{esc(t["text"])}</div></div>')
    with st.container(key="sm_stb"):
        if st.button("Start task", type="primary", key="st_start"):
            sd.update(running=True, t0=time.time(), nav=0, undos=0, searches=0, opened0=set(S.opened), removed0=set(S.removed), copies0=len(S.copies),
                      fav0=set(S.fav), manual0=len(S.manual), excl0=set(S.excluded_imgs), gone=set())
            if sd["cond"] == "PixelSense":
                S.view = "home"
            else:
                S.bl_view, S.view = "photos", "baseline"
            st.rerun()


def study_survey():
    """Old progress files may still say 'survey': there is no survey after a single version any more, so move on."""
    sd = S.study
    sd["step"] = "between" if sd["part"] == 0 else "final"
    st.rerun()


def study_between():
    sd = S.study
    nxt = "PixelSense" if sd["order"][1] == "PixelSense" else "the Gallery"
    md(f'<div class="card pad glass info"><p><b>Version 1 is done. Thank you!</b></p>'
       f'<p>Next you will do similar tasks in {nxt}. Some photos will be different, so you cannot rely on what you remember.</p></div>')
    with st.container(key="sm_stb"):
        if st.button("Start version 2", type="primary", key="st_part2"):
            study_goto_part(1)
            st.rerun()


def study_final():
    """The only survey: how each version felt (same statements for both, side by side), then which one was better, then a comment."""
    sd = S.study
    md('<div class="sect"><b>Comparing the two versions</b></div>'
       '<div class="sub" style="margin-top:0">One short survey for both versions. “Gallery” is the regular photo gallery you used first; '
       '“PixelSense” is the version with the search bar. Everything is required except the last box.</div>')
    names = ("Gallery", "PixelSense")
    conds = ("Gallery (baseline)", "PixelSense")
    with st.form("final_form"):
        md('<div class="sect" style="margin-top:6px"><b>1. How did each version feel?</b></div>'
           '<div class="sub" style="margin-top:0">Pick a number for each. <b>1 = strongly disagree, 5 = strongly agree</b>.</div>')
        rated = {c: [] for c in conds}
        for i, q in enumerate(ST.SUS_ITEMS):
            text = sus_text(q).replace("this system", "this app").replace("the system", "the app")
            with st.container(key=f"cmp_box_{i}"):
                md(f'<div class="cmp-q">{i + 1}. {esc(text)}</div>')
                cols = st.columns(2)
                for col, nm, c in zip(cols, names, conds):
                    with col:
                        rated[c].append(st.selectbox(nm, [1, 2, 3, 4, 5], index=None, placeholder="Choose", format_func=lambda v: ST.AGREE_LABELS[v],
                                                     key=f"cmp_{'g' if nm == 'Gallery' else 'p'}_{i}"))
        md('<div class="sect" style="margin-top:14px"><b>2. Which one was better?</b></div>')
        ans = {}
        for q in ST.FINAL_FORM:
            with st.container(key=f"fin_box_{q['key']}"):
                ans[q["key"]] = st.radio(q["text"], q["options"], index=None, key=f"fin_{q['key']}")
        comment = st.text_area("Anything else you want to tell us? (optional)", key="fin_comment", height=90)
        submitted = st.form_submit_button("Finish", type="primary")
    if submitted:
        missing = [f"1.{i + 1} ({n})" for n, c in zip(names, conds) for i, v in enumerate(rated[c]) if v is None]
        missing += [f"2.{n + 1}" for n, q in enumerate(ST.FINAL_FORM) if ans[q["key"]] is None]
        if missing:
            st.warning("Please answer: " + ", ".join(missing) + ".")
            return
        for c in conds:
            row = dict(participant=sd["pid"], condition=c, sus_score=ST.sus_score(rated[c]))
            row.update({f"sus_{i + 1}": v for i, v in enumerate(rated[c])})
            ST.log_questionnaire(**row)
        ST.log_final(participant=sd["pid"], comment=comment.replace("\n", " "), **ans)
        sd["step"] = "done"
        study_clear_answers()
        st.rerun()


def study_done():
    sd = S.study
    md(f'<div class="card pad glass info"><p><b>All done. Thank you, {esc(sd["pid"])}!</b></p><p>Your answers have been saved. You can hand the device back.</p></div>')
    with st.expander("Researcher: download data"):
        c1, c2 = st.columns(2)
        for col, name in zip((c1, c2), ("tasks.csv", "questionnaires.csv")):
            with col:
                st.download_button(f"Download {name}", ST.read_csv_bytes(name), file_name=name, mime="text/csv", key=f"dl_{name}")
        c1, c2 = st.columns(2)
        for col, name in zip((c1, c2), ("participants.csv", "final.csv")):
            with col:
                st.download_button(f"Download {name}", ST.read_csv_bytes(name), file_name=name, mime="text/csv", key=f"dl_{name}")
    with st.container(key="sm_stb"):
        if st.button("Start next participant", type="primary", key="st_next"):
            st.query_params.clear()
            S.update(fresh_state())
            S.view = "welcome"
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
    selection_bar("photos", rows, "Photos" if S.hfilter == "All" else f"Photos ({S.hfilter})")
    groups = {}
    for r in sorted(rows, key=lambda r: (r.taken, r.id), reverse=True):
        d = E.taken_date(r)
        groups.setdefault((d.year, d.month) if d else (0, 0), []).append(r)
    for (y, mo), items in groups.items():
        label = date(y, mo, 1).strftime("%B %Y") if y else "Undated"
        md(f'<div class="monthh"><b>{label}</b><span>{len(items)} photo{"s" if len(items) != 1 else ""}</span></div>')
        select_grid(items, f"t{y}{mo}", "photos")


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
def ps_act(key, icon, label, fn, *args, active=False):
    tappable(key, f'<div class="ps-act{" on" if active else ""} pressable">{svg(icon, 24, "currentColor", 1.9, "currentColor" if active and icon == "heart" else "none")}<span>{label}</span></div>', fn, *args, label=label)


def toggle_fav(i):
    snap()
    S.fav.symmetric_difference_update({i})
    notify("Added to Favorites." if i in S.fav else "Removed from Favorites.")
    st.rerun()


def detail_order():
    """The photos the person can swipe through from the photo screen: the same list they opened it from."""
    back = S.back or "home"
    everything = [r.id for r in sorted(visible_rows(), key=lambda r: (r.taken, r.id), reverse=True)]
    if back == "collection" and S.cur_coll in all_cats():
        ids = coll_items(S.cur_coll)
    elif back == "photos":
        rows = visible_rows()
        if S.hfilter == "Favorites":
            rows = [r for r in rows if r.id in S.fav]
        elif S.hfilter != "All":
            rows = [r for r in rows if r.type.title() == S.hfilter]
        ids = [r.id for r in sorted(rows, key=lambda r: (r.taken, r.id), reverse=True)]
    elif back == "person" and S.cur_person:
        ids = person_images(S.cur_person)
    elif S.chat and [m for m in S.chat if m["role"] == "ai"]:
        ids = [i for i in [m for m in S.chat if m["role"] == "ai"][-1]["reply"].ids if i in R and visible(R[i])]
    else:
        ids = everything
    return ids if S.sel in ids else everything


def detail_step(d):
    ids = detail_order()
    if S.sel in ids:
        k = ids.index(S.sel) + d
        if 0 <= k < len(ids):
            S.sel = ids[k]
            S.opened.add(S.sel)
            S.scroll = False


def view_detail():
    if S.sel is None or S.sel not in R or not visible(R[S.sel]):
        go("home")
    ev = _SWIPE(key="sw_detail", default=None)      # swipe left = next photo, swipe right = previous (arrow keys on a computer)
    if isinstance(ev, dict) and ev.get("n") != S.get("sw_detail_n"):
        S.sw_detail_n = ev.get("n")
        detail_step(1 if ev.get("dir") == "next" else -1)
    r = R[S.sel]
    topbar("Photo", S.back or "home", "det")
    snack_ui()
    cur, (auto, reason) = cat_of(r), AUTO[r.id]
    moved = r.id in S.override
    d = E.taken_date(r)
    with st.container(key="stack_detail"):
        left, right = st.columns([5, 4])
        with left:
            md(f'<div class="hero-img" data-swipe-zone><img src="{img_uri(r.file, 900, 675)}" alt="{esc(r.description)}"></div>')
            order = detail_order()
            k = order.index(S.sel) if S.sel in order else 0
            with st.container(key="pkctl_det"):
                c = st.columns([1, 2, 1])
                with c[0]:
                    st.button("‹ Back", key="det_prev", on_click=detail_step, args=(-1,), disabled=k == 0, use_container_width=True)
                with c[1]:
                    md(f'<div class="pk-count" style="text-align:center;margin:10px 0 0">Photo {k + 1} of {len(order)} · swipe</div>')
                with c[2]:
                    st.button("Next ›", key="det_next", on_click=detail_step, args=(1,), disabled=k >= len(order) - 1, use_container_width=True)
        with right:
            md(f'<div class="dtitle">{esc(r.description)}</div>'
               f'<div class="ccount" style="margin-top:4px">{r.type.title()}' + (f' · Taken {d.strftime("%d %b %Y")}' if d else "") + '</div>')
            md(f'<div class="dcat"><span>Collection</span><b>{esc(cur)}</b><i>{"Moved by you" if moved else "Sorted by AI"}</i></div>')
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
            ev = []
            if S.query:
                ev = next((e for _, rr, e in E.search(make_ctx(), S.query) if rr.id == r.id), [])
            if ev:
                items = "".join(f'<div class="ev"><i>{svg("tick", 13, "#18936A", 3)}</i><span>{esc(E.ev_sentence(e))}</span></div>' for e in ev)
                md(f'<div class="card pad"><div class="sect" style="margin:0 0 4px"><b style="font-size:16px">Why this result?</b>'
                   f'<span>for “{esc(S.query)}”</span></div>{items}</div>')
            if r.visible_text:
                md(f'<div class="found"><small>Text found in image</small><div>{highlight(r.visible_text, list(E.search_terms(S.query)) if S.query else [])}</div></div>')
            if moved:
                with st.container(key="plain_reset"):
                    if st.button("Back to AI’s choice", key="d_reset"):
                        snap()
                        S.override.pop(r.id, None)
                        notify(f"Back in “{auto}”.")
                        st.rerun()
    md('<div style="height:90px"></div>')
    with st.container(key="psbar"):
        cols = st.columns(4)
        fav = r.id in S.fav
        with cols[0]:
            ps_act("d_fav", "heart", "Favorite", toggle_fav, r.id, active=fav)
        with cols[1]:
            ps_act("d_edit", "edit", "Edit", open_editor, r.id)
        with cols[2]:
            ps_act("d_move", "folder", "Collection", move_dialog, r.id)
        with cols[3]:
            ps_act("d_del", "trash", "Delete", remove_dialog, r.id)


# ---- photo editor ------------------------------------------------------------------------------------------
_CROP_FRAME = components.declare_component("crop_frame", path=str(ROOT / "crop_frame"))
_LONGPRESS = components.declare_component("longpress", path=str(ROOT / "longpress"))
_SWIPE_HTML = r'''<!doctype html>
<html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:transparent}</style></head>
<body>
<script>
  // Invisible helper: lets a photo screen be swiped left / right (phone) or moved with the arrow keys (computer).
  // It listens on the parent page, but only while the page contains an element marked data-swipe-zone (the photo viewer or the
  // "add photos" preview). A swipe left means "next photo", a swipe right means "previous photo". Python gets {dir, n}.
  function send(type, data) { window.parent.postMessage(Object.assign({ isStreamlitMessage: true, type: type }, data), "*"); }
  var P = window.parent;
  P.__psSwSend = function (dir) { send("streamlit:setComponentValue", { value: { dir: dir, n: Date.now() }, dataType: "json" }); };
  if (!P.__psSwInstalled) {
    P.__psSwInstalled = true;
    var doc = P.document, sx = 0, sy = 0, t0 = 0, tracking = false;
    function zoneActive() { return !!doc.querySelector("[data-swipe-zone]"); }
    function blocked(t) {
      return !!(t && t.closest && t.closest("button, input, textarea, select, a, [role='slider'], [data-baseweb='slider'], [data-testid='stSlider']"));
    }
    doc.addEventListener("touchstart", function (e) {
      if (!zoneActive() || e.touches.length !== 1 || blocked(e.target)) { tracking = false; return; }
      var t = e.touches[0];
      sx = t.clientX; sy = t.clientY; t0 = Date.now(); tracking = true;
    }, { passive: true, capture: true });
    doc.addEventListener("touchend", function (e) {
      if (!tracking) return;
      tracking = false;
      var t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
      // a quick, mostly sideways flick of at least 60 px (so a normal scroll or a tap never counts)
      if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5 && Date.now() - t0 < 900) {
        if (P.__psSwSend) P.__psSwSend(dx < 0 ? "next" : "prev");
      }
    }, { passive: true, capture: true });
    doc.addEventListener("keydown", function (e) {
      if (!zoneActive()) return;
      var tag = (e.target && e.target.tagName) || "";
      if (/INPUT|TEXTAREA|SELECT/.test(tag)) return;
      if (e.key === "ArrowLeft") { if (P.__psSwSend) P.__psSwSend("prev"); }
      else if (e.key === "ArrowRight") { if (P.__psSwSend) P.__psSwSend("next"); }
    }, true);
  }
  window.addEventListener("message", function (ev) {
    if (ev.data && ev.data.type === "streamlit:render") send("streamlit:setFrameHeight", { height: 0 });
  });
  send("streamlit:componentReady", { apiVersion: 1 });
  send("streamlit:setFrameHeight", { height: 0 });
</script>
</body></html>
'''
try:                                        # the helper lives in swipe/index.html; if that folder was never uploaded (git), it is recreated here
    (ROOT / "swipe").mkdir(exist_ok=True)
    if not (ROOT / "swipe" / "index.html").exists():
        (ROOT / "swipe" / "index.html").write_text(_SWIPE_HTML, encoding="utf-8")
except OSError:
    pass
_SWIPE = components.declare_component("swipe", path=str(ROOT / "swipe"))
ED_EXAMPLES = [("Brighter", "make it brighter"), ("B&W", "make it black and white"),
               ("Square crop", "crop to a square"), ("Vintage", "give it a vintage look")]


def pil_uri(im, q=88):
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def ed_size(i):
    return ImageOps.exif_transpose(Image.open(ROOT / R[i].file)).size


def ed_default_crop(i, asp, rot):
    """Centred frame with the chosen ratio, on the rotated photo, as percent trimmed from (left, top, right, bottom)."""
    w, h = ed_size(i)
    if rot in (90, 270):
        w, h = h, w
    ratio = ED.ASPECTS.get(asp)
    if not ratio:
        return (0.0, 0.0, 0.0, 0.0)
    if w / h > ratio:
        trim = round((1 - (h * ratio) / w) / 2 * 100, 2)
        return (trim, 0.0, trim, 0.0)
    trim = round((1 - (w / ratio) / h) / 2 * 100, 2)
    return (0.0, trim, 0.0, trim)


def ed_reframe():
    """Put the crop frame back to the default for the current ratio and rotation (also tells the frame widget to redraw)."""
    S.ed_crop = ed_default_crop(S.sel, S.get("ed_asp", "Original"), S.get("ed_rot", 0))
    S.ed_nonce = S.get("ed_nonce", 0) + 1


def ed_reset():
    for k in [k for k in S.keys() if str(k).startswith("ed_") and k not in ("ed_dest", "ed_nonce")]:
        del S[k]
    S.ed_nonce = S.get("ed_nonce", 0) + 1


def ed_show_frame():
    S.ed_view = "Crop frame"


def ed_show_preview():
    S.ed_view = "Preview"


ED_HELP = ("I can change brightness, contrast, colour, warmth, sharpness, black & white, sepia, vintage, rotate, flip, crop "
           "(square, 4:3, 16:9 …) and upscale 2x or 4x. Try “warmer and sharper” or “rotate right and crop to 16:9”.")


def ed_prompt_apply(text=None):
    """Turn a typed request into slider / crop settings. Runs as a callback, so it only sets state; the controls then show the result."""
    t = (text if text is not None else S.get("ed_prompt", "")).strip()
    S["ed_prompt"] = ""
    if not t:
        return
    track("edit_prompt", words=len(t.split()))
    if re.search(r"\b(reset|start over|revert|undo (all|everything)|original)\b", t, re.I) and not ED.parse_edit(t):
        ed_reset()
        S.ed_msg = ("ok", "Back to the original photo.")
        return
    parsed = ED.parse_edit(t) or ED.parse_edit("make it " + t)   # allow bare requests such as "black and white"
    if not parsed:
        S.ed_msg = ("warn", "I couldn’t turn that into an edit. " + ED_HELP)
        return
    o = parsed[0]

    def add(key, delta, lo, hi):
        S[key] = max(lo, min(hi, int(S.get(key, 0)) + int(delta)))

    if o["auto"]:
        S["ed_auto"] = True
    if o["brightness"]: add("ed_b", o["brightness"], -50, 50)
    if o["contrast"]: add("ed_c", o["contrast"], -50, 50)
    if o["saturation"]: add("ed_sat", o["saturation"], -60, 60)
    if o["warmth"]: add("ed_warm", o["warmth"], -50, 50)
    if o["sharpness"]: add("ed_sharp", o["sharpness"], -50, 100)
    if o["filter"] != "None": S["ed_look"] = o["filter"]
    if o["scale"] > 1: S["ed_sc"] = o["scale"]
    needs_frame = False
    if o["rotate"]:
        S["ed_rot"] = (int(S.get("ed_rot", 0)) + o["rotate"]) % 360
        needs_frame = True
    if o["flip"]:
        S["ed_flip"] = not S.get("ed_flip", False)
        needs_frame = True
    if o["aspect"] != "Original":
        S["ed_asp"] = o["aspect"]
        needs_frame = True
    if needs_frame:
        ed_reframe()
    S.ed_msg = ("ok", "Done: " + ", ".join(ED.describe(o)) + ". Fine-tune below, then save a copy.")


def view_edit():
    if S.sel is None or S.sel not in R or not visible(R[S.sel]):
        go("home")
    r = R[S.sel]
    topbar("Edit photo", "detail", "edit")
    snack_ui()
    src = Image.open(ROOT / r.file)
    small = ImageOps.exif_transpose(src).convert("RGB")
    small.thumbnail((1100, 1100))
    nonce = S.get("ed_nonce", 0)
    with st.container(key="stack_edit"):
        left, right = st.columns([5, 4])

        # ---- left: the photo. "Crop frame" shows a draggable frame, "Preview" shows the live result ----
        with left:
            if "ed_view" not in S:
                S["ed_view"] = "Crop frame"     # open straight into the draggable crop box
            st.radio("View", ["Crop frame", "Preview"], horizontal=True, key="ed_view", label_visibility="collapsed")
            crop_mode = S.get("ed_view") == "Crop frame"
            if crop_mode:
                rot_now, flip_now = S.get("ed_rot", 0), S.get("ed_flip", False)
                # show the photo with every other edit applied, so you crop what you will actually get
                base = ED.apply(small, ED.new_ops(
                    brightness=S.get("ed_b", 0), contrast=S.get("ed_c", 0), saturation=S.get("ed_sat", 0),
                    warmth=S.get("ed_warm", 0), sharpness=S.get("ed_sharp", 0), auto=S.get("ed_auto", False),
                    filter=S.get("ed_look", "None"), rotate=rot_now, flip=flip_now))
                fw, fh = ed_size(r.id)
                if rot_now in (90, 270):
                    fw, fh = fh, fw
                # on a phone the frame is as wide as the photo's shape allows in the space above the tool panel, so the whole photo shows without scrolling
                md(f"<style>@media (max-width:767px){{.st-key-ed_cropwrap{{width:min(100%,calc((60dvh - 150px - var(--sbo,0px)) * {fw / fh:.4f}))!important;margin:0 auto!important}}}}</style>")
                with st.container(key="ed_cropwrap"):
                    v = _CROP_FRAME(img=pil_uri(base, 85), crop=list(S.get("ed_crop", (0.0, 0.0, 0.0, 0.0))),
                                    ratio=ED.ASPECTS.get(S.get("ed_asp", "Original")), nonce=nonce, full_w=fw, full_h=fh,
                                    key="ed_cropper", default=None)
                if isinstance(v, dict) and v.get("nonce") == nonce and v.get("crop"):
                    S.ed_crop = tuple(float(x) for x in v["crop"])
                d1, d2 = st.columns(2)
                with d1:
                    st.button("Reset frame", key="ed_frame_reset", on_click=ed_reframe)
                with d2:
                    st.button("Done cropping", key="ed_frame_done", type="primary", on_click=ed_show_preview)
            else:
                show_orig = st.toggle("Show original", key="ed_orig")
                preview_slot = st.empty()

        # ---- right: prompt, then the manual controls ----
        with right:
            with st.container(key="ed_prompt_box"):
                pc1, pc2 = st.columns([5, 2])
                with pc1:
                    st.text_input("Edit with a prompt", key="ed_prompt", on_change=ed_prompt_apply,
                                  placeholder="e.g. make it brighter and crop to a square")
                with pc2:
                    md('<div style="height:28px"></div>')
                    st.button("Apply", key="ed_prompt_go", type="primary", on_click=ed_prompt_apply)
                with st.container(key="chips_edit"):
                    ec = st.columns(len(ED_EXAMPLES))
                    for col, (label, text) in zip(ec, ED_EXAMPLES):
                        with col:
                            st.button(label, key=f"ed_ex_{slug(label)}", on_click=ed_prompt_apply, args=(text,))
                msg = S.get("ed_msg")
                if msg:
                    md(f'<div class="ccount" style="margin:4px 0 8px">{esc(msg[1])}</div>')

            with st.container(key="ed_tabs_box"):
                t_adj, t_crop, t_look, t_res = st.tabs(["Adjust", "Crop & rotate", "Filters", "Resolution"])
                with t_adj:
                    auto = st.toggle("Auto-enhance", key="ed_auto")
                    b = st.slider("Brightness", -50, 50, 0, key="ed_b")
                    c = st.slider("Contrast", -50, 50, 0, key="ed_c")
                    sat = st.slider("Colour", -60, 60, 0, key="ed_sat")
                    warm = st.slider("Warmth", -50, 50, 0, key="ed_warm")
                    sharp = st.slider("Sharpness", -50, 100, 0, key="ed_sharp")
                with t_crop:
                    asp = st.selectbox("Crop shape", list(ED.ASPECTS), key="ed_asp", on_change=ed_reframe,
                                       help="Original = free crop. Any other choice locks the frame to that ratio.")
                    st.button("Crop with the frame", key="ed_open_frame", on_click=ed_show_frame, disabled=crop_mode)
                    rot = st.radio("Rotate", [0, 90, 180, 270], horizontal=True, format_func=lambda d: f"{d}°", key="ed_rot", on_change=ed_reframe)
                    flip = st.toggle("Flip horizontally", key="ed_flip", on_change=ed_reframe)
                    st.caption("Rotating, flipping or changing the crop shape puts the frame back in the centre.")
                with t_look:
                    look = st.radio("Look", ED.FILTERS, horizontal=True, key="ed_look")
                with t_res:
                    sc = st.radio("Output size", [1, 2, 4], horizontal=True, format_func=lambda x: "Original" if x == 1 else f"{x}x larger", key="ed_sc")
                    st.caption("Resizes with high-quality resampling and gentle sharpening. It cannot invent detail the way a generative AI would.")

            crop = tuple(S.get("ed_crop", (0.0, 0.0, 0.0, 0.0)))
            ops = ED.new_ops(brightness=b, contrast=c, saturation=sat, warmth=warm, sharpness=sharp, auto=auto, aspect="Original",
                             crop=crop, rotate=rot, flip=flip, filter=look, scale=sc)
            opts = ["Edited"] + [x for x in all_cats() if x not in S.excluded_cats and x != "Edited"]
            with st.container(key="ed_dest_box"):
                dest = st.selectbox("Save copy to collection", opts, key="ed_dest")
            with st.container(key="edact"):
                c1, c2 = st.columns(2)
                with c1:
                    st.button("Reset", key="ed_reset", on_click=ed_reset)
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

        # ---- fill the preview now that every setting is known ----
        if not crop_mode:
            with left:
                shown = small if show_orig else ED.apply(small, {**ops, "scale": 1})
                with preview_slot.container():
                    md(f'<div class="edprev"><img src="{pil_uri(shown)}" alt="Preview"></div>')
                    done = ED.describe(ops)
                    md(f'<div class="ccount" style="margin-top:2px">{esc(", ".join(done).capitalize()) if done else "No changes yet"} · original {src.size[0]}×{src.size[1]} px'
                       + (f' · saved copy will be {min(sc, 4096 / max(src.size)) * max(src.size):.0f}px on the long side' if sc > 1 else '') + '</div>')


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
    cards = [("cl_fav", f'<div class="card crow pressable"><div class="cthumb" style="background:#FFE9EC;color:#D6455D">{svg("heart", 24, "#D6455D", 2, "#D6455D")}</div>'
                        f'<div style="flex:1;min-width:0"><div class="rtitle" style="font-size:15.5px">Favorites</div><div class="ccount">{len([i for i in S.fav if i in R and visible(R[i])])} items</div></div>'
                        f'<div class="chev">{svg("chev", 20)}</div></div>', nav_to, "favorites", "Open Favorites")]
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


def restore_all():
    snap()
    S.removed.clear()
    notify("All photos restored.")
    st.rerun()


def restore_selected(ids):
    snap()
    S.removed.difference_update(ids)
    for i in ids:
        untick_later(sel_key("trash", i))
    notify(f"{len(ids)} photo{'s' if len(ids) != 1 else ''} restored.")
    st.rerun()


def flip_tick(i, scope):
    """Tapping a photo in Trash ticks or unticks it (a tick square can only change before it is drawn, so the router does it next run)."""
    S.setdefault("_flip", []).append(sel_key(scope, i))
    st.rerun()


def view_trash():
    appbar("Trash")
    snack_ui()
    gone = [R[i] for i in sorted(S.removed, key=lambda x: int(x[3:]))]
    if not gone:
        empty_state("trash", "Trash is empty", "Photos you delete show up here so you can bring them back.")
        return
    ids = [r.id for r in gone]
    picked = [i for i in ids if S.get(sel_key("trash", i))]
    md(f'<div class="sub" style="margin-top:6px">{len(gone)} deleted photo{"s" if len(gone) != 1 else ""}. Tap photos to choose them, or restore everything.</div>')
    with st.container(key="trashbar"):
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"Restore selected ({len(picked)})", key="tr_restore_sel", type="primary", disabled=not picked):
                restore_selected(picked)
        with c2:
            if st.button("Restore all", key="tr_restore_all"):
                restore_all()
    select_grid(gone, "tr", "trash", n=6, opener=flip_tick, extra=("trash",))


def view_collection():
    name = S.cur_coll
    if name not in all_cats() or name in S.excluded_cats:
        go("collections")
    topbar(name, "collections", "coll")
    snack_ui()
    items = [R[i] for i in coll_items(name)]
    md(f'<div class="sub" style="margin-top:0">{len(items)} item{"s" if len(items) != 1 else ""}</div>')
    with st.container(key="coll_actions"):
        ca, cb = st.columns(2)
        with ca:
            if st.button("+ Add photos", key="coll_add_photos", type="primary"):
                add_photos_dialog(name)
        with cb:
            if st.button("Rename", key="coll_rename", icon=":material/edit:"):
                rename_collection_dialog(name)
    if items:
        selection_bar(f"c_{slug(name)}", items, f"“{name}”")
        select_grid(items, "cg", f"c_{slug(name)}")
    else:
        empty_state("folder", "This collection is empty", "Tap Add photos to fill it.")
    md('<div style="height:8px"></div>')
    with st.container(key="danger_delcoll"):
        if st.button("Delete collection", key="coll_del"):
            delete_collection_dialog(name)
    if name not in S.extra_cats:
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
    nm = len([p for p, n in S.names.items() if n != E.PRESET_NAMES.get(p)]) + len(S.hidden_people)   # names you added or changed
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
                S.names, S.hidden_people, S.notp = dict(E.PRESET_NAMES), set(), set()
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
       '<div class="sub" style="margin-top:0">Simulate new photos arriving, or reset everything so the next participant starts fresh.</div>')
    with st.container(key="sm_arrive"):
        if st.button(f"Simulate {len(HELD)} new photos arriving", key="arrive", disabled=len(S.arrived) == len(HELD)):
            S.arrived = set(HELD)
            live = [i for i in sorted(HELD) if visible(R[i])]
            cats = sorted({cat_of(R[i]) for i in live})
            notify(f"{len(HELD)} new photos arrived. " + (f"{len(live)} sorted into {', '.join(cats)}." if live else "AI is paused for them."), False)
            st.rerun()
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


def ps_nav():
    """One bar along the bottom on every screen size: Home, Photos, People, Collections, Clean up, Trash."""
    if S.view in ("welcome", "analysing", "detail", "edit"):
        return
    cur = {"home": "home", "memory": "home", "attention": "home", "chat": "home", "results": "home", "photos": "photos", "people": "people", "person": "people",
           "collections": "collections", "collection": "collections", "trash": "trash", "cleanup": "cleanup"}.get(S.view, "")
    n_clean = sum(len(v) for v in E.cleanup_groups(visible_rows(), S.kept).values())
    items = [("home", "Home", "home", ""), ("photos", "Photos", "image", ""), ("people", "People", "users", ""),
             ("collections", "Collections", "folder", ""), ("cleanup", "Clean up", "sparkle", str(n_clean) if n_clean else ""),
             ("trash", "Trash", "trash", str(len(S.removed)) if S.removed else "")]
    with st.container(key="psnav"):
        cols = st.columns(len(items))
        for col, (key, label, icon, badge) in zip(cols, items):
            with col:
                tappable(f"nv_{key}", f'<div class="ps-nv{" on" if cur == key else ""} pressable">{svg(icon, 24)}<span>{label}</span>'
                                      + (f'<em>{badge}</em>' if badge else "") + '</div>', nav_to, key, label=label)


# --------------------------------------------------------------------------- router
VIEWS = {"attention": view_attention, "study": view_study, "baseline": view_baseline, "edit": view_edit, "home": view_home, "cleanup": view_cleanup, "memory": view_memory, "welcome": view_welcome, "analysing": view_analysing, "chat": view_chat, "photos": view_photos,
         "results": view_results, "people": view_people, "person": view_person, "detail": view_detail,
         "collections": view_collections, "collection": view_collection, "settings": view_settings, "trash": view_trash}
if not S.get("restore_done"):
    # A refresh starts a new session; the URL (?pid=P01) and study_data/progress_P01.json bring the participant back to where they were.
    S.restore_done = True
    _pid = st.query_params.get("pid")
    _prog = ST.load_progress(_pid) if _pid else None
    if _prog and _prog.get("step") not in (None, "done"):
        _prog.update(running=False, nav=0, undos=0)
        if _prog["step"] == "seq":
            _prog["step"] = "tasks"
        S.study, S.view = _prog, "study"
if S.study and S.study.get("running") and S.study["cond"] != "PixelSense":
    S.view = "baseline"                  # the baseline condition is a plain gallery with no assistant and no navigation
install_as_app()
if S.study:
    study_autocheck()
for _k in S.pop("_untick", []):
    S[_k] = False                      # photos that were moved, kept or deleted lose their tick
for _k in S.pop("_flip", []):
    S[_k] = not S.get(_k, False)       # a photo tapped in Trash is ticked / unticked
with st.container(key=f"v_{S.view}"):
    VIEWS.get(S.view, view_chat)()
if S.study and S.study.get("running"):
    study_bar()

if S.view not in ("baseline", "study"):
    ps_nav()          # no app navigation on the baseline or on study screens, so a participant cannot wander into the other version

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