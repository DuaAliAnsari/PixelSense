# PixelSense: never miss a bill or deadline you photographed

An HCI prototype built as a Streamlit web app. You **ask your photos** instead of browsing menus, and the app pulls the bills, deadlines and events trapped inside your screenshots back to you in time.

## The problem it solves
People photograph or screenshot bills, deadline notices and posters "for later", then lose them among thousands of images. The result is late fees, missed submissions and minutes of scrolling to find one date.

PixelSense reads the date and amount inside those photos, shows the exact words it read as proof, and lists what needs you. The full reasoning (the loopholes of each possible fix, the information architecture and the design system) is in **PROBLEM_AND_DESIGN.md**.

## Run
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Keep `.streamlit/config.toml` next to `app.py` (it locks the light theme).

## Main features
- **Needs attention:** every bill, deadline and event found in your photos, grouped Overdue / This week / Later, with the words each date was read from. Mark done (bills ask "Did you pay?" once) and undo. Shown on Home under Coming up; it is not a separate page.
- **Library progress:** a ring on Home counting bills and deadlines you handled plus clutter you decided on. Keep and Remove count the same, so deleting is never rewarded.
- **Ask PixelSense (chat):** answers show the source photo, highlight the matching text and list "How I found this". Built-in conversation (greetings, what can you do, thanks, undo).
- **Home dashboard:** search chips, quick stats, Needs attention, Collections with covers, Memories, Recent photos, People.
- **Photos, People, Collections, Favorites:** timeline by month; face groups (tap a face to see all their photos, name, hide, "Wrong person?" fix, "Often with"); auto-sorted and your own collections; photo details with "Why this result?".
- **Clean up:** groups photos you may not need: blurry and low-resolution (real sharpness and size measurements), **near-duplicates** (a real image fingerprint, the sharpest of each set stays out of the list), old screenshots, **not opened in over a year**. Review, Keep, or Remove (undoable, originals untouched).
- **Add a deadline:** deadlines that never became a photo can be typed, or pasted from a message (SMS, email, chat). PixelSense finds the date and amount in the pasted text and shows the words it used.
- **Study mode (evaluation kit):** Settings, Open study mode. Consent, counterbalanced condition, timed tasks with a task bar, a plain **Gallery (baseline)** condition for comparison, built-in SUS, NASA-TLX, UEQ-S and trust questionnaires, and CSV export. See **RESEARCH_PLAN.md**.
- **Photo editor:** Adjust, Crop & rotate, Filters, Resolution (2x / 4x), with live preview and *Show original*. Save as a copy to a collection or download. Originals are never changed. Editing is ordinary image processing (Pillow); "improve resolution" is resampling with gentle sharpening, not generative super-resolution.
- **Edit by chat:** e.g. `Make the wedding photos black and white and save to Eid`, then `make it brighter`.
- **Smart chat (optional):** turn on in Settings (needs `ANTHROPIC_API_KEY` and `pip install anthropic`). It sends your message and the *text descriptions* of photos the AI may use, never the photos.

## Things to try in the prompt bar
| Type | What happens |
| --- | --- |
| `What needs my attention?` | Opens Needs attention |
| `When is my HCI assignment due?` | Reads the date from the text inside the screenshot and shows the photo |
| `How much is the electricity bill?` / `How much are my bills` | Reads amounts from bills |
| `Show photos of Person 1` | Needs face groups on (People). Shows every photo of that person |
| `Who is in the dinner photo?` | Lists the people found in that photo |
| `how many receipts do I have` | Counts matches |
| `photos from September`, `show favorites` | Month and favourites filters |
| `Create a collection called Eid with family dinner photos` | Makes the collection, with Undo |
| `rename Person 2 to Aisha` | Names a face group, with Undo |
| `Upscale the field photo 4x` | Saves an upscaled copy to a collection |

## Information architecture
Home (Coming up: what needs me now) · Ask · Photos · People · Collections · Clean up · Favorites · Settings. Frequent tasks are one tap from Home; rare or risky ones live in Settings.

## Design: Liquid Glass
Translucent blurred surfaces over a soft colour backdrop, large nested rounded corners, capsule buttons, one type family (SF Pro on Apple devices, Inter elsewhere) on a fixed scale, and an 8-point spacing grid. Navigation floats above content (inset glass sidebar on computers, glass drawer on phones) and the prompt bar floats below it. The design tokens are CSS variables at the top of the `GLASS` block in `styles.py`.

## Layout
- **Computers:** permanent floating sidebar, centred content, multi-column grids, photo details in two columns.
- **Phones:** single column with a top-left menu drawer.
- **Ask screen:** the bottom prompt bar appears only here. Type a request or question. The **+** opens New collection, New chat, People. Home has no prompt bar; its suggestion chips open Ask.

## Staying in control (the HCI idea)
Face groups are opt-in and can be turned off and forgotten. You name people. Every change has Undo. Move any photo, stop AI for a photo, pause AI per collection ("Sensitive" is paused by default), Remove and Restore. Answers explain how they were found. "Mark done" is your word: the app cannot see your bank or university portal, and it says so.

## What is real and what is simulated
- **Real:** search, question answering (extracts dates, amounts and times from prepared text), deadline detection and urgency, pasted-text date reading, near-duplicate detection, commands, collections, naming/hiding people, clean-up measurements, photo editing, undo.
- **Simulated:** collection sorting (simple rules), in-image text and face boxes (prepared in `manifest.csv` / `faces.csv`), face grouping (assigned by the researcher; nothing is recognised live), the "last opened" dates in `manifest.csv`, whether a photo has people in it (face boxes plus the prepared description), analysis progress, new-photo arrival. A real version would use on-device text recognition and face grouping. Nothing leaves the machine.
- `make_faces.py` shows how the face data and the extra "shots" of the same people were prepared.

## Researcher tools (Settings, bottom)
Simulate 3 new photos arriving, and Reset prototype between participants.

## Files
| File | Purpose |
| --- | --- |
| `app.py` | Interface and screens |
| `engine.py` | Search, answers, commands, deadline detection, face data |
| `study.py` | Evaluation kit: tasks, questionnaires, scoring, CSV logging |
| `editor.py` | Photo editing |
| `styles.py` | All CSS, including the Liquid Glass design system |
| `manifest.csv` | Photo metadata: `description`, in-image text, `tags` (what is visible), `wearing` (clothing and colours), `taken` dates. Every new photo needs a row with tags, or it cannot be found |
| `faces.csv` | Face boxes and person groups |
| `images/` | Sample photos |
| `make_faces.py`, `make_samples.py` | Data preparation |
| `PROBLEM_AND_DESIGN.md` | The problem, loopholes, information architecture and design system |
| `RESEARCH_PLAN.md` | Research questions, study design, analysis plan and paper outline |
| `study_data/` | Created when you run a study session (ignored by git) |
