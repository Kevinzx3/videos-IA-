"""Synthesized music bed and SFX (no external assets). Usage: python3 sfx.py OUTDIR DURATION"""
import numpy as np, wave, sys, os
SR = 44100
rng = np.random.default_rng(1)

def save(path, x):
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    s = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    if s.ndim == 1: s = np.stack([s, s], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s.tobytes())

def lowpass(x, a):  # one-pole, a in (0,1): smaller = darker
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += a * (v - acc); y[i] = acc
    return y

def t(d): return np.arange(int(SR * d)) / SR

def music(d):
    tt = t(d)
    notes = [55.0, 55.0, 51.91, 49.0]  # A1 A1 G#1 G1, slow minor descent
    seg = np.minimum((tt // 8).astype(int) % 4, 3)
    f = np.array(notes)[seg]
    ph = 2 * np.pi * np.cumsum(f) / SR
    drone = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3.01 * ph)
    pulse = 0.6 + 0.4 * np.sin(2 * np.pi * 0.5 * tt) ** 8  # heartbeat-ish swell every 2s
    pad = lowpass(rng.standard_normal(len(tt)), 0.01) * 3 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * tt))
    hi = np.sin(2 * np.pi * 440 * tt + 3 * np.sin(2 * np.pi * 0.2 * tt)) * 0.04 * (np.sin(2 * np.pi * 0.05 * tt) > 0.3)
    x = (drone * pulse + pad) * 0.6 + hi
    fade = np.minimum(1, np.minimum(tt / 2, (d - tt) / 2))
    return x * fade

def explosion():
    tt = t(2.5); env = np.exp(-tt * 2.2) * np.minimum(1, tt / 0.005)
    n = lowpass(rng.standard_normal(len(tt)), 0.08)
    boom = np.sin(2 * np.pi * (60 * np.exp(-tt * 3)) * tt) * np.exp(-tt * 3)
    return n * env * 4 + boom * 1.5

def whoosh():
    tt = t(0.6); env = np.sin(np.pi * tt / 0.6) ** 2
    n = rng.standard_normal(len(tt)); out = np.empty_like(n); acc = 0
    a = 0.02 + 0.3 * env  # brighter in the middle = sweep
    for i, v in enumerate(n): acc += a[i] * (v - acc); out[i] = acc
    return out * env

def clink():
    tt = t(1.2)
    return sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * k) for f, k in [(2400, 6), (3710, 9), (5230, 12)]) + rng.standard_normal(len(tt)) * np.exp(-tt * 60)

def thud():
    tt = t(1.0)
    return np.sin(2 * np.pi * (90 * np.exp(-tt * 8) + 40) * tt) * np.exp(-tt * 9) + lowpass(rng.standard_normal(len(tt)), 0.1) * np.exp(-tt * 25) * 3

def boom():
    tt = t(2.5)
    return np.sin(2 * np.pi * (80 * np.exp(-tt * 1.5) + 30) * tt) * np.exp(-tt * 1.6) + lowpass(rng.standard_normal(len(tt)), 0.03) * np.exp(-tt * 4) * 2

def cart():
    tt = t(4.0); x = lowpass(rng.standard_normal(len(tt)), 0.05) * 0.5
    for k in np.arange(0, 4, 0.45):  # wheel knocks + creak
        i = int(k * SR); seg = t(0.25)
        x[i:i+len(seg)] += (np.sin(2 * np.pi * 180 * seg) * np.exp(-seg * 30))[:len(x)-i]
        x[i:i+len(seg)] += (np.sin(2 * np.pi * (700 + 300 * seg) * seg) * 0.15 * np.exp(-seg * 8))[:len(x)-i]
    return x

if __name__ == '__main__':
    out, dur = sys.argv[1], float(sys.argv[2]); os.makedirs(out, exist_ok=True)
    for name, x in [('musica', music(dur)), ('explosion', explosion()), ('whoosh', whoosh()), ('chispa', clink()),
                    ('golpe', thud()), ('impacto', boom()), ('carreta', cart())]:
        assert np.isfinite(x).all() and len(x) > 0, name
        save(f'{out}/{name}.wav', x)
    print('ok')
