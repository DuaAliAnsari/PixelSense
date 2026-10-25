"""PixelSense photo editing: real pixel operations with Pillow (no AI model). Used by the editor screen and by chat.

Edits are non-destructive: they are described by a small `ops` dict, and a copy is only written when the user saves.
"Improve resolution" is resampling plus gentle sharpening, not AI super-resolution, and the app says so.
"""
from __future__ import annotations

import re

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

DEFAULT = dict(brightness=0, contrast=0, saturation=0, sharpness=0, warmth=0, rotate=0, flip=False,
               crop=(0, 0, 0, 0), aspect="Original", filter="None", scale=1, auto=False)
ASPECTS = {"Original": None, "1:1": 1.0, "4:3": 4 / 3, "3:4": 3 / 4, "16:9": 16 / 9, "9:16": 9 / 16}
FILTERS = ["None", "B&W", "Sepia", "Vivid", "Fade", "Warm", "Cool"]
MAX_SIDE = 4096


def new_ops(**kw):
    ops = dict(DEFAULT)
    ops.update(kw)
    return ops


def is_default(ops):
    return all(tuple(ops.get(k)) == tuple(v) if isinstance(v, tuple) else ops.get(k) == v for k, v in DEFAULT.items())


def _balance(im, warmth):
    r, g, b = im.split()
    k = warmth / 200.0
    r = r.point(lambda v: max(0, min(255, int(v * (1 + k)))))
    b = b.point(lambda v: max(0, min(255, int(v * (1 - k)))))
    return Image.merge("RGB", (r, g, b))


def apply(img, ops):
    im = ImageOps.exif_transpose(img).convert("RGB")
    if ops["rotate"]:
        im = im.rotate(-ops["rotate"], expand=True)          # degrees clockwise
    if ops["flip"]:
        im = ImageOps.mirror(im)
    l, t, r, b = ops["crop"]                                   # percent trimmed from each side
    if any((l, t, r, b)):
        w, h = im.size
        im = im.crop((int(w * l / 100), int(h * t / 100), int(w * (1 - r / 100)), int(h * (1 - b / 100))))
    ratio = ASPECTS.get(ops["aspect"])
    if ratio:
        w, h = im.size
        if w / h > ratio:
            nw = int(h * ratio); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
        else:
            nh = int(w / ratio); y = (h - nh) // 2; im = im.crop((0, y, w, y + nh))
    if ops["auto"]:
        im = ImageOps.autocontrast(im, cutoff=1)
    if ops["brightness"]:
        im = ImageEnhance.Brightness(im).enhance(1 + ops["brightness"] / 100)
    if ops["contrast"]:
        im = ImageEnhance.Contrast(im).enhance(1 + ops["contrast"] / 100)
    if ops["saturation"]:
        im = ImageEnhance.Color(im).enhance(1 + ops["saturation"] / 100)
    if ops["warmth"]:
        im = _balance(im, ops["warmth"])
    f = ops["filter"]
    if f == "B&W":
        im = ImageOps.grayscale(im).convert("RGB")
    elif f == "Sepia":
        g = ImageOps.grayscale(im)
        im = ImageOps.colorize(g, "#2B1A0A", "#F2DFC0")
    elif f == "Vivid":
        im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.35)).enhance(1.1)
    elif f == "Fade":
        im = ImageEnhance.Brightness(ImageEnhance.Contrast(im).enhance(.85)).enhance(1.08)
    elif f in ("Warm", "Cool"):
        im = _balance(im, 30 if f == "Warm" else -30)
    if ops["scale"] and ops["scale"] > 1:
        w, h = im.size
        s = min(ops["scale"], MAX_SIDE / max(w, h))
        if s > 1:
            im = im.resize((int(w * s), int(h * s)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.4, percent=60, threshold=2))
    if ops["sharpness"]:
        im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=int(abs(ops["sharpness"]) * 2.4), threshold=2)) if ops["sharpness"] > 0 \
            else im.filter(ImageFilter.GaussianBlur(abs(ops["sharpness"]) / 40))
    return im


def describe(ops):
    """Plain-language list of what the edit does, e.g. ['brightened', 'cropped to 1:1']."""
    out = []
    if ops["auto"]: out.append("auto-enhanced")
    if ops["brightness"]: out.append("brightened" if ops["brightness"] > 0 else "darkened")
    if ops["contrast"]: out.append("raised contrast" if ops["contrast"] > 0 else "lowered contrast")
    if ops["saturation"]: out.append("boosted colour" if ops["saturation"] > 0 else "muted colour")
    if ops["warmth"]: out.append("warmed the tones" if ops["warmth"] > 0 else "cooled the tones")
    if ops["sharpness"]: out.append("sharpened" if ops["sharpness"] > 0 else "softened")
    if ops["filter"] != "None": out.append(f"applied the {ops['filter']} look")
    if ops["rotate"]: out.append(f"rotated {ops['rotate']}°")
    if ops["flip"]: out.append("flipped")
    if any(ops["crop"]) or ops["aspect"] != "Original":
        out.append("cropped" + (f" to {ops['aspect']}" if ops["aspect"] != "Original" else ""))
    if ops["scale"] > 1: out.append(f"upscaled {ops['scale']}x")
    return out


