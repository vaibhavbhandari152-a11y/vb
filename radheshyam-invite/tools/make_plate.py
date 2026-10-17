"""Build assets/plate.png: the poster with the old date, day, hour and address
lifted out.

Both panels' parchment is near-flat within a band (std ~1.2 levels), so
each patch is filled by interpolating, per column, between the clean rows just
above and just below it, plus fixed-seed grain at the measured std. Run from
the project root:  python3 tools/make_plate.py
"""
import numpy as np
from PIL import Image, ImageFilter

# x0, y0, x1, y1 (inclusive). Each is the old ink box dilated ~8px to take the
# JPEG halo with it, and still clears the pills above and below
# (Date pill ends y=621, Day pill y=700-742, Time pill starts y=820).
PATCHES = {
    "date": (628, 631, 864, 686),  # "29.8.2026" ink 636-856 x 639-675
    "day": (647, 750, 847, 812),   # "Saturday"  ink 655-839 x 758-804
    # Only the "3" of "3:00 p.m" - the ":00 p.m" stays the source's own ink.
    # Right edge stops short of the colon (ink from x=684).
    "hour": (654, 875, 682, 916),  # "3" ink 658-679 x 879-912
    # Address panel: one band per old line, each bounded by the clean gaps
    # between lines (the top ornament ends y=1011, the bottom one starts
    # y=1218). Line 3 runs nearly frame to frame, so its band does too.
    "addr1": (640, 1011, 866, 1050),  # "Navita ji ke ghar"     646-858 x 1014-1046
    "addr2": (627, 1054, 874, 1090),  # "near A.V.M school"     633-868 x 1057-1082
    "addr3": (606, 1094, 890, 1136),  # "Adarsh Enclave colony" 612-884 x 1100-1131
    "addr4": (639, 1140, 863, 1173),  # "Bhandari Mohala"       645-857 x 1142-1166
    "addr5": (704, 1177, 797, 1213),  # "Batala"                710-791 x 1184-1208
}
EDGE_ROWS = 3   # clean rows sampled on each side
GRAIN_STD = 1.2

img = np.asarray(Image.open("assets/poster.jpg").convert("RGB")).astype(float)
rng = np.random.default_rng(29102026)

for x0, y0, x1, y1 in PATCHES.values():
    top = img[y0 - EDGE_ROWS:y0, x0:x1 + 1].mean(0)
    bot = img[y1 + 1:y1 + 1 + EDGE_ROWS, x0:x1 + 1].mean(0)
    # Smooth along x so a stray dark pixel in a sample row can't streak down.
    k = np.ones(9) / 9
    for edge in (top, bot):
        for c in range(3):
            edge[:, c] = np.convolve(np.pad(edge[:, c], 4, mode="edge"), k, "valid")
    h = y1 - y0 + 1
    t = ((np.arange(h) + 0.5) / h)[:, None, None]
    fill = (1 - t) * top[None] + t * bot[None]
    grain = rng.normal(0, GRAIN_STD, fill.shape[:2])[..., None]
    img[y0:y1 + 1, x0:x1 + 1] = fill + grain

out = Image.fromarray(np.clip(img.round(), 0, 255).astype(np.uint8))
out.save("assets/plate.png")
print("wrote assets/plate.png")
