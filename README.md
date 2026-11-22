# PixelSense: find any photo in seconds

An HCI prototype built as a Streamlit web app. You **ask your photos** in your own words instead of browsing menus. PixelSense also keeps photos tidy (collections, Clean up, Trash) and lists the dates and amounts it can read inside bills and screenshots, so you do not have to open each one to check.

## The problem it addresses
A photo library grows faster than anyone can manage it. People cannot **find** a specific photo, cannot tell **what is safe to delete**, lose bills, notices and posters that were screenshotted "for later", and are unsure how much to trust AI with their most private images. PixelSense is a redesign of the everyday photo-library experience around those four problems.

**What it does not do.** It does not send reminders or notifications, it does not track whether you paid or submitted anything, and you cannot add a deadline by hand. "Coming up" only shows dates and amounts it can read from your photos. The reasoning behind the design is in **PROBLEM_AND_DESIGN.md**.

## Run
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Keep `.streamlit/config.toml` next to `app.py` (it locks the light theme).

## Main features
- **Ask PixelSense (chat):** type a request or a question. Answers show the source photo, highlight the matching text and list "How I found this". Built-in conversation (greetings, what can you do, thanks, undo).
- **Home:** a search box (try "gas bill October") and Coming up. Search suggestions open Ask.
- **Coming up (view only):** bills, deadlines and events found in your photos, grouped Overdue / This week / Later, with the words each date was read from. Tap one to open the photo. There is nothing to tick off and nothing to add.
- **Photos, People, Collections:** timeline by month with source filters, and **Select all** once you tick a photo; face groups (tap a face to see all their photos, name, hide, "Wrong person?" fix); auto-sorted and your own collections; photo details with "Why this result?"; deleted photos go to Trash (inside Collections) and can be restored.
- **Clean up:** groups photos you may not need: blurry and low-resolution (real sharpness and size measurements), **near-duplicates** (a real image fingerprint, the sharpest of each set stays out of the list), old screenshots, **not opened in over a year**. Review, Keep, or Remove (undoable, originals untouched).
- **Photo editor:** Adjust, Crop & rotate, Filters, Resolution (2x / 4x), with live preview and *Show original*. Save as a copy to a collection or download. Originals are never changed. Editing is ordinary image processing (Pillow); "improve resolution" is resampling with gentle sharpening, not generative super-resolution.
- **Edit by chat:** e.g. `Make the wedding photos black and white and save to Eid`, then `make it brighter`.
- **Usability study (evaluation kit):** a card on Home starts it. Consent, then every participant does both versions (PixelSense and a Google Photos-style **Gallery**), Gallery first, timed tasks with a task bar and a one-tap ease rating after each task, then **one 15-question survey** at the end, and CSV export. See **RESEARCH_PLAN.md**.
- **Smart chat (optional):** turn on in Settings (needs `ANTHROPIC_API_KEY` and `pip install anthropic`). It sends your message and the *text descriptions* of photos, never the photos. Keep it off during the study.

## Things to try in the prompt bar
| Type | What happens |
| --- | --- |
| `What needs my attention?` | Opens Coming up |
| `When is my HCI assignment due?` | Reads the date from the text inside the screenshot and shows the photo |
| `How much is the electricity bill?` / `How much are my bills` | Reads amounts from bills |
| `Fetch me all photos of Sara` | Needs face groups on (People). Every photo of that person. Typos are forgiven (`Sarah`) |
| `Fetch me that photo in which I am wearing pink` | "I", "me" and "my" mean the account holder (the face People calls **Me**). Combines Me with clothing colour |
| `Fetch me all event posters` | Type words (posters, receipts, bills, tickets, documents) are hard filters |
| `Get me the photo of the poster of the Tech Fest event` | Poster type plus the event name read from the poster |
| `Show photos where I am wearing pink at a wedding` | Me + colour + scene |
| `Photos from last month`, `bills from 2024`, `latest photos` | Date words: last/this month, week or year, a year, newest or oldest first |
| `gulabi kapray`, `meri tasveer gulabi pehni` | A few Roman-Urdu words are understood (colours, tasveer, dawat, bijli...) |
| `Who is in the dinner photo?` | Lists the people found in that photo |
| `how many receipts do I have` | Counts matches |
| `photos from September`, `show favorites` | Month and favourites filters |
| `Create a collection called Eid with family dinner photos` | Makes the collection, with Undo |
| `rename Person 2 to Aisha` | Names a face group, with Undo |
| `Upscale the field photo 4x` | Saves an upscaled copy to a collection |

