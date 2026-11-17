#!/usr/bin/env python3
"""Música lo-fi original + efectos de sonido sintetizados + mezcla con la voz.

Todo el audio (salvo la voz) se genera por síntesis: no hay derechos de terceros.

Uso:
    python3 audio.py voz.wav efectos.sfx.json salida.wav --bpm 104
"""
import argparse
import json
import subprocess
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def leer_wav(ruta):
    with wave.open(ruta) as w:
        n, ch, sw = w.getnframes(), w.getnchannels(), w.getsampwidth()
        x = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
        if ch > 1:
            x = x.reshape(-1, ch).mean(1)
        assert w.getframerate() == SR
    return x


def guardar_wav(ruta, x):
    x = np.clip(x, -1, 1)
    est = np.stack([x, x], 1) if x.ndim == 1 else x
    with wave.open(ruta, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((est * 32767).astype(np.int16).tobytes())


def _sumar(out, a, x):
    if 0 <= a < len(out):
        n = min(len(x), len(out) - a)
        out[a:a + n] += x[:n]


def t_(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4))
    return e


def lp(x, k):
    """Paso bajo simple (media móvil)."""
    if k <= 1:
        return x
    return np.convolve(x, np.ones(k) / k, "same")


def ruido(d):
    return rng.uniform(-1, 1, int(d * SR))


# ------------------------------------------------------------------ efectos
def sfx_whoosh(d=0.45, grave=False):
    n = ruido(d)
    t = t_(d)
    out = np.zeros_like(n)
    ks = np.linspace(40 if not grave else 120, 4 if not grave else 20, 8)
    seg = len(n) // len(ks)
    for i, k in enumerate(ks):  # barrido de filtro
        a, b = i * seg, (i + 1) * seg if i < len(ks) - 1 else len(n)
        out[a:b] = lp(n, int(k))[a:b]
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return out * e * (3.5 if not grave else 6)


def sfx_pop(f0=500):
    t = t_(0.12)
    f = f0 + 900 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.04) * 0.9


def sfx_impacto():
    t = t_(0.7)
    f = 50 + 90 * np.exp(-t * 18)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.25)
    golpe = lp(ruido(0.7), 6) * env(len(t), 0.001, 0.05) * 1.5
    return (sub + golpe) * 0.9


def sfx_blip():
    t = t_(0.18)
    a = np.sin(2 * np.pi * 1300 * t) * env(len(t), 0.002, 0.05)
    b = np.sin(2 * np.pi * 1950 * t) * env(len(t), 0.002, 0.05)
    b = np.roll(b, int(0.06 * SR)) * (t > 0.06)
    return (a + b) * 0.35


def sfx_ding():
    t = t_(1.0)
    x = sum(np.sin(2 * np.pi * f * t) * w for f, w in ((1568, 1), (2352, 0.5), (3136, 0.25), (4704, 0.1)))
    return x * env(len(t), 0.002, 0.35) * 0.3


def sfx_squish():
    t = t_(0.3)
    f = 300 + 200 * np.sin(t * 60)
    tono = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4
    return (lp(ruido(0.3), 12) * 2 + tono) * env(len(t), 0.01, 0.1) * 0.6


def sfx_boing():
    t = t_(0.5)
    f = 180 + 220 * t / 0.5 + 40 * np.sin(2 * np.pi * 18 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.003, 0.2) * 0.6


def sfx_click():
    t = t_(0.05)
    return lp(ruido(0.05), 2) * env(len(t), 0.0005, 0.008) * 0.9


def sfx_tictac(d=1.5, n=8):
    out = np.zeros(int(d * SR))
    for i in range(n):
        a = int(i * d / n * SR)
        c = sfx_click() * (0.8 if i % 2 else 0.5)
        _sumar(out, a, c)
    return out


def sfx_riser(d=0.7, suave=False):
    t = t_(d)
    f = 200 + 900 * (t / d) ** 2
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + lp(ruido(d), 3) * 0.4
    return x * (t / d) ** 2 * (0.5 if suave else 0.8)


def sfx_scratch():
    t = t_(0.4)
    f = 800 + 600 * np.sin(2 * np.pi * 9 * t)
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    return lp(saw + ruido(0.4) * 0.5, 4) * env(len(t), 0.005, 0.18) * 0.6


def sfx_bonk():
    t = t_(0.35)
    f = 420 * np.exp(-t * 4)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) + lp(ruido(0.35), 3) * 0.3) * env(len(t), 0.001, 0.08) * 0.8


