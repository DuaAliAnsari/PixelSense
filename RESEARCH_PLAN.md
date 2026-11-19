# Evaluation plan and paper outline (Phase 3)

## 1. What is being evaluated
PixelSense is a chat-first, privacy-controlled photo assistant. It helps people **find** photos and facts, **surface** bills and deadlines trapped in screenshots, **clean up** unneeded photos (blurry, low-resolution, near-duplicate, old screenshots, not opened in a year, no people) and **edit** by prompt, while keeping the person in control (undo, pause AI, "how I found this").

Because the prototype's AI is simulated (prepared text and face groups), the study evaluates the **interaction design**, not recognition accuracy.

## 2. Research questions
**Main RQ.** How does a chat-first, privacy-controlled photo assistant affect people's ability to find, clean up and act on information in their photo libraries, compared with a conventional gallery?

| RQ | Question | Task | Measures |
|---|---|---|---|
| RQ1 Finding | Does natural-language search help people find photos and facts faster and more accurately than browsing? | F1 to F4 | Success, time, errors, screens visited |
| RQ2 Clean-up | Do grouped suggestions reduce the effort of clearing a library, without regret? | C1 | Time, photos removed, undo count, NASA-TLX |
| RQ3 Surfacing | Does Needs attention help people notice upcoming bills and deadlines? | S1 | Success (items found), time, confidence |
| RQ4 Editing | Can people make an edit with a chat prompt instead of manual tools? | E1 (PixelSense only) | Success, time, errors |
| RQ6 Core usability | Can people complete everyday photo-app tasks (trash and restore, albums, view by face, act on a bill, add a deadline) without help? | M1 to M4, P1 | Success, time, wrong actions, SEQ |
| RQ5 Trust and control | Do the privacy and control features make people feel in control and willing to trust it? | Whole session | SUS, UEQ-S, trust items, interview themes |

**Hypotheses.** H1: PixelSense is faster and more accurate than the baseline for F1 to F4 and S1. H2: workload (NASA-TLX) is lower with PixelSense for C1. H3: SUS is above 68 for PixelSense. H4: trust and control items score above the scale midpoint (4 of 7). Drop RQ4 if you do not want to claim anything about editing.

