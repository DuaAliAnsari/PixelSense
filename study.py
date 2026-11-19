"""Evaluation kit: tasks, questionnaires, scoring and data files for the usability study.

Design (see RESEARCH_PLAN.md): a within-subjects comparison. Each participant does matched tasks twice, once with PixelSense and
once with a plain 'Gallery (baseline)' that has no search, no suggestions and no assistant, in counterbalanced order.
One session = one participant + one condition. Run the app twice per participant.

Data is appended to study_data/tasks.csv and study_data/questionnaires.csv the moment it is collected, so nothing is lost
if the browser closes. These files stay on the researcher's machine. Participant ids only; no names.
"""
from __future__ import annotations

import csv
import json
import os
import threading
import urllib.request
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "study_data"
CONDITIONS = ["PixelSense", "Gallery (baseline)"]

CONSENT = ("You are invited to take part in a short usability study of a photo app. It takes about 15 minutes. "
           "You will do a few tasks in two versions of the app, answer short questions after each task and each version, and tell us what you think. "
           "The photos are samples, not yours. If a task is too hard you can tap Give up at any time; that is useful for us and is not a failure on your part. "
           "We record task times, taps and your answers under a participant number, not your name. You may stop at any time without giving a reason.")

# Six task types, each in two parallel versions (set A and set B) so nobody repeats the same task in the second condition.
# Each participant does one set with PixelSense and the other with the Gallery baseline (which set goes with which condition rotates
# with the participant number), then PixelSense-only editing and core tasks. Total per participant: 6 + 6 + 8 = 20 tasks.
# Success is detected by the app: the correct photo was opened, the right photos were favourited, enough of the right photos were removed,
# or the edited copy was saved. Nothing is typed and nobody has to watch.
# kind: open = any target photo opened; fav = all targets favourited; clean = 5+ removed and 4+ of them are targets; bw = B&W copy of a beach photo.
TYPES = [
    dict(type="F1", rq="RQ1", title="Find by text in a screenshot", kind="open",
         A=("Find and open the screenshot of the lecture slide about cognitive load theory.", {"img14"}),
         B=("Find and open the screenshot of a doctor’s contact card.", {"img52"})),
    dict(type="F2", rq="RQ1", title="Find a bill or receipt", kind="open",
         A=("Find and open the electricity bill from July 2024.", {"img62"}),
         B=("Find and open the Imtiaz Supermarket grocery receipt.", {"img08"})),
    dict(type="F3", rq="RQ1", title="Find by people and scene", kind="open",
         A=("Find and open a photo of a family sitting together in a field.", {"img25"}),
         B=("Find and open a photo of a bride with her bridesmaids.", {"img87"})),
    dict(type="F4", rq="RQ1", title="Find by place", kind="open",
         A=("Find and open the photo of a beach sunset with a camel.", {"img36"}),
         B=("Find and open the photo of snow-capped mountains above a green valley.", {"img68"})),
    dict(type="S1", rq="RQ3", title="Surface what matters", kind="fav",
         A=("Mark with a heart (♥) the two bills that are coming due soon.", {"img10", "img11"}),
         B=("Mark with a heart (♥) the assignment deadline and the Tech Fest event that are coming up.", {"img13", "img18"})),
    dict(type="C1", rq="RQ2", title="Clean up", kind="clean",
         A=("Free up space: remove at least 5 blurry photos.", {"img06", "img38", "img39", "img40", "img41", "img42", "img43"}),
         B=("Free up space: remove at least 5 memes or joke screenshots.", {f"img{n}" for n in range(73, 80)})),
]
EDIT_TASK = dict(type="E1", rq="RQ4", title="Edit by prompt", kind="bw",
                 text="Make a beach photo black and white and save it as a copy.", targets=set())
BEACH_IDS = {"img22", "img36", "img49"}

