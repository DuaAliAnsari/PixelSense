"""Evaluation kit: tasks, questionnaires, scoring and data files for the usability study.

Design (see RESEARCH_PLAN.md): a within-subjects comparison. Each participant does matched tasks twice, once with PixelSense and
once with 'Classic', a typical gallery app in the style of Google Photos, in counterbalanced order.
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
CONDITIONS = ["PixelSense", "Classic"]

CONSENT = ("You are invited to take part in a short usability study of a photo app. It takes about 15 minutes. "
           "You will do a few tasks in two versions of the app, answer short questions after each task and each version, and tell us what you think. "
           "The photos are samples, not yours. If a task is too hard you can tap Give up at any time; that is useful for us and is not a failure on your part. "
           "We record task times, taps and your answers under a participant number, not your name. You may stop at any time without giving a reason.")

# One task per everyday photo-app category, each in two parallel versions (set A and set B) so nobody repeats the same task in the second condition.
# Each participant does one set with PixelSense and the other with Classic, a typical gallery app in the style of Google Photos
# (Photos, Search and Library tabs; search matches file names only; manual albums; no assistant, no suggestions, no deadline tracking).
# Which set goes with which condition rotates with the participant number. 10 categories x 2 conditions = 20 tasks per participant.
# Success is detected by the app itself (target photo opened, favourited, deleted, restored, cropped copy saved, album made, person screen
# opened, signed out), so nothing is typed and nobody has to watch. Search targets are chosen so that they cannot be found from a chip or a
# recent search: the suggestion chips are hidden and recent searches are cleared before every task.
CATEGORIES = [
    dict(type="T1", rq="RQ1", title="Search for a photo", kind="open",
         A=("Find and open the screenshot that has a surgeon’s phone number.", {"img52"}),
         B=("Find and open the photo of friends and family sharing dinner around a table.", {"img24", "img29", "img30"})),
    dict(type="T2", rq="RQ2", title="Favourite a photo", kind="fav",
         A=("Add the photo of biryani and karahi to your favourites.", {"img37"}),
         B=("Add the photo of the chocolate cake slice to your favourites.", {"img53", "img54"})),
    dict(type="T3", rq="RQ2", title="Edit a photo (crop)", kind="crop",
         A=("Crop the photo of the snow-capped mountains and save the cropped copy.", {"img68"}),
         B=("Crop the photo of the green valley with a river and clouds and save the cropped copy.", {"img80"})),
    dict(type="T4", rq="RQ2", title="Delete a photo", kind="delete",
         A=("Delete the photo of handwritten pre-calculus notes.", {"img81"}),
         B=("Delete the photo of the blank electricity bill form.", {"img70"})),
    dict(type="T5", rq="RQ2", title="Restore a deleted photo", kind="restore",
         A=("The chocolate cake photo was deleted by mistake. Bring it back.", {"img53"}),
         B=("The photo of the other chocolate cake slice was deleted by mistake. Bring it back.", {"img54"})),
    dict(type="T6", rq="RQ3", title="Find a deadline", kind="open",
         A=("Find out when the HCI assignment is due. Open the photo that shows it.", {"img13"}),
         B=("Find out when the internet bill is due. Open the photo that shows it.", {"img11"})),
    dict(type="T7", rq="RQ1", title="Find all photos of a person", kind="person",
         A=("Show all the photos of Sara.", {"sara"}),
         B=("Show all the photos of yourself (you are the person in your profile picture).", {"me"})),
    dict(type="T8", rq="RQ2", title="Make an album", kind="album", name_A="Trip", name_B="Weekend",
         A=("Create an album called Trip and put at least 2 photos in it.", set()),
         B=("Create an album called Weekend and put at least 2 photos in it.", set())),
    dict(type="T9", rq="RQ3", title="Free up space", kind="clean", min_A=4, min_B=4,
         A=("Free up space: delete at least 4 blurry photos.", {"img38", "img39", "img40", "img41", "img42", "img43"}),
         B=("Free up space: delete all 4 meme screenshots.", {"img73", "img74", "img75", "img76"})),
    dict(type="T10", rq="RQ2", title="Sign out", kind="logout",
         A=("Sign out of your account.", set()),
         B=("Sign out of your account.", set())),
]


def sets_for(pid: str) -> dict:
    """Which parallel task set goes with which condition. Rotates so all four order x set combinations are used equally often."""
    digits = "".join(ch for ch in pid if ch.isdigit())
    n = int(digits) if digits else 1
    ps = "A" if ((n - 1) // 2) % 2 == 0 else "B"
    return {"PixelSense": ps, "Classic": "B" if ps == "A" else "A"}


def tasks_for(cond: str, set_letter: str) -> list:
    return [dict(id=t["type"], task_set=set_letter, rq=t["rq"], title=t["title"], kind=t["kind"], text=t[set_letter][0], targets=t[set_letter][1],
                 name=t.get("name_" + set_letter, ""), min=t.get("min_" + set_letter, 0)) for t in CATEGORIES]


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
