# Evaluation plan and paper outline (Phase 3)

## 1. What is being evaluated
PixelSense is a chat-first, privacy-controlled photo assistant. It helps people **find** photos and facts, **surface** bills and deadlines trapped in screenshots, **clean up** unneeded photos (blurry, low-resolution, near-duplicate, old screenshots, not opened in a year, no people) and **edit** by prompt, while keeping the person in control (undo, pause AI, "how I found this").

Because the prototype's AI is simulated (prepared text and face groups), the study evaluates the **interaction design**, not recognition accuracy.

## 2. Research questions
**Main RQ.** How does a chat-first, privacy-controlled photo assistant affect people's ability to find, clean up and act on information in their photo libraries, compared with a conventional gallery?

| RQ | Question | Task | Measures |
|---|---|---|---|
| RQ1 Finding | Does natural-language search help people find photos and facts faster and more accurately than browsing? | T1, T2 | Success, time, errors, screens visited |
| RQ2 Clean-up | Do grouped suggestions reduce the effort of clearing a library, without regret? | T4 | Time, photos removed, undo count, NASA-TLX |
| RQ3 Surfacing | Does Needs attention help people notice upcoming bills and deadlines? | T3 | Success (items found), time, confidence |
| RQ4 Editing | Can people make an edit with a chat prompt instead of manual tools? | T5 (PixelSense only) | Success, time, errors |
| RQ5 Trust and control | Do the privacy and control features make people feel in control and willing to trust it? | Whole session | SUS, UEQ-S, trust items, interview themes |

**Hypotheses.** H1: PixelSense is faster and more accurate than the baseline for T1 to T3. H2: workload (NASA-TLX) is lower with PixelSense for T4. H3: SUS is above 68 for PixelSense. H4: trust and control items score above the scale midpoint (4 of 7). Drop RQ4 if you do not want to claim anything about editing.

## 3. Design
- **Within-subjects comparison.** Every participant does the same tasks in two conditions: **PixelSense** and **Gallery (baseline)** (a date-sorted grid with open, select and delete; no search, no suggestions, no assistant). T5 is PixelSense only.
- **Counterbalanced order.** Odd participant numbers start with PixelSense, even numbers with the baseline (the app suggests this when you type the number).
- **Participants.** About 8 to 15 smartphone users who keep many photos. Record age range, how many photos they keep, and how often they search or clean their library. Exclude anyone who has seen the prototype. Say clearly whether they are students or a wider sample.
- **Materials.** The sample photos in this prototype (not participants' own photos, which avoids privacy problems).
- **Procedure (about 20 to 25 minutes per condition).** Consent, short demo of the interface, tasks T1 to T4 (and T5), think-aloud throughout, SUS and NASA-TLX (plus UEQ-S and trust items for PixelSense), then a short interview. Run the second condition after a break.

## 4. Measures
| Type | Measure | How it is collected |
|---|---|---|
| Objective | Task success (Yes / Partly / No) | Researcher, in the finish-task box |
| Objective | Completion time (seconds) | Automatic, from Start task to I'm finished |
| Objective | Errors | Researcher count in the finish-task box |
| Objective | Undo taps, screens visited | Automatic |
| Subjective | SUS (0 to 100) | Questionnaire step |
| Subjective | NASA-TLX raw (0 to 100) | Questionnaire step |
| Subjective | UEQ-S pragmatic and hedonic (-3 to +3) | Questionnaire step (PixelSense) |
| Subjective | Trust and control (3 items, 1 to 7) | Questionnaire step (PixelSense) |
| Qualitative | Think-aloud quotes, interview notes | Notes box |

## 5. Running a session in the app
1. Settings, bottom, **Open study mode**.
2. Type the participant number, read the consent text, tick consent, pick the condition, **Begin session**.
3. **Start task**. A bar at the top shows the task. In the baseline condition the app becomes a plain gallery with no navigation.
4. When the participant says they are done, press **I'm finished**, record success, errors and quotes, **Save and continue**.
5. After the last task, **Continue to questionnaires** and hand over the screen.
6. **Download tasks.csv and questionnaires.csv** (also saved in `study_data/` as you go). **Start next session** resets the sample library.

`tasks.csv` has one row per task. `questionnaires.csv` has one row per participant per condition, with item scores and totals.

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
- Researcher-coded errors and success are subjective.
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
