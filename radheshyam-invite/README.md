# Ek Shaam Radheshyam — date change

The poster re-dated from **29.8.2026 (Saturday), 3:00 p.m** to
**26.10.2026 (Monday), 2:00 p.m**,
composed and rendered with HyperFrames.

Output: `renders/ek-shaam-radheshyam-26-10-2026-2pm.png` (lossless) and `.jpg` (q95, for WhatsApp).

## How it works

1. `tools/make_plate.py` lifts the old date, day and the "3" of the time out of `assets/poster.jpg`
   into `assets/plate.png`. The panel's parchment is near-flat (std ~1.2 levels),
   so each patch is a per-column interpolation between the clean rows above and
   below, plus fixed-seed grain at that std.
2. `index.html` lays the new lines over the plate as SVG text, so each baseline
   is set exactly.

| Property | Value | How it was established |
| --- | --- | --- |
| Typeface | Mukta Bold | Best of 20 candidates. Reproduces "29.8.2026" at 222px wide (source 221) and "Saturday" at 185px (source 185), with matching ink density. |
| Size | 54.5px date, 47.5px day, 50px hour | Fitted to the source lines' ink height. |
| Baselines | y = 675, y = 792, y = 912 | Solved from the source ink boxes; the renders land within 1px top and bottom. The "2" sits on the same bottom row (911) as the source's flat-based "m". |
| Centres | x = 746, x = 747, x = 668.5 | The source lines' own ink centres; the "2" on the old "3"'s (ink x 658-679 → 658-678). |
| Colour | `#320a03` | Rendered stroke core averages RGB (54, 14, 6) vs the source's (55, 13, 6). |

Only the hour digit is redrawn: ":00 p.m" is the source's own ink, so the time line
keeps its original lettering. Outside the three text areas the render is pixel-identical to the source (0 pixels differ).

## Re-rendering

```bash
python3 tools/make_plate.py      # only if poster.jpg changes
npm run check
npx --yes hyperframes@0.7.94 render --format png-sequence --fps 1 -q high -o renders/frames
```
