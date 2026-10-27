"""Evaluation kit: tasks, questionnaires, scoring and data files for the usability study.

Design (see RESEARCH_PLAN.md): a within-subjects comparison. Each participant does matched tasks twice, once with PixelSense and
once with a plain 'Gallery (baseline)' that has no search, no suggestions and no assistant, in counterbalanced order.
One session = one participant + one condition. Run the app twice per participant.

Data is appended to study_data/tasks.csv and study_data/questionnaires.csv the moment it is collected, so nothing is lost
if the browser closes. These files stay on the researcher's machine. Participant ids only; no names.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "study_data"
CONDITIONS = ["PixelSense", "Gallery (baseline)"]

CONSENT = ("You are invited to take part in a short usability study of a photo app. It takes about 20 minutes. "
           "You will do a few tasks, answer short questionnaires and talk about what you think. The photos are samples, not yours. "
           "We record task times and your answers under a participant number, not your name. You may stop at any time without giving a reason.")

# id, research question, short title, what the participant is asked, what counts as success (for the researcher), conditions
TASKS = [
    ("T1", "RQ1", "Find a fact", "Find out when the HCI assignment is due.", "Says 23 Nov", CONDITIONS),
    ("T2", "RQ1", "Find a group of photos", "Find the photos from the family dinner.", "Finds at least 3 of the dinner photos", CONDITIONS),
    ("T3", "RQ3", "Spot what matters", "List every bill or deadline coming up in the next two weeks.", "Names the electricity bill (28 Oct) and the internet bill (5 Nov)", CONDITIONS),
    ("T4", "RQ2", "Clean up", "Free up space: remove at least 5 photos you think you do not need.", "Removes 5 or more photos and can say why", CONDITIONS),
    ("T5", "RQ4", "Edit by prompt", "Make the beach photo black and white and save a copy.", "A black-and-white copy exists", ["PixelSense"]),
]

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


TASK_FIELDS = ["timestamp", "participant", "condition", "task_id", "rq", "seconds", "success", "errors", "undos", "screens_visited", "notes"]
Q_FIELDS = (["timestamp", "participant", "condition"] + [f"sus_{i + 1}" for i in range(10)] + ["sus_score"]
            + [f"tlx_{k}" for k, _, _ in TLX_ITEMS] + ["tlx_raw"] + [f"ueq_{i + 1}" for i in range(8)] + ["ueq_pragmatic", "ueq_hedonic"]
            + [f"trust_{i + 1}" for i in range(3)] + ["interview_notes"])


def _append(name: str, fields: list, row: dict):
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