## Information architecture
Home (search, Coming up) · Ask · Photos · People · Collections (Trash lives here) · Clean up. Settings opens from the profile picture. Frequent tasks are one tap from Home; rare or risky ones live in Settings.

## Design: Liquid Glass
Translucent blurred surfaces over a soft colour backdrop, large nested rounded corners, capsule buttons, one type family (SF Pro on Apple devices, Inter elsewhere) on a fixed scale, and an 8-point spacing grid. Navigation floats above content (inset glass sidebar on computers, glass drawer on phones) and the prompt bar floats below it. The design tokens are CSS variables at the top of the `GLASS` block in `styles.py`.

## Layout
- **Computers:** permanent floating sidebar, centred content, multi-column grids, photo details in two columns.
- **Phones:** single column with a top-left menu drawer.
- **Ask screen:** the bottom prompt bar appears here. Type a request or question. The **+** opens New collection, New chat, People.

## Staying in control (the HCI idea)
Face groups are opt-in and can be turned off and forgotten. You name people. Every change has Undo. Photos you delete go to Trash (inside Collections) and can be restored, and originals are never modified. Answers explain how they were found ("How I found this"). Settings (from the profile picture) shows what is stored and who controls it. Dates shown in Coming up are only what the app read from a photo, and it says so.

## What is real and what is simulated
- **Real:** search, question answering (extracts dates, amounts and times from prepared text), date urgency grouping, near-duplicate detection, commands, collections, naming/hiding people, clean-up measurements, photo editing, undo.
- **Simulated:** collection sorting (simple rules), in-image text and face boxes (prepared in `manifest.csv` / `faces.csv`), face grouping (assigned by the researcher; nothing is recognised live), the "last opened" dates in `manifest.csv`, whether a photo has people in it (face boxes plus the prepared description), analysis progress, new-photo arrival. A real version would use on-device text recognition and face grouping. Nothing leaves the machine.
- `make_faces.py` shows how the face data and the extra "shots" of the same people were prepared. **Do not run `make_faces.py` or `make_samples.py` again**: they rewrite `faces.csv` and `manifest.csv` from the original 33 images and would erase the newer photos and faces.
- To add a photo: put the file in `images/`, add a row to `manifest.csv` (`tags` = what is visible, 10 to 15 words; `wearing` = clothes and colours; `visible_text` = words printed in the image), and add its face boxes to `faces.csv`. Use the same `person_id` for the same person in every photo.

## Researcher tools (Settings, bottom: simulate new photos, reset)
Simulate 2 new photos arriving, and Reset prototype between participants.

## Files
| File | Purpose |
| --- | --- |
| `app.py` | Interface and screens |
| `engine.py` | Search, answers, commands, date detection, face data |
| `study.py` | Evaluation kit: tasks, the 15-question survey, CSV logging |
| `analyze.py` | Phase 3 analysis: reads `study_data/` and prints the numbers for the paper |
| `editor.py` | Photo editing |
| `styles.py` | All CSS, including the Liquid Glass design system |
| `manifest.csv` | Photo metadata: `description`, in-image text, `tags` (what is visible), `wearing` (clothing and colours), `taken` dates. Every new photo needs a row with tags, or it cannot be found |
| `faces.csv` | Face boxes and person groups |
| `people.csv` | Names given from the start, and which person is the account holder (`is_me`). Today: `me` = "Me" (the girl in `pink sari.jpg`) and `sara` = "Sara". The account picture on Home is Me's face |
| `images/` | Sample photos |
| `make_faces.py`, `make_samples.py` | Data preparation |
| `PROBLEM_AND_DESIGN.md` | The problem, loopholes, information architecture and design system |
| `RESEARCH_PLAN.md` | Research questions, study design, analysis plan and paper outline |
| `study_data/` | Created when you run a study session (ignored by git) |
