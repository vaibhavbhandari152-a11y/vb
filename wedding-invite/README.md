# Wedding invitation — name swap

Replaces both names baked into the source invitation video:
**Shruti & Vaibhaw → Ayush & Bharti**. Everything else in the card — artwork,
layout, the wreath, the "&", date, venue, music and all three scene animations —
is the untouched original.

- Source: `source.mp4` (360×640, 21.13s, 30fps, 634 frames)
- Output: `renders/Ayush-and-Bharti.mp4`

## Approach

The old names are pixels in the footage, not text, so they can't be edited in
place. The composition plays the original video as its base layer and patches
only the two name lines:

1. A flat `#fff` rectangle covers each old name. The wreath interior behind them
   is pure white (verified: 0 non-white pixels across both patch rects on frames
   388–389, after the scene-3 transition clears and before the names type on), so
   the patches are seamless — no clean-plate image needed.
2. The new names are drawn as SVG text on top, in the source's own typeface.

Both patches enter at 12.9333s (frame 388) and hold to the end.

## Matching the source

Everything below was measured off the source frames rather than eyeballed.

| Property | Value | How it was established |
| --- | --- | --- |
| Typeface | Great Vibes | Best of 10 script candidates. At 30px it reproduces "Vaibhaw" at 94×29px and at 37px "Shruti" at 84×34px — both the source's exact ink boxes. |
| Size | 37px, both lines | The template's own maximum (what "Shruti" used). Both new names fit their bands at it, so the pair reads at one scale. |
| Colour | `#2c2c26` | Calibrated so rendered ink averages RGB ~(89, 89, 84) vs the original's (90.2, 90.2, 84.2). |
| Baselines | y = 176 and y = 235 | Solved against each original ink box; ±1px both land visibly off. |
| Centres | x = 187.9 and x = 200.3 | Each line's own advance-centre in the source. A least-squares fit of the wreath ring puts its centre at x≈186 — the top name sits on that axis, the lower one is nudged right, staggering the pair around the off-centre "&". Keeping both preserves that composition. |
| Patches | 144,144 → 91×41px and 144,206 → 110×35px | The largest rects that cover the old ink and still clear the wreath ring (x≥237 on line 1, x≥254 on line 2), the sprig on the left (x≤142), and the "&" between the lines (y 189–205). |
| Type-on | 1 letter / 2 frames, from f390 and f392 | The source types both names at this cadence with the lower line starting 2 frames later; the new names pick up the same frames. |

Two rendering details keep the new text from looking pasted on:

- `filter: blur(0.3px)` forces its own compositing layer, which drops Chromium's
  subpixel antialiasing. Without it the strokes carry orange/blue fringes (colour
  spread 60 vs the source's 6) where the card's own type is neutral grey. The
  sub-pixel blur also softens the vector edges to sit with the surrounding artwork.
- The reveal `set()` calls sit half a frame early. Landing one exactly on a frame
  time is a float-equality coin toss, which made every letter appear one frame late.

## Verification

Against the source, frame by frame across all 634 frames:

- Outside the two name areas, 0.02% of pixels differ at all — chroma rounding from
  the decode/re-encode round trip, in saturated orange florals. The source's own
  frame-to-frame compression noise is an order of magnitude larger, so nothing
  structural changed.
- Type-on lands exactly: "Ayush" on frames 390/392/394/396/398, "Bharti" on
  392/394/396/398/400/402.
- The "&" rows (y 189–205) come through pixel-identical, and the "Ayush" descender
  stops at y=187 — two rows clear of it, with no horizontal overlap.
- Audio correlates at 0.997 with the original, offset 21ms (AAC priming delay,
  sub-frame).

## Changing the names again

The constants above are calibrated for these two names — a different one needs its
size and centring re-checked so it still sits in the wreath. To change one, edit
the per-letter `<tspan>`s in `index.html`, adjust `font-size` / `x` on that
`<text>`, then:

```bash
npm run check
npm run render
```

The letter count drives the type-on automatically; no timeline edit is needed. If
a name is long enough to run past the wreath ring, widen its patch too — the clean
limits are x 142–235 on line 1 and x 142–253 on line 2.

## Notes

- GSAP is vendored in `vendor/` and Great Vibes in `assets/` — this environment
  blocks the CDN, and self-hosting keeps renders deterministic and offline.
- Output is rendered at the source's native 360×640. Upscaling would make the new
  names crisp against blurry surrounding artwork; no detail exists to recover.
