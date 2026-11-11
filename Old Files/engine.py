"""PixelSense engine: data, simulated AI sorting, search, face groups, and the assistant's answers.

Everything here is plain Python (no Streamlit) so it can be tested on its own.
It is a prototype stand-in for a real model: sorting is rule-based, in-image text and face boxes are prepared
in manifest.csv / faces.csv, and answers are extracted from that prepared text. Nothing is generated.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Callable

import pandas as pd

import editor

ROOT = Path(__file__).parent

# --------------------------------------------------------------------------- data
df = pd.read_csv(ROOT / "manifest.csv").fillna("")
R = {r.id: r for r in df.itertuples()}
FACES = pd.read_csv(ROOT / "faces.csv") if (ROOT / "faces.csv").exists() else pd.DataFrame(
    columns=["image_id", "person_id", "x", "y", "w", "h"])
FACE_OF = {(r.image_id, r.person_id): (int(r.x), int(r.y), int(r.w), int(r.h)) for r in FACES.itertuples()}
PERSON_IMAGES: dict[str, list[str]] = {}
for _r in FACES.itertuples():
    PERSON_IMAGES.setdefault(_r.person_id, []).append(_r.image_id)
# default names "Person 1..N": most photos first, so the numbering is stable
PNUM = {pid: n + 1 for n, (pid, _) in enumerate(sorted(PERSON_IMAGES.items(), key=lambda kv: (-len(kv[1]), kv[0])))}
FACES_IN: dict[str, list[str]] = {}
for _r in FACES.itertuples():
    FACES_IN.setdefault(_r.image_id, []).append(_r.person_id)

CAT_ORDER = ["Travel", "Family", "Bills & Receipts", "Study", "Shopping", "Food", "Events", "Everyday"]
CAT_RULES = [  # simulated AI: first matching rule wins (whole words only)
    ("Travel", ["flight", "boarding", "beach", "hiking", "mountains", "sunset", "sea", "trip", "seat", "gate"]),
    ("Family", ["family", "cousins", "wedding", "birthday", "parents", "father", "mother", "daughter", "children"]),
    ("Study", ["assignment", "lecture", "hci", "cognitive", "lms", "submit", "deadline", "notes", "notebook", "handwritten"]),
    ("Shopping", ["sale", "listing", "laptop", "shoes"]),
    ("Food", ["biryani", "food", "cake"]),
    ("Events", ["fest", "poster", "event", "concert"]),
]
HELD = {"img03", "img07", "img16"}  # "new images" the researcher can make arrive
TYPE_WORDS = {"photo": "photo", "photos": "photo", "screenshot": "screenshot", "screenshots": "screenshot",
              "receipt": "receipt", "receipts": "receipt", "bill": "bill", "bills": "bill", "ticket": "ticket",
              "tickets": "ticket", "document": "document", "documents": "document"}
SUGGESTIONS = ["When is my HCI assignment due?", "Show photos of Person 1", "How much is the electricity bill?",
               "Who is in the dinner photo?", "Create a collection called Eid with family dinner photos"]
SYN = {"grocery": ["supermarket", "imtiaz"], "groceries": ["supermarket", "imtiaz"], "trip": ["travel", "beach", "flight"], "pic": ["photo"], "pics": ["photo"], "picture": ["photo"],
       "money": ["rs", "total"], "paid": ["receipt", "total"], "holiday": ["travel", "trip"],
       "shopping": ["sale", "listing"], "assignment": ["hci", "deadline", "submit"], "lecture": ["cognitive", "theory"],
       "selfie": ["selfie"], "notes": ["handwritten", "notebook", "lecture"], "notebook": ["notes", "handwritten"], "writing": ["handwritten"],
       "ocean": ["sea", "coast"], "water": ["sea", "waves"], "sand": ["dunes", "beach"], "crowd": ["street"], "dinner": ["dining"], "glasses": ["glasses"], "kids": ["children", "daughter"], "wedding": ["family"]}
STOP = {"the", "a", "an", "of", "my", "me", "i", "to", "for", "from", "with", "that", "in", "on", "and", "find",
        "show", "where", "is", "are", "was", "were", "do", "does", "did", "have", "has", "any", "all", "some",
        "please", "can", "you", "give", "get", "look", "up", "what", "when", "who", "whom", "which", "how", "much",
        "many", "there", "this", "these", "those", "it", "its", "at", "by", "about", "photo", "photos", "image",
        "images", "picture", "pictures", "pics", "pic", "total", "amount", "price", "cost", "time", "day", "date",
        "count", "number", "s", "anyone", "anybody", "someone", "somebody", "everyone", "r", "u", "ur", "pls", "plz", "wearing", "wear", "wears", "wore", "dressed", "having", "got", "show", "me", "photu", "pix", "snaps", "shots", "whats", "who's", "tell", "ask", "mine", "our", "us", "we", "them", "or"}
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december"]


def auto_category(r):
    """(category, plain-language reason). Rules on prepared text, standing in for a real model."""
    if r.album == "Private":
        return "Sensitive", "it looks like a private message or note"
    if r.type in ("receipt", "bill"):
        return "Bills & Receipts", f"it is a {r.type}"
    toks = set(re.findall(r"\w+", (r.description + " " + r.visible_text).lower()))
    for name, kws in CAT_RULES:
        hit = next((k for k in kws if k in toks), None)
        if hit:
            return name, f"it mentions “{hit}”"
    return "Everyday", "nothing in it pointed to a more specific collection"


AUTO = {r.id: auto_category(r) for r in df.itertuples()}


def taken_date(r):
    try:
        return datetime.strptime(r.taken, "%Y-%m-%d").date()
    except ValueError:
        return None


# --------------------------------------------------------------------------- context handed in by the app
@dataclass
class Ctx:
    """A snapshot of what the AI may use right now. The app builds one per run."""
    rows: list                                   # visible image rows
    cat_of: Callable                             # row -> collection name
    names: dict = field(default_factory=dict)    # person id -> display name (shown people only)
    people_ids: dict = field(default_factory=dict)  # person id -> visible image ids
    fav: set = field(default_factory=set)
    faces_on: bool = False
    custom_collections: list = field(default_factory=list)
    last_ids: list = field(default_factory=list)   # photos in the assistant's last answer ("make it brighter")
    collections: list = field(default_factory=list)


@dataclass
class Reply:
    kind: str                       # results | answer | count | people | command | none | info
    text: str
    ids: list = field(default_factory=list)
    sources: list = field(default_factory=list)   # [(image id, snippet)]
    steps: list = field(default_factory=list)     # "how I found this"
    chips: list = field(default_factory=list)     # follow-up suggestions
    cmd: dict | None = None
    person: str | None = None
    query: str = ""


# --------------------------------------------------------------------------- search
def search_terms(q):
    toks = [t for t in re.findall(r"\w+", q.lower()) if t not in STOP]
    out = {}
    for t in toks:
        out.setdefault(t, None)
    for t in toks:
        if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
            out.setdefault(t[:-1], t)
        for x in SYN.get(t, []):
            out.setdefault(x, t)
    return out  # term -> word the user typed (None if typed directly)


COLORS = {"red", "green", "blue", "pink", "purple", "yellow", "orange", "white", "black", "brown", "grey", "gray", "beige",
          "gold", "maroon", "olive", "magenta", "cream", "violet"}
WEAR_RE = re.compile(r"\b(wear|wearing|wears|wore|dressed|clothes|outfit)\b", re.I)


def search(ctx, q, rfilter="All", rows=None):
    """[(score, row, evidence)] best first. Evidence = [(kind, term, origin)].
    Looks at: text inside the image, what is visible (tags and clothing), the description, then type and collection."""
    terms = search_terms(q)
    typed = [t for t, o in terms.items() if o is None]
    colours = [t for t in typed if t in COLORS]
    wear = bool(WEAR_RE.search(q))
    out = []
    for r in (rows if rows is not None else ctx.rows):
        if rfilter not in ("All", "Text in images") and r.type.title() != rfilter:
            continue
        tags = (getattr(r, "tags", "") + " " + getattr(r, "wearing", "")).lower()
        if colours:   # a colour is a hard requirement: "wearing green" must not return photos with no green in them
            hay = getattr(r, "wearing", "").lower() if wear else (tags + " " + r.description.lower() + " " + r.visible_text.lower())
            if not all(re.search(rf"\b{c}\b", hay) for c in colours):
                continue
        ev, score, hits = [], 0.0, 0
        meta = (r.type + " " + ctx.cat_of(r)).lower()
        for term, origin in terms.items():
            w = 1.0 if origin is None else 0.5
            if term in r.visible_text.lower():
                ev.append(("text", term, origin)); score += 4 * w
            elif re.search(rf"\b{re.escape(term)}", tags):
                ev.append(("tag", term, origin)); score += 3 * w
            elif term in r.description.lower():
                ev.append(("desc", term, origin)); score += 2 * w
            elif term in meta:
                ev.append(("meta", term, origin)); score += 1 * w
            else:
                continue
            hits += origin is None
        if rfilter == "Text in images" and not any(k == "text" for k, _, _ in ev):
            continue
        if score:
            out.append((hits, score, r, ev))
    out.sort(key=lambda x: (-x[0], -x[1]))
    # when the user typed several words, keep only rows that matched the most typed words
    if len(typed) > 1 and out:
        top = out[0][0]
        out = [x for x in out if x[0] >= max(1, top)] if top >= 2 else out
    return [(s, r, ev) for _, s, r, ev in out]


def ev_sentence(e):
    kind, term, origin = e
    base = {"text": "appears as text inside this image", "desc": "matches the image description",
            "meta": "matches its type or collection", "tag": "matches what is visible in the image"}[kind]
    return f"Related word “{term}” (from “{origin}”) {base}" if origin else f"“{term}” {base}"


# --------------------------------------------------------------------------- helpers for answers
def find_people(ctx, q):
    """Person ids named in the question, and the question with those names removed."""
    low, found = " " + q.lower() + " ", []
    for pid, name in sorted(ctx.names.items(), key=lambda kv: -len(kv[1])):
        pat = re.compile(r"(?<!\w)" + re.escape(name.lower()) + r"(?!\w)")
        if pat.search(low):
            found.append(pid)
            low = pat.sub(" ", low)
    return found, low.strip()


MON3 = "|".join(m[:3] for m in MONTHS)
DATE_RE = re.compile(rf"\b(\d{{1,2}})\s+({MON3})[a-z]*\b(?:\s+(\d{{4}}))?", re.I)
MONEY_RE = re.compile(r"\bRs\.?\s?[\d,]+", re.I)
TIME_RE = re.compile(r"\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b", re.I)


def month_filter(q):
    """('in October' | 'October photos') -> (month index, year|None, query without it)."""
    m = re.search(rf"\b(?:in|from|during|of|on)\s+({'|'.join(MONTHS)})(?:\s+(\d{{4}}))?\b", q, re.I) or \
        re.search(rf"\b({'|'.join(MONTHS)})(?:\s+(\d{{4}}))?\s+(?:photos|pictures|pics|images)\b", q, re.I)
    if not m:
        return None, None, q
    return MONTHS.index(m.group(1).lower()) + 1, int(m.group(2)) if m.group(2) else None, (q[:m.start()] + " " + q[m.end():]).strip()


def snippet(r, terms):
    return r.visible_text or r.description


def person_label(ctx, pid):
    return ctx.names.get(pid, f"Person {PNUM.get(pid, '?')}")


def make_steps(ctx, q, hits, extra=()):
    terms = [t for t, o in search_terms(q).items() if o is None]
    s = [f"Read your question and looked for: {', '.join(terms) if terms else 'no specific words'}.",
         f"Checked the text and descriptions of {len(ctx.rows)} photos the AI is allowed to use."]
    if hits:
        s.append(f"Best match: “{hits[0][1].description}”.")
    s.extend(extra)
    return s


def src(r, terms=None):
    return (r.id, snippet(r, terms))


# --------------------------------------------------------------------------- the assistant
def answer(ctx, q):  # noqa: C901 - one readable decision list on purpose
    q = (q or "").strip()
    low = q.lower().strip(" ?!.")
    if not low:
        return Reply("none", "Ask me about your photos.")
    if low in {"yes", "y", "yeah", "yep", "ok", "okay", "sure", "thanks", "thank you", "thx", "cool", "great", "nice", "no", "nope"}:
        return Reply("none", "Nothing to confirm, I only search and run commands when you ask. What would you like to find next?",
                     chips=["Show my latest photos"], query=q)
    if low in {"hi", "hello", "hey"}:
        return Reply("none", "Hi! Ask about your photos, for example “photos from September” or “how much is the electricity bill?”.",
                     chips=["Show my latest photos"], query=q)

    # ---- conversation, undo and photo editing ----------------------------------------------------
    talk = small_talk(low)
    if talk:
        return talk
    if re.match(r"^(?:please\s+)?undo(?:\s+(?:that|it|the last (?:change|edit|action)))?$", low):
        return Reply("command", "Undone.", cmd={"type": "undo"}, query=q)
    pe = editor.parse_edit(q)
    if pe:
        ops, target_q, coll, pron = pe
        pool = {r.id for r in ctx.rows}
        ids = [i for i in (ctx.last_ids if pron else answer_find(ctx, target_q, allow_count=False).ids) if i in pool][:6]
        if not ids:
            return Reply("info", "Which photo should I edit? Try “brighten the cat photo”, or open a photo and tap **Edit**.",
                         chips=["Show my latest photos"], query=q)
        name = next((c for c in ctx.collections if c.lower() == (coll or "").lower()), None) or (coll.strip().title() if coll else "Edited")
        what = ", ".join(editor.describe(ops))
        return Reply("command", f"I will {what}.", ids=ids, query=q, chips=["Open in editor"],
                     cmd={"type": "edit_photos", "ids": ids, "ops": ops, "collection": name},
                     steps=[f"Understood: edit {len(ids)} photo{'s' if len(ids) != 1 else ''} ({what}).",
                            f"The result is saved as a new copy in “{name}”. Your original is never changed.",
                            "Editing uses ordinary image processing on this device, not a generative model."])

    # ---- commands -------------------------------------------------------------------------------
    m = re.match(r"^(?:please\s+)?(?:create|make|start|add|new)\s+(?:a\s+|an\s+|new\s+)?(?:collection|album)"
                 r"(?:\s+(?:called|named))?\s+[\"“']?(?P<name>.+?)[\"”']?(?:\s+(?:with|from|of|using|containing)\s+(?P<q>.+))?$",
                 q, re.I)
    if m:
        name = m.group("name").strip().strip("\"“”'")
        sub = (m.group("q") or "").strip()
        ids, how = [], ""
        if sub:
            sub_reply = answer_find(ctx, sub, allow_count=False)
            ids = sub_reply.ids
            how = f" with the {len(ids)} photo{'s' if len(ids) != 1 else ''} that match “{sub}”"
        text = f"Created the collection **{name}**" + (how if sub else "") + "." if (ids or not sub) else \
            f"I made the collection **{name}**, but nothing matched “{sub}”, so it is empty."
        return Reply("command", text, ids=ids[:6], cmd={"type": "create_collection", "name": name, "ids": ids},
                     steps=[f"Understood: create a collection called “{name}”" + (f", filled from a search for “{sub}”." if sub else ".")],
                     query=q)
    m = re.match(r"^(?:rename|call|name)\s+(?P<who>.+?)\s+(?:to|as)\s+(?P<new>.+)$", q, re.I)
    if m:
        who, _ = find_people(ctx, m.group("who"))
        if not ctx.faces_on:
            return Reply("info", "Face groups are off. Turn them on in People first.", chips=["Open People"])
        if who:
            new = m.group("new").strip().strip("\"“”'")
            return Reply("command", f"Done. **{person_label(ctx, who[0])}** is now **{new}**.", person=who[0],
                         cmd={"type": "rename_person", "pid": who[0], "name": new}, query=q,
                         steps=["Understood: rename a face group. Only you can name people."])
        return Reply("info", "I could not tell which person you mean. Open People to see everyone.", chips=["Open People"])

    return answer_find(ctx, q)


def answer_find(ctx, q, allow_count=True):  # noqa: C901
    low = q.lower().strip(" ?!.")
    rows = ctx.rows

    # ---- people ---------------------------------------------------------------------------------
    pids, rest = find_people(ctx, q) if ctx.faces_on else ([], q)
    unknown_person = None
    if not pids:
        mm = re.search(r"(?:photos?|pictures?|pics?|images?)\s+(?:of|with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", q)
        if mm and mm.group(1).lower() not in MONTHS and mm.group(1).lower() not in TYPE_WORDS:
            unknown_person = mm.group(1)

    # ---- filters: month, favourites, type -------------------------------------------------------
    mon, yr, rest = month_filter(rest)
    favs = bool(re.search(r"\b(favou?rites?|starred|hearted|liked)\b", rest, re.I))
    if favs:
        rest = re.sub(r"\b(favou?rites?|starred|hearted|liked)\b", " ", rest, flags=re.I)
    pool = rows
    if pids:
        keep = set.intersection(*[set(ctx.people_ids.get(p, ())) for p in pids])
        pool = [r for r in pool if r.id in keep]
    if mon:
        pool = [r for r in pool if (d := taken_date(r)) and d.month == mon and (not yr or d.year == yr)]
    if favs:
        pool = [r for r in pool if r.id in ctx.fav]

    # ---- question kinds -------------------------------------------------------------------------
    is_count = bool(re.search(r"\bhow many\b|\bcount\b|\bnumber of\b", low))
    is_who = bool(re.search(r"\bwho\b|\bwhos\b|\bwho's\b|\bwhich people\b", low))
    is_time = bool(re.search(r"\bwhat time\b|\bat what time\b", low))
    is_when = bool(re.search(r"^when\b|\bwhen is\b|\bwhat (day|date)\b|\bdue date\b|\bdeadline\b.*\?|\bwhen are\b", low))
    is_money = bool(re.search(r"\bhow much\b|\bprice\b|\bcost\b|\btotal\b|\bamount\b|\bbalance\b|\bbill\b.*\b(due|is)\b", low))

    content = [t for t, o in search_terms(rest).items() if o is None]
    typed_only = [t for t in content if t not in TYPE_WORDS]
    type_filter = next((TYPE_WORDS[t] for t in re.findall(r"\w+", rest.lower()) if t in TYPE_WORDS), None)

    # a person with no other words: show all their photos
    if pids and not typed_only and not is_who:
        ids = [r.id for r in pool]
        nm = " and ".join(person_label(ctx, p) for p in pids)
        if is_count:
            return Reply("count", f"You have **{len(ids)}** photo{'s' if len(ids) != 1 else ''} with {nm}.",
                         ids=ids[:6], person=pids[0], query=q,
                         steps=[f"Looked up the face group for {nm}.", f"Counted its photos: {len(ids)}."])
        if not ids:
            return Reply("none", f"I could not find photos with {nm} in what the AI may use.", person=pids[0], query=q)
        return Reply("people", f"Here {'are' if len(ids) != 1 else 'is'} **{len(ids)}** photo{'s' if len(ids) != 1 else ''} with **{nm}**.",
                     ids=ids, person=pids[0], query=q, chips=["Save these as a collection"],
                     steps=[f"Looked up the face group for {nm}.",
                            "Face groups were prepared in advance for this prototype; nothing was recognised live."])
    if unknown_person and not pids:
        if not ctx.faces_on:
            return Reply("info", "Face groups are off, so I can’t search by person. You can turn them on in People.",
                         chips=["Open People"], query=q)
        return Reply("info", f"I don’t know anyone called **{unknown_person}** yet. Name a face in People, "
                             f"or try “Person 1”.", chips=["Open People"], query=q)

    # who is in a photo
    if is_who:
        hits = search(ctx, rest, rows=pool) if content else []
        if not hits:
            return Reply("none", "Which photo do you mean? Try “Who is in the dinner photo?”.", query=q)
        withfaces = [h for h in hits if any(p in ctx.names for p in FACES_IN.get(h[1].id, []))]
        r = (withfaces or hits)[0][1]
        if not ctx.faces_on:
            return Reply("info", "Face groups are off, so I can’t say who is in a photo. Turn them on in People.",
                         chips=["Open People"], ids=[r.id], query=q)
        ppl = [p for p in FACES_IN.get(r.id, []) if p in ctx.names]
        if not ppl:
            return Reply("answer", f"I can’t find any faces I can group in “{r.description}”.", ids=[r.id], sources=[src(r)],
                         steps=make_steps(ctx, rest, hits, ["No face boxes were found for that photo."]), query=q)
        names = ", ".join(f"**{person_label(ctx, p)}**" for p in ppl)
        more = [h[1].id for h in withfaces[1:3]]
        tail = f" {len(more)} similar photo{'s' if len(more) != 1 else ''} below." if more else ""
        return Reply("answer", f"I can see {len(ppl)} {'person' if len(ppl) == 1 else 'people'} in “{r.description}”: {names}.{tail}",
                     ids=[r.id] + more, sources=[src(r)], person=ppl[0], query=q,
                     steps=make_steps(ctx, rest, hits, [f"Listed the {len(ppl)} face groups found in that photo."]))

    hits = search(ctx, rest, rfilter="All", rows=pool) if content else []
    if type_filter and not typed_only:
        hits = [(1, r, [("meta", type_filter, None)]) for r in pool if r.type == type_filter]
    elif not content and (mon or favs):
        hits = [(1, r, [("meta", "taken", None)]) for r in pool]
    if favs and not ctx.fav:
        return Reply("none", "You haven’t marked any favourites yet. Tap the heart on a photo to add one.", query=q)

    # how many
    if is_count and allow_count:
        n = len(hits) if (content or type_filter) else len(pool)
        what = (f"matching “{rest.strip()}”" if typed_only else (type_filter + "s" if type_filter else "photos"))
        return Reply("count", f"You have **{n}** {what}.", ids=[h[1].id for h in hits][:6], query=q,
                     steps=make_steps(ctx, rest, hits, [f"Counted {n} matching photo{'s' if n != 1 else ''}."]))

    # extractive questions: when / how much / what time / generic
    if hits and (is_when or is_money or is_time):
        kind = "date" if (is_when and not is_money) else ("time" if is_time else "money")
        pat = {"date": DATE_RE, "time": TIME_RE, "money": MONEY_RE}[kind]
        withval = [(h, pat.search(h[1].visible_text)) for h in hits[:4] if pat.search(h[1].visible_text)]
        if withval:
            top_score = withval[0][0][0]
            best = [w for w in withval if w[0][0] >= top_score - 0.01]
            word = {"date": "date", "time": "time", "money": "amount"}[kind]
            if len(best) == 1:
                (_, r, _), mt = best[0]
                text = f"The {word} I found is **{mt.group(0)}**. The image says: “{r.visible_text}”."
                return Reply("answer", text, ids=[r.id], sources=[src(r)], query=q, chips=["Open the photo"],
                             steps=make_steps(ctx, rest, hits, [f"Read the {word} from the text inside that image: “{mt.group(0)}”."]))
            best = best[:3]
            lines = "; ".join(f"{h[1].description}: **{mt.group(0)}**" for h, mt in best)
            return Reply("answer", f"I found {len(best)} that fit. {lines}.", ids=[h[1].id for h, _ in best],
                         sources=[src(h[1]) for h, _ in best], query=q,
                         steps=make_steps(ctx, rest, hits, [f"Read the {word} from each image’s text."]))

    # generic question: answer with the best text match
    isq = q.strip().endswith("?") or re.match(r"^(what|which|where|is|are|do|did|can)\b", low)
    if hits and isq and hits[0][1].visible_text and allow_count:
        r = hits[0][1]
        return Reply("answer", f"The closest match says: “{r.visible_text}”.", ids=[r.id], sources=[src(r)], query=q,
                     chips=["Open the photo"], steps=make_steps(ctx, rest, hits, ["Quoted the text found inside that image."]))

    # plain search
    ids = [h[1].id for h in hits]
    if not ids:
        extra = " Try fewer words, or a person, month or type like “receipts”." if allow_count else ""
        return Reply("none", f"I couldn’t find anything for “{q}”.{extra}", query=q, chips=["Show my latest photos"],
                     steps=make_steps(ctx, rest, hits, ["Nothing in the AI-readable text or descriptions matched."]))
    # be honest about words nothing matched ("cat sleeping on a sofa" must not just return the sofa)
    matched = {(o or t) for _, t, o in hits[0][2]}
    for h in hits[:5]:
        matched |= {(o or t) for _, t, o in h[2]}
    missing = [t for t in typed_only if t not in matched]
    if missing and len(typed_only) > 1 and (len(typed_only) - len(missing)) * 2 < len(typed_only):
        ml = ", ".join(f"“{t}”" for t in missing)
        return Reply("none", f"I couldn’t find {ml} in the photos the AI can read. Try describing what is in the picture, like “people in a field” or “handwritten notes”.",
                     query=q, chips=["Show my latest photos"] if allow_count else [],
                     steps=make_steps(ctx, rest, [], [f"Nothing matched {ml}, so I did not guess."]))
    why = ("text inside the image" if any(k == "text" for _, _, ev in hits[:3] for k, _, _ in ev) else
           "what is visible in the photos" if any(k == "tag" for _, _, ev in hits[:3] for k, _, _ in ev) else "descriptions and types")
    bits = [f"Matched on {why}."]
    if pids:
        bits.insert(0, f"Used the face group for {', '.join(person_label(ctx, p) for p in pids)}.")
    if mon:
        bits.append(f"Kept photos taken in {MONTHS[mon - 1].title()}.")
    what = f" for “{' '.join(typed_only)}”" if typed_only else ""
    when = f" taken in {MONTHS[mon - 1].title()}" if mon else ""
    kind_word = (type_filter + "s") if (type_filter and not typed_only) else "photos"
    n = len(ids)
    part = (f" Nothing matched {', '.join('“' + t + '”' for t in missing)}, so these are partial matches." if missing else "")
    return Reply("results", f"I found **{n}** {kind_word if n != 1 else kind_word.rstrip('s')}{what}{when}"
                 + (" (favourites)" if favs else "") + "." + part, ids=ids, query=q,
                 chips=["Save these as a collection"] if allow_count else [],
                 steps=make_steps(ctx, rest, hits, bits))


# --------------------------------------------------------------------------- quality checks, clean-up and memories
from collections import Counter  # noqa: E402
from functools import lru_cache  # noqa: E402

import numpy as np  # noqa: E402
from PIL import Image, ImageOps  # noqa: E402


@lru_cache(maxsize=None)
def quality(file):
    """Real measurements on the image file: size in megapixels and sharpness (variance of the Laplacian)."""
    im = Image.open(ROOT / file).convert("L")
    w, h = im.size
    g = np.asarray(ImageOps.fit(im, (256, 192)), dtype=float)
    lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return {"mp": w * h / 1e6, "sharp": float(lap.var())}


BLUR_BELOW = 60      # sharpness score under this looks blurry
LOWRES_BELOW = 0.05  # megapixels
CLEAN_META = {
    "blurry": ("Blurry photos", "Out of focus or too soft to read. The sharpness score is far below your other photos."),
    "lowres": ("Low-resolution photos", "Very small files. They look pixelated when opened full size."),
    "dupes": ("Near-duplicates", "Almost identical shots taken the same day. The sharpest one of each set stays out of this list."),
    "shots": ("Screenshots you may not need", "Chats, listings and other screenshots that are usually temporary."),
    "unopened": ("Not opened in over a year", "Photos you have not looked at for more than 12 months."),
}

OPENED: set = set()          # photos opened in this session (kept in step by the app, like edited copies)
UNOPENED_DAYS = 365
PEOPLE_WORDS = re.compile(r"family|friends?|cousins?|people|couple|selfie|father|mother|daughter|son|guests?|wedding|portrait|crowd|group", re.I)


def sync_opened(s):
    OPENED.clear()
    OPENED.update(s)


def dhash(file, n=16):
    """Difference hash: a 256-bit fingerprint of the picture's light/dark structure. Real, computed on the file."""
    im = Image.open(ROOT / file).convert("L").resize((n + 1, n))
    a = np.asarray(im, dtype=float)
    return (a[:, 1:] > a[:, :-1]).flatten()


