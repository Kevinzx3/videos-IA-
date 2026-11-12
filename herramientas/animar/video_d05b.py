"""Día 05 · Video B (misterio resuelto): El Bloop, el sonido gigante bajo el océano."""
import math
import random

from PIL import Image, ImageDraw

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-05/datos/02-misterio-bloop.json"


def abismo(t, sup=380):
    c = degradado(W, H, [(0, "#2A6F9B"), (sup / H, "#1F5E86"), (0.5, "#0B2A44"), (1, "#030A14")])
    img, d = capa()
    d.line([(x, sup + math.sin(x / 70 + t * 3) * 12) for x in range(0, W + 20, 20)], fill=(230, 245, 255, 255), width=10)
    c.alpha_composite(img)
    particulas(c, t, 45, (160, 220, 255), 6, (2, 5), 18, 140)
    return c


def hidrofono(c, x, y, esc=1.0):
    m = Image.new("L", (160, 260), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([30, 40, 130, 230], radius=40, fill=255)
    d.ellipse([20, 0, 140, 90], fill=255)
    spr = sprite(m, "#E8B04B", 700)
    pegar(c, spr, x, y, esc, sombra=True)
    img, dd = capa()
    dd.line([(x, y + 120 * esc), (x - 200, H)], fill=(40, 40, 50, 255), width=int(10 * esc))
    c.alpha_composite(img)


def sombra_monstruo(c, x, y, esc, t, alfa=0.85):
    m = Image.new("L", (900, 700), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([250, 120, 650, 520], fill=255)
    for k in range(7):
        a = math.pi * (0.1 + 0.8 * k / 6)
        pts = []
        for j in range(14):
            r = 180 + j * 26
            aa = a + math.sin(t * 2 + k + j * 0.4) * 0.15
            pts.append((450 + math.cos(aa) * r, 320 + math.sin(aa) * r))
        d.line(pts, fill=255, width=44 - k % 3 * 6, joint="curve")
    for s in (-1, 1):
        d.ellipse([450 + s * 90 - 30, 260, 450 + s * 90 + 30, 300], fill=0)
    spr = Image.new("RGBA", m.size, (5, 15, 25, 0))
    spr.putalpha(m.point(lambda v: int(v * alfa)))
    pegar(c, spr, x, y, esc)
    for s in (-1, 1):
        pegar(c, brillo(30 * esc, "#FFE45C", 0.9), x + (s * 90) * esc, y + (280 - 350) * esc)


def ballena(c, x, y, esc):
    m = Image.new("L", (700, 260), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([0, 40, 560, 230], fill=255)
    d.polygon([(520, 130), (700, 40), (650, 135), (700, 230)], fill=255)
    pegar(c, sprite(m, "#4A6FA5", 710), x, y, esc)


def bloque_hielo(c, x, y, esc, rot=0):
    m = Image.new("L", (520, 420), 0)
    ImageDraw.Draw(m).polygon([(40, 400), (0, 150), (120, 20), (380, 0), (520, 160), (470, 410)], fill=255)
    spr = sprite(m, "#DFF4FF", 720)
    dd = ImageDraw.Draw(spr)
    for k in range(5):
        dd.line([(80 + k * 80, 60 + k * 15), (60 + k * 85, 380)], fill=(170, 210, 235, 255), width=6)
    pegar(c, spr, x, y, esc, rot=rot, sombra=True)


def e_gancho(t, d):
    c = abismo(t)
    ondas(c, 540, 1300, t * 1.5, (180, 230, 255), 5, 1100, 14, (0, 360))
    texto(c, "1997", 540, 1650, t - 0.1, 150, "#9FE8FF")
    return c, dict(zoom=1.0 + 0.12 * ease_out(t / d), temblor=8 if t < 0.3 else 0, t=t)


def e_bloop(t, d):
    c = abismo(t)
    img, dd = capa()
    pts = [(x, 1000 + math.sin(x / 18 - t * 10) * 140 * math.exp(-((x - 540) / 300) ** 2)) for x in range(80, 1000, 6)]
    dd.line(pts, fill=(120, 255, 200, 255), width=10)
    c.alpha_composite(img)
    texto(c, "«BLOOP»", 540, 1450, t - 0.15, 170, "#FFFFFF")
    return c, dict(zoom=1.0, temblor=6 if 0.15 < t < 0.4 else 0, t=t)


def e_hidrofonos(t, d):
    c = abismo(t)
    hidrofono(c, 540, 1300, 1.3)
    ondas(c, 540, 1300, t, (180, 230, 255), 3, 600, 8, (180, 360))
    texto(c, "HIDRÓFONOS", 540, 800, t - 0.2, 120, "#FFD400")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_distancia(t, d):
    c = degradado(W, H, [(0, "#0F3A5A"), (1, "#0A2540")])
    pts = [(220, 900), (840, 980), (520, 1500)]
    origen = (300, 1550)
    ondas(c, origen[0], origen[1], t * 1.3, (180, 230, 255), 5, 1200, 10, (0, 360))
    for x, y in pts:
        pegar(c, brillo(30, "#FFD400", 1), x, y)
    img, dd = capa()
    dd.line([pts[0], pts[1]], fill=(255, 212, 0, 200), width=6)
    c.alpha_composite(img)
    tag(c, "+3000", "km", 540, 760, t - 0.3, 130)
    return c, dict(zoom=1.0, t=t)


def e_minuto(t, d):
    c = abismo(t)
    img, dd = capa()
    u = clamp01(t / d)
    pts = [(100 + k * 9, 1350 - (k * 9 / 900) ** 1.6 * 500) for k in range(int(100 * u))]
    if len(pts) > 1:
        dd.line(pts, fill=(120, 255, 200, 255), width=14)
    dd.line([(100, 1380), (1000, 1380)], fill=(255, 255, 255, 120), width=4)
    c.alpha_composite(img)
    tag(c, "≈1", "min", 540, 1580, t - 0.3, 130)
    texto(c, "GRAVE Y SUBIENDO", 540, 760, t - 0.1, 90, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_monstruo(t, d):
    c = abismo(t)
    sombra_monstruo(c, 540, 1250, 1.0 + 0.04 * t, t)
    texto(c, "¿UN MONSTRUO?", 540, 1750, t - 0.3, 110, "#FF4D6D")
    return c, dict(zoom=1.0 + 0.06 * t, t=t)


def e_ballena(t, d):
    c = abismo(t)
    sombra_monstruo(c, 600, 1150, 1.4, t, 0.7)
    ballena(c, 300, 1600, 0.55)
    texto(c, "MÁS GRANDE QUE\nUNA BALLENA AZUL", 540, 760, t - 0.2, 85, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_giro(t, d):
    c = abismo(0.0)
    sombra_monstruo(c, 540, 1250, 1.0, 0.0)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def antartida(t):
    c = degradado(W, H, [(0, "#9FC8E8"), (0.5, "#DDEEFF"), (0.51, "#2A6F9B"), (1, "#0B2A44")])
    m = Image.new("L", (W, 600), 0)
    ImageDraw.Draw(m).polygon([(0, 600), (0, 120), (300, 60), (650, 140), (W, 80), (W, 600)], fill=255)
    pegar(c, sprite(m, "#EEF8FF", 730, costura=False), 540, 1050)
    particulas(c, t, 50, (255, 255, 255), 14, (2, 4), -30, 200)
    return c


def e_iceberg(t, d):
    c = antartida(t)
    u = ease_in(clamp01((t - 0.4) / 0.8)) if False else clamp01((t - 0.4) / 0.8) ** 2
    bloque_hielo(c, 820 + u * 80, 900 + u * 260, 0.8, rot=-u * 20)
    texto(c, "ICEBERG", 540, 1650, t - 0.2, 130, "#FFFFFF")
    return c, dict(zoom=1.0, temblor=8 if 0.5 < t < 0.8 else 0, t=t)


def e_terremoto(t, d):
    c = antartida(t)
    img, dd = capa()
    rng = random.Random(3)
    for k in range(6):
        x = 200 + k * 130
        pts = [(x + rng.uniform(-20, 20), 760 + j * 60) for j in range(6)]
        dd.line(pts[: 1 + int(5 * clamp01(t / 0.6))], fill=(60, 120, 170, 255), width=8)
    c.alpha_composite(img)
    ondas(c, 540, 1300, t, (220, 240, 255), 4, 700, 10, (0, 360))
    texto(c, "TERREMOTO\nDE HIELO", 540, 1650, t - 0.2, 110, "#9FE8FF")
    return c, dict(zoom=1.0, temblor=10 if t < 0.6 else 0, t=t)


def e_era_hielo(t, d):
    c = abismo(t)
    u = ease_in_out(clamp01((t - 0.2) / 0.6))
    sombra_monstruo(c, 540, 1150, 1.0, t, 0.85 * (1 - u))
    if u > 0:
        bloque_hielo(c, 540, 1150, 0.4 + 0.6 * u)
    texto(c, "ERA HIELO", 540, 1680, t - 0.7, 140, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_cta(t, d):
    c = abismo(t)
    bloque_hielo(c, 800, 1500, 0.4)
    pegar(c, nico(t, "feliz", 10, 140 + 25 * math.sin(t * 10), traje="#2D3E5C", casco=True), 330, 1880, 0.9, ancla="abajo")
    globo_texto(c, "¿QUÉ SONIDO\nINVESTIGO AHORA?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto", "riser_suave"]),
    (1, 0.0, e_bloop, None, ["latido", ("impacto", 0.15)]),
    (2, 0.0, e_hidrofonos, "barrido", ["whoosh_grave", "burbujas"]),
    (3, 0.0, e_distancia, None, ["whoosh", ("pop", 0.3)]),
    (4, 0.0, e_minuto, None, ["riser_corto", ("pop", 0.3)]),
    (5, 0.0, e_monstruo, "barrido", ["whoosh_grave", "latido"]),
    (6, 0.0, e_ballena, None, [("pop", 0.2)]),
    (7, 0.0, e_giro, None, ["scratch"]),
    (8, 0.0, e_iceberg, None, ["whoosh", ("impacto", 0.5)]),
    (9, 0.0, e_terremoto, None, ["squish3", "ola"]),
    (10, 0.0, e_era_hielo, None, [("ding", 0.7)]),
    (11, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]
ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
