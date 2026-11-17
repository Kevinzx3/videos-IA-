"""Día 05 · Video A: ¿Por qué el cielo es azul? (y en Marte no)."""
import math
import random

from PIL import Image, ImageDraw

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-05/datos/01-por-que-el-cielo-es-azul.json"
ARCOIRIS = ["#FF3B3B", "#FF8A2B", "#FFD400", "#4ED46A", "#3D7BE0", "#6A4FD0"]


def campo(t, cielo=("#3E8EE8", "#9FD3FF"), suelo="#6E8A2E"):
    c = degradado(W, H, [(0, cielo[0]), (0.7, cielo[1]), (0.71, suelo), (1, oscurecer(hexrgb(suelo), 0.3) and suelo)])
    particulas(c, t, 20, (255, 255, 255), 3, (2, 4), 6, 90)
    img, d = capa()
    for k in range(3):
        x = (150 + k * 380 + t * 20) % (W + 300) - 150
        for cx, r in ((0, 70), (80, 95), (170, 70)):
            d.ellipse([x + cx - r, 400 + k * 90 - r * 0.7, x + cx + r, 400 + k * 90 + r * 0.6], fill=(255, 255, 255, 230))
    c.alpha_composite(img)
    return c


def sol(c, x, y, esc=1.0, t=0, color="#FFD45C"):
    pegar(c, brillo(240 * esc, color, 0.8), x, y)
    pegar(c, prop("icono", "sol"), x, y, 1.3 * esc, rot=t * 10)


def rayo(d, x0, y0, x1, y1, color, ancho=14, zigzag=0, t=0):
    if not zigzag:
        d.line([(x0, y0), (x1, y1)], fill=color, width=ancho)
        return
    pts = []
    for k in range(13):
        u = k / 12
        dx = (zigzag if k % 2 else -zigzag) * (0 < k < 12)
        pts.append((x0 + (x1 - x0) * u + dx, y0 + (y1 - y0) * u))
    d.line(pts, fill=color, width=ancho, joint="curve")


def moleculas(c, t, n=26, seed=3, brillar=0.0):
    rng = random.Random(seed)
    for k in range(n):
        x, y = rng.uniform(80, W - 80), rng.uniform(500, 1500)
        x += math.sin(t * 2 + k) * 12
        if brillar:
            pegar(c, brillo(40, "#7FB8FF", brillar * (0.5 + 0.5 * math.sin(t * 6 + k))), x, y)
        pegar(c, planeta("#B9C6E8", 26, None, 600 + k % 3), x, y, 1.0)
        pegar(c, planeta("#B9C6E8", 26, None, 603 + k % 3), x + 34, y + 6, 1.0)


def e_gancho(t, d):
    c = campo(t)
    sol(c, 820, 330, 0.7, t)
    pegar(c, nico(t, "esceptico", 10, 165), 420, 1900, 1.0, ancla="abajo")
    texto(c, "¿POR QUÉ AZUL?", 540, 1580, t - 0.1, 115, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.12 * ease_out(t / d), temblor=5 if t < 0.25 else 0, t=t)


