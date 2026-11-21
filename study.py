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
# with the participant number), plus core tasks. PixelSense: 6 + 1 + 7 = 14 tasks. Gallery (Google Photos style): 6 + 4 = 10 tasks.
# PixelSense also has the clean-up (blurry photos) task; the Gallery baseline has no such feature, so it does not get that task.
# Success is detected by the app: the correct photo was opened, the right photos were favourited, enough of the right photos were removed,
# or the edited copy was saved. Nothing is typed and nobody has to watch.
# kind: open = any target photo opened; fav = all targets favourited; clean = 5+ removed and 4+ of them are targets; bw = B&W copy of a beach photo.
# F1: every month has several bills (a second electricity meter and a gas bill), so a plain gallery means opening each one to read the amount,
# while PixelSense can search the amount or read it in the result. The amount in the task text is what tells the right bill apart.
# S1: two different photos must be hearted.
# C1: PixelSense only (blurry photos). Its meme variant (B) is kept for a meme-deletion task but is not used by default.
TYPES = [
    dict(type="F1", rq="RQ1", title="Find a bill from a specific month", kind="open",
         A=("Find and open the electricity bill from July 2024 for Rs 10,510.", {"img62"}),
         B=("Find and open the electricity bill from August 2025 for Rs 9,311.", {"img60"})),
    dict(type="S1", rq="RQ3", title="Surface what matters", kind="fav",
         A=("Mark two different photos with a heart (♥): the electricity bill and the internet bill that need paying.", {"img10", "img11"}),
         B=("Mark two different photos with a heart (♥): the HCI assignment notice and the Tech Fest poster.", {"img13", "img18"})),
    dict(type="C1", rq="RQ2", title="Clean up", kind="clean", only="PixelSense",
         A=("Free up space: remove at least 5 blurry photos.", {"img06", "img38", "img39", "img40", "img41", "img42", "img43"}),
         B=("Free up space: remove at least 5 memes or joke screenshots.", {"img73", "img74", "img75", "img76", "img101", "img102", "img103", "img104"})),
]
# E1: the same edit (black and white, saved as a copy) in both versions, on a different photo in each. Where the photo is differs per version, so
# nobody learns its position; PixelSense asks them to use Edit with a prompt, the Gallery leaves them to find the manual editor.
EDIT_TYPE = dict(type="E1", rq="RQ4", title="Edit a photo: crop and black and white", kind="bw",
                 A=dict(subject="a photo of the beach at sunset", targets={"img22", "img36", "img49", "img99", "img100"}),
                 B=dict(subject="a photo of a tiger", targets={"img56", "img96"}))
BEACH_IDS = EDIT_TYPE["A"]["targets"]          # kept for older code

# Core photo-app tasks. Most exist in both conditions, because the Gallery baseline is modelled on Google Photos and a real gallery app has
# them: Favorites (heart), Recently deleted and restore, Albums (add photos from inside the album) and the editor (Crop).
# Each task is worded per condition (text_base) so it names what that app actually calls things. Tasks with no Google Photos equivalent
# (edit by prompt, faces, bills, deadlines, AI control) are PixelSense only.
CORE = [
    dict(id="M1", rq="RQ6", title="Delete and restore (trash)", kind="restore", targets={"img53", "img54"}, both=True,
         text="Remove one photo of the chocolate cake, then bring it back.",
         text_base="Delete one photo of the chocolate cake, then restore it from Recently deleted."),
    dict(id="M2", rq="RQ6", title="Make an album, then add to it", kind="album", targets=set(), both=True,
         text="Create a new collection called Trip with one photo in it, then add a second photo to the same collection.",
         text_base="Create a new album called Trip with one photo in it, then add a second photo to the same album."),
    # P1: the same idea in both versions. PixelSense: open a person's face group. Gallery: no face groups, so find Sara by looking and open 3 of her photos.
    dict(id="P1", rq="RQ6", title="Find photos of a person", kind="face", targets={"bro"}, both=True,
         text="Use the face groups (People) to show all the photos of Person 1.",
         kind_base="open3", targets_base={"img92", "img93", "img94"},
         text_base="Find photos of Sara and open three of them.", person_base="sara"),
    dict(id="X1", rq="RQ6", title="Make a collection from search results", kind="searchcoll", targets=set(), both=False,
         text="Search for photos of the beach, then make a collection from the results."),
    dict(id="P2", rq="RQ5", title="Stay in control of AI", kind="control", targets=set(), both=False,
         text="Choose any one photo and stop the app’s AI from using it."),
]
# Removed on request: the crop-only task (now part of the edit task), "mark the bill as paid" and "add a reminder".
CLEAN_MIN, CLEAN_MIN_CORRECT = 5, 4