# Core photo-app tasks, the things people do in any gallery app such as Google Photos (PixelSense only; the plain Gallery baseline has no
# equivalent of most of them). They test the usability of the app itself rather than a comparison.
CORE = [
    dict(id="M1", rq="RQ6", title="Delete and restore (trash)", kind="restore", targets={"img53", "img54", "img55"},
         text="Remove one photo of the chocolate cake, then bring it back."),
    dict(id="E2", rq="RQ4", title="Crop a photo", kind="crop", targets={"img68"},
         text="Crop the photo of the snow-capped mountains and save the cropped copy."),
    dict(id="M2", rq="RQ6", title="Make an album", kind="album", targets=set(),
         text="Create a new collection called Trip and put at least 2 photos in it."),
    dict(id="P1", rq="RQ6", title="View photos by face", kind="face", targets={"sara"},
         text="Show all the photos of Sara."),
    dict(id="M3", rq="RQ6", title="Act on a bill", kind="paid", targets={"img10"},
         text="Mark the electricity bill as paid."),
    dict(id="M4", rq="RQ6", title="Add a deadline", kind="deadline", targets=set(),
         text="Add a reminder for a passport renewal due next month."),
    dict(id="P2", rq="RQ5", title="Stay in control of AI", kind="control", targets=set(),
         text="Choose any one photo and stop the app’s AI from using it."),
]
CLEAN_MIN, CLEAN_MIN_CORRECT = 5, 4


def sets_for(pid: str) -> dict:
    """Which parallel task set goes with which condition. Rotates so all four order x set combinations are used equally often."""
    digits = "".join(ch for ch in pid if ch.isdigit())
    n = int(digits) if digits else 1
    ps = "A" if ((n - 1) // 2) % 2 == 0 else "B"
    return {"PixelSense": ps, "Gallery (baseline)": "B" if ps == "A" else "A"}


def tasks_for(cond: str, set_letter: str) -> list:
    out = [dict(id=t["type"], task_set=set_letter, rq=t["rq"], title=t["title"], kind=t["kind"], text=t[set_letter][0], targets=t[set_letter][1]) for t in TYPES]
    if cond == "PixelSense":
        e = EDIT_TASK
        out.append(dict(id=e["type"], task_set="-", rq=e["rq"], title=e["title"], kind=e["kind"], text=e["text"], targets=e["targets"]))
        out += [dict(task_set="-", **{k: v for k, v in c.items()}) for c in CORE]
    return out


AGE_RANGES = ["18-22", "23-27", "28-35", "36+"]
PHOTO_COUNTS = ["Under 500", "500 to 2,000", "2,000 to 10,000", "Over 10,000"]
SEARCH_FREQ = ["Never", "A few times a year", "Monthly", "Weekly or more"]


SUS_ITEMS = [
    "I think that I would like to use this system frequently.",
    "I found the system unnecessarily complex.",
    "I thought the system was easy to use.",
    "I think that I would need the support of a technical person to be able to use this system.",
    "I found the various functions in this system were well integrated.",
    "I thought there was too much inconsistency in this system.",
    "I would imagine that most people would learn to use this system very quickly.",
    "I found the system very cumbersome to use.",
    "I felt very confident using the system.",
    "I needed to learn a lot of things before I could get going with this system.",
]

TLX_ITEMS = [
    ("mental", "Mental demand", "How mentally demanding was it? (0 = very low, 100 = very high)"),
    ("physical", "Physical demand", "How physically demanding was it? (0 = very low, 100 = very high)"),
    ("temporal", "Hurry", "How hurried or rushed was the pace? (0 = very low, 100 = very high)"),
    ("performance", "Performance", "How unsuccessful were you? (0 = perfect, 100 = failure)"),
    ("effort", "Effort", "How hard did you have to work? (0 = very low, 100 = very high)"),
    ("frustration", "Frustration", "How insecure, irritated or stressed were you? (0 = very low, 100 = very high)"),
]

# UEQ-S: (left term, right term). 1 = left, 7 = right. First four = pragmatic quality, last four = hedonic quality.
UEQ_S = [("obstructive", "supportive"), ("complicated", "easy"), ("inefficient", "efficient"), ("confusing", "clear"),
         ("boring", "exciting"), ("not interesting", "interesting"), ("conventional", "inventive"), ("usual", "leading edge")]

TRUST_ITEMS = [
    "I felt in control of what the app did with my photos.",
    "I understood how the app found its results.",
    "I would trust this app with my own photo library.",
]


def sus_score(answers: list[int]) -> float:
    """Standard SUS: odd items score-1, even items 5-score, sum x 2.5 (0 to 100). Benchmark average is about 68."""
    return round(sum((a - 1) if i % 2 == 0 else (5 - a) for i, a in enumerate(answers)) * 2.5, 1)


def ueq_scores(answers: list[int]) -> tuple[float, float]:
    """Each answer 1..7 becomes -3..+3. Returns (pragmatic, hedonic) means."""
    v = [a - 4 for a in answers]
    return round(sum(v[:4]) / 4, 2), round(sum(v[4:]) / 4, 2)


def tlx_raw(values: dict) -> float:
    """Raw (unweighted) NASA-TLX: the mean of the six subscales."""
    return round(sum(values.values()) / len(values), 1)


def counterbalance(pid: str) -> str:
    """Odd participant numbers start with PixelSense, even ones with the baseline, so order effects cancel out."""
    digits = "".join(ch for ch in pid if ch.isdigit())
    return CONDITIONS[0] if (int(digits) % 2 == 1 if digits else True) else CONDITIONS[1]


TASK_FIELDS = ["timestamp", "participant", "order", "condition", "task_id", "task_set", "rq", "seconds", "outcome", "success", "wrong_actions",
               "photos_opened", "searches", "undos", "screens_visited", "seq"]
Q_FIELDS = (["timestamp", "participant", "condition"] + [f"sus_{i + 1}" for i in range(10)] + ["sus_score"]
            + [f"tlx_{k}" for k, _, _ in TLX_ITEMS] + ["tlx_raw"] + [f"ueq_{i + 1}" for i in range(8)] + ["ueq_pragmatic", "ueq_hedonic"]
            + [f"trust_{i + 1}" for i in range(3)])
PARTICIPANT_FIELDS = ["timestamp", "participant", "order", "task_sets", "age_range", "photos_kept", "search_freq"]
FINAL_FIELDS = ["timestamp", "participant", "preferred", "easiest", "most_confusing", "would_use"]


def _webhook_url():
    url = os.environ.get("STUDY_WEBHOOK", "")
    if not url:
        try:
            import streamlit as st
            url = st.secrets.get("STUDY_WEBHOOK", "")
        except Exception:
            url = ""
    return url


def _push(name: str, row: dict):
    """Optional: also send every row to a Google Sheet (see google_sheet_logger.gs). A hosted app's own files can be wiped on restart, the sheet cannot."""
    url = _webhook_url()
    if not url:
        return
    body = json.dumps({"sheet": name.replace(".csv", ""), "row": row}).encode()

    def send():
        try:
            urllib.request.urlopen(urllib.request.Request(url, data=body, headers={"Content-Type": "text/plain"}), timeout=8)
        except Exception:
            pass
    threading.Thread(target=send, daemon=True).start()


def save_progress(sd: dict):
    """Lets a participant resume after a refresh or a dropped connection. Only the study position is kept, never answers."""
    keep = {k: sd[k] for k in ("pid", "order", "sets", "part", "cond", "i", "step") if k in sd}
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / f"progress_{sd['pid']}.json").write_text(json.dumps(keep), encoding="utf-8")


