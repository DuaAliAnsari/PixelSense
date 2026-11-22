# Evaluation plan and paper outline (Phase 3)

## 1. What is being evaluated
PixelSense is a chat-first, privacy-controlled photo assistant. It helps people **find** photos and facts, **surface** bills and deadlines trapped in screenshots, **clean up** unneeded photos (blurry, low-resolution, near-duplicate, old screenshots, not opened in a year, no people) and **edit** by prompt, while keeping the person in control (undo, originals never changed, "how I found this", face groups that are opt-in).

Because the prototype's AI is simulated (prepared text and face groups), the study evaluates the **interaction design**, not recognition accuracy.

## 2. Research questions
**Main RQ.** How does a chat-first, privacy-controlled photo assistant affect people's ability to find, clean up and act on information in their photo libraries, compared with a conventional gallery?

| RQ | Question | Task | Measures |
|---|---|---|---|
| RQ1 Finding | Does natural-language search help people find photos and facts faster and more accurately than browsing? | F1 | Success, time, errors, screens visited |
| RQ2 Clean-up | Do grouped suggestions reduce the effort of clearing a library, without regret? | C1 | Time, photos removed, undo count, SEQ |
| RQ3 Surfacing | Does Needs attention help people notice upcoming bills and deadlines? | S1 | Success (items found), time, confidence |
| RQ4 Editing | Can people make an edit with a chat prompt instead of manual tools? | E1 (PixelSense only) | Success, time, errors |
| RQ6 Core usability | Can people complete everyday photo-app tasks (trash and restore, collections, view by face) without help? | M1, M2, P1 | Success, time, wrong actions, SEQ, survey Q8 |
| RQ5 Trust and control | Do the privacy and control features make people feel in control and willing to trust it? | Whole session | Survey Q9 to Q11 (control, what felt safest, comfort with reading bills and screenshots), interview themes |

**Hypotheses.** H1: PixelSense is faster and more accurate than the baseline for F1 and S1. H2: perceived ease (SEQ) is higher with PixelSense for C1. H3: more participants prefer PixelSense than the Gallery for their own photos (survey Q12). H4: most participants say they would use PixelSense at least monthly on their own photos (survey Q13: Daily, Weekly or Monthly). Drop RQ4 if you do not want to claim anything about editing.

