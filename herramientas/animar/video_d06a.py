"""Día 06 · Video A (mito): ¿Tienes 10 veces más bacterias que células?"""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-06/datos/01-mito-mas-bacterias-que-celulas.json"


def fondo(t, c1="#14112B", c2="#2E2458"):
    c = degradado(W, H, [(0, c1), (1, c2)])
    particulas(c, t, 35, (200, 220, 255), 9, (2, 5), 15, 120)
    return c


@lru_cache(maxsize=8)
def bacteria(color="#7BD88F", seed=800, cara=True):
    m = Image.new("L", (260, 130), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([10, 15, 250, 115], radius=50, fill=255)
    for k in range(6):
        d.line([(30 + k * 40, 115), (25 + k * 40, 128)], fill=255, width=5)
    spr = sprite(m, color, seed)
    if cara:
        dd = ImageDraw.Draw(spr)
        for s in (-1, 1):
            dd.ellipse([130 + s * 30 - 11, 45, 130 + s * 30 + 11, 67], fill=(30, 20, 30, 255))
        dd.arc([110, 62, 150, 88], 20, 160, fill=(30, 20, 30, 255), width=5)
    return spr


@lru_cache(maxsize=4)
def celula(color="#F29BB0", seed=810):
    m = Image.new("L", (260, 260), 0)
    ImageDraw.Draw(m).ellipse([5, 5, 255, 255], fill=255)
    spr = sprite(m, color, seed)
    ImageDraw.Draw(spr).ellipse([95, 95, 165, 165], fill=(150, 70, 140, 255))
    return spr


@lru_cache(maxsize=2)
def globulo():
    m = Image.new("L", (200, 200), 0)
    ImageDraw.Draw(m).ellipse([5, 5, 195, 195], fill=255)
    spr = sprite(m, "#D83A4A", 820)
    ImageDraw.Draw(spr).ellipse([55, 55, 145, 145], fill=(170, 30, 45, 255))
    return spr


def enjambre(c, t, n, x0, y0, w, h, seed=1, esc=0.5):
    rng = random.Random(seed)
    cols = ["#7BD88F", "#7FB8FF", "#FFC56B", "#C49BFF"]
    for k in range(n):
        x = x0 + rng.uniform(0, w) + math.sin(t * 2 + k) * 15
        y = y0 + rng.uniform(0, h) + math.cos(t * 1.7 + k) * 15
        pegar(c, bacteria(cols[k % 4], 800 + k % 4), x, y, esc, rot=rng.uniform(-40, 40))


def e_gancho(t, d):
    c = fondo(t)
    enjambre(c, t, 22, 60, 650, 960, 700, 1, 0.45)
    pegar(c, nico(t, "sorpresa", 30, 30), 540, 1900, 0.9, ancla="abajo")
    tag(c, "×10", "BACTERIAS", 540, 820, t - 0.2, 140)
    return c, dict(zoom=1.0 + 0.1 * ease_out(t / d), temblor=5 if t < 0.25 else 0, t=t)


def e_falso(t, d):
    c = fondo(t)
    enjambre(c, t, 22, 60, 650, 960, 700, 1, 0.45)
    sello(c, "FALSO", t - 0.1, "#FF4D6D", 1100, 200)
    return c, dict(zoom=1.05, temblor=10 if 0.1 < t < 0.35 else 0, t=t)


def e_1972(t, d):
    c = fondo(t, "#2A1C10", "#5A3A20")
    m = Image.new("L", (520, 680), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 520, 680], radius=16, fill=255)
    hoja = sprite(m, "#EFE3C2", 830)
    dd = ImageDraw.Draw(hoja)
    for k in range(10):
        dd.line([(60, 200 + k * 42), (460 - (k % 3) * 60, 200 + k * 42)], fill=(120, 100, 80, 255), width=6)
    r = rotulo("10 : 1", 110, "#B03A2E", "#EFE3C2", 4)
    hoja.alpha_composite(r, (260 - r.width // 2, 110 - r.height // 2))
    pegar(c, hoja, 540, 1050, pop_scale(t - 0.05) * 1.0, rot=-5, sombra=True)
    tag(c, "1972", "", 540, 1560, t - 0.4, 140)
    return c, dict(zoom=1.0 + 0.05 * t, t=t)


def microscopio(c, x, y, esc):
    m = Image.new("L", (360, 560), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([20, 480, 340, 550], radius=20, fill=255)
    d.rounded_rectangle([230, 120, 290, 500], radius=26, fill=255)
    d.polygon([(110, 40), (190, 0), (270, 260), (190, 300)], fill=255)
    d.rectangle([60, 360, 260, 390], fill=255)
    pegar(c, sprite(m, "#E8ECF2", 840), x, y, esc, sombra=True)


def e_2016(t, d):
    c = fondo(t, "#0F2A3A", "#1F4A5A")
    microscopio(c, 720, 1350, 1.0)
    pegar(c, nico(t, "aja", 10, 165), 330, 1880, 0.9, ancla="abajo")
    tag(c, "2016", "WEIZMANN", 540, 800, t - 0.2, 120)
    return c, dict(zoom=1.0, t=t)


def e_celulas(t, d):
    c = fondo(t, "#2A1430", "#5A2A58")
    rng = random.Random(2)
    for k in range(14):
        pegar(c, celula(), 120 + (k % 4) * 280 + rng.uniform(-30, 30), 650 + (k // 4) * 260, 0.7 + 0.03 * math.sin(t * 3 + k))
    tag(c, "≈30", "BILLONES DE CÉLULAS", 540, 1700, t - 0.2, 110)
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_bacterias(t, d):
    c = fondo(t, "#10301C", "#1F5A30")
    enjambre(c, t, 26, 40, 620, 1000, 900, 3, 0.5)
    tag(c, "≈38", "BILLONES DE BACTERIAS", 540, 1700, t - 0.2, 110)
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_uno_a_uno(t, d):
    c = fondo(t)
    img, dd = capa()
    ang = math.sin(t * 3) * 3 * (1 - clamp01(t / 1.2))
    dd.polygon([(540, 1150), (470, 1450), (610, 1450)], fill=(200, 200, 210, 255))
    a = math.radians(ang)
    x0, y0, x1, y1 = 540 - math.cos(a) * 380, 1150 - math.sin(a) * 380, 540 + math.cos(a) * 380, 1150 + math.sin(a) * 380
    dd.line([(x0, y0), (x1, y1)], fill=(220, 220, 230, 255), width=18)
    c.alpha_composite(img)
    pegar(c, celula(), x0, y0 - 110, 0.7)
    pegar(c, bacteria(), x1, y1 - 70, 0.8)
    tag(c, "≈ 1 : 1", "", 540, 780, t - 0.3, 150)
    return c, dict(zoom=1.0, t=t)


def e_intestino(t, d):
    c = fondo(t, "#3A1420", "#6A2A3A")
    img, dd = capa()
    pts = [(200 + 680 * (0.5 + 0.5 * math.sin(k * 0.5)), 650 + k * 30) for k in range(36)]
    dd.line(pts, fill=(242, 155, 176, 255), width=110, joint="curve")
    dd.line(pts, fill=(255, 190, 205, 255), width=60, joint="curve")
    c.alpha_composite(img)
    for k in range(10):
        ph = (t * 0.25 + k / 10) % 1
        i = int(ph * (len(pts) - 1))
        pegar(c, bacteria("#7BD88F", 800), pts[i][0], pts[i][1], 0.32)
    texto(c, "EN TU INTESTINO", 540, 1780, t - 0.2, 100, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_giro(t, d):
    c = fondo(0.0)
    enjambre(c, 0.0, 22, 60, 650, 960, 700, 1, 0.45)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def e_globulos(t, d):
    c = fondo(t, "#3A0A14", "#6A1A28")
    rng = random.Random(5)
    for k in range(26):
        x = (rng.uniform(0, W) + t * rng.uniform(60, 160)) % (W + 200) - 100
        pegar(c, globulo(), x, rng.uniform(620, 1550), rng.uniform(0.5, 0.9), rot=rng.uniform(0, 360))
    tag(c, "≈90 %", "GLÓBULOS ROJOS Y PLAQUETAS", 540, 1700, t - 0.3, 100)
    return c, dict(zoom=1.0, t=t)


def e_peso(t, d):
    c = fondo(t, "#10301C", "#1F5A30")
    img, dd = capa()
    dd.rounded_rectangle([290, 1250, 790, 1430], radius=40, fill=(230, 232, 240, 255))
    dd.rectangle([330, 1220, 750, 1250], fill=(200, 200, 210, 255))
    dd.rounded_rectangle([440, 1300, 640, 1390], radius=14, fill=(30, 40, 30, 255))
    c.alpha_composite(img)
    enjambre(c, t, 12, 360, 1060, 360, 140, 7, 0.32)
    hud(rotulo("200 g", 60, "#7BFF9A", "#0A200F", 4), 540, 1345, 1)
    texto(c, "SOLO ≈200 GRAMOS", 540, 1700, t - 0.3, 100, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_cta(t, d):
    c = fondo(t)
    enjambre(c, t, 6, 650, 1300, 380, 400, 9, 0.4)
    pegar(c, nico(t, "feliz", 10, 140 + 25 * math.sin(t * 10)), 330, 1880, 0.95, ancla="abajo")
    globo_texto(c, "¿QUÉ DATO TE\nSORPRENDIÓ MÁS?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto", ("pop", 0.2)]),
    (1, 0.0, e_falso, None, [("buzz", 0.1), ("impacto", 0.12)]),
    (2, 0.0, e_1972, "barrido", ["whoosh", ("pop", 0.4)]),
    (3, 0.0, e_2016, "barrido", ["whoosh", ("pop", 0.2)]),
    (4, 0.0, e_celulas, None, ["pop3"]),
    (5, 0.0, e_bacterias, None, ["burbujas", ("pop", 0.2)]),
    (6, 0.0, e_uno_a_uno, None, ["boing", ("ding", 0.3)]),
    (7, 0.0, e_intestino, "barrido", ["whoosh", "squish"]),
    (8, 0.0, e_giro, None, ["scratch"]),
    (9, 0.0, e_globulos, None, ["whoosh", ("pop", 0.3)]),
    (10, 0.0, e_peso, None, [("ding", 0.3)]),
    (11, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]
ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
