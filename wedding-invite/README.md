# Wedding invitation — name swap

Replaces the groom's name baked into the source invitation video: **Vaibhaw → Ayush**.
Everything else in the card — artwork, layout, the bride's name, date, venue, music and
all three scene animations — is the untouched original.

- Source: `source.mp4` (360×640, 21.13s, 30fps, 634 frames)
- Output: `renders/shruti-and-ayush.mp4`

## Approach

The old name is pixels in the footage, not text, so it can't be edited in place. The
composition plays the original video as its base layer and patches only the name:

1. A flat `#fff` rectangle covers the old name. The card interior behind it is pure
   white (verified: 0 variance across the patch region on a frame before the name types
   on), so the patch is seamless — no clean-plate image needed.
2. The new name is drawn as SVG text on top, in the source's own typeface.

The patch enters at 12.9333s — after the wreath finishes drawing, one beat before the
source starts typing the old name at 13.0667s — and holds to the end.

## Matching the source

Everything below was measured off the source frames rather than eyeballed.

| Property   | Value                        | How it was established                                                                                       |
| ---------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Typeface   | Great Vibes                  | Best of 10 script candidates. At 30px it reproduces "Vaibhaw" at 94×29px — the source's exact ink box.        |
| Size       | 35px                         | Matches the cap height of "Shruti" (set at ~37px), so the two names read as a pair.                          |
| Colour     | `#2c2c26`                    | Calibrated so rendered ink averages RGB(89.5, 89.4, 84.5) vs the original's (90.2, 90.2, 84.2).              |
| Baseline   | y = 235                      | Solved against the original ink box; 234 and 236 both land a pixel off.                                       |
| Left edge  | x = 164                      | Pen origin, centring the word on x≈201.5 where the old name was centred.                                      |
| Patch      | 153,206 → 100×36px           | Covers the old ink (x155–248, y209–237) with margin, clear of the "&" above and the wreath circle at x≥253.  |
| Type-on    | 1 letter / 2 frames from f392| The source types both names at this cadence; "Ayush" starts on the same frame so they stay in lockstep.       |

Two rendering details keep the new text from looking pasted on:

- `filter: blur(0.3px)` forces its own compositing layer, which drops Chromium's subpixel
  antialiasing. Without it the strokes carry orange/blue fringes (colour spread 60 vs the
  source's 6) where the card's own type is neutral grey. The sub-pixel blur also softens
  the vector edges to sit with the surrounding artwork.
- The reveal `set()` calls sit half a frame early. Landing one exactly on a frame time is a
  float-equality coin toss, which made every letter appear one frame late.

## Verification

Against the source, frame by frame across all 634 frames:

- Outside the name area, 0.02% of pixels differ at all — chroma rounding from the
  decode/re-encode round trip, in saturated orange florals. The source's own frame-to-frame
  compression noise is an order of magnitude larger, so nothing structural changed.
- Type-on lands on frames 392/394/396/398/400 exactly, matching the source's cadence.
- Audio correlates at 0.997 with the original, offset 21ms (AAC priming delay, sub-frame).

## Changing the name again

The constants above are calibrated for "Ayush" specifically — a different name needs the
size and centring re-checked so it still sits in the wreath. To change it, edit the
per-letter `<tspan>`s in `index.html`, adjust `font-size` / `x` on `#name-text`, then:

```bash
npm run check
npm run render
```

The letter count drives the type-on automatically; no timeline edit is needed.

## Notes

- GSAP is vendored in `vendor/` and Great Vibes in `assets/` — this environment blocks the
  CDN, and self-hosting keeps renders deterministic and offline.
- Output is rendered at the source's native 360×640. Upscaling would make the new name
  crisp against blurry surrounding artwork; no detail exists to recover.