def sfx_burbujas(d=1.0):
    out = np.zeros(int(d * SR))
    for i in range(7):
        a = int(rng.uniform(0, d - 0.1) * SR)
        t = t_(0.08)
        f = rng.uniform(500, 1100) * (1 + 3 * t)
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.03) * 0.3
        out[a:a + len(b)] += b
    return out


def sfx_goteo():
    out = np.zeros(int(1.2 * SR))
    for i in range(3):
        b = sfx_pop(900 + i * 150) * 0.5
        a = int(i * 0.35 * SR)
        out[a:a + len(b)] += b
    return out


def sfx_paso():
    out = np.zeros(int(1.0 * SR))
    for i in range(3):
        t = t_(0.1)
        b = lp(ruido(0.1), 20) * env(len(t), 0.001, 0.03) * 2.0
        a = int(i * 0.32 * SR)
        out[a:a + len(b)] += b
    return out


def sfx_estirar():
    t = t_(0.6)
    f = 150 + 250 * (t / 0.6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.6) * 0.35


def sfx_espacio(d=1.6):
    t = t_(d)
    x = sum(np.sin(2 * np.pi * f * t) for f in (220, 277, 330)) / 3
    return x * np.sin(np.pi * t / d) * 0.25


def sfx_chapoteo(d=0.9):
    out = np.zeros(int(d * SR))
    for i in range(6):
        t = t_(0.12)
        b = lp(ruido(0.12), 5) * env(len(t), 0.002, 0.04) * 1.2
        a = int(rng.uniform(0, d - 0.12) * SR)
        out[a:a + len(b)] += b
    return out


def sfx_ola(d=1.6):
    t = t_(d)
    return lp(ruido(d), 30) * 4 * np.sin(np.pi * t / d) ** 2 * 0.6


def sfx_buzz():
    t = t_(0.45)
    saw = 2 * ((140 * t) % 1) - 1
    return lp(saw, 3) * env(len(t), 0.005, 0.3) * 0.45


def sfx_latido(d=1.3):
    out = np.zeros(int(d * SR))
    for i, a0 in enumerate((0.0, 0.18, 0.75, 0.93)):
        t = t_(0.15)
        b = np.sin(2 * np.pi * 55 * t) * env(len(t), 0.002, 0.05) * (0.9 if i % 2 == 0 else 0.6)
        a = int(a0 * SR)
        _sumar(out, a, b)
    return out


def sfx_alarma(d=1.0):
    t = t_(d)
    f = np.where((t * 4).astype(int) % 2 == 0, 880, 660)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.18 * np.minimum(1, (d - t) * 10)


def sfx_silbato(d=0.6):
    t = t_(d)
    f = 2600 + 120 * np.sin(2 * np.pi * 30 * t)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) + lp(ruido(d), 2) * 0.15) * env(len(t), 0.01, 0.5) * 0.25