_hash_cache: dict = {}


def _hash(file):
    if file not in _hash_cache:
        _hash_cache[file] = dhash(file)
    return _hash_cache[file]


def duplicate_ids(rows, max_dist=56):
    """Photos that are near-copies of a sharper photo taken within a day. Only real photos are compared
    (flat screenshots and bills look alike to a hash). The sharpest in each set is never listed."""
    ph = sorted([r for r in rows if r.type == "photo"], key=lambda r: -quality(r.file)["sharp"])
    keep, flagged = [], set()
    for r in ph:
        h = _hash(r.file)
        match = next((k for k in keep if abs((pd.to_datetime(k.taken) - pd.to_datetime(r.taken)).days) <= 1
                      and int((h != _hash(k.file)).sum()) <= max_dist), None)
        if match:
            flagged.add(r.id)
        else:
            keep.append(r)
    return flagged


def has_people(r):
    """Someone is in the photo if a face box exists or its description names people (prepared data, not a live detector)."""
    return r.id in FACES_IN or bool(PEOPLE_WORDS.search(r.description))


def cleanup_groups(rows, kept=()):
    """Group the photos the AI may use into clean-up suggestions. A photo is suggested in one group only,
    by this priority: blurry, low-res, near-duplicate, screenshot, not opened in a year."""
    out = {k: [] for k in CLEAN_META}
    rows = list(rows)
    dupes = duplicate_ids(rows)
    today = date.today()
    for r in rows:
        if r.id in kept:
            continue
        q = quality(r.file)
        lo = getattr(r, "last_opened", "")
        stale = bool(lo) and (today - pd.to_datetime(lo).date()).days > UNOPENED_DAYS and r.id not in OPENED
        if q["sharp"] < BLUR_BELOW:
            out["blurry"].append(r)
        elif q["mp"] < LOWRES_BELOW:
            out["lowres"].append(r)
        elif r.id in dupes:
            out["dupes"].append(r)
        elif r.type == "screenshot":
            out["shots"].append(r)
        elif stale:
            out["unopened"].append(r)
    return out


