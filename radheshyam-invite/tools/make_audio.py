"""Build assets/score.wav: the video's devotional soundtrack.

Every instrument is synthesised here, so there is no recording to license and
every render is identical. Run from the project root:
    python3 tools/make_audio.py

Arrangement (Sa = D, 100 bpm, keherwa taal from 2.5s):
  0.0s   shankh (conch) blown over a temple bell, tanpura enters
  0.6s   bansuri phrase over the title / Krishna shot
  2.5s   harmonium bhajan melody, dholak in keherwa, manjira on the beat
  bells  on each on-screen reveal (BELLS below; index.html uses the same beats)
  10.9s  final bell; the last Sa rings out as everything fades by 12s
"""
import wave

import numpy as np

SR = 44100
DURATION = 12.0
N = int(SR * DURATION)
t = np.arange(N) / SR
rng = np.random.default_rng(24102026)

SA = 146.83  # D3
# Just-intonation swaras, relative to Sa.
SWARA = {"S": 1, "R": 9 / 8, "G": 5 / 4, "M": 4 / 3, "P": 3 / 2, "D": 5 / 3, "N": 15 / 8}

BPM = 100
BEAT = 60 / BPM  # 0.6s
GROOVE_START = 2.5
# Bell strikes: opening, date reveal, address reveal, pull-back, finale.
BELLS = [(0.05, 0.55), (3.7, 0.32), (6.7, 0.32), (8.5, 0.4), (10.9, 0.5)]


def freq(swara, octave=0):
    """'S', 'R'... with ' for the upper octave and . for the lower."""
    base = swara.strip("'.")
    octave += swara.count("'") - swara.count(".")
    return SA * SWARA[base] * 2.0**octave


def env_adsr(n, a, r, sr=SR):
    e = np.ones(n)
    na, nr = max(1, int(a * sr)), max(1, int(r * sr))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def place(buf, start, sig):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


# ---- Tanpura: Karplus-Strong plucks with a jawari buzz ------------------------
def pluck(f, dur, bright=0.996):
    n = int(dur * SR)
    p = int(round(SR / f))
    out = np.zeros(n)
    buf = rng.uniform(-1, 1, p)
    buf = np.convolve(buf, np.ones(3) / 3, "same")
    pos = 0
    while pos < n:
        m = min(p, n - pos)
        out[pos : pos + m] = buf[:m]
        nxt = bright * 0.5 * (buf + np.roll(buf, -1))
        buf = nxt
        pos += p
    # Jawari: the bridge's buzz, a soft asymmetric saturation that adds the
    # shimmering upper partials a plain plucked string lacks.
    out = np.tanh(2.2 * out + 0.25 * out**2) / 1.6
    return out * env_adsr(n, 0.004, 0.3)


def tanpura():
    out = np.zeros(N)
    cycle = ["P.", "S", "S", "S."]  # Pa, Sa, Sa, low Sa
    step = 0.78
    k, start = 0, 0.15
    while start < DURATION - 0.5:
        s = cycle[k % 4]
        place(out, start, pluck(freq(s), 3.4))
        start += step if k % 4 != 3 else step * 1.6
        k += 1
    return out * np.clip(t / 1.2, 0, 1)