SFX = {
    "whoosh": lambda: sfx_whoosh(), "whoosh_grave": lambda: sfx_whoosh(0.6, True),
    "whoosh_suave": lambda: sfx_whoosh(0.6) * 0.5, "whoosh_bajada": lambda: sfx_whoosh(0.8, True),
    "pop": sfx_pop, "pop3": lambda: np.concatenate([sfx_pop(500), sfx_pop(650), sfx_pop(800), np.zeros(SR // 10)]),
    "impacto": sfx_impacto, "blip": sfx_blip, "ding": sfx_ding, "squish": sfx_squish,
    "squish3": lambda: np.concatenate([sfx_squish(), sfx_squish(), sfx_squish()]),
    "boing": sfx_boing, "click": sfx_click, "tictac": sfx_tictac, "riser_corto": lambda: sfx_riser(0.6),
    "riser_suave": lambda: sfx_riser(1.2, True), "scratch": sfx_scratch, "bonk": sfx_bonk,
    "burbujas": sfx_burbujas, "goteo": sfx_goteo, "paso": sfx_paso, "esfuerzo": lambda: sfx_estirar() * 0.6,
    "estirar": sfx_estirar, "espacio": sfx_espacio, "chapoteo": sfx_chapoteo, "ola": sfx_ola,
    "buzz": sfx_buzz, "latido": sfx_latido, "alarma": sfx_alarma, "silbato": sfx_silbato,
}


# ------------------------------------------------------------------- música
def nota(f, d, tipo="piano"):
    t = t_(d)
    if tipo == "piano":  # piano eléctrico suave
        x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6) + 0.1 * np.sin(2 * np.pi * 3 * f * t)
        return x * env(len(t), 0.004, 0.7)
    if tipo == "bajo":
        x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
        return x * env(len(t), 0.005, 0.35)
    if tipo == "pizz":
        x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 20)
        return x * env(len(t), 0.002, 0.12)
    raise ValueError(tipo)


def hz(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def musica(dur, bpm=104, modo="alegre"):
    beat = 60 / bpm
    out = np.zeros(int((dur + 2) * SR))
    # progresión: Fmaj7 - Em7 - Dm7 - Cmaj7 (un compás cada una)
    acordes = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
    escala = [60, 62, 64, 67, 69, 72, 74, 76]
    if modo == "misterio":  # La menor - Fa - Re menor - Mi (tensión)
        acordes = [[45, 52, 57, 60], [41, 48, 53, 57], [38, 50, 53, 57], [40, 52, 56, 59]]
        escala = [57, 60, 62, 64, 65, 69, 72]
    comp = 4 * beat
    n_comp = int(dur / comp) + 2
    r = np.random.default_rng(3)
    for c in range(n_comp):
        t0 = c * comp
        ac = acordes[c % 4]
        for k, m in enumerate(ac):  # acorde rasgueado suave
            x = nota(hz(m), comp * 1.1) * 0.10
            a = int((t0 + k * 0.02) * SR)
            _sumar(out, a, x)
        for b in range(4):  # bajo
            if b in (0, 2, 3):
                x = nota(hz(ac[0] - 12 + (7 if b == 3 else 0)), beat * 0.9, "bajo") * 0.22
                a = int((t0 + b * beat) * SR)
                _sumar(out, a, x)
        for s in range(8):  # pizzicato juguetón
            if r.random() < 0.55:
                x = nota(hz(r.choice(escala)), beat * 0.6, "pizz") * 0.08
                a = int((t0 + s * beat / 2) * SR)
                _sumar(out, a, x)
        for b in range(4):  # batería
            tb = t0 + b * beat
            if b in (0, 2):
                tk = t_(0.35)
                k = np.sin(2 * np.pi * np.cumsum(45 + 110 * np.exp(-tk * 30)) / SR) * env(len(tk), 0.001, 0.12) * 0.35
                a = int(tb * SR)
                _sumar(out, a, k)
            else:
                sn = lp(ruido(0.2), 3) * env(int(0.2 * SR), 0.001, 0.06) * 0.12
                a = int(tb * SR)
                _sumar(out, a, sn)
            for h in range(2):
                hh = (ruido(0.05) - lp(ruido(0.05), 4)) * env(int(0.05 * SR), 0.001, 0.015) * 0.05
                a = int((tb + h * beat / 2 + (0.02 if h else 0)) * SR)
                _sumar(out, a, hh)
    out += lp(ruido(dur + 2), 2) * 0.004  # "vinilo"
    out = lp(out, 2)
    return out[: int(dur * SR)]


def mezclar(voz_ruta, sfx_ruta, salida, bpm=104, corte_musica=None, modo="alegre"):
    voz = leer_wav(voz_ruta)
    dur = len(voz) / SR + 0.6
    total = int(dur * SR)
    v = np.zeros(total)
    v[: len(voz)] = voz
    m = musica(dur, bpm, modo)
    # ducking: la música baja cuando hay voz
    envv = np.sqrt(lp(v ** 2, int(0.05 * SR)))
    duck = 1 / (1 + envv / 0.02 * 3)
    duck = lp(duck, int(0.15 * SR))
    gm = 10 ** (-14 / 20) * (0.35 + 0.65 * duck)  # ≈ -20 dB bajo la voz al hablar
    if corte_musica:  # silencio de música en el "giro"
        a, b = corte_musica
        mask = np.ones(total)
        ia, ib = int(a * SR), int(b * SR)
        mask[ia:ib] = 0.0
        mask = lp(mask, int(0.03 * SR))
        gm = gm * mask
    s = np.zeros(total)
    for t0, nombre in json.load(open(sfx_ruta)):
        if nombre not in SFX:
            print("SFX desconocido:", nombre)
            continue
        x = SFX[nombre]()
        a = int(t0 * SR)
        if a >= total:
            continue
        s[a:a + len(x)] += x[: total - a]
    mezcla = v * 1.0 + m * gm + s * 0.35
    guardar_wav(salida + ".tmp.wav", mezcla * 0.7)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", salida + ".tmp.wav", "-af",
                    "loudnorm=I=-14:TP=-1.0:LRA=11", "-ar", str(SR), salida], check=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("voz")
    ap.add_argument("sfx")
    ap.add_argument("salida")
    ap.add_argument("--bpm", type=float, default=104)
    ap.add_argument("--corte", type=float, nargs=2, default=None)
    ap.add_argument("--modo", default="alegre", choices=["alegre", "misterio"])
    a = ap.parse_args()
    mezclar(a.voz, a.sfx, a.salida, a.bpm, a.corte, a.modo)
