#!/usr/bin/env python3
"""Renderiza un video de escenas a MP4 (solo imagen) y lista de SFX.

Uso:
    python3 render.py video_d01a salida_sin_audio.mp4 [--desde 0 --hasta 5] [--fotograma 3.2 out.png]
"""
import argparse
import importlib
import json
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from motor import FPS, HUD, H, W, _comp, barrido, camara, pintar_hud, vineta  # noqa: E402

MOD = None


def _init(nombre):
    global MOD
    MOD = importlib.import_module(nombre)


def fotograma(t):
    esc = MOD.ESCENAS
    i = next((k for k, e in enumerate(esc) if e["ini"] <= t < e["fin"]), len(esc) - 1)
    e = esc[i]
    tl = t - e["ini"]
    HUD.clear()
    img, cam = e["f"](tl, e["fin"] - e["ini"])
    img = camara(img, **cam)
    pintar_hud(img)
    TR = 0.2
    if e["tr"] == "barrido" and tl < TR and i > 0:
        p = esc[i - 1]
        prev, camp = p["f"](p["fin"] - p["ini"] - 0.001, p["fin"] - p["ini"])
        prev = camara(prev, **camp)
        pintar_hud(prev)
        u = tl / TR
        from PIL import Image
        lienzo = Image.new("RGBA", (W, H))
        _comp(lienzo, prev, int(-u * W), 0)
        _comp(lienzo, img, int((1 - u) * W), 0)
        img = barrido(lienzo, 1 - abs(u - 0.5) * 2 + 0.3)
    elif e["tr"] == "barrido" and tl < TR + 0.1:
        img = barrido(img, (TR + 0.1 - tl) * 3)
    img = vineta(img, 0.4)
    return img.convert("RGB")


def _pegar_x(lienzo, img, x):
    if x < W:
        lienzo.alpha_composite(img.crop((0, 0, W - x, H)), (x, 0))


def _frame_bytes(n):
    return fotograma(n / FPS).tobytes()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modulo")
    ap.add_argument("salida")
    ap.add_argument("--desde", type=float, default=0)
    ap.add_argument("--hasta", type=float, default=None)
    ap.add_argument("--fotograma", type=float, default=None)
    ap.add_argument("--procesos", type=int, default=4)
    a = ap.parse_args()
    _init(a.modulo)
    if a.fotograma is not None:
        fotograma(a.fotograma).save(a.salida)
        return
    fin = a.hasta if a.hasta is not None else MOD.DURACION
    frames = range(int(a.desde * FPS), int(fin * FPS))
    # lista de efectos de sonido (tiempos absolutos)
    sfx = []
    for e in MOD.ESCENAS:
        for s in e["sfx"]:
            nombre, off = (s, 0.0) if isinstance(s, str) else s
            sfx.append([round(e["ini"] + off, 3), nombre])
    Path(a.salida).with_suffix(".sfx.json").write_text(json.dumps(sfx, ensure_ascii=False))
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                           "-pix_fmt", "yuv420p", a.salida], stdin=subprocess.PIPE)
    with Pool(a.procesos, initializer=_init, initargs=(a.modulo,)) as pool:
        for k, b in enumerate(pool.imap(_frame_bytes, frames, chunksize=4)):
            ff.stdin.write(b)
            if k % 150 == 0:
                print(f"  fotograma {k}/{len(frames)}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("listo:", a.salida)


if __name__ == "__main__":
    main()