def moments(rows, cat_of):
    """Memories: days with at least 2 photos. Title uses the most common collection; cover is the sharpest photo."""
    by = {}
    for r in rows:
        d = taken_date(r)
        if d and r.type == "photo":
            by.setdefault(d, []).append(r)
    out = []
    for d, items in sorted(by.items(), reverse=True):
        if len(items) >= 2:
            cat = Counter(cat_of(r) for r in items).most_common(1)[0][0]
            cover = max(items, key=lambda r: quality(r.file)["sharp"])
            out.append({"date": d, "iso": d.isoformat(), "title": f"{cat} · {d.strftime('%d %b %Y')}", "items": items, "cover": cover})
    return out


# --------------------------------------------------------------------------- conversation
_TALK = [
    (r"^(how are you|how's it going|hows it going|how are things|what's up|whats up)\b",
     "Doing well, thanks for asking! I'm ready to dig through your photos. What are you after?"),
    (r"^(who are you|what are you|what is your name|what's your name|whats your name)\b",
     "I'm the PixelSense assistant. I find photos, answer questions from the text inside them, keep collections tidy and edit pictures when you ask."),
    (r"^(what can you do|help|what do you do|how do you work|what can i ask|can you help me|commands)\b",
     "I can **find** photos and answer questions from the text inside them, **make collections**, **name people**, and **edit photos**: brighten, darken, crop, "
     "rotate, black and white, sharpen or upscale, then save the result to a collection. Try “make the wedding photos black and white and save to Eid”."),
    (r"^(can you|could you|do you)\s+(edit|crop|brighten|enhance|improve|upscale)",
     "Yes. Tell me what to do and to which photos, for example “brighten the cat photo and crop it to a square, save to Pets”. For fine control open a photo and tap **Edit**."),
    (r"^(bye|goodbye|see you|good night|cya)\b", "Bye for now! Your photos will be here, and nothing changes without you."),
    (r"^(tell me a joke|joke|make me laugh)\b", "Why did the photo go to therapy? Too many negatives."),
    (r"^(good (morning|afternoon|evening))\b", "Hello! What would you like to look at today?"),
    (r"^(sorry|my bad|oops)\b", "No problem at all. Anything you change here can be undone."),
    (r"^(you are|you're|youre)\s+(great|awesome|amazing|good|the best|helpful)", "Thank you! Happy to help. What next?"),
]


