#!/usr/bin/env python3
"""Acelera la voz (atempo) hasta una duración objetivo y escala los tiempos del JSON.

Uso: python3 herramientas/acelerar_voz.py guion.json voz.wav --objetivo 58.5
"""
import argparse, json, shutil, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("guion"); ap.add_argument("wav"); ap.add_argument("--objetivo", type=float, default=58.5)
a = ap.parse_args()
d = json.load(open(a.guion, encoding="utf-8"))
dur = d["segmentos"][-1][1]
f = max(1.0, dur / a.objetivo)
if f > 1.0:
    tmp = a.wav + ".orig.wav"
    shutil.copy(a.wav, tmp)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"atempo={f:.4f}", a.wav], check=True)
    for s in d["segmentos"]:
        s[0], s[1] = round(s[0] / f, 2), round(s[1] / f, 2)
    for p in d.get("palabras", []):
        p[0], p[1] = round(p[0] / f, 3), round(p[1] / f, 3)
    d.setdefault("voz", {})["aceleracion"] = round(f, 4)
    json.dump(d, open(a.guion, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"✔ {a.guion}: ×{f:.3f} → {d['segmentos'][-1][1]:.1f} s")