def sets_for(pid: str) -> dict:
    """Which parallel task set goes with which condition. Rotates so all four order x set combinations are used equally often."""
    digits = "".join(ch for ch in pid if ch.isdigit())
    n = int(digits) if digits else 1
    ps = "A" if ((n - 1) // 2) % 2 == 0 else "B"
    return {"PixelSense": ps, "Gallery (baseline)": "B" if ps == "A" else "A"}


def tasks_for(cond: str, set_letter: str) -> list:
    base = cond != "PixelSense"
    out = []
    for t in TYPES:
        if base and t.get("only") == "PixelSense":
            continue                               # no blurry-photo clean-up task in the Gallery baseline
        sl = "A" if t["type"] == "C1" else set_letter      # PixelSense always gets the blurry-photos version
        out.append(dict(id=t["type"], task_set=sl, rq=t["rq"], title=t["title"], kind=t["kind"], text=t[sl][0], targets=t[sl][1]))
    e = EDIT_TYPE
    subj, tg = e[set_letter]["subject"], e[set_letter]["targets"]
    text = (f"Edit a photo: search for {subj}, then use Edit with a prompt to crop it and make it black and white, and save it as a copy." if not base
            else f"Edit a photo: find {subj}, crop it, make it black and white and save it as a copy.")
    out.append(dict(id=e["type"], task_set=set_letter, rq=e["rq"], title=e["title"], kind=e["kind"], text=text, targets=tg))
    for c in CORE:
        if base and not c["both"]:
            continue
        out.append(dict(id=c["id"], task_set="-", rq=c["rq"], title=c["title"], kind=c.get("kind_base", c["kind"]) if base else c["kind"],
                        person=c.get("person_base") if base else None,
                        targets=c.get("targets_base", c["targets"]) if base else c["targets"], text=c["text_base"] if base else c["text"]))
    return out


AGE_RANGES = ["18-22", "23-27", "28-35", "36+"]
PHOTO_COUNTS = ["Under 500", "500 to 2,000", "2,000 to 10,000", "Over 10,000"]
SEARCH_FREQ = ["Never", "A few times a year", "Monthly", "Weekly or more"]


# Short SUS, the same 5 statements for both versions. Original SUS items 4, 8, 9 and 10 (needing technical support, cumbersome, confident,
# needed to learn a lot) overlapped with each other and with the others, and item 3 ("easy to use") mirrored item 2 ("unnecessarily complex"),
# so they are dropped. Kept: SUS 1, 2, 5, 6, 7. (text, positively worded?)  Workload (NASA-TLX), UEQ-S and trust items were removed to keep the
# survey short; the per-task SEQ and the final questions still cover effort and preference.
SUS_ITEMS = [
    ("I think that I would like to use this system frequently.", True),
    ("I found the system unnecessarily complex.", False),
    ("I found the various functions in this system were well integrated.", True),
    ("I thought there was too much inconsistency in this system.", False),
    ("I would imagine that most people would learn to use this system very quickly.", True),
]
SUS_N = len(SUS_ITEMS)


def sus_score(answers: list[int]) -> float:
    """Short-SUS, 0 to 100: positive items score-1, negative items 5-score, summed and scaled by 100 / (4 x items).
    With all 10 items this equals the standard SUS (sum x 2.5). With 5 items it is on the same 0 to 100 range but is NOT the standard SUS,
    so do not compare it with the usual benchmark of 68; compare PixelSense with the Gallery instead."""
    pts = sum((a - 1) if SUS_ITEMS[i][1] else (5 - a) for i, a in enumerate(answers))
    return round(pts * 100 / (4 * len(answers)), 1)


def counterbalance(pid: str) -> str:
    """Odd participant numbers start with PixelSense, even ones with the baseline, so order effects cancel out."""
    digits = "".join(ch for ch in pid if ch.isdigit())
    return CONDITIONS[0] if (int(digits) % 2 == 1 if digits else True) else CONDITIONS[1]


TASK_FIELDS = ["timestamp", "participant", "order", "condition", "task_id", "task_set", "rq", "seconds", "outcome", "success", "wrong_actions",
               "photos_opened", "searches", "undos", "screens_visited", "seq"]
Q_FIELDS = ["timestamp", "participant", "condition"] + [f"sus_{i + 1}" for i in range(SUS_N)] + ["sus_score", "edit_prompt_pref"]
PARTICIPANT_FIELDS = ["timestamp", "participant", "order", "task_sets", "age_range", "photos_kept", "search_freq"]
FINAL_FIELDS = ["timestamp", "participant", "preferred", "easiest", "most_useful", "most_confusing", "would_use"]
USEFUL_FEATURES = ["Asking in plain words (search)", "Overdue and Coming up", "Clean up", "Edit with a prompt", "People (face groups)",
                   "Making a collection from search results", "Stopping the AI from using a photo"]


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
    """Everyone does the Gallery (baseline) first, then PixelSense: the baseline is what people already know, so it is the reference."""
    return [CONDITIONS[1], CONDITIONS[0]]