def small_talk(low):
    for pat, text in _TALK:
        if re.search(pat, low):
            return Reply("chat", text, chips=["Show my latest photos"], query=low)
    return None


# --------------------------------------------------------------------------- edited copies (saved by the editor or chat)
COPY_COLS = ["id", "file", "type", "description", "visible_text", "album", "suggested_label", "taken"]


def register_copy(rec):
    """Write the edited image and add it to the library tables (in place, so every module sees it)."""
    from PIL import Image
    src = R[rec["src"]]
    out = ROOT / "edited" / f"{rec['id']}.jpg"
    out.parent.mkdir(exist_ok=True)
    im = editor.apply(Image.open(ROOT / src.file), rec["ops"])
    im.save(out, "JPEG", quality=92)
    row = {"id": rec["id"], "file": f"edited/{rec['id']}.jpg", "type": src.type, "description": f"{src.description} (edited)",
           "visible_text": src.visible_text, "album": src.album, "suggested_label": "", "taken": datetime.now().strftime("%Y-%m-%d"),
           "last_opened": "", "tags": getattr(src, "tags", ""), "wearing": getattr(src, "wearing", "")}
    row = [row.get(c, "") for c in df.columns]
    df.loc[(df.index.max() + 1) if len(df) else 0] = row   # new label, never reuses one left by a dropped copy
    R[rec["id"]] = next(df.iloc[[-1]].itertuples())
    AUTO[rec["id"]] = ("Everyday", "you saved it as an edited copy")