def load_progress(pid: str):
    p = DATA_DIR / f"progress_{pid}.json"
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    except Exception:
        return None


def _append(name: str, fields: list, row: dict):
    _push(name, {k: row.get(k, "") for k in fields})
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / name
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow(row)


def log_task(**row):
    _append("tasks.csv", TASK_FIELDS, {"timestamp": datetime.now().isoformat(timespec="seconds"), **row})


def log_questionnaire(**row):
    _append("questionnaires.csv", Q_FIELDS, {"timestamp": datetime.now().isoformat(timespec="seconds"), **row})


def read_csv_bytes(name: str) -> bytes:
    p = DATA_DIR / name
    return p.read_bytes() if p.exists() else b""


def log_participant(**row):
    _append("participants.csv", PARTICIPANT_FIELDS, {"timestamp": datetime.now().isoformat(timespec="seconds"), **row})


def log_final(**row):
    _append("final.csv", FINAL_FIELDS, {"timestamp": datetime.now().isoformat(timespec="seconds"), **row})


def next_pid() -> str:
    """Participant numbers are handed out automatically: P01, P02, ... so the order is counterbalanced without a researcher."""
    p = DATA_DIR / "participants.csv"
    n = (sum(1 for _ in p.open(encoding="utf-8")) - 1) if p.exists() else 0
    return f"P{max(n, 0) + 1:02d}"


def order_for(pid: str) -> list[str]:
    first = counterbalance(pid)
    return [first] + [c for c in CONDITIONS if c != first]
