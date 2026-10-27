# PixelSense: the problem, the loopholes, the data, the design

## 1. The problem
A photo library grows faster than anyone can manage it. People cannot **find** things, cannot **spot what matters** (people photograph or screenshot bills, deadline notices and posters "for later", then lose them), cannot tell **what to delete**, and do not trust AI tools with their most private images.
Result: late fees, missed submissions, minutes of scrolling to find one date, and libraries full of clutter.

PixelSense answers with four capabilities: find by natural language, surface what matters (Needs attention), clean up (blurry, low-resolution, near-duplicate, old screenshots, not opened in a year, no people), and edit by prompt, all with the person in control.

**What it does not cover.** Deadlines that never became a photo are only caught if the person adds them (typed, or pasted from a message). "Done" is the user's word. The AI is simulated in this prototype (see README).

- **Who:** students and busy households.
- **Success measure:** deadlines ticked off *before* their date.

## 2. Every fix has a loophole
| Idea | Loophole or cost | What PixelSense does |
|---|---|---|
| Ask people to type reminders | Nobody keeps it up | Reads date and amount from the photo, shows the exact words as proof, user confirms |
| Reward with scores or streaks | Gaming: tick without doing, delete to look tidy | Progress counts *reviewed* items. Keep and Remove count the same. Removal is undoable. Bills ask "Did you pay?" once |
| Strong identity checks (face scan, biometrics) | Expensive, and a photo library is the most private place | Weakest check that works: face groups opt-in, on-device, user-named, no biometric template. Private-looking photos start with AI paused |
| Cloud AI reads everything | Bills leave the device | All on-device. Pause AI per collection or photo |
| Track usage | Hidden tracking breaks trust | No tracking, no cookies, nothing leaves the device |

Honest limit: "Mark done" is the user's word. PixelSense cannot see a bank or university portal.

## 3. Information architecture
**Screens:** Home (Coming up: what needs me now) / Ask / Photos / People / Collections / Clean up / Favorites / Settings.
Frequent tasks are one tap from Home; rare or risky ones live in Settings.

## 4. Visual design: Liquid Glass
- **Material:** translucent blurred surfaces over a soft colour backdrop.
- **Shape:** large continuous corners that nest (28 outer, 20 inner, 14 smallest); capsule buttons.
- **Typography:** SF Pro on Apple devices, Inter elsewhere. Scale 34 / 22 / 17 / 15 / 13 / 12, weights 500-700, tight tracking on titles.
- **Spacing:** 8-point grid (4, 8, 12, 16, 24, 32).
- **Navigation:** floats above content (inset glass sidebar on desktop, glass drawer on phones). The prompt bar floats below, on the Ask screen only. Photos stay the hero.
- **Activity screens:** the analysing screen is a glass card with step status.
- Tokens are CSS variables at the top of the `GLASS` block in `styles.py`.