def sync_copies(copies):
    """Make the library tables match the session: add missing copies, drop copies that were undone or reset."""
    keep = {c["id"] for c in copies}
    for i in [i for i in list(R) if i.startswith("ed") and i not in keep]:
        df.drop(df.index[df["id"] == i], inplace=True)
        R.pop(i, None); AUTO.pop(i, None)
    for c in copies:
        if c["id"] not in R and c["src"] in R:
            register_copy(c)


# --------------------------------------------------------------------------- optional AI chat (off by default, user opt-in)
def llm_available():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def llm_reply(ctx, history, q):
    """Free conversation through an AI model. Sends the conversation and TEXT descriptions of the photos the AI may use. No images."""
    try:
        import anthropic
        lib = "\n".join(f"- {r.description}" + (f" | text in image: {r.visible_text}" if r.visible_text else "")
                        + f" | collection {ctx.cat_of(r)} | taken {r.taken}" for r in ctx.rows)
        system = ("You are PixelSense, a friendly assistant inside a photo-library app. Chat naturally and briefly. You know the library only through "
                  "these text descriptions, so never invent photos. The app itself can edit photos (brightness, contrast, crop, rotate, black and white, "
                  "sharpen, upscale) when the user types a request such as 'brighten the cat photo and save to Pets', and can search, make collections and undo. "
                  "If the user wants one of those, tell them to type that request.\n\nLibrary:\n" + lib)
        msgs = []
        for role, text in history[-8:] + [("user", q)]:
            if msgs and msgs[-1]["role"] == role:
                msgs[-1]["content"] += "\n" + text
            else:
                msgs.append({"role": role, "content": text})
        if msgs[0]["role"] != "user":
            msgs = msgs[1:]
        resp = anthropic.Anthropic().messages.create(model=os.environ.get("PIXELSENSE_MODEL", "claude-sonnet-5-5"), max_tokens=500, system=system, messages=msgs)
        return Reply("chat", "".join(b.text for b in resp.content if b.type == "text").strip(), query=q,
                     steps=["Answered by an AI model using only the text descriptions of photos the AI may use. No images were sent."])
    except Exception:
        return None


