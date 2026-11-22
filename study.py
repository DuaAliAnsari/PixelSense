"""Evaluation kit: tasks, the end-of-session survey and data files for the usability study.

Design (see RESEARCH_PLAN.md): a within-subjects comparison. Each participant does matched tasks twice, once with PixelSense and
once with a plain 'Gallery (baseline)' that has no search, no suggestions and no assistant, in a fixed order (Gallery first, then PixelSense).
One session = one participant + one condition. Run the app twice per participant.

Data is appended to study_data/tasks.csv and study_data/final.csv the moment it is collected, so nothing is lost
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
         text="Delete one photo of the chocolate cake, then bring it back from Trash (inside Collections).",
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


# Every choice carries its own words, so it is always clear which end is which.
SEQ_LABELS = {1: "1 - Very difficult", 2: "2 - Difficult", 3: "3 - Slightly difficult", 4: "4 - Neither easy nor difficult",
              5: "5 - Slightly easy", 6: "6 - Easy", 7: "7 - Very easy"}


def counterbalance(pid: str) -> str:
    """Odd participant numbers start with PixelSense, even ones with the baseline, so order effects cancel out."""
    digits = "".join(ch for ch in pid if ch.isdigit())
    return CONDITIONS[0] if (int(digits) % 2 == 1 if digits else True) else CONDITIONS[1]


TASK_FIELDS = ["timestamp", "participant", "order", "condition", "task_id", "task_set", "rq", "seconds", "outcome", "success", "wrong_actions",
               "photos_opened", "searches", "undos", "screens_visited", "seq"]
PARTICIPANT_FIELDS = ["timestamp", "participant", "order", "task_sets", "age_range", "photos_kept", "search_freq"]
# The only survey, shown once after both versions (15 questions; three have a one-tap follow-up, the last has an optional free-text box).
# kind: "radio" (one answer) or "multi" (up to `max`). ordered=True means the options run from low to high, so analyze.py can also report a 1-to-N mean.
# follow = a second question under the first (always shown, with a "not applicable" option where needed). other_key = optional free-text box.
# group "ps" = about PixelSense only, "overall" = about both versions. Edit the wording or options here and the form follows.
LIKELY = ["Very unlikely", "Unlikely", "Not sure", "Likely", "Very likely"]
HELPFUL = ["Not helpful at all", "Slightly helpful", "Moderately helpful", "Very helpful", "Extremely helpful"]
COMFORT = ["Very uncomfortable", "Uncomfortable", "Neutral", "Comfortable", "Very comfortable"]
FINAL_FORM = [
    dict(key="find_type", group="ps", kind="radio", ordered=True, options=LIKELY,
         text="How likely are you to search your photos by typing a sentence (e.g. \u201cgas bill October 2026\u201d) instead of scrolling?"),
    dict(key="find_match", group="ps", kind="radio", ordered=True, options=["Never", "Sometimes", "Most of the time", "Always"],
         text="When you typed a request, how often did the first results match what you meant?"),
    dict(key="attn_helpful", group="ps", kind="radio", ordered=True, options=HELPFUL,
         text="How helpful is a list of upcoming bills and deadlines pulled from your screenshots?"),
    dict(key="clean_worry", group="ps", kind="radio", ordered=True, options=["Not worried", "A little", "Quite", "Very"],
         text="While removing photos, how worried were you about deleting something you would want later?"),
    dict(key="clean_monthly", group="ps", kind="radio", ordered=True, options=LIKELY,
         text="How likely are you to use Clean up on your own library every month?"),
    dict(key="edit_use", group="ps", kind="radio", ordered=True, options=LIKELY,
         text="How likely are you to use edit by prompt (e.g. \u201cmake it black and white\u201d) instead of manual tools?"),
    dict(key="edit_match", group="ps", kind="radio", ordered=True, options=["Not at all", "Partly", "Mostly", "Exactly"],
         text="How closely did the edit match what you typed?"),
    dict(key="people_helpful", group="ps", kind="radio", ordered=True, options=HELPFUL,
         text="How helpful is seeing all photos of one person by tapping their face?"),
    dict(key="control", group="ps", kind="radio", ordered=True, options=["None", "A little", "Some", "A lot", "Complete"],
         text="How much control did you feel you had over what the app did with your photos?"),
    dict(key="safest", group="ps", kind="multi", max=2,
         options=["Undo", "Originals never changed", "\u201cHow I found this\u201d", "Face groups are opt-in", "Nothing leaves the device", "None of these"],
         text="Which made you feel safest? (choose up to two)"),
    dict(key="read_comfort", group="ps", kind="radio", ordered=True, options=COMFORT,
         text="How comfortable would you be letting PixelSense read bills and screenshots in your own library?"),
    dict(key="prefer", group="overall", kind="radio", options=["Gallery", "PixelSense", "No preference"],
         text="Which version would you rather use for your own photos?",
         follow=dict(key="prefer_why", text="What mainly decided it?",
                     options=["Finding photos faster", "Easier clean-up", "Editing by typing", "Felt more in control", "Easier to learn",
                              "More familiar", "Privacy concerns", "Other", "No strong reason"])),
    dict(key="freq", group="overall", kind="radio", options=["Daily", "Weekly", "Monthly", "Rarely", "Never"],
         text="If PixelSense were on your phone today, how often would you use it?",
         follow=dict(key="freq_barrier", text="What is the main thing that would hold you back?",
                     options=["Privacy", "Not accurate enough", "I don\u2019t need it", "I already have a similar app", "Takes time to learn",
                              "Nothing, I\u2019d use it"])),
    dict(key="hardest", group="overall", kind="radio",
         options=["Knowing what to type in the search bar", "Deciding what to Keep or Remove in Clean up", "Editing a photo (typing a request or cropping)",
                  "Finding things (People, Collections, Trash)", "Nothing was hard"],
         text="Which part was hardest to figure out?",
         follow=dict(key="hardest_problem", text="What was the problem?",
                     options=["Couldn\u2019t find where to do it", "The wording was unclear", "The result wasn\u2019t what I expected",
                              "Not applicable, nothing was hard"])),
    dict(key="change", group="overall", kind="radio", other_key="change_other",
         options=["Search that understands my wording better", "A clearer reason why the app showed each result", "Easier editing",
                  "Clearer menu names", "Nothing, it works well as it is", "Something else"],
         text="Which one change would help you most?"),
]


def final_keys() -> list[str]:
    """Every column final.csv needs, in question order (answer, then its follow-up or free-text box)."""
    out = []
    for q in FINAL_FORM:
        out.append(q["key"])
        if q.get("follow"):
            out.append(q["follow"]["key"])
        if q.get("other_key"):
            out.append(q["other_key"])
    return out


FINAL_FIELDS = ["timestamp", "participant"] + final_keys()


def _webhook_url():
    url = os.environ.get("STUDY_WEBHOOK", "")
    if not url:
        try:
            import streamlit as st
            url = st.secrets.get("STUDY_WEBHOOK", "")
        except Exception:
            url = ""
    return url


def _log_push_error(msg: str):
    try:
        DATA_DIR.mkdir(exist_ok=True)
        with (DATA_DIR / "push_errors.log").open("a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat(timespec='seconds')} {msg}\n")
    except Exception:
        pass


def _post(url: str, payload: dict, timeout: int = 40) -> str:
    """POST one row to the Apps Script web app and return its reply text (the script answers 'ok' when the row was written)."""
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "text/plain"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(300).decode("utf-8", "replace").strip()


def _push(name: str, row: dict):
    """Optional: also send every row to a Google Sheet (see google_sheet_logger.gs). A hosted app's own files can be wiped on restart, the sheet cannot."""
    url = _webhook_url()
    if not url:
        return
    payload = {"sheet": name.replace(".csv", ""), "row": row}

    def send():
        try:
            reply = _post(url, payload)
            if reply != "ok":
                _log_push_error(f"{name}: the sheet script answered: {reply[:160]}")
        except Exception as e:
            _log_push_error(f"{name}: {type(e).__name__}: {e}")
    threading.Thread(target=send, daemon=True).start()


