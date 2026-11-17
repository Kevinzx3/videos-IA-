#!/usr/bin/env python3
"""Alinea los segmentos del guion JSON con la locución real.

Detecta pausas con ffmpeg (silencedetect) y elige, por programación dinámica,
qué pausas son fronteras entre segmentos, de modo que la duración de cada
segmento sea proporcional a su número de caracteres (velocidad de habla constante).
Las pausas largas se prefieren como fronteras. Sobrescribe los tiempos del JSON.

Uso: python3 herramientas/alinear_voz.py guion.json voz.wav
"""
import json, re, subprocess, sys

def silencios(wav):
    out = subprocess.run(["ffmpeg", "-i", wav, "-af", "silencedetect=noise=-35dB:d=0.1", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav],
                               capture_output=True, text=True).stdout)
    return [(a, b) for a, b in zip(ini, fin)], dur

def alinear(ruta, wav):
    d = json.load(open(ruta, encoding="utf-8"))
    segs = d["segmentos"]
    sil, T = silencios(wav)
    cand = [((a + b) / 2, b - a) for a, b in sil if 0.3 < (a + b) / 2 < T - 0.3]
    L = [len(s[2]) + 4 for s in segs]
    n, m = len(segs), len(cand)
    rate = T / sum(L)
    INF = float("inf")
    # f[i][j]: coste con la frontera i (fin del segmento i) en el candidato j
    f = [[INF] * m for _ in range(n - 1)]
    p = [[-1] * m for _ in range(n - 1)]
    def coste(dur, i, pausa):
        e = (dur - L[i] * rate) / (L[i] * rate)
        return e * e - 0.6 * min(pausa, 0.6)
    for j, (t, pz) in enumerate(cand):
        f[0][j] = coste(t, 0, pz)
    for i in range(1, n - 1):
        for j, (t, pz) in enumerate(cand):
            for k in range(j):
                if f[i - 1][k] == INF:
                    continue
                c = f[i - 1][k] + coste(t - cand[k][0], i, pz)
                if c < f[i][j]:
                    f[i][j], p[i][j] = c, k
    best, bj = INF, -1
    for j, (t, _) in enumerate(cand):
        if f[n - 2][j] < INF:
            c = f[n - 2][j] + coste(T - t, n - 1, 0.6)
            if c < best:
                best, bj = c, j
    fr = []
    j = bj
    for i in range(n - 2, -1, -1):
        fr.append(cand[j][0]); j = p[i][j]
    fr = [0.0] + fr[::-1] + [T]
    for i, s in enumerate(segs):
        s[0], s[1] = round(fr[i], 2), round(fr[i + 1], 2)
        print(f"{s[0]:6.2f}-{s[1]:6.2f} ({s[1]-s[0]:4.2f}s) {s[2]}")
    d.pop("mapa_original", None)
    json.dump(d, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    alinear(sys.argv[1], sys.argv[2])