## 3. Design
- **Within-subjects comparison.** Every participant does the same tasks in two conditions: **PixelSense** and **Gallery (baseline)** (a date-sorted grid with open, select and delete; no search, no suggestions, no assistant). T5 is PixelSense only.
- **Counterbalanced order.** Odd participant numbers start with PixelSense, even numbers with the baseline (the app suggests this when you type the number).
- **Participants.** About 8 to 15 smartphone users who keep many photos. Record age range, how many photos they keep, and how often they search or clean their library. Exclude anyone who has seen the prototype. Say clearly whether they are students or a wider sample.
- **Materials.** The sample photos in this prototype (not participants' own photos, which avoids privacy problems).
- **Procedure (about 20 to 25 minutes per condition).** Consent, short demo of the interface, tasks T1 to T4 (and T5), think-aloud throughout, SUS and NASA-TLX (plus UEQ-S and trust items for PixelSense), then a short interview. Run the second condition after a break.

## 4. Measures
| Type | Measure | How it is collected |
|---|---|---|
| Objective | Task success and give-up (success / gave_up) | Automatic check when the participant taps I'm done |
| Objective | Completion time (seconds) | Automatic, from Start task to success or Give up |
| Objective | Wrong actions, photos opened, searches | Automatic |
| Objective | Undo taps, screens visited | Automatic |
| Subjective | SUS (0 to 100) | Questionnaire step |
| Subjective | NASA-TLX raw (0 to 100) | Questionnaire step |
| Subjective | UEQ-S pragmatic and hedonic (-3 to +3) | Questionnaire step (PixelSense) |
| Subjective | Trust and control (3 items, 1 to 7) | Questionnaire step (PixelSense) |
| Subjective | Single Ease Question per task (1 to 7) | After each task |
| Qualitative | Free-text answers (best, confusing), optional think-aloud subset | final.csv |

## 5. Tasks
Six task types, each in two parallel versions (set A, set B). Each participant does one set with PixelSense and the other with the Gallery, so no task is repeated; which set goes with which condition rotates with the participant number (all four order x set combinations are used equally often). PixelSense-only task E1 comes last. 20 tasks per participant (6 + 6 + 8), about 15 to 18 minutes plus questionnaires. The core tasks are the everyday actions of a mainstream gallery app such as Google Photos; the Gallery baseline has no equivalent of most of them, so they are reported as standalone usability results (success, time, wrong actions, SEQ), not as a comparison.

| Type | RQ | Set A | Set B |
|---|---|---|---|
| F1 Find by text | RQ1 | Lecture slide on cognitive load theory | Doctor's contact card |
| F2 Find a bill or receipt | RQ1 | Electricity bill, July 2024 | Imtiaz Supermarket receipt |
| F3 Find by people and scene | RQ1 | Family sitting in a field | Bride with bridesmaids |
| F4 Find by place | RQ1 | Beach sunset with a camel | Snow-capped mountains above a green valley |
| S1 Surface what matters | RQ3 | Heart the two bills due soon | Heart the assignment deadline and the Tech Fest event |
| C1 Clean up | RQ2 | Remove 5+ blurry photos | Remove 5+ memes |
| E1 Edit by prompt | RQ4 | Black-and-white copy of a beach photo (PixelSense only) | same |
| E2 Crop | RQ4 | Crop the snow-capped mountains photo and save the copy (PixelSense only) | same |
| M1 Trash and restore | RQ6 | Remove a chocolate cake photo, then restore it (PixelSense only) | same |
| M2 Make an album | RQ6 | Create the collection "Trip" with 2+ photos (PixelSense only) | same |
| P1 View by face | RQ6 | Show all photos of Sara (PixelSense only) | same |
| M3 Act on a bill | RQ6 | Mark the electricity bill as paid (PixelSense only) | same |
| M4 Add a deadline | RQ6 | Add a passport-renewal reminder (PixelSense only) | same |
| P2 Control over AI | RQ5 | Stop the AI using one photo (PixelSense only) | same |

**Automatic success rules.** F1 to F4: a target photo was opened. S1: all target photos hearted. C1: 5 or more photos removed, at least 4 of them from the target group. E1: a saved B&W copy of a beach photo. Core task rules: M1 a cake photo was removed and is back; E2 a saved copy of the mountain photo with a crop or aspect change; M2 a new collection called Trip holding 2+ photos; P1 the Sara person screen was opened; M3 the electricity bill ticked off; M4 a deadline was added; P2 at least one photo had AI stopped. Wrong actions are counted per task (non-target photos opened, hearted or removed). The task ends the moment the rule is met, or when the participant taps Give up.

## 5. Running the study (self-guided, on phones)
Participants run the whole session alone. Nobody has to sit next to them.
1. Start the app and open it on the phone with `?study=1` on the end of the address (for example `http://<your-laptop-ip>:8501/?study=1`; phone and laptop on the same Wi-Fi). Put this link in a QR code.
2. The participant reads the consent text, answers three background questions (age range, photos on phone, how often they search or clean up), and taps **Start the study**. A participant number (P01, P02, ...) and the condition order are assigned automatically, so order is counterbalanced without you.
3. **Part 1 and Part 2** (PixelSense and Gallery, in the assigned order). For each task: read it, tap **Start task** (timer starts), do it, or tap **Give up**. There is no done button: the app decides. Nothing is typed. See the success rules in Section 5.
4. After every task: one **Single Ease Question** (1 to 7). After every part: **SUS** and **NASA-TLX**, plus **UEQ-S** and **trust items** for PixelSense.
5. At the end: preferred version, would-use, and two free-text boxes (best, confusing).
6. Download the CSVs from Settings, **Researcher tools** (hidden while a study is running). Run `python analyze.py`.

Files written to `study_data/` as the participant goes: `participants.csv`, `tasks.csv` (one row per task), `questionnaires.csv` (one row per participant per condition), `final.csv`.

**Metrics logged automatically:** completion time, outcome (success or gave_up), failed checks, screens visited, undo taps, SEQ. **Think-aloud** is optional in this version; if you want it, add a short screen-recorded or voice-note subset (3 to 5 participants) and code it with the free-text answers.

## 6. Analysis plan
- **Quantitative.** Per task and condition: success rate, median and mean time, errors. Compare conditions with a paired test (paired t-test, or Wilcoxon signed-rank for small or skewed samples). Report effect sizes and confidence intervals, not only p-values. SUS against the 68 benchmark (one-sample test). NASA-TLX and UEQ-S per condition.
- **Qualitative.** Transcribe the think-aloud and interview notes. Code them inductively (open coding, then group into themes such as "finding", "trust", "control", "confusion"). Link each theme to an RQ and keep two or three quotes per theme. A second coder on part of the data would improve reliability.
- **Linking to RQs.** Present results in RQ order so every finding answers a stated question.

## 7. Limitations to state honestly
- Simulated AI: results speak to the interface, not to real recognition accuracy.
- Small, convenience sample, probably students; limited generalisation.
- Sample photos, not participants' own libraries, so personal relevance and privacy feelings are only partly captured.
- The baseline is a simple gallery built for this study, not a commercial product such as Google Photos.
- Short exposure; novelty effects; first-use only.
- Success is checked by simple rules (target photo opened, hearted or removed), so a participant who finds the right photo by luck is marked successful; `photos_opened` and `wrong_actions` show how much guessing happened.
- Unsupervised sessions: no think-aloud for everyone, and participants may be distracted.
- The deadline feature depends on a deadline existing in a photo or pasted text.

## 8. Paper outline
1. **Abstract.**
2. **Introduction.** The problem (information trapped in photos, library overload), why existing tools fall short, contribution, RQs.
3. **Related work.** Photo management, conversational interfaces, privacy-preserving AI, usable privacy and control.
4. **PixelSense design.** Problem analysis and loopholes (see PROBLEM_AND_DESIGN.md), information architecture, Liquid Glass design system, features.
5. **Method.** Participants, design, tasks, procedure, measures, ethics.
6. **Results.** By RQ: task performance, SUS, NASA-TLX, UEQ-S, trust, qualitative themes with quotes.
7. **Discussion.** What worked and what failed, theoretical and practical contributions, design implications.
8. **Limitations and future work.** Section 7 above, plus real on-device OCR and face grouping, long-term field study.
9. **Conclusion.**
10. **References and appendix** (consent form, task script, questionnaires).
