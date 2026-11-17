"""Día 08 · Video A (¿Sabías que…?): Los flamencos son rosas por lo que comen."""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-08/datos/01-flamencos-rosas-por-comer.json"
ROPA = "explorador"  # laguna / naturaleza
ROSA, GRIS, BLANCO = "#F27FA6", "#A9A4AE", "#F1ECEF"


@lru_cache(maxsize=4)
def _laguna():
    c = degradado(W, H, [(0, "#2B1E3F"), (0.45, "#C2577A"), (0.62, "#F29E5C"), (0.63, "#5C8FA8"), (1, "#2F5E78")])
    img, d = capa()
    for k, col in enumerate([(70, 50, 90), (50, 40, 70)]):  # montes lejanos
        base = 1180 + k * 25
        pts = [(0, base)] + [(x, base - 120 + k * 50 - math.sin(x / 140 + k * 2) * 70) for x in range(0, W + 30, 30)] + [(W, base)]
        d.polygon(pts, fill=col + (255,))
    for k in range(9):  # reflejos
        y = 1260 + k * 70
        d.line([(120 + (k * 97) % 600, y), (300 + (k * 97) % 600, y)], fill=(255, 220, 200, 70), width=6)
    c.alpha_composite(img)
    pegar(c, brillo(160, "#FFE0A0", 0.6), 760, 1150)
    return c


def laguna(t):
    c = _laguna().copy()
    particulas(c, t, 30, (255, 230, 200), 8, (2, 4), 12, 120)
    return c


