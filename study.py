"""Evaluation kit: tasks, questionnaires, scoring and data files for the usability study.

Design (see RESEARCH_PLAN.md): a within-subjects comparison. Each participant does matched tasks twice, once with PixelSense and
once with a plain 'Gallery (baseline)' that has no search, no suggestions and no assistant, in a fixed order (Gallery first, then PixelSense).
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

# Seven tasks, the same in both versions. Where the wording says "different photos" (find a bill, favourite two photos, edit a photo, find a person)
# each version gets a different photo so nobody remembers where it was; the kind of task is identical. Which parallel set goes with which
# version rotates with the participant number. Success is detected by the app (the right photo opened, the right photos hearted,
# every meme removed, an edited copy saved, a collection holding all the posters), so nothing is typed and nobody has to watch.
# kind: open = a target photo opened; fav = all targets hearted; clean = every target removed; edit = a black-and-white AND cropped copy
# of a target; restore = removed then brought back; collect = a collection/album with this name that holds every target.
MEMES = {"img73", "img74", "img75", "img76", "img77", "img78", "img79", "img82"}
POSTERS = {"img18", "img63", "img65"}
TYPES = [
    dict(type="F1", rq="RQ1", title="Find one bill among several from the same month", kind="open",
         A=("Find and open the gas bill from October 2026.", {"img101"}),
         B=("Find and open the water bill from August 2025.", {"img105"})),
    dict(type="S1", rq="RQ3", title="Heart two photos", kind="fav",
         A=("Mark with a heart (\u2665) the electricity bill from October 2026 and the internet bill from October 2026.", {"img10", "img11"}),
         B=("Mark with a heart (\u2665) the assignment notice and the Tech Fest poster.", {"img13", "img18"})),
    dict(type="E1", rq="RQ4", title="Edit a photo (black and white + square crop)", kind="edit",
         A=("Find the photo of the snow-capped mountains. Make it black and white and crop it to a square, then save it as a copy.", {"img68"}),
         B=("Find the photo of the green valley in Naran. Make it black and white and crop it to a square, then save it as a copy.", {"img80"}),
         ps_hint=" Use edit by prompt."),
]
# Tasks that are the same for every participant. text_base is the wording for the Gallery; ps_targets / base_targets differ where the task
# is "a different photo in each version".
CORE = [
    dict(id="P1", rq="RQ6", title="Find a person in a setting (face groups)", kind="open",
         text="Find the photo where you are wearing a pink dress at the wedding venue hallway.",
         text_base="Find the photo where Sara is hugging her little brother and sister in a park.",
         targets={"img88"}, targets_base={"img94"}),
    dict(id="M2", rq="RQ6", title="Collect the photos from a search", kind="collect", name="Posters", targets=POSTERS,
         text="Search for the event posters and save them together as a new collection called Posters.",
         text_base="Create a new collection called Posters and add all the event posters to it."),
    dict(id="C1", rq="RQ2", title="Delete all the memes", kind="clean", targets=MEMES,
         text="Free up space: delete all the memes (joke screenshots).",
         text_base="Free up space: delete all the memes (joke screenshots)."),
    dict(id="M1", rq="RQ6", title="Delete and restore (trash)", kind="restore", targets={"img53", "img54"},
         text="Delete one photo of the chocolate cake, then bring it back from Trash.",
         text_base="Delete one photo of the chocolate cake, then restore it from Recently Deleted (inside Collections)."),
]
TASK_ORDER = ["F1", "S1", "P1", "M2", "E1", "C1", "M1"]


def sets_for(pid: str) -> dict:
    """Which parallel task set goes with which condition. Rotates so all four order x set combinations are used equally often."""
    digits = "".join(ch for ch in pid if ch.isdigit())
    n = int(digits) if digits else 1
    ps = "A" if ((n - 1) // 2) % 2 == 0 else "B"
    return {"PixelSense": ps, "Gallery (baseline)": "B" if ps == "A" else "A"}


def tasks_for(cond: str, set_letter: str) -> list:
    base = cond != "PixelSense"
    out = {}
    for t in TYPES:
        text = t[set_letter][0] + ("" if base else t.get("ps_hint", ""))
        out[t["type"]] = dict(id=t["type"], task_set=set_letter, rq=t["rq"], title=t["title"], kind=t["kind"], text=text, targets=t[set_letter][1])
    for c in CORE:
        out[c["id"]] = dict(id=c["id"], task_set="-", rq=c["rq"], title=c["title"], kind=c["kind"], name=c.get("name", ""),
                            text=c["text_base"] if base else c["text"], targets=c.get("targets_base", c["targets"]) if base else c["targets"])
    return [out[k] for k in TASK_ORDER]


AGE_RANGES = ["18-22", "23-27", "28-35", "36+"]
PHOTO_COUNTS = ["Under 500", "500 to 2,000", "2,000 to 10,000", "Over 10,000"]
SEARCH_FREQ = ["Never", "A few times a year", "Monthly", "Weekly or more"]


# Short SUS, the same 5 statements for both versions, answered once for each version in the single comparison survey at the end. Original SUS items 4, 8, 9 and 10 (needing technical support, cumbersome, confident,
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

# Every choice carries its own words, so it is always clear which end is which.
SEQ_LABELS = {1: "1 - Very difficult", 2: "2 - Difficult", 3: "3 - Slightly difficult", 4: "4 - Neither easy nor difficult",
              5: "5 - Slightly easy", 6: "6 - Easy", 7: "7 - Very easy"}
AGREE_LABELS = {1: "1 - Strongly disagree", 2: "2 - Disagree", 3: "3 - Neutral", 4: "4 - Agree", 5: "5 - Strongly agree"}


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
Q_FIELDS = ["timestamp", "participant", "condition"] + [f"sus_{i + 1}" for i in range(SUS_N)] + ["sus_score"]
PARTICIPANT_FIELDS = ["timestamp", "participant", "order", "task_sets", "age_range", "photos_kept", "search_freq"]
# The last form, after both versions. Each question is a multiple choice; edit the wording or the options here and the form follows.
# kind: "radio" (one answer). {v1} / {v2} in the options are replaced with the two version names in the order the participant used them.
FINAL_FORM = [
    dict(key="easier_find", text="Which version made it easier to find a specific photo (a bill, a person)?", options=["PixelSense", "Gallery", "No difference"]),
    dict(key="faster_cleanup", text="Which version was quicker for deleting the memes?", options=["PixelSense", "Gallery", "No difference"]),
    dict(key="easier_collect", text="Which version made it easier to put photos together in a collection?", options=["PixelSense", "Gallery", "No difference"]),
    dict(key="prompt_vs_manual", text="Compared with editing by hand, how likely are you to use edit by prompt?",
         options=["Much more likely", "A little more likely", "About the same", "A little less likely", "Much less likely", "I did not try it"]),
    dict(key="more_likely_use", text="Which version are you more likely to use for your own photos?", options=["PixelSense", "Gallery", "Both equally", "Neither"]),
    dict(key="would_use", text="Would you use PixelSense on your own photos?", options=["Yes", "Maybe", "No"]),
    dict(key="most_useful", text="Which PixelSense feature did you find most useful?",
         options=["Search results under the search bar", "Coming up (bills and deadlines)", "Face groups (People)", "Edit by prompt",
                  "Saving search results as a collection", "Clean up", "None of them"]),
    dict(key="most_confusing", text="Which version had the part you found most confusing?", options=["PixelSense", "Gallery", "Neither"]),
]
FINAL_FIELDS = ["timestamp", "participant"] + [q["key"] for q in FINAL_FORM] + ["comment"]


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
    """Everyone does the Gallery (baseline) first, then PixelSense. The order is fixed, so say in the report that order effects are not cancelled out."""
    return [CONDITIONS[1], CONDITIONS[0]]
