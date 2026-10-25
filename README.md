# PixelSense V4.2: a chat-first, Google-Photos-style prototype (HCI)

A Streamlit web-app prototype where you **ask your photos** instead of browsing menus.

## Run
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Keep `.streamlit/config.toml` next to `app.py` (locks the light theme).

## How it is laid out
- **Full-page layout on computers**: permanent left sidebar (Ask PixelSense, Photos, People, Collections, Favorites, Settings), centred content, multi-column photo/people/collection grids, photo details in two columns. Phones (narrow screens) keep the single-column layout with the **top-left corner menu** drawer.
- **Bottom prompt bar**: type a request or a question. The **+** opens: New collection (optionally filled from a search), New chat, People.
- **Chat**: answers show the source photo, highlight the matching text, and have a "How I found this" list.

## New in V4.1
- **Home dashboard**: search chips, quick stats, Coming up, Collections with cover photos, Memories, Recent photos, People.
- **Clean up**: groups photos you may not need (blurry, low-resolution, leftover screenshots) using real sharpness and size measurements on the image files. Review, Keep these, or Remove (undoable, originals untouched).
- **Memories**: days with several photos, titled by collection and date.
- Redesigned welcome page with real photos. Short replies like "yes" or "thanks" get a friendly answer instead of a failed search.

## New in V4.2: chat that chats, and photo editing
- **Photo editor**: open any photo and tap **Edit**. Tabs for Adjust (auto-enhance, brightness, contrast, colour, warmth, sharpness), Crop & rotate (aspect ratios, trim edges, rotate, flip), Filters (B&W, Sepia, Vivid, Fade, Warm, Cool) and Resolution (2x / 4x). Live preview with *Show original*, then **Save as copy** to a collection, or **Download**. Originals are never changed.
- **Edit by chat**: type e.g. `Make the wedding photos black and white and save to Eid`, `Brighten the cat photo and crop it to a square, save to Pets`, `Upscale the field photo 4x`, then `make it brighter` (acts on the photos from the last answer). Result is a new copy in the named collection (default "Edited"), with Undo and an *Open in editor* chip.
- **Chat**: built-in conversation (greetings, what can you do, thanks, undo). For free conversation turn on **Smart chat** in Settings (needs `ANTHROPIC_API_KEY` and `pip install anthropic`). It sends your message and the *text descriptions* of photos the AI may use, never the photos.
- Honest limits: editing is ordinary image processing (Pillow). "Improve resolution" is resampling with gentle sharpening, not generative super-resolution.

## Things to try in the prompt bar
| Type | What happens |
| --- | --- |
| `When is my HCI assignment due?` | Reads the date from the text inside the screenshot and shows the photo |
| `How much is the electricity bill?` / `How much are my bills` | Reads amounts from bills |
| `Show photos of Person 1` | Needs face groups on (People). Shows every photo of that person |
| `Who is in the dinner photo?` | Lists the people found in that photo |
| `how many receipts do I have` | Counts matches |
| `photos from September`, `show favorites` | Month and favourites filters |
| `Create a collection called Eid with family dinner photos` | Makes the collection, with Undo |
| `rename Person 2 to Aisha` | Names a face group, with Undo |

## Google Photos-style features
Photos timeline by month, People (face groups: tap a face to see all their photos, name, hide, "Wrong person?" fix, "Often with"),
Favorites, Collections (auto-sorted + your own), Coming up (dates found in text), Photo details with "Why this result?".

## Staying in control (the HCI idea)
Face groups are opt-in and can be turned off and forgotten. You name people. Every change has Undo.
Move any photo, Stop AI for a photo, Pause AI per collection ("Sensitive" is paused by default), Remove and Restore.
Answers explain how they were found.

## What is real and what is simulated
- Real: the search, question answering (extracts dates, amounts and times from prepared text), commands, collections, naming/hiding people, undo.
- Simulated: collection sorting (simple rules), in-image text and face boxes (prepared in `manifest.csv` / `faces.csv`), face grouping (assigned by the researcher; nothing is recognised live), analysis progress, new-photo arrival. Nothing leaves the machine.
- `make_faces.py` shows how the face data and the extra "shots" of the same people were prepared.

## Researcher tools (Settings, bottom)
Simulate 3 new photos arriving, and Reset prototype between participants.

## Files
`app.py` interface, `engine.py` search/answers/commands/face data, `styles.py` all CSS, `manifest.csv` photo metadata (with `taken` dates),
`faces.csv` face boxes and person groups, `images/` sample photos, `make_faces.py` and `make_samples.py` data preparation.
