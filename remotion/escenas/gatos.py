#!/usr/bin/env python3
"""Clips animados para el guion 'gatos' (por qué los gatos caen de pie).

Uso (después de `python3 preparar.py gatos`):
  python3 escenas/gatos.py
"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import dibujo as D

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "gatos")
W, H = D.W, D.H
PISO = 1500


def habitacion(ventana_cerrada=True):
    img = D.textura(W, H, (74, 50, 92), (120, 76, 104), seed=21, vertical=True, fuerza=0.12)
    # ventana con el cielo del atardecer
    cielo = D.cielo(560).crop((0, 0, 460, 560))
    img.alpha_composite(cielo, (520, 360))
    d = ImageDraw.Draw(img)
    for r in ((500, 340, 1000, 940),):
        d.rectangle(r, outline=(236, 220, 200), width=22)
    d.line((750, 350, 750, 930), fill=(236, 220, 200), width=14)
    d.line((510, 640, 990, 640), fill=(236, 220, 200), width=14)
    d.rectangle((480, 930, 1020, 965), fill=(230, 214, 196))
    # suelo de madera
    piso = D.textura(W, H - PISO, (150, 96, 60), (110, 68, 42), seed=22, vertical=False, fuerza=0.35)
    img.alpha_composite(piso, (0, PISO))
    d = ImageDraw.Draw(img)
    for y in range(PISO + 80, H, 110):
        d.line((0, y, W, y), fill=(90, 56, 36), width=3)
    # sofá
    d.rounded_rectangle((-80, 1080, 420, 1560), radius=70, fill=(60, 110, 120))
    d.rounded_rectangle((-80, 1260, 460, 1580), radius=60, fill=(70, 126, 136))
    d.rounded_rectangle((-80, 1230, 400, 1320), radius=40, fill=(84, 142, 150))
    # lámpara
    d.line((960, 1500, 960, 1120), fill=(40, 34, 40), width=10)
    d.polygon([(880, 1130), (1040, 1130), (1010, 1030), (910, 1030)], fill=(250, 214, 150))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((700, 880, 1220, 1360), fill=(255, 210, 140, 70))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)))
    return img


def flecha_curva(d, cx, cy, r, a0, a1, col=(255, 226, 140)):
    pts = [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(a0, a1, 20)]
    d.line(pts, fill=col, width=10, joint="curve")
    ax, ay = pts[-1]; bx, by = pts[-2]; ang = math.atan2(ay - by, ax - bx)
    d.polygon([(ax + 26 * math.cos(ang), ay + 26 * math.sin(ang)),
               (ax + 22 * math.cos(ang + 2.3), ay + 22 * math.sin(ang + 2.3)),
               (ax + 22 * math.cos(ang - 2.3), ay + 22 * math.sin(ang - 2.3))], fill=col)


def e1(clip):
    base = habitacion()
    for t, pr in clip.frames():
        fr = base.copy()
        rot = math.pi * (1 - D.eio((pr - 0.15) / 0.6))
        y = 650 + 750 * D.eio(pr / 0.85)
        pose = "paracaidas" if pr > 0.65 else "cayendo"
        sp = D.gato(t, pose, rot=rot)
        D.sombra(fr, W / 2, PISO + 60, 120 + 120 * pr, a=int(60 + 60 * pr))
        D.pegar(fr, sp, W / 2, y + 300, 0.75)
        clip.escribir(fr)


def e2(clip):
    base = habitacion()
    for t, pr in clip.frames():
        fr = base.copy()
        salto = abs(math.sin(t * 3.2)) * 90
        D.pegar(fr, D.gato(t, "sentado"), 220, 1290 - salto, 0.45)
        clip.escribir(fr)


def e3(clip):
    base = habitacion()
    etapas = [(math.pi, 230), (math.pi / 2, 540), (0.0, 850)]
    for t, pr in clip.frames():
        fr = base.copy(); d = ImageDraw.Draw(fr)
        for k, (rot, x) in enumerate(etapas):
            ap = D.eob((pr - k * 0.25) / 0.2)
            if ap <= 0.02: continue
            D.pegar(fr, D.gato(t, "cayendo", rot=rot), x, 1300, 0.42 * ap)
            if k < 2 and ap > 0.9:
                flecha_curva(d, x + 155, 1150, 60, -2.6, -0.5)
        clip.escribir(fr)


def e4(clip):
    """Rayos X: silueta del gato y columna que se dobla."""
    silueta = D.gato(0, "cayendo")
    a = np.asarray(silueta.split()[3].filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5)), float)
    borde = Image.fromarray(np.dstack([np.full_like(a, 120), np.full_like(a, 230), np.full_like(a, 255), a]).astype(np.uint8), "RGBA")
    brillo = borde.filter(ImageFilter.GaussianBlur(10))
    for t, pr in clip.frames():
        fr = Image.new("RGBA", (W, H), (14, 22, 48, 255))
        d = ImageDraw.Draw(fr)
        for x in range(0, W, 60): d.line((x, 0, x, H), fill=(30, 46, 84), width=1)
        for y in range(0, H, 60): d.line((0, y, W, y), fill=(30, 46, 84), width=1)
        ox, oy = 140, 760
        fr.alpha_composite(brillo, (ox, oy)); fr.alpha_composite(borde, (ox, oy))
        # columna: vértebras sobre una curva que se dobla
        curva = 70 * math.sin(t * 2.4)
        for i in range(16):
            u = i / 15
            x = ox + 250 + u * 380; y = oy + 420 - curva * math.sin(math.pi * u)
            r = 16 - 4 * abs(u - 0.5)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 245, 220), outline=(255, 210, 120), width=3)
        clip.escribir(fr)


def e5(clip):
    base = habitacion()
    for t, pr in clip.frames():
        fr = base.copy()
        y = 500 + 950 * D.eio(min(1, pr / 0.7))
        aterriza = pr > 0.7
        sp = D.gato(t, "paracaidas" if not aterriza else "sentado")
        D.sombra(fr, W / 2, PISO + 60, 100 + 160 * pr, a=int(50 + 70 * pr))
        D.pegar(fr, sp, W / 2, y + (300 if not aterriza else 160), 0.7 if not aterriza else 0.55)
        clip.escribir(fr)


def e6(clip):
    base = habitacion()
    for t, pr in clip.frames():
        fr = base.copy()
        D.pegar(fr, D.gato(t, "sentado"), 750, 960, 0.5)
        clip.escribir(fr)


def main():
    ruta = os.path.join(BASE, "datos.json")
    datos = json.load(open(ruta, encoding="utf-8"))
    for i, (esc, fn) in enumerate(zip(datos["escenas"], [e1, e2, e3, e4, e5, e6])):
        dur = esc["fin"] - esc["ini"]
        c = D.Clip(os.path.join(BASE, f"escena{i + 1}.mp4"), dur); fn(c); c.cerrar()
        esc["imagen"] = f"gatos/escena{i + 1}.mp4"
        print(f"  escena {i + 1}: {dur:.1f}s ✔")
    json.dump(datos, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
