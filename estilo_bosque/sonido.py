"""Música de fondo, ambiente y efectos generados por código (sin derechos de autor)."""
import numpy as np

SR = 44100
rng = np.random.default_rng(42)


def _t(d):
    return np.arange(int(d * SR)) / SR


def lowpass(x, fc):
    """Filtro paso bajo de un polo (fc puede ser array del mismo largo)."""
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc; y[i] = acc
    return y


def lowpass_fast(x, fc):
    """Paso bajo de un polo con fc fijo, vectorizado vía scipy-free IIR por bloques."""
    a = np.exp(-2 * np.pi * fc / SR)
    # aproximación con filtrado FFT (respuesta de un polo)
    n = len(x); N = 1 << (n - 1).bit_length() + 1
    f = np.fft.rfftfreq(N, 1 / SR)
    H = (1 - a) / (1 - a * np.exp(-2j * np.pi * f / SR))
    return np.fft.irfft(np.fft.rfft(x, N) * H, N)[:n]


def env_adsr(n, a, r):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def saw_suave(f, t, armonicos=7):
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, armonicos + 1))


def nota(m):
    return 440 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------ música
def musica(dur, bpm=84):
    t = _t(dur); out = np.zeros_like(t)
    acordes = [[57, 60, 64], [53, 57, 60], [50, 53, 57], [52, 56, 59]]  # Am F Dm E
    comp = 4 * 60 / bpm * 2  # 2 compases por acorde
    i = 0; t0 = 0.0
    while t0 < dur:
        ac = acordes[i % 4]; d = min(comp, dur - t0)
        tt = _t(d); seg = np.zeros_like(tt)
        for m in ac:
            for det in (-0.004, 0.0, 0.004):
                seg += saw_suave(nota(m) * (1 + det), tt + t0, 5) * 0.06
        seg += np.sin(2 * np.pi * nota(ac[0] - 12) * tt) * 0.25  # bajo
        seg *= env_adsr(len(tt), 0.8, 0.8)
        s0 = int(t0 * SR); out[s0:s0 + len(seg)] += seg
        t0 += comp; i += 1
    out = lowpass_fast(out, 900)
    # arpegio tipo campanita (pentatónica menor)
    esc = [69, 72, 74, 76, 79, 81]
    paso = 60 / bpm / 2; k = 0; tp = 0.0
    while tp < dur - 0.6:
        if rng.random() < 0.55:
            f = nota(esc[rng.integers(len(esc))]); tt = _t(0.6)
            b = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt * 6) * 0.10
            s0 = int(tp * SR); out[s0:s0 + len(b)] += b
        tp += paso; k += 1
    # pulso grave (latido de suspense) en cada pulso
    tb = 0.0
    while tb < dur - 0.3:
        tt = _t(0.3); kick = np.sin(2 * np.pi * (55 + 40 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14) * 0.35
        s0 = int(tb * SR); out[s0:s0 + len(kick)] += kick
        tb += 60 / bpm
    out *= env_adsr(len(out), 1.5, 2.0)
    return out / (np.max(np.abs(out)) + 1e-9)


# ------------------------------------------------------------------ ambiente
def ambiente(dur):
    n = int(dur * SR)
    viento = lowpass_fast(rng.standard_normal(n), 250)
    viento *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * _t(dur))
    viento = viento / (np.max(np.abs(viento)) + 1e-9) * 0.25
    grillos = np.zeros(n); tc = 0.2
    while tc < dur - 0.5:
        f = rng.uniform(4200, 5200)
        for p in range(3):
            tt = _t(0.035); c = np.sin(2 * np.pi * f * tt) * np.hanning(len(tt)) * 0.12
            s0 = int((tc + p * 0.06) * SR); grillos[s0:s0 + len(c)] += c
        tc += rng.uniform(0.5, 1.1)
    return viento + grillos


# ------------------------------------------------------------------ efectos
def whoosh(d=0.45):
    tt = _t(d); x = rng.standard_normal(len(tt))
    fc = 300 + 3500 * np.sin(np.pi * tt / d) ** 2
    y = lowpass(x, fc) * np.sin(np.pi * tt / d) ** 1.5
    return y / np.max(np.abs(y)) * 0.6


def pop():
    tt = _t(0.12)
    f = 700 + 900 * (tt / 0.12)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 35) * 0.5


def golpe_grave():
    tt = _t(1.2)
    y = np.sin(2 * np.pi * (40 + 60 * np.exp(-tt * 8)) * tt) * np.exp(-tt * 3)
    y += lowpass_fast(rng.standard_normal(len(tt)), 200) * np.exp(-tt * 6) * 2
    return y / np.max(np.abs(y)) * 0.9


def gruñido(d=1.6):
    tt = _t(d)
    base = 75 + 15 * np.sin(2 * np.pi * 1.3 * tt) + 8 * rng.standard_normal(len(tt)).cumsum() / np.sqrt(len(tt))
    fase = 2 * np.pi * np.cumsum(base) / SR
    voz = saw_suave(1, fase / (2 * np.pi), 12)
    ruido = rng.standard_normal(len(tt))
    am = 0.6 + 0.4 * np.sin(2 * np.pi * 28 * tt + rng.standard_normal(len(tt)) * 0.3)
    y = lowpass_fast(voz * 0.6 + ruido * 0.9, 700) * am
    y *= env_adsr(len(tt), 0.15, 0.5)
    return y / np.max(np.abs(y)) * 0.8


def paso():
    tt = _t(0.09)
    y = lowpass_fast(rng.standard_normal(len(tt)), 1800) * np.exp(-tt * 45)
    return y / np.max(np.abs(y)) * 0.25


def latido():
    out = np.zeros(int(0.6 * SR))
    for off, a in ((0, 1.0), (0.22, 0.7)):
        tt = _t(0.25); th = np.sin(2 * np.pi * 50 * tt) * np.exp(-tt * 18) * a
        s0 = int(off * SR); out[s0:s0 + len(th)] += th
    return out * 0.9


def subida(d=1.0):
    tt = _t(d); x = rng.standard_normal(len(tt))
    y = lowpass(x, 200 + 5000 * (tt / d) ** 2) * (tt / d) ** 2
    return y / np.max(np.abs(y)) * 0.4


def pegar(pista, clip, t, gan=1.0):
    s0 = int(t * SR)
    if s0 >= len(pista): return
    e = min(len(pista), s0 + len(clip)); pista[s0:e] += clip[:e - s0] * gan
