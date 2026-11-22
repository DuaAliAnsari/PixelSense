# PixelSense: the problem, the loopholes, the data, the design

## 1. The problem
A photo library grows faster than anyone can manage it. People cannot **find** things, cannot **spot what matters** (people photograph or screenshot bills, deadline notices and posters "for later", then lose them), cannot tell **what to delete**, and do not trust AI tools with their most private images.
Result: minutes of scrolling to find one date, forgotten screenshots, and libraries full of clutter.

PixelSense answers with four capabilities: find by natural language, surface the dates and amounts inside photos (Coming up, view only), clean up (blurry, low-resolution, near-duplicate, old screenshots, not opened in a year, no people), and edit by prompt, all with the person in control.

**What it does not cover.** Coming up only shows dates and amounts that PixelSense can read from a photo. It does not send reminders, does not track whether anything was paid or submitted, and has no way to add a deadline by hand. The AI is simulated in this prototype (see README).

- **Who:** students and busy households.
- **Success measure:** the right photo or date found quickly and correctly (task success and time in the study).

## 2. Every fix has a loophole
| Idea | Loophole or cost | What PixelSense does |
|---|---|---|
| Ask people to type reminders | Nobody keeps it up | Reads date and amount from the photo, shows the exact words as proof |
| Strong identity checks (face scan, biometrics) | Expensive, and a photo library is the most private place | Weakest check that works: face groups opt-in, on-device, user-named, no biometric template. |
| Cloud AI reads everything | Bills leave the device | All on-device |
| Track usage | Hidden tracking breaks trust | No tracking, no cookies, nothing leaves the device |

Honest limit: PixelSense only reads what is printed in a photo. It cannot see a bank or university portal, so it cannot know whether a bill was paid.

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