## 3. Design
- **Within-subjects comparison.** Every participant does the same tasks in two conditions: **PixelSense** and **Gallery (baseline)** (modelled on the phone's stock Gallery app, in a light theme: Photos and Albums tabs, select mode (button or hold a photo) with Copy, Move and Delete, heart Favorite, Edit, Delete and More on an open photo, Recently Deleted with Recover and Delete; no assistant, no Needs-attention, no Clean-up, no search, no faces), Screenshots, Trash, Albums and unnamed faces under People & pets, an editor with Auto / Crop / Adjust / Filters; no assistant, no Needs-attention, no Clean-up, no search by meaning). E1 is PixelSense only.
- **Fixed order.** Everyone does the Gallery first, then PixelSense. The Gallery is what people already know, so it is the reference; the cost is that order effects are not cancelled out, which is a limitation to state.
- **Participants.** About 8 to 15 smartphone users who keep many photos. Record age range, how many photos they keep, and how often they search or clean their library. Exclude anyone who has seen the prototype. Say clearly whether they are students or a wider sample.
- **Materials.** The sample photos in this prototype (not participants' own photos, which avoids privacy problems).
- **Procedure (about 20 to 25 minutes per condition).** Consent, short demo of the interface, tasks T1 to T4 (and T5), think-aloud throughout, one 15-question survey at the very end (nothing between the two versions except the one-tap SEQ after each task), then a short interview. Run the second condition after a break.

## 4. Measures
| Type | Measure | How it is collected |
|---|---|---|
| Objective | Task success and give-up (success / gave_up) | Automatic check when the participant taps I'm done |
| Objective | Completion time (seconds) | Automatic, from Start task to success or Give up |
| Objective | Wrong actions, photos opened, searches | Automatic |
| Objective | Undo taps, screens visited | Automatic |
| Subjective | Final survey, 15 questions answered once after both versions: likelihood of use (Q1, Q5, Q6, Q13), helpfulness (Q3, Q8), match and worry (Q2, Q4, Q7), control and trust (Q9 to Q11), preference and reasons (Q12), difficulty and the one change wanted (Q14, Q15). Three questions have a one-tap follow-up. No standardised scale (SUS, UEQ, NASA-TLX) is used, so say why in the paper | Final survey step |
| Subjective | Single Ease Question per task (1 to 7) | After each task |
| Qualitative | Optional free text under Q15, optional think-aloud subset, short interview (3 to 5 people) | final.csv, interview notes |

## 5. Tasks
One hard-to-find photo (F1), then one task per feature. F1, S1 and C1 have two parallel versions (set A, set B): the Gallery gets one set and PixelSense the other, so no task is repeated, and which set goes with which version rotates with the participant number. The other tasks are the same in both versions where the Gallery (Google Photos style) has the feature: delete and restore, crop, album. Edit by prompt and faces are PixelSense only. F1 asks for one electricity bill by year: in the Gallery people scroll and open bills to check the year, in PixelSense they ask for it.

| Type | RQ | Set A | Set B |
|---|---|---|---|
| F1 Find by text | RQ1 | Lecture slide on cognitive load theory | Doctor's contact card |
| S1 Surface what matters | RQ3 | Heart the two bills due soon | Heart the assignment deadline and the Tech Fest event |
| C1 Clean up | RQ2 | Remove 5+ blurry photos | Remove 5+ memes |
| E1 Edit by prompt | RQ4 | Black-and-white copy of a beach photo (PixelSense only) | same |
| E2 Crop | RQ4 | Crop the snow-capped mountains photo and save the copy (both conditions, each app's own editor) | same |
| M1 Trash and restore | RQ6 | Remove a chocolate cake photo, then restore it (both conditions) | same |
| M2 Make an album, then add to it | RQ6 | Create "Trip" with one photo, then add a second photo to it (both conditions). Gallery follows the stock app: Albums, ＋, name, pick photos (X, None Selected, All Photos / Albums tabs, tick), Adding Method (Copy or Move), then in the album ⋮ > Add photos | same |
| P1 View by face | RQ6 | Show all photos of Sara (named group in PixelSense; unnamed face in the Gallery) | same |

**Automatic success rules.** The app checks after every tap and ends the task the moment the rule is met, or when the participant taps Give up. F1: the target photo was opened. S1: all target photos marked (heart in both). C1: 5 or more photos removed, at least 4 from the target group. E1: a saved B&W copy of a beach photo. M1: a cake photo was removed and is back. E2: a saved copy of the mountain photo with a crop or aspect change. M2: a collection or album called Trip holding 2+ photos. P1 (PixelSense only): Sara's photos are on screen. `wrong_actions` counts non-target photos opened (F1), marked (S1) or removed (C1); it is blank for the other tasks.

## 5. Running the study (self-guided, on phones)
Participants run the whole session alone. Nobody has to sit next to them.
1. Start the app and open it on the phone (same Wi-Fi as the laptop). Put the link in a QR code.
2. The participant opens **Take part in our usability study** on the Home dashboard, reads the consent text, answers three background questions (age range, photos on phone, how often they search), and taps **Begin**. A participant number (P01, P02, ...) is assigned automatically. There is no choice of version: every participant does both, **Gallery first, then PixelSense**.
3. **Version 1 and version 2.** For each task: read it, tap **Start task** (timer starts), do it, The app detects when it is done; **Give up** is always available.
4. After every task: one **Single Ease Question** (1 to 7). There is no survey between the versions.
5. At the end: the single 15-question survey (see study.py, FINAL_FORM).
6. The finish screen has a **Researcher: download data** box with the CSVs. Run `python analyze.py`.

Files written to `study_data/` as the participant goes: `participants.csv`, `tasks.csv` (one row per task), `final.csv` (one row per participant, the 15-question survey).

**Metrics logged automatically:** completion time, outcome (success or gave_up), failed checks, screens visited, undo taps, SEQ. **Think-aloud** is optional in this version; if you want it, add a short screen-recorded or voice-note subset (3 to 5 participants) and code it with the free-text answers.

## 6. Analysis plan
- **Quantitative.** Per task and condition: success rate, median and mean time, errors. Compare conditions with a paired test (paired t-test, or Wilcoxon signed-rank for small or skewed samples). Report effect sizes and confidence intervals, not only p-values. Survey answers: report counts and percentages per option, and for the ordered questions the mean and the share of the top two answers. Q12 is a PixelSense vs Gallery preference, reported as counts.
- **Qualitative.** Transcribe the think-aloud and interview notes. Code them inductively (open coding, then group into themes such as "finding", "trust", "control", "confusion"). Link each theme to an RQ and keep two or three quotes per theme. A second coder on part of the data would improve reliability.
- **Linking to RQs.** Present results in RQ order so every finding answers a stated question.

## 7. Limitations to state honestly
- Simulated AI: results speak to the interface, not to real recognition accuracy.
- Small, convenience sample, probably students; limited generalisation.
- Sample photos, not participants' own libraries, so personal relevance and privacy feelings are only partly captured.
- The baseline imitates Google Photos' structure and features but is a prototype, not the real app; it omits Google Photos' search and auto-collections such as Documents.
- The survey is 15 purpose-written questions, not a validated scale (no SUS, UEQ, NASA-TLX), so results cannot be compared with published benchmarks. RQ5 rests on survey Q9 to Q11 and the interviews.
- Short exposure; novelty effects; first-use only.
- Success is checked by simple rules (target photo opened, hearted or removed), so a participant who finds the right photo by luck is marked successful; `photos_opened` and `wrong_actions` show how much guessing happened.
- Unsupervised sessions: no think-aloud for everyone, and participants may be distracted.
- Needs attention only shows dates it can read from a photo; there is no way to mark an item done or add a deadline by hand.

## 8. Paper outline
1. **Abstract.**
2. **Introduction.** The problem (information trapped in photos, library overload), why existing tools fall short, contribution, RQs.
3. **Related work.** Photo management, conversational interfaces, privacy-preserving AI, usable privacy and control.
4. **PixelSense design.** Problem analysis and loopholes (see PROBLEM_AND_DESIGN.md), information architecture, Liquid Glass design system, features.
5. **Method.** Participants, design, tasks, procedure, measures, ethics.
6. **Results.** By RQ: task performance, SEQ, survey answers, qualitative themes with quotes.
7. **Discussion.** What worked and what failed, theoretical and practical contributions, design implications.
8. **Limitations and future work.** Section 7 above, plus real on-device OCR and face grouping, long-term field study.
9. **Conclusion.**
10. **References and appendix** (consent form, task script, questionnaires).
