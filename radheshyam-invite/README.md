# Ek Shaam Radheshyam — poster and video

The poster moved from **29.8.2026 (Saturday), 3:00 p.m** at Navita ji ke ghar to
**24.10.2026 (Saturday), 2:00 p.m** at Madhu Bhandari ke ghar, Old Grain Market,
Dera Road, Batala, near State Bank of India,
composed and rendered with HyperFrames.

Outputs:

- `renders/ek-shaam-radheshyam-24-10-2026.png` (lossless) and `.jpg` (q95, for WhatsApp): the still.
- `renders/ek-shaam-radheshyam-24-10-2026.mp4`: a 12s, 900×1600, 30fps video version with sound.

Files:

- `index.html`: the video (the project's root composition).
- `stills/poster.html`: the still.

## How it works

1. `tools/make_plate.py` lifts the old date, day, the "3" of the time and the
   five address lines out of `assets/poster.jpg`
   into `assets/plate.png`. The panel's parchment is near-flat (std ~1.2 levels),
   so each patch is a per-column interpolation between the clean rows above and
   below, plus fixed-seed grain at that std.
2. `stills/poster.html` lays the new lines over the plate as SVG text, so each
   baseline is set exactly. `index.html` uses the same plate, fonts and
   placement for the video.

| Property | Value | How it was established |
| --- | --- | --- |
| Typeface | Mukta Bold | Best of 20 candidates. Reproduces "29.8.2026" at 222px wide (source 221) and "Saturday" at 185px (source 185), with matching ink density. |
| Size | 54.5px date, 47.5px day, 50px hour | Fitted to the source lines' ink height. |
| Baselines | y = 675, y = 792, y = 912 | Solved from the source ink boxes; the renders land within 1px top and bottom. The "2" sits on the same bottom row (911) as the source's flat-based "m". |
| Centres | x = 746, x = 747, x = 668.5 | The source lines' own ink centres; the "2" on the old "3"'s (ink x 658-679 → 658-678). |
| Address face | Open Sans Condensed Bold, 28.5px | The address panel uses a narrower face than the date panel. Best of 21 condensed candidates. Sized so "Madhu Bhandari ke ghar" spans the 273px the source's widest line did; four lines at the source's 42px pitch, centred on its block (ink y 1037-1185 vs the source's 1014-1208, same centre). |
| Colour | `#320a03` | Rendered stroke core averages RGB (54, 14, 6) vs the source's (55, 13, 6). |

Only the hour digit is redrawn: ":00 p.m" is the source's own ink, so the time line
keeps its original lettering. Outside the edited text areas the render is pixel-identical to the source (0 pixels differ).

## The video

| Time | Shot | On screen |
| --- | --- | --- |
| 0–2.5s | Title, slow push across to Krishna | Fade up from black; bell |
| 2.5–5.6s | Date / Day / Time panel, 1.8× | Date and day rise in; gold glint across the panel; bell |
| 5.6–8.9s | Address panel, 1.8× | The four address lines rise in, one every 0.3s; glint; bell |
| 8.9–12s | Pull back to the full poster | Glint over both panels; final bell; ends on the finished poster |

- **Camera:** one transform on `#camera` moves the plate, the text and the
  glints together. Every shot stays inside the poster, so its edges never show.
- **Address shot:** framed with the panel low in the frame. Centring on the
  panel would cut through the singer's name plate just below it.
- **Time line:** ":00 p.m" is baked into the plate, so the time shows from the
  first frame rather than being revealed.
- **Sparkles:** placed by a seeded PRNG, so every render is identical.
- **Soundtrack:** `assets/score.wav` comes from `tools/make_audio.py`. It is a
  soft Sa-Pa drone with temple-bell strikes on the reveal beats. It is fully
  synthesised, so there is no licensing to clear.

## Re-rendering

```bash
python3 tools/make_plate.py      # only if poster.jpg changes
python3 tools/make_audio.py      # only if the soundtrack changes
npm run check

# video
npx --yes hyperframes@0.7.94 render -q high -o renders/ek-shaam-radheshyam-24-10-2026.mp4
# still (one frame, then save it as the .png/.jpg)
npx --yes hyperframes@0.7.94 render -c stills/poster.html --format png-sequence --fps 1 -q high -o renders/frames
```