# ------------------------------------------------------------------ understanding an edit request typed in chat
_VERBS = r"\b(brighten|brighter|darken|darker|lighten|crop|rotate|flip|mirror|enhance|improve|upscale|sharpen|sharper|edit|increase|boost|reduce|lower|raise|fix|convert|turn|apply|resize|enlarge|retouch|make)\b"
_NOT_EDIT = r"^\s*(show|find|search|how|what|when|who|where|list|count|which|why|do i|did i|are there|is there)\b"
_VOCAB = set("""brighten brightness brighter darken darker lighten lighter contrast crop cropped square rotate flip mirror enhance improve
upscale resolution sharpen sharper clearer black white sepia vivid warm warmer cool cooler fade edit fix increase boost reduce lower raise
make convert turn apply resize straighten bigger enlarge quality higher hd mono grayscale greyscale b w bw left right degrees by more less
again also then x saturation colour color colors colours vibrant crisp auto tone portrait landscape ratio aspect into save put add store keep
collection album folder to in under up down a an the it this that them these those photo photos picture pictures pic pics image images and of
for my me please can you could would just really very little bit slightly much retouch vintage retro editing edited""".split())


def parse_edit(text):
    """Return (ops, target_query, collection_or_None, pronoun_only) or None when the text is not an edit request."""
    t = text.strip()
    if re.search(_NOT_EDIT, t, re.I) or not re.search(_VERBS, t, re.I):
        return None
    coll = None
    m = re.search(r"(?:,?\s*(?:and\s+)?(?:then\s+)?)(?:save|put|add|move|store|keep)(?:\s+(?:it|them|this|these|the\s+result|the\s+copy))?\s+"
                  r"(?:to|in|into|under)\s+(?:the\s+)?[\"“']?(?P<c>[^\"”']+?)[\"”']?(?:\s+(?:collection|album|folder))?\s*$", t, re.I)
    if m:
        coll, t = m.group("c").strip(), t[:m.start()].strip()
    low = t.lower()
    o = new_ops()
    num = re.search(r"(\d{1,3})\s*%", low)
    mag = min(60, int(num.group(1))) if num else 25
    neg = bool(re.search(r"\b(less|reduce|lower|decrease|down)\b", low))
    if re.search(r"\b(darken|darker)\b", low) or (neg and "bright" in low): o["brightness"] = -mag
    elif re.search(r"\b(brighten|brighter|lighten|lighter|brightness)\b", low): o["brightness"] = mag
    if "contrast" in low: o["contrast"] = -mag if neg else mag
    if re.search(r"\b(saturation|colou?rs?|vivid|vibrant)\b", low):
        o["saturation"] = -mag if neg or "muted" in low else max(mag, 30)
    if re.search(r"\bwarm(er)?\b", low): o["warmth"] = mag
    if re.search(r"\bcool(er)?\b", low): o["warmth"] = -mag
    if re.search(r"\b(sharpen|sharper|clearer|crisp|crisper)\b", low): o["sharpness"] = 50
    if re.search(r"\b(auto[- ]?enhance|enhance|improve (?:the )?(?:quality|photo|picture|pic|image)|fix)\b", low): o["auto"] = True
    if re.search(r"\b(upscale|upscaling|resolution|enlarge|bigger|\bhd\b|[24]x|x[24])\b", low):
        o["scale"] = 4 if re.search(r"\b(4x|x4|4k)\b", low) else 2
        o["sharpness"] = o["sharpness"] or 20
    if re.search(r"\b(black and white|b ?& ?w|bw|monochrome|gr[ae]yscale|mono)\b", low): o["filter"] = "B&W"
    elif "sepia" in low: o["filter"] = "Sepia"
    elif re.search(r"\b(vintage|retro|fade)\b", low): o["filter"] = "Fade"
    if re.search(r"\b(rotate|turn)\b", low):
        o["rotate"] = 180 if "180" in low else 270 if "left" in low or "counter" in low else 90
    if re.search(r"\b(flip|mirror)\b", low): o["flip"] = True
    if "crop" in low or re.search(r"\bsquare\b", low):
        asp = next((a for a in ("16:9", "9:16", "4:3", "3:4", "1:1") if a in low), None)
        if not asp:
            asp = "1:1" if "square" in low or "crop" in low and not re.search(r"portrait|landscape", low) else \
                  "3:4" if "portrait" in low else "16:9"
        o["aspect"] = asp
    if is_default(o):
        return None
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z']*", low) if w not in _VOCAB]
    pron = not words
    return o, " ".join(words), coll, pron