@lru_cache(maxsize=16)
def flamenco(color=ROSA, pierna_doblada=True, seed=500):
    """Flamenco de fieltro mirando a la derecha; pies en el borde inferior."""
    m = Image.new("L", (420, 820), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([60, 330, 340, 500], fill=255)  # cuerpo
    d.polygon([(60, 400), (0, 360), (40, 440)], fill=255)  # cola
    d.line([(300, 380), (330, 280), (270, 180), (300, 90)], fill=255, width=46, joint="curve")  # cuello en S
    d.ellipse([270, 50, 360, 130], fill=255)  # cabeza
    d.line([(210, 480), (210, 800)], fill=255, width=16)  # pierna
    if pierna_doblada:
        d.line([(170, 480), (150, 600), (210, 640)], fill=255, width=16, joint="curve")
    else:
        d.line([(170, 480), (160, 800)], fill=255, width=16)
    spr = sprite(m, color, seed)
    dd = ImageDraw.Draw(spr)
    dd.polygon([(350, 80), (410, 100), (400, 150), (360, 120)], fill=(245, 235, 225, 255))  # pico claro
    dd.polygon([(395, 125), (410, 100), (400, 160)], fill=(30, 25, 30, 255))  # punta negra
    dd.ellipse([318, 72, 336, 90], fill=(30, 25, 30, 255))
    dd.arc([110, 360, 300, 470], 200, 330, fill=oscurecer(hexrgb(color), 0.2) + (255,), width=8)  # ala
    return spr


def flamenco_t(c, t, x, y, esc, color=ROSA, fase=0.0, espejo=False):
    spr = flamenco(color)
    if espejo:
        spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    pegar(c, spr, x, y + math.sin(t * 2 + fase) * 6, esc, rot=math.sin(t * 1.5 + fase) * 2, ancla="abajo", sombra=True)


def mezcla_hex(a, b, u):
    return "#%02X%02X%02X" % mezcla(hexrgb(a), hexrgb(b), clamp01(u))


@lru_cache(maxsize=8)
def comida(tipo):
    m = Image.new("L", (240, 240), 0)
    d = ImageDraw.Draw(m)
    if tipo == "alga":
        for k in range(3):
            d.line([(80 + k * 40, 230), (60 + k * 40, 150), (100 + k * 40, 80), (70 + k * 40, 10)], fill=255, width=30, joint="curve")
        return sprite(m, "#5FA84A", 600)
    if tipo == "gamba":
        d.arc([30, 40, 210, 220], 100, 330, fill=255, width=60)
        d.polygon([(40, 130), (0, 90), (10, 170)], fill=255)
        spr = sprite(m, "#F2875A", 601)
        ImageDraw.Draw(spr).ellipse([175, 75, 195, 95], fill=(30, 25, 30, 255))
        return spr
    if tipo == "larva":
        for k in range(5):
            d.ellipse([20 + k * 40, 90 - (k % 2) * 20, 80 + k * 40, 150 - (k % 2) * 20], fill=255)
        return sprite(m, "#E8C95A", 602)
    if tipo == "zanahoria":
        d.polygon([(60, 40), (180, 40), (120, 235)], fill=255)
        spr = sprite(m, "#F28C28", 603)
        dd = ImageDraw.Draw(spr)
        for k in range(3):
            dd.line([(120, 40), (90 + k * 30, 0)], fill=(80, 160, 70, 255), width=18)
        return spr
    if tipo == "cuenco":
        d.chord([10, 40, 230, 230], 0, 180, fill=255)
        spr = sprite(m, "#7FB8FF", 604)
        ImageDraw.Draw(spr).ellipse([30, 110, 210, 160], fill=(242, 135, 90, 255))
        return spr
    raise KeyError(tipo)


def e_gancho(t, d):
    c = laguna(t)
    flamenco_t(c, t, 380, 1750, 1.05)
    flamenco_t(c, t, 790, 1760, 0.55, GRIS, 1.0)
    texto(c, "¿ROSAS?", 540, 900, t - 0.1, 150, "#FFD400")
    return c, dict(zoom=1.0 + 0.1 * ease_out(t / d), temblor=5 if t < 0.25 else 0, t=t)


def e_grises(t, d):
    c = laguna(t)
    flamenco_t(c, t, 540, 1780, 0.9, GRIS)
    texto(c, "NACEN GRISES", 540, 900, t - 0.05, 130, "#FFFFFF")
    return c, dict(zoom=1.1 + 0.05 * t, fy=0.7, t=t)


def e_pierden(t, d):
    c = laguna(t)
    flamenco_t(c, t, 650, 1760, 0.95, mezcla_hex(ROSA, BLANCO, (t - 1.2) / 2.5))
    pegar(c, nico(t, "sorpresa", 30, 150, ropa=ROPA), 250, 1880, 0.7, ancla="abajo")
    texto(c, "SIN SU COMIDA,\nPIERDEN EL COLOR", 540, 900, t - 0.3, 90, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_comida(t, d):
    c = degradado(W, H, [(0, "#1F5E78"), (1, "#0E3A4F")])
    particulas(c, t, 40, (200, 240, 255), 3, (3, 7), -30, 140)  # burbujas
    for k, (tipo, x, nom, at) in enumerate((("alga", 230, "ALGAS", 0.3), ("gamba", 540, "GAMBAS", 1.3), ("larva", 850, "LARVAS", 2.4))):
        s = pop_scale(t - at)
        if s:
            pegar(c, comida(tipo), x, 1250 + math.sin(t * 3 + k) * 15, 1.4 * s, rot=math.sin(t * 2 + k) * 8)
            texto(c, nom, x, 1500, t - at, 70, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.03 * t, t=t)


def e_carotenoides(t, d):
    c = degradado(W, H, [(0, "#1F5E78"), (1, "#0E3A4F")])
    particulas(c, t, 40, (200, 240, 255), 3, (3, 7), -30, 140)
    pegar(c, comida("gamba"), 540, 1200, 2.4, rot=math.sin(t * 2) * 6)
    for k in range(10):  # pigmento que brilla
        a = k / 10 * math.tau + t
        pegar(c, brillo(26, "#FF8A3D", 0.9), 540 + math.cos(a) * 300, 1200 + math.sin(a) * 300)
    tag(c, "CAROTENOIDES", "", 540, 1650, t - 0.2, 110)
    return c, dict(zoom=1.05 + 0.04 * t, t=t)


def e_zanahoria(t, d):
    c = degradado(W, H, [(0, "#3B2F6B"), (1, "#14112B")])
    particulas(c, t, 30, (255, 220, 180), 5, (2, 5), 12, 120)
    pegar(c, comida("zanahoria"), 300, 1200, 1.8 * pop_scale(t), rot=-10, sombra=True)
    texto(c, "=", 540, 1200, t - 0.3, 200, "#FFD400")
    pegar(c, comida("gamba"), 790, 1200, 1.6 * pop_scale(t - 0.5), rot=8, sombra=True)
    texto(c, "MISMO PIGMENTO", 540, 1600, t - 0.8, 90, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.03 * t, t=t)


def e_digiere(t, d):
    c = laguna(t)
    flamenco_t(c, t, 470, 1800, 1.25, ROSA)
    for k, (nom, x, y, at) in enumerate((("PLUMAS", 280, 1180, 1.0), ("PIEL", 760, 1430, 1.9), ("PICO", 820, 880, 2.6))):
        if t > at:
            pegar(c, brillo(70, "#FFD400", 0.5 + 0.2 * math.sin(t * 6)), x, y)
            texto(c, nom, x, y - 90, t - at, 70, "#FFD400")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_intensidad(t, d):
    c = laguna(t)
    for k, (col, x) in enumerate(((BLANCO, 220), ("#F6B3CB", 540), ("#E8467F", 860))):
        if t > k * 0.4:
            flamenco_t(c, t, x, 1700, 0.6 * pop_scale(t - k * 0.4), col, k)
    for k, (et, x) in enumerate((("POCA\nCOMIDA", 220), ("NORMAL", 540), ("MUCHA\nCOMIDA", 860))):
        texto(c, et, x, 1000, t - k * 0.4, 60, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_crias(t, d):
    c = laguna(t)
    u = clamp01((t - 0.3) / (d - 0.6))
    flamenco_t(c, t, 540, 1760, 0.45 + 0.5 * ease_in_out(u), mezcla_hex(GRIS, ROSA, u))
    tag(c, "HASTA 3", "AÑOS", 540, 900, t - 0.2, 120)
    return c, dict(zoom=1.0, t=t)


def e_giro(t, d):
    c = laguna(0.0)
    flamenco_t(c, 0.0, 380, 1750, 1.05)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def e_zoo(t, d):
    c = degradado(W, H, [(0, "#8EC5E8"), (0.6, "#CDE8C8"), (1, "#6E8A2E")])
    img, dd = capa()
    for x in range(0, W + 1, 90):  # valla
        dd.rectangle([x, 1150, x + 22, 1420], fill=(150, 110, 70, 255))
    dd.rectangle([0, 1200, W, 1225], fill=(150, 110, 70, 255))
    dd.rectangle([0, 1330, W, 1355], fill=(150, 110, 70, 255))
    c.alpha_composite(img)
    texto(c, "ZOO", 540, 900, t - 0.1, 140, "#FFFFFF")
    u = clamp01((t - 1.8) / 1.5)
    flamenco_t(c, t, 380, 1750, 0.9, mezcla_hex(BLANCO, ROSA, u))
    pegar(c, comida("cuenco"), 760, 1700, 1.2 * pop_scale(t - 0.6), sombra=True)
    if t > 1.0:
        texto(c, "+ PIGMENTO", 760, 1500, t - 1.0, 70, "#FFD400")
    return c, dict(zoom=1.0 + 0.03 * t, t=t)


def e_maquillaje(t, d):
    c = laguna(t)
    flamenco_t(c, t, 380, 1800, 1.1, "#EE5D93")
    flamenco_t(c, t, 760, 1800, 1.0, "#F6B3CB", 2.0, espejo=True)
    rng = random.Random(3)
    for k in range(12):
        ph = (t * 0.8 + k / 12) % 1
        pegar(c, brillo(16, "#FFFFFF", 1 - ph), rng.uniform(240, 520), 1350 - ph * 300)
    if t > 1.5:
        pegar(c, corazon(), 570, 1100 - (t - 1.5) * 40, 0.45 * pop_scale(t - 1.5))
    sello(c, "SE MAQUILLAN", t - 0.6, "#FF4D6D", 880, 120, -6)
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_cta(t, d):
    c = laguna(t)
    flamenco_t(c, t, 820, 1760, 0.75)
    pegar(c, nico(t, "feliz", 10, 140 + 25 * math.sin(t * 10), ropa=ROPA), 330, 1880, 0.95, ancla="abajo")
    globo_texto(c, "¿QUÉ ANIMAL\nEXPLICO AHORA?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto", ("pop", 0.1)]),
    (0, 0.55, e_grises, None, [("boing", 0.05)]),
    (1, 0.0, e_pierden, "barrido", ["whoosh", ("estirar", 1.2)]),
    (2, 0.0, e_comida, "barrido", ["whoosh", "burbujas", ("pop", 0.3), ("pop", 1.3), ("pop", 2.4)]),
    (2, 0.62, e_carotenoides, None, [("pop", 0.2), ("ding", 0.4)]),
    (3, 0.0, e_zanahoria, None, ["pop3"]),
    (4, 0.0, e_digiere, "barrido", ["whoosh", ("blip", 1.0), ("blip", 1.9), ("blip", 2.6)]),
    (5, 0.0, e_intensidad, None, ["pop3"]),
    (6, 0.0, e_crias, None, ["estirar", ("pop", 0.2)]),
    (7, 0.0, e_giro, None, ["scratch"]),
    (8, 0.0, e_zoo, "barrido", ["whoosh", ("pop", 0.6), ("ding", 2.0)]),
    (9, 0.0, e_maquillaje, None, ["squish", ("impacto", 0.6), ("ding", 1.5)]),
    (10, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]
ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