# ---- Shankh (conch) ---------------------------------------------------------
def shankh(start, dur=1.9, f0=220.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    # Blown conch: the pitch rises into the note, wavers, and drops at the end.
    bend = 0.93 + 0.07 * np.clip(tt / 0.35, 0, 1) - 0.04 * np.clip((tt - dur + 0.3) / 0.3, 0, 1)
    f = f0 * bend * (1 + 0.004 * np.sin(2 * np.pi * 5.2 * tt))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = sum(a * np.sin(k * ph) for k, a in enumerate((1, 0.75, 0.6, 0.42, 0.3, 0.2, 0.13, 0.08, 0.05), 1))
    # Breath noise, band-limited to roughly 0.7-5 kHz so it hisses, not rumbles.
    noise = rng.normal(0, 1, n)
    breath = (np.convolve(noise, np.ones(8) / 8, "same") - np.convolve(noise, np.ones(64) / 64, "same")) * 0.18
    swell = np.clip(tt / 0.3, 0, 1) ** 1.5 * np.clip((dur - tt) / 0.35, 0, 1)
    return (tone / 3.2 + breath) * swell


# ---- Ghanti (temple bell) -----------------------------------------------------
def bell(dur=4.0, f0=1318.5):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    out = np.zeros(n)
    for ratio, amp, decay in ((1.0, 1.0, 2.6), (2.32, 0.5, 1.6), (4.25, 0.28, 0.9), (6.63, 0.16, 0.5), (0.5, 0.22, 3.2)):
        for d in (0.0, 2.7):  # paired detune: the bell's slow beating
            out += amp * np.sin(2 * np.pi * (f0 * ratio + d) * tt) * np.exp(-tt / decay)
    click = np.convolve(rng.normal(0, 1, n) * np.exp(-tt / 0.004), np.ones(6) / 6, "same")
    return out / 4.4 + 0.5 * click


# ---- Bansuri (bamboo flute) ---------------------------------------------------
def bansuri(notes, start):
    """notes: (swara, seconds). Glides (meend) into each note over 110ms."""
    total = sum(d for _, d in notes)
    n = int(total * SR)
    f = np.empty(n)
    vib = np.zeros(n)
    pos, prev = 0, freq(notes[0][0], 1) * 0.94
    for s, d in notes:
        m = int(d * SR)
        target = freq(s, 1)
        g = min(m, int(0.11 * SR))
        f[pos : pos + g] = np.geomspace(prev, target, g)
        f[pos + g : pos + m] = target
        # Vibrato blooms in only on held notes, as a player would.
        if d > 0.45:
            tt = np.arange(m) / SR
            vib[pos : pos + m] = 0.006 * np.clip((tt - 0.2) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.4 * tt)
        prev, pos = target, pos + m
    f = f[:pos] * (1 + vib[:pos])
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.07 * np.sin(3 * ph)
    breath = rng.normal(0, 1, pos)
    breath = (breath - np.convolve(breath, np.ones(4) / 4, "same")) * 0.05
    e = env_adsr(pos, 0.12, 0.5)
    out = np.zeros(N)
    place(out, start, (tone + breath * (0.6 + 0.4 * np.abs(np.sin(ph / 2)))) * e)
    return out


# ---- Harmonium ------------------------------------------------------------------
def reed(f, dur):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    out = np.zeros(n)
    for detune in (1.0, 1.0023):  # two reeds a hair apart: the harmonium's chorus
        ph = 2 * np.pi * f * detune * tt
        for k in range(1, 18):
            if f * k > 9000:
                break
            out += np.sin(k * ph) / k / (1 + (f * k / 1800) ** 2)
    # Bass coupler: the reed an octave down, quieter.
    ph = 2 * np.pi * f / 2 * tt
    for k in range(1, 10):
        out += 0.35 * np.sin(k * ph) / k / (1 + (f / 2 * k / 1500) ** 2)
    bellows = 1 + 0.03 * np.sin(2 * np.pi * 0.9 * tt)
    return out * bellows * env_adsr(n, 0.035, 0.07)


def harmonium(melody, start):
    out = np.zeros(N)
    at = start
    for s, beats in melody:
        d = beats * BEAT
        place(out, at, reed(freq(s), d + 0.05))
        at += d
    return out


def harmonium_drone(start):
    n = N - int(start * SR)
    drone = reed(freq("S", -1), n / SR) + 0.7 * reed(freq("P", -1), n / SR)
    out = np.zeros(N)
    place(out, start, drone * env_adsr(len(drone), 0.6, 0.01))
    return out


# ---- Dholak and manjira, keherwa taal -------------------------------------------
def dholak_bass(dur=0.45):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 95 + 60 * np.exp(-tt / 0.03)  # the palm pressing the left head bends it
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.exp(-tt / 0.16)


def dholak_treble(dur=0.25, f0=460.0, decay=0.07):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    tone = np.sin(2 * np.pi * f0 * tt) + 0.6 * np.sin(2 * np.pi * f0 * 1.52 * tt) + 0.3 * np.sin(2 * np.pi * f0 * 2.31 * tt)
    slap = rng.normal(0, 1, n) * np.exp(-tt / 0.006)
    return tone * np.exp(-tt / decay) * 0.6 + 0.35 * slap


def manjira(open_=True):
    dur = 0.9 if open_ else 0.12
    n = int(dur * SR)
    tt = np.arange(n) / SR
    decay = 0.45 if open_ else 0.03
    out = np.zeros(n)
    for fr, a in ((2870, 1.0), (3935, 0.7), (5210, 0.55), (6480, 0.4), (7790, 0.3)):
        for d in (0, 11):
            out += a * np.sin(2 * np.pi * (fr + d) * tt + rng.uniform(0, 6.28))
    hit = rng.normal(0, 1, n) * np.exp(-tt / 0.003)
    return (out / 6 * np.exp(-tt / decay) + 0.3 * hit)


def rhythm(start, end):
    drums = np.zeros(N)
    cym = np.zeros(N)
    # Keherwa: Dha Ge Na Ti | Na Ka Dhi Na
    bols = ["dha", "ge", "na", "ti", "na", "ka", "dhi", "na"]
    k = 0
    at = start
    while at < end:
        b = bols[k % 8]
        if b in ("dha", "dhi", "ge"):
            place(drums, at, dholak_bass() * (1.0 if b != "ge" else 0.75))
        if b in ("dha", "dhi", "na"):
            place(drums, at, dholak_treble() * (0.8 if b == "na" else 0.6))
        if b in ("ti", "ka"):
            place(drums, at, dholak_treble(0.12, 700.0, 0.025) * 0.45)
        # Off-beat "ka" ghost note on the right head keeps the bhajan lilt.
        place(drums, at + BEAT * 0.5, dholak_treble(0.1, 650.0, 0.02) * 0.22)
        place(cym, at, manjira(open_=(k % 2 == 0)) * (1.0 if k % 2 == 0 else 0.6))
        at += BEAT
        k += 1
    fade = np.clip((end + 0.3 - t) / 0.8, 0, 1)
    return drums * fade, cym * fade


# ---- Reverb: a small stone-hall impulse ------------------------------------------
def reverb(x, seconds=1.6, mix=0.22):
    n = int(seconds * SR)
    tt = np.arange(n) / SR
    ir = rng.normal(0, 1, n) * np.exp(-tt / 0.45)
    ir[: int(0.012 * SR)] = 0  # pre-delay
    ir /= np.sqrt((ir**2).sum())
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    wet = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    return (1 - mix) * x + mix * wet * 3.0


# ---- Score ----------------------------------------------------------------------
# A bhajan phrase pair in Bilawal (all shuddh swaras), 8 beats each: the first
# climbs to Pa and rests on Ga, the answer comes home to Sa.
MELODY = [
    ("G", 1), ("G", 0.5), ("M", 0.5), ("P", 1), ("P", 1), ("D", 0.5), ("P", 0.5), ("M", 1), ("G", 2),
    ("G", 1), ("M", 0.5), ("G", 0.5), ("R", 1), ("S", 1), ("R", 0.5), ("G", 0.5), ("R", 1), ("S", 2.5),
]
# Over the title: a flute calls, lifting to Sa' and settling on Pa.
FLUTE = [("P", 0.5), ("D", 0.25), ("P", 0.25), ("S'", 0.7), ("D", 0.2), ("P", 0.35)]

tracks = {
    "tanpura": (tanpura(), 0.16),
    "shankh": (np.zeros(N), 0.42),
    "bells": (np.zeros(N), 0.6),
    "bansuri": (bansuri(FLUTE, 0.55), 0.20),
    "harmonium": (harmonium(MELODY, GROOVE_START), 0.085),
    "drone": (harmonium_drone(GROOVE_START), 0.025),
}
place(tracks["shankh"][0], 0.0, shankh(0.0))
for at, g in BELLS:
    place(tracks["bells"][0], at, bell() * g)
drums, cym = rhythm(GROOVE_START, DURATION - 0.9)
tracks["dholak"] = (drums, 0.38)
tracks["manjira"] = (cym, 0.28)

mix = sum(sig * gain for sig, gain in tracks.values())
mix = reverb(mix)
mix *= np.clip((DURATION - t) / 0.9, 0, 1)
mix = np.tanh(1.3 * mix / np.abs(mix).max()) / np.tanh(1.3)  # gentle glue
mix *= 0.89  # -1 dBFS

delay = int(0.011 * SR)  # a little stereo width
left, right = mix, np.concatenate([np.zeros(delay), mix[:-delay]])
pcm = (np.stack([left, right], 1) * 32767).astype("<i2")
with wave.open("assets/score.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/score.wav")