def e_prisma(t, d):
    c = degradado(W, H, [(0, "#14112B"), (1, "#2A2152")])
    img, dd = capa()
    u = ease_out(t / 0.6)
    dd.line([(0, 1000), (420, 1000)], fill=(255, 255, 255, 255), width=26)
    dd.polygon([(420, 820), (600, 1150), (240, 1150)], fill=(200, 230, 255, 120), outline=(255, 255, 255, 255))
    for k, col in enumerate(ARCOIRIS):
        dd.line([(470, 1010), (470 + 600 * u, 880 + k * 55 + 200 * u * (k / 5))], fill=hexrgb(col) + (255,), width=20)
    c.alpha_composite(img)
    texto(c, "TODOS LOS COLORES", 540, 1560, t - 0.4, 95, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_moleculas(t, d):
    c = degradado(W, H, [(0, "#1E3A6A"), (1, "#3E6EB0")])
    moleculas(c, t)
    img, dd = capa()
    for k, col in enumerate(["#FF3B3B", "#FFD400", "#3D7BE0"]):
        x = -200 + ((t * 500 + k * 200) % 1500)
        dd.line([(x - 180, 700 + k * 260), (x, 700 + k * 260)], fill=hexrgb(col) + (255,), width=16)
    c.alpha_composite(img)
    texto(c, "MOLÉCULAS DEL AIRE", 540, 1700, t - 0.2, 90, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_desvio(t, d):
    c = degradado(W, H, [(0, "#1E3A6A"), (1, "#3E6EB0")])
    moleculas(c, t, 14, 5)
    img, dd = capa()
    u = clamp01(t / 0.8)
    rayo(dd, 0, 820, W * u, 820, (255, 59, 59, 255), 16)
    rayo(dd, 0, 1180, W * u, 1180, (61, 123, 224, 255), 16, zigzag=90)
    c.alpha_composite(img)
    tag(c, "×5–6", "MÁS DESVÍO", 540, 1500, t - 0.6, 120)
    return c, dict(zoom=1.0, t=t)


def e_rayleigh(t, d):
    c = degradado(W, H, [(0, "#1E3A6A"), (1, "#3E6EB0")])
    moleculas(c, t, 20, 7, brillar=1.0)
    texto(c, "DISPERSIÓN\nDE RAYLEIGH", 540, 1050, t - 0.1, 115, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.05 * t, t=t)


def e_todo_azul(t, d):
    c = campo(t)
    sol(c, 820, 330, 0.7, t)
    img, dd = capa()
    rng = random.Random(4)
    for k in range(10):
        x0, y0 = rng.uniform(0, W), rng.uniform(250, 1200)
        a = rng.uniform(0, math.tau)
        ph = (t * 0.8 + k / 10) % 1
        rayo(dd, x0, y0, x0 + math.cos(a) * 260 * ph, y0 + math.sin(a) * 260 * ph, (40, 90, 220, int(220 * (1 - ph))), 10, 30)
    c.alpha_composite(img)
    pegar(c, nico(t, "feliz", 120, 120), 540, 1900, 0.95, ancla="abajo")
    return c, dict(zoom=1.0, t=t)


def e_camino(t, d):
    c = cielo_estrellas(t, "#05040F", "#14112B")
    pegar(c, planeta("#2F7FD1", 420, "#5BAA4E", 610), 540, 1650, 1.0)
    img, dd = capa()
    dd.ellipse([540 - 480, 1650 - 480, 540 + 480, 1650 + 480], outline=(120, 180, 255, 120), width=60)
    u = clamp01(t / 0.8)
    dd.line([(-50, 1080), (-50 + 650 * u, 1180 + 20 * u)], fill=(255, 230, 120, 255), width=14)
    dd.line([(540, 1230), (540, 1150)], fill=(255, 255, 255, 120), width=6)
    c.alpha_composite(img)
    sol(c, -20, 1060, 0.4, t)
    texto(c, "MUCHO MÁS AIRE", 540, 800, t - 0.4, 105, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def e_atardecer(t, d):
    u = ease_in_out(t / d)
    c = degradado(W, H, [(0, "#2B1E3F"), (0.45, "#C2577A"), (0.7, "#F29E5C"), (0.71, "#2A1E2A"), (1, "#1A1218")])
    sol(c, 540, 1100 + u * 120, 0.9, t, "#FF8A2B")
    pegar(c, nico(t, "feliz", 10, 10), 300, 1900, 0.9, ancla="abajo")
    texto(c, "ROJOS Y NARANJAS", 540, 1580, t - 0.2, 100, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def e_giro(t, d):
    c = campo(0.0)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def marte(t, cielo):
    c = degradado(W, H, [(0, cielo[0]), (0.66, cielo[1]), (0.67, "#B5532E"), (1, "#7A3418")])
    particulas(c, t, 40, (255, 210, 160), 4, (2, 5), 10, 120)
    img, d = capa()
    for k in range(4):
        x = 100 + k * 300
        d.polygon([(x - 200, 1290), (x, 1150 - k % 2 * 60), (x + 200, 1290)], fill=(140, 60, 30, 255))
    c.alpha_composite(img)
    return c


def e_marte_dia(t, d):
    c = marte(t, ("#C9A26B", "#E8C89A"))
    sol(c, 760, 400, 0.4, t, "#FFF2D0")
    pegar(c, nico(t, "sorpresa", 10, 150, traje="#E8ECF2", casco=True), 360, 1900, 0.95, ancla="abajo")
    texto(c, "COLOR CARAMELO", 540, 1600, t - 0.2, 105, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_marte_atardecer(t, d):
    c = marte(t, ("#3A3048", "#6A84B8"))
    pegar(c, brillo(330, "#9FC8FF", 0.75), 540, 1250)
    sol(c, 540, 1260, 0.35, t, "#E8F4FF")
    texto(c, "ATARDECER AZUL", 540, 1600, t - 0.2, 110, "#9FC8FF")
    return c, dict(zoom=1.0 + 0.06 * t, t=t)


def e_cta(t, d):
    c = campo(t)
    pegar(c, nico(t, "feliz", 10, 140 + 25 * math.sin(t * 10)), 330, 1880, 0.95, ancla="abajo")
    globo_texto(c, "¿CIELO AZUL\nO CARAMELO?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto"]),
    (1, 0.0, e_prisma, "barrido", ["whoosh", ("ding", 0.6)]),
    (2, 0.0, e_moleculas, None, ["whoosh", "burbujas"]),
    (3, 0.0, e_desvio, None, ["riser_corto", ("pop", 0.6)]),
    (4, 0.0, e_rayleigh, None, [("pop", 0.1)]),
    (5, 0.0, e_todo_azul, "barrido", ["whoosh", "blip"]),
    (6, 0.0, e_camino, None, ["whoosh_grave"]), (6, 0.6, e_atardecer, None, ["riser_suave"]),
    (7, 0.5, e_atardecer, None, [("pop", 0.1)]),
    (8, 0.0, e_giro, None, ["scratch"]),
    (9, 0.0, e_marte_dia, None, ["whoosh_grave", ("pop", 0.2)]),
    (10, 0.0, e_marte_atardecer, None, [("ding", 0.2)]),
    (11, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]
ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
