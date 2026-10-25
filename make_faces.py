"""Data preparation for the People (face groups) feature. Run once: python make_faces.py

What this does (and what it does NOT do):
  * Face boxes below were found with a standard detector and then checked and corrected by hand.
  * Person groups ("w1", "d6", ...) were assigned by the researcher. PixelSense does not recognise faces live.
  * To let the same person appear in several photos, extra "shots" are cropped from the real photos.
  * A `taken` date is added to every image (EXIF-style metadata, prepared by hand).
It is idempotent: running it again rewrites the same files.
"""
from pathlib import Path

import pandas as pd
from PIL import Image

ROOT = Path(__file__).parent
IMG = ROOT / "images"

# base photo file -> (image id, {person: (x, y, w, h) in pixels})
BASE = {
    "images.jpg": ("img21", {"w1": (83, 106, 41, 41), "w2": (142, 114, 41, 41), "w3": (199, 89, 44, 44),
                             "w4": (267, 79, 43, 43), "w5": (99, 196, 43, 43), "w6": (214, 187, 54, 54)}),
    "images (1).jpg": ("img22", {}),  # backlit silhouettes: no faces can be found
    "images (2).jpg": ("img23", {"s1": (310, 148, 90, 90), "s2": (247, 178, 90, 90), "s3": (147, 136, 68, 95)}),
    "images (3).jpg": ("img24", {"d1": (36, 98, 60, 72), "d2": (97, 84, 42, 56), "d3": (162, 32, 44, 50),
                                 "d4": (262, 24, 44, 50), "d5": (332, 0, 44, 53), "d6": (182, 141, 59, 56),
                                 "d7": (281, 159, 44, 52)}),
    "photo1.jpg": ("img25", {"f1": (63, 42, 23, 28), "f2": (80, 68, 18, 24), "f3": (143, 28, 24, 24),
                             "f4": (150, 50, 22, 25)}),
}
# derived "other shots": new file, source file, crop box (x, y, w, h), new image id
CROPS = [
    ("wedding_standing.jpg", "images.jpg", (50, 55, 290, 140), "img26"),
    ("wedding_seated.jpg", "images.jpg", (20, 160, 300, 260), "img27"),
    ("selfie_closeup.jpg", "images (2).jpg", (240, 120, 230, 190), "img28"),
    ("dinner_standing.jpg", "images (3).jpg", (140, 0, 300, 215), "img29"),
    ("dinner_seated.jpg", "images (3).jpg", (0, 70, 250, 230), "img30"),
    ("field_closeup.jpg", "photo1.jpg", (30, 20, 125, 130), "img31"),
]
NEW_ROWS = [  # id, file, type, description, album, taken
    ("img21", "images/images.jpg", "photo", "Family portrait at a wedding", "Family", "2026-09-26"),
    ("img22", "images/images (1).jpg", "photo", "People jumping on a beach at sunset", "Travel", "2026-08-14"),
    ("img23", "images/images (2).jpg", "photo", "Two people taking a selfie in a street crowd", "Camera", "2026-10-04"),
    ("img24", "images/images (3).jpg", "photo", "Friends and family sharing dinner around a table", "Family", "2026-09-19"),
    ("img25", "images/photo1.jpg", "photo", "Family sitting together in a field", "Family", "2026-09-06"),
    ("img26", "images/wedding_standing.jpg", "photo", "Wedding portrait, standing guests", "Family", "2026-09-26"),
    ("img27", "images/wedding_seated.jpg", "photo", "Wedding portrait, seated couple", "Family", "2026-09-26"),
    ("img28", "images/selfie_closeup.jpg", "photo", "Selfie close-up in the crowd", "Camera", "2026-10-04"),
    ("img29", "images/dinner_standing.jpg", "photo", "Dinner with friends and family, standing guests", "Family", "2026-09-19"),
    ("img30", "images/dinner_seated.jpg", "photo", "Dinner with friends and family, seated guests", "Family", "2026-09-19"),
    ("img31", "images/field_closeup.jpg", "photo", "Father and daughter in a field", "Family", "2026-09-06"),
]
TAKEN = {"img01": "2026-08-14", "img02": "2026-07-30", "img03": "2026-08-14", "img04": "2026-09-19",
         "img05": "2026-09-26", "img06": "2026-10-02", "img07": "2026-10-09", "img08": "2026-09-12",
         "img09": "2026-10-03", "img10": "2026-10-15", "img11": "2026-10-18", "img12": "2026-08-12",
         "img13": "2026-10-12", "img14": "2026-10-08", "img15": "2026-10-20", "img16": "2026-10-21",
         "img17": "2026-10-17", "img18": "2026-10-19", "img19": "2026-10-10", "img20": "2026-10-11"}


def inside(box, crop):
    x, y, w, h = box
    cx, cy, cw, ch = crop
    ix = max(0, min(x + w, cx + cw) - max(x, cx))
    iy = max(0, min(y + h, cy + ch) - max(y, cy))
    return ix * iy >= 0.8 * w * h


def main():
    faces = []
    for fname, (iid, people) in BASE.items():
        for pid, (x, y, w, h) in people.items():
            faces.append((iid, pid, x, y, w, h))
    for new, src, crop, iid in CROPS:
        Image.open(IMG / src).convert("RGB").crop((crop[0], crop[1], crop[0] + crop[2], crop[1] + crop[3])).save(IMG / new, quality=92)
        for pid, box in BASE[src][1].items():
            if inside(box, crop):
                faces.append((iid, pid, box[0] - crop[0], box[1] - crop[1], box[2], box[3]))
    pd.DataFrame(faces, columns=["image_id", "person_id", "x", "y", "w", "h"]).to_csv(ROOT / "faces.csv", index=False)

    m = pd.read_csv(ROOT / "manifest.csv").fillna("")
    m = m[~m.id.isin([r[0] for r in NEW_ROWS])]
    new = pd.DataFrame([dict(id=i, file=f, type=t, description=d, visible_text="", album=a, suggested_label="", taken=k)
                        for i, f, t, d, a, k in NEW_ROWS])
    m = pd.concat([m, new], ignore_index=True)
    old = m["taken"] if "taken" in m.columns else [""] * len(m)
    m["taken"] = [TAKEN.get(i, k) for i, k in zip(m.id, old)]
    m.to_csv(ROOT / "manifest.csv", index=False)
    print(f"{len(faces)} faces, {len(m)} images")


if __name__ == "__main__":
    main()
