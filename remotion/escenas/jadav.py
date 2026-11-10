#!/usr/bin/env python3
"""Clips animados para el guion 'jadav' (el hombre que plantó un bosque).

Uso (después de `python3 preparar.py jadav`):
  python3 escenas/jadav.py
"""
import json, math, os, random
from PIL import Image, ImageDraw, ImageFilter
import dibujo as D

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "jadav")
W, H = D.W, D.H
RIO_Y, ARENA_Y = 1000, 1170


def fondo_rio(arena=True):
    img = D.cielo(RIO_Y)
    d = ImageDraw.Draw(img)
    # orilla lejana con selva baja
    rnd = random.Random(4)
    x = -50
    while x < W + 50:
        r = rnd.uniform(40, 80)
        d.ellipse((x - r, RIO_Y - r * 0.9, x + r, RIO_Y + r * 0.6), fill=(44, 66, 72))
        x += r * 1.1
    agua = D.textura(W, ARENA_Y - RIO_Y, (150, 110, 150), (90, 80, 140), seed=5, vertical=False, fuerza=0.3)
    img.alpha_composite(agua, (0, RIO_Y))
    d = ImageDraw.Draw(img)
    for _ in range(25):
        y = rnd.uniform(RIO_Y + 10, ARENA_Y - 10); x = rnd.uniform(0, W); l = rnd.uniform(40, 140)
        d.line((x, y, x + l, y), fill=(255, 200, 160, 120), width=3)
    suelo = (D.textura(W, H - ARENA_Y, (226, 196, 150), (186, 150, 106), seed=6, vertical=False, fuerza=0.35) if arena
             else D.textura(W, H - ARENA_Y, (110, 140, 70), (60, 92, 48), seed=7, vertical=True, fuerza=0.5))
    img.alpha_composite(suelo, (0, ARENA_Y))
    # línea de luz en la orilla
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).rectangle((0, ARENA_Y - 3, W, ARENA_Y + 3), fill=(255, 230, 170, 255))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(8)))
    return img


def bosque(densidad=1.0, suelo_verde=True, seed=1):
    img = fondo_rio(arena=not suelo_verde)
    rnd = random.Random(seed)
    arboles = []
    filas = [(ARENA_Y + 10, 0.42, 16), (ARENA_Y + 80, 0.55, 12), (ARENA_Y + 170, 0.7, 9)]
    for y, sc, n in filas:
        for _ in range(int(n * densidad)):
            arboles.append((rnd.uniform(-60, W + 60), y + rnd.uniform(-15, 15), sc * rnd.uniform(0.85, 1.15), rnd.random() < 0.3, rnd.randint(0, 5)))
    for x, y, sc, bambu, sd in sorted(arboles, key=lambda a: a[1]):
        D.pegar(img, D.arbol(1 if bambu else 0, sd), x, y, sc)
    return img


def hojas(fr, t, n=14, seed=2, col=(120, 170, 70, 220)):
    d = ImageDraw.Draw(fr); rnd = random.Random(seed)
    for _ in range(n):
        x0, y0, v, ph = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(40, 90), rnd.uniform(0, 6)
        y = (y0 + v * t) % H; x = (x0 + 40 * math.sin(t + ph)) % W
        d.ellipse((x - 12, y - 6, x + 12, y + 6), fill=col)


def serpientes(fr):
    d = ImageDraw.Draw(fr)
    for (x0, y0, k) in ((260, 1640, 0), (760, 1700, 1), (560, 1820, 2)):
        pts = [(x0 + i * 14, y0 + 16 * math.sin(i * 0.7 + k)) for i in range(14)]
        d.line(pts, fill=(60, 55, 40), width=14, joint="curve")
        d.ellipse((pts[-1][0] - 10, pts[-1][1] - 9, pts[-1][0] + 12, pts[-1][1] + 9), fill=(60, 55, 40))


def arena_volando(fr, t):
    d = ImageDraw.Draw(fr); rnd = random.Random(8)
    for _ in range(40):
        x0, y0, v = rnd.uniform(0, W), rnd.uniform(1150, 1900), rnd.uniform(200, 420)
        x = (x0 + v * t) % W
        d.line((x, y0, x + 18, y0 - 2), fill=(255, 235, 200, 140), width=3)


def sol_fuerte(fr, t):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    cx, cy = 760, 420
    for k in range(12):
        a = k * math.pi / 6 + t * 0.2
        d.polygon([(cx, cy), (cx + 900 * math.cos(a - 0.05), cy + 900 * math.sin(a - 0.05)),
                   (cx + 900 * math.cos(a + 0.05), cy + 900 * math.sin(a + 0.05))], fill=(255, 230, 150, 40))
    d.ellipse((cx - 150, cy - 150, cx + 150, cy + 150), fill=(255, 220, 120, 120))
    fr.alpha_composite(g.filter(ImageFilter.GaussianBlur(20)))
    ImageDraw.Draw(fr).ellipse((cx - 85, cy - 85, cx + 85, cy + 85), fill=(255, 238, 170))