# --------------------------------------------------------------------------- "Needs attention" (the core problem)
def deadlines(rows, today):
    """Every dated obligation found in the text inside photos, with urgency.

    PROBLEM THIS SOLVES: people photograph or screenshot bills, notices and event posters, then never look at
    them again, so they miss due dates and pay late fees. Typing reminders by hand is effort nobody keeps up,
    so PixelSense reads the date and amount for them. Each item is a *suggestion* the user confirms.
    Real parsing, on prepared in-image text (see manifest.csv).
    """
    out = []
    for r in rows:
        if r.type not in ("bill", "screenshot", "document"):
            continue
        t = r.visible_text
        m = re.search(r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", t)
        kind = next((k for w, k in (("due", "Bill due"), ("deadline", "Deadline"), ("fest", "Event")) if w in t.lower()), None)
        if not (m and kind):
            continue
        d = datetime.strptime(f"{m.group(1)} {m.group(2)} {today.year}", "%d %b %Y").date()
        days = (d - today).days
        if days < -180:           # a date this far back is almost certainly next year's
            d = d.replace(year=today.year + 1)
            days = (d - today).days
        amt = re.search(r"Rs\.?\s?[\d,]+", t)
        money = int(re.sub(r"\D", "", amt.group(0))) if amt else 0
        # what does it cost to ignore this? bills cost money, deadlines cost marks, events cost nothing but the chance
        stakes = {"Bill due": "Late fee risk", "Deadline": "Missed submission", "Event": "Optional"}[kind]
        urgency = "overdue" if days < 0 else "soon" if days <= 7 else "later"
        out.append({"id": r.id, "row": r, "title": r.description, "source": "photo", "kind": kind, "date": d, "days": days, "money": money,
                    "stakes": stakes, "urgency": urgency, "evidence": snippet_of(t, m.group(0))})
    return sorted(out, key=lambda x: x["days"])


def snippet_of(text, token):
    """The exact words in the photo the date was read from (shown as proof, so the user can check it)."""
    i = text.find(token)
    a, b = max(0, i - 28), min(len(text), i + len(token) + 28)
    if a:                                   # start and end on whole words, never mid-word
        a = text.find(" ", a) + 1 or a
    if b < len(text):
        b = text.rfind(" ", i + len(token), b) if text.rfind(" ", i + len(token), b) > 0 else b
    return ("…" if a else "") + text[a:b].strip() + ("…" if b < len(text) else "")


def when_words(days):
    if days < 0:
        return f"{-days} day{'s' if days != -1 else ''} ago"
    return "today" if days == 0 else "tomorrow" if days == 1 else f"in {days} days"


MON_ABBR = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"   # (was a second "MONTHS", which broke the month filter above)


def parse_pasted(text, today):
    """Find a date and an amount in pasted text (an SMS, an email, a chat message). Same idea as reading a photo,
    but for deadlines that never became a picture. Returns None when no date is found, so nothing is guessed."""
    m = re.search(rf"(\d{{1,2}})\s*(?:st|nd|rd|th)?\s+({MON_ABBR})[a-z]*", text, re.I) or None
    day = mon = None
    if m:
        day, mon = int(m.group(1)), m.group(2)
    else:
        m2 = re.search(rf"({MON_ABBR})[a-z]*\s+(\d{{1,2}})", text, re.I)
        if m2:
            mon, day = m2.group(1), int(m2.group(2))
    if not day:
        return None
    try:
        d = datetime.strptime(f"{day} {mon.title()} {today.year}", "%d %b %Y").date()
    except ValueError:
        return None
    if (d - today).days < -180:
        d = d.replace(year=today.year + 1)
    amt = re.search(r"(?:Rs\.?|PKR|\$)\s?[\d,]+", text)
    money = int(re.sub(r"\D", "", amt.group(0))) if amt else 0
    low = text.lower()
    kind = "Bill due" if ("due" in low or money) else "Deadline" if "deadline" in low or "submit" in low else "Event"
    return {"date": d, "money": money, "kind": kind}


def manual_deadlines(items, today):
    """Turn the deadlines a person typed or pasted into the same shape as ones read from photos."""
    out = []
    for m in items:
        d = date.fromisoformat(m["date"])
        days = (d - today).days
        stakes = {"Bill due": "Late fee risk", "Deadline": "Missed submission", "Event": "Optional"}[m["kind"]]
        out.append({"id": m["id"], "row": None, "title": m["title"], "source": m["source"], "kind": m["kind"], "date": d, "days": days,
                    "money": m["money"], "stakes": stakes, "urgency": "overdue" if days < 0 else "soon" if days <= 7 else "later",
                    "evidence": m.get("evidence", "")})
    return out
