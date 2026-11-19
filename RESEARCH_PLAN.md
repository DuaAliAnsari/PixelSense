# Evaluation plan and paper outline (Phase 3)

## 1. What is being evaluated
PixelSense is a chat-first, privacy-controlled photo assistant. It helps people **find** photos and facts, **surface** bills and deadlines trapped in screenshots, **clean up** unneeded photos (blurry, low-resolution, near-duplicate, old screenshots, not opened in a year, no people) and **edit** by prompt, while keeping the person in control (undo, pause AI, "how I found this").

Because the prototype's AI is simulated (prepared text and face groups), the study evaluates the **interaction design**, not recognition accuracy.

## 2. Research questions
Comparison: **PixelSense** against **Classic**, a typical gallery app in the style of Google Photos (Photos, Search and Library tabs; search matches file names; albums made by hand; favourites, trash, people, editor and account menu; no assistant, no suggestions, no deadline tracking, no clean-up suggestions).

| RQ | Question | Tasks | Measures |
|---|---|---|---|
| RQ1 Finding | Does natural-language search help people find photos, facts and people faster and more accurately than file-name search and browsing? | T1, T7 | Success, time, wrong actions, searches, SEQ |
| RQ2 Everyday actions | Are everyday photo actions (favourite, edit, delete, restore, albums, sign out) as easy in PixelSense as in a familiar app? | T2, T3, T4, T5, T8, T10 | Success, time, wrong actions, SEQ |
| RQ3 Surfacing and clean-up | Do Coming up and Clean up help people notice deadlines and clear clutter faster than manual work? | T6, T9 | Success, time, wrong actions, SEQ, NASA-TLX |
| RQ4 Trust and control | Do the privacy and control features make people feel in control and willing to trust it? | Whole session | SUS, UEQ-S, trust items, preference |

**Hypotheses.** H1: PixelSense is faster and more accurate than Classic for finding (T1, T6, T7). H2: it is as easy as Classic for everyday actions (no worse on success and SEQ). H3: workload (NASA-TLX) is lower with PixelSense. H4: SUS for PixelSense is above the benchmark of 68. H5: trust items sit above the scale midpoint.

## 3. Design
- **Within-subjects.** Every participant uses both conditions. Each does 10 tasks per condition (20 in total), one task for each everyday category.
- **Parallel task sets.** Each category has a set A and a set B version, so no task is repeated. Which set goes with which condition rotates with the participant number; with the order of the two conditions, all four combinations are used equally often.
- **Fair search tasks.** Targets are chosen so they cannot be found from a suggestion chip or recent search: chips are hidden during the study and recent searches and chats are cleared before every task.
- **Fully self-guided on a phone.** The app detects success itself, so no researcher is needed.

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
| Category | RQ | Set A | Set B |
|---|---|---|---|
| T1 Search for a photo | RQ1 | Screenshot with a surgeon's phone number | Friends and family sharing dinner |
| T2 Favourite a photo | RQ2 | Biryani and karahi photo | Chocolate cake photo |
| T3 Edit (crop) | RQ2 | Snow-capped mountains | Green valley with river and clouds |
| T4 Delete a photo | RQ2 | Handwritten pre-calculus notes | Blank electricity bill form |
| T5 Restore a deleted photo | RQ2 | Chocolate cake (deleted before the task) | The other chocolate cake photo |
| T6 Find a deadline | RQ3 | When is the HCI assignment due | When is the internet bill due |
| T7 Find all photos of a person | RQ1 | Sara | Yourself (profile picture) |
| T8 Make an album | RQ2 | Album "Trip" with 2+ photos | Album "Weekend" with 2+ photos |
| T9 Free up space | RQ3 | Delete 4+ blurry photos | Delete all 4 meme screenshots |
| T10 Sign out | RQ2 | Sign out | Sign out |

**Automatic success rules.** T1 and T6: a target photo was opened. T2: a target was favourited. T3: a saved copy of the target with a crop or aspect change. T4: the target was deleted. T5: the target is out of the trash. T7: the person's screen was opened. T8: an album with that name holds 2+ photos. T9: the required number of target photos was deleted. T10: the user signed out. Wrong actions are counted per task (non-target photos opened, favourited or deleted). A task ends the moment its rule is met, or when the participant taps Give up.

## 5. Running the study (self-guided, on phones)
Participants run the whole session alone. Nobody has to sit next to them.
1. Start the app and open it on the phone with `?study=1` on the end of the address (for example `http://<your-laptop-ip>:8501/?study=1`; phone and laptop on the same Wi-Fi). Put this link in a QR code.
2. The participant reads the consent text, answers three background questions (age range, photos on phone, how often they search or clean up), and taps **Start the study**. A participant number (P01, P02, ...) and the condition order are assigned automatically, so order is counterbalanced without you.
3. **Part 1 and Part 2** (PixelSense and Classic, in the assigned order). For each task: read it, tap **Start task** (timer starts), do it, or tap **Give up**. There is no done button: the app decides. Nothing is typed. See the success rules in Section 5.
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
- Classic is a gallery built for this study in the style of Google Photos, not the commercial product itself, and its search is deliberately limited to file names.
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