def pajaros(fr, t):
    d = ImageDraw.Draw(fr)
    for i in range(6):
        x = (100 + i * 130 + 90 * t) % (W + 200) - 100; y = 520 + 40 * math.sin(i * 1.7) + 8 * math.sin(t * 3 + i)
        a = 14 * math.sin(t * 9 + i)
        d.line((x - 22, y - a, x, y, x + 22, y - a), fill=(30, 25, 35), width=5)


# ------------------------------------------------------------------ escenas
def e1(clip):
    base = fondo_rio(); serpientes(base)
    for t, pr in clip.frames():
        fr = base.copy()
        D.sombra(fr, W / 2, 1745, 150)
        D.pegar(fr, D.persona("de_pie", t, triste=True), W / 2, 1760, 0.95)
        arena_volando(fr, t)
        clip.escribir(fr)


def e2(clip):
    base = fondo_rio()
    for t, pr in clip.frames():
        fr = base.copy(); sol_fuerte(fr, t); arena_volando(fr, t)
        clip.escribir(fr)


def e3(clip):
    base = fondo_rio()
    for t, pr in clip.frames():
        fr = base.copy()
        D.sombra(fr, 430, 1745, 170)
        D.pegar(fr, D.persona("arrodillado", t), 430, 1760, 0.9)
        g = D.eob((pr - 0.25) / 0.4)
        ImageDraw.Draw(fr).ellipse((620, 1700, 820, 1760), fill=(140, 100, 60))
        if g > 0.02: D.pegar(fr, D.brote(), 720, 1735, 1.2 * g)
        clip.escribir(fr)


def e4(clip):
    base = fondo_rio()
    rnd = random.Random(3)
    pos = []
    for y, sc in ((ARENA_Y + 20, 0.38), (ARENA_Y + 110, 0.5), (ARENA_Y + 220, 0.62)):
        for k in range(7):
            pos.append((60 + k * 160 + rnd.uniform(-40, 40), y, sc, rnd.random() < 0.3, rnd.randint(0, 5), rnd.uniform(0, 0.35)))
    pos.sort(key=lambda a: a[1])
    for t, pr in clip.frames():
        fr = base.copy()
        for x, y, sc, bambu, sd, dl in pos:
            g = D.eio((pr - dl) / 0.6)
            if g > 0.03: D.pegar(fr, D.arbol(1 if bambu else 0, sd), x, y, sc * g)
        px = -150 + (W + 300) * pr
        D.sombra(fr, px, 1830, 150)
        D.pegar(fr, D.persona("cubos", t), px, 1850, 0.62)
        clip.escribir(fr)


def e5(clip):
    base = bosque(1.3, suelo_verde=True, seed=5)
    for t, pr in clip.frames():
        fr = base.copy(); pajaros(fr, t); clip.escribir(fr)


def e6(clip):
    base = bosque(0.8, suelo_verde=True, seed=6)
    for t, pr in clip.frames():
        fr = base.copy()
        ex = -300 + 700 * pr
        D.sombra(fr, ex + 50, 1560, 280)
        D.pegar(fr, D.elefante(t), ex, 1580, 0.75)
        D.sombra(fr, 230, 1880, 130)
        D.pegar(fr, D.ciervo(t), 200, 1890, 0.55)
        D.sombra(fr, 760, 1890, 260)
        D.pegar(fr, D.tigre(t, anda=False), 720, 1900, 0.62)
        hojas(fr, t)
        clip.escribir(fr)


def e7(clip):
    base = bosque(0.9, suelo_verde=True, seed=7)
    D.luz_calida(base, 90)
    for t, pr in clip.frames():
        fr = base.copy()
        D.sombra(fr, W / 2, 1855, 170)
        D.pegar(fr, D.persona("saluda", t, viejo=True, sonrisa=True), W / 2, 1870, 0.95)
        hojas(fr, t, 18)
        clip.escribir(fr)


def main():
    ruta = os.path.join(BASE, "datos.json")
    datos = json.load(open(ruta, encoding="utf-8"))
    fns = [e1, e2, e3, e4, e5, e6, e7]
    for i, (esc, fn) in enumerate(zip(datos["escenas"], fns)):
        dur = esc["fin"] - esc["ini"]
        out = os.path.join(BASE, f"escena{i + 1}.mp4")
        c = D.Clip(out, dur); fn(c); c.cerrar()
        esc["imagen"] = f"jadav/escena{i + 1}.mp4"
        print(f"  escena {i + 1}: {dur:.1f}s ✔")
    json.dump(datos, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
