"""Build assets/score.wav: the video's soundtrack, synthesised so it carries
no licensing questions and renders identically every time.

A soft Sa-Pa drone (D3 / A3, tanpura-like swell) under small temple-bell
(ghanti) strikes timed to the video's beats. Run from the project root:
    python3 tools/make_audio.py
"""
import wave

import numpy as np

SR = 44100
DURATION = 12.0
# (time s, gain) - opening, date reveal, address reveal, pull-back.
STRIKES = [(0.10, 0.55), (3.40, 0.30), (6.45, 0.30), (8.95, 0.42)]

t = np.arange(int(SR * DURATION)) / SR
rng = np.random.default_rng(24102026)


def drone():
    out = np.zeros_like(t)
    for f0, amp in ((146.83, 1.0), (220.0, 0.6), (293.66, 0.35)):
        for n, h in enumerate((1.0, 0.45, 0.25, 0.12), start=1):
            # Slight detune per voice gives the tanpura's slow shimmer.
            det = 1 + 0.0015 * np.sin(2 * np.pi * 0.07 * n * t)
            out += amp * h * np.sin(2 * np.pi * f0 * n * det * t)
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * 0.18 * t - np.pi / 2)
    env = np.clip(t / 1.5, 0, 1) * np.clip((DURATION - t) / 1.5, 0, 1)
    return out * swell * env


def bell(start, gain):
    out = np.zeros_like(t)
    tt = t - start
    on = tt >= 0
    tt = np.where(on, tt, 0)
    f0 = 1318.5  # E6: a small brass ghanti
    # Inharmonic partials with paired detunes for the bell's beating.
    for ratio, amp, decay in ((1.0, 1.0, 2.6), (2.32, 0.5, 1.6), (4.25, 0.28, 0.9),
                              (6.63, 0.16, 0.5), (0.5, 0.22, 3.2)):
        for d in (0.0, 2.7):
            out += amp * np.sin(2 * np.pi * (f0 * ratio + d) * tt) * np.exp(-tt / decay)
    # Strike transient: a few ms of filtered noise.
    click = rng.normal(0, 1, t.shape) * np.exp(-tt / 0.004)
    click = np.convolve(click, np.ones(6) / 6, "same")
    return gain * on * (out / 4.4 + 0.5 * click)


mix = 0.10 * drone() / 2.5
for s, g in STRIKES:
    mix += bell(s, g)
mix *= np.clip((DURATION - t) / 0.4, 0, 1)
peak = np.abs(mix).max()
mix = mix / peak * 0.7  # -3 dBFS headroom

# A touch of stereo width: right channel delayed 9 ms.
delay = int(0.009 * SR)
left = mix
right = np.concatenate([np.zeros(delay), mix[:-delay]])
pcm = (np.stack([left, right], 1) * 32767).astype("<i2")
with wave.open("assets/score.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/score.wav")