def test_webhook() -> str:
    """Researcher check: is the secret set, and does the Google Sheet accept a row? Writes one row to a tab called 'test'."""
    url = _webhook_url()
    if not url:
        return "NOT SET: the STUDY_WEBHOOK secret is empty. Add it under Manage app > Settings > Secrets, save, then reboot the app."
    if "/macros/s/" not in url or not url.rstrip("/").endswith("/exec"):
        return "The STUDY_WEBHOOK value does not look like a web app URL. It must start with https://script.google.com/macros/s/ and end with /exec."
    try:
        reply = _post(url, {"sheet": "test", "row": {"timestamp": datetime.now().isoformat(timespec="seconds"), "note": "connection test"}})
    except Exception as e:
        return f"FAILED to reach the script: {type(e).__name__}: {e}"
    if reply == "ok":
        return "WORKING: a row was added to a tab called 'test' in your Google Sheet."
    return "The script answered, but did not write the row: " + reply[:200] + " (If it mentions 'null' or 'getSheetByName', set SHEET_ID at the top of the script.)"


def read_push_errors() -> str:
    p = DATA_DIR / "push_errors.log"
    try:
        return "".join(p.read_text(encoding="utf-8").splitlines(True)[-8:]) if p.exists() else ""
    except Exception:
        return ""


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


def claim_pid() -> str:
    """Hand out the next free participant number at the moment someone taps Begin. Creating the claim file is atomic, so two people
    starting at the same second can never get the same number (next_pid only previews it and can be stale)."""
    DATA_DIR.mkdir(exist_ok=True)
    n = int(next_pid()[1:])
    while True:
        pid = f"P{n:02d}"
        try:
            with (DATA_DIR / f"claim_{pid}").open("x"):
                return pid
        except FileExistsError:
            n += 1


def order_for(pid: str) -> list[str]:
    """Everyone does the Gallery (baseline) first, then PixelSense. The order is fixed, so say in the report that order effects are not cancelled out."""
    return [CONDITIONS[1], CONDITIONS[0]]
