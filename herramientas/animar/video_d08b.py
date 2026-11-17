"""Día 08 · Video B (mito): ¿Los murciélagos son ciegos?"""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-08/datos/02-mito-murcielagos-ciegos.json"
ROPA = "cientifico"  # mito de biología: Nico con bata


@lru_cache(maxsize=2)
def _cueva():
    c = degradado(W, H, [(0, "#0B0A1C"), (0.6, "#1E1A3A"), (1, "#2B2440")])
    img, d = capa()
    rng = random.Random(5)
    for k in range(14):  # estalactitas
        x = k * 85 + rng.uniform(-20, 20)
        d.polygon([(x - 45, 0), (x + 45, 0), (x, rng.uniform(160, 380))], fill=(45, 38, 60, 255))
    pts = [(0, H)] + [(x, 1560 + math.sin(x / 90) * 40 + rng.uniform(-10, 10)) for x in range(0, W + 40, 40)] + [(W, H)]
    d.polygon(pts, fill=(38, 32, 52, 255))
    c.alpha_composite(img)
    return c


def cueva(t):
    c = _cueva().copy()
    particulas(c, t, 35, (190, 180, 255), 13, (2, 4), 10, 110)
    return c


@lru_cache(maxsize=2)
def _noche():
    c = degradado(W, H, [(0, "#0A1030"), (0.7, "#2A2058"), (1, "#3B2F6B")])
    img, d = capa()
    rng = random.Random(8)
    for _ in range(150):
        x, y = rng.uniform(0, W), rng.uniform(0, 1200)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 255, 255, rng.randint(90, 230)))
    c.alpha_composite(img)
    pegar(c, brillo(220, "#FFF3C4", 0.5), 800, 520)
    m = Image.new("L", (240, 240), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 240, 240], fill=255)
    pegar(c, sprite(m, "#FFF3C4", 700), 800, 520)
    return c


def noche(t):
    c = _noche().copy()
    particulas(c, t, 25, (255, 240, 200), 4, (2, 3), 8, 90)
    return c


@lru_cache(maxsize=32)
def murcielago(fase=0, color="#4A3B5C", ojos=1.0, fruta=False):
    """Murciélago de frente; fase 0..3 = aleteo. ojos: escala de los ojos."""
    m = Image.new("L", (600, 360), 0)
    d = ImageDraw.Draw(m)
    alto = (-90, -40, 20, 60)[fase]
    for s in (-1, 1):  # alas festoneadas
        tip = (300 + s * 290, 150 + alto)
        d.polygon([(300 + s * 40, 140), tip, (300 + s * 230, 250 + alto * 0.3), (300 + s * 160, 230), (300 + s * 100, 260), (300 + s * 40, 220)], fill=255)
    d.ellipse([235, 110, 365, 300], fill=255)  # cuerpo
    d.ellipse([240, 50, 360, 170], fill=255)  # cabeza
    if fruta:  # hocico de zorro
        d.polygon([(275, 130), (325, 130), (300, 195)], fill=255)
        d.polygon([(250, 70), (265, 0), (295, 60)], fill=255)
        d.polygon([(350, 70), (335, 0), (305, 60)], fill=255)
    else:
        d.polygon([(245, 80), (240, -10 + 20), (290, 60)], fill=255)
        d.polygon([(355, 80), (360, 10), (310, 60)], fill=255)
    spr = sprite(m, color, 710 + fase, pelo=True)
    dd = ImageDraw.Draw(spr)
    r = 16 * ojos
    for s in (-1, 1):
        ex = 300 + s * 26
        dd.ellipse([ex - r, 105 - r, ex + r, 105 + r], fill=(255, 255, 255, 255))
        dd.ellipse([ex - r * 0.55, 105 - r * 0.55, ex + r * 0.55, 105 + r * 0.55], fill=(25, 20, 30, 255))
    dd.arc([285, 125, 315, 150], 20, 160, fill=(25, 20, 30, 255), width=4)
    return spr


def bat(c, t, x, y, esc, color="#4A3B5C", ojos=1.0, fruta=False, vel=14):
    f = int(t * vel) % 4
    pegar(c, murcielago(f, color, ojos, fruta), x, y + math.sin(t * 3 + x) * 20, esc)


def bandada(c, t, n=7, seed=1, esc=0.35):
    rng = random.Random(seed)
    for k in range(n):
        x = (rng.uniform(0, W) + t * rng.uniform(80, 200)) % (W + 300) - 150
        bat(c, t + k * 0.13, x, rng.uniform(500, 1300), esc * rng.uniform(0.7, 1.2))


@lru_cache(maxsize=4)
def bicho(tipo):
    m = Image.new("L", (200, 160), 0)
    d = ImageDraw.Draw(m)
    if tipo == "polilla":
        d.ellipse([20, 20, 100, 140], fill=255)
        d.ellipse([100, 20, 180, 140], fill=255)
        d.ellipse([85, 40, 115, 140], fill=255)
        return sprite(m, "#D9C8A0", 720)
    if tipo == "mosquito":
        d.ellipse([60, 60, 150, 100], fill=255)
        d.ellipse([20, 20, 90, 70], fill=255)
        d.ellipse([110, 20, 180, 70], fill=255)
        return sprite(m, "#8E8E9A", 721)
    if tipo == "mango":
        d.ellipse([20, 10, 180, 150], fill=255)
        return sprite(m, "#F2A93B", 722)
    if tipo == "flor":
        for k in range(6):
            a = k / 6 * math.tau
            d.ellipse([100 + math.cos(a) * 45 - 35, 80 + math.sin(a) * 45 - 35, 100 + math.cos(a) * 45 + 35, 80 + math.sin(a) * 45 + 35], fill=255)
        return sprite(m, "#F4F0F8", 723)
    raise KeyError(tipo)


def e_gancho(t, d):
    c = cueva(t)
    bandada(c, t, 8, 1, 0.4)
    texto(c, "¿CIEGOS?", 540, 900, t - 0.1, 160, "#FFD400")
    return c, dict(zoom=1.0 + 0.1 * ease_out(t / d), temblor=5 if t < 0.25 else 0, t=t)


def e_nico(t, d):
    c = cueva(t)
    bat(c, t, 760, 900, 0.7)
    pegar(c, nico(t, "esceptico", 10, 150, ropa=ROPA), 330, 1880, 0.95, ancla="abajo")
    texto(c, "MITO FAMOSO", 540, 1300, t - 0.2, 100, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_falso(t, d):
    c = cueva(t)
    bandada(c, t, 8, 1, 0.4)
    sello(c, "FALSO", t - 0.1, "#FF4D6D", 1100, 200)
    return c, dict(zoom=1.05, temblor=10 if 0.1 < t < 0.35 else 0, t=t)


def e_ojos(t, d):
    c = cueva(t)
    bat(c, t, 540, 1180, 1.55, ojos=1.0 + 0.4 * pop_scale(t - 0.8), vel=6)
    tag(c, "TODOS", "TIENEN OJOS", 540, 1650, t - 1.0, 110)
    return c, dict(zoom=1.0 + 0.05 * t, t=t)


def e_ecolocalizacion(t, d):
    c = cueva(t)
    bat(c, t, 300, 1100, 0.9)
    ondas(c, 420, 1080, t, (61, 224, 230), 4, 600, 10, (-40, 40))
    texto(c, "ECOLOCALIZACIÓN", 540, 1650, t - 0.3, 95, "#3DE0E6")
    return c, dict(zoom=1.0 + 0.03 * t, t=t)


def e_eco(t, d):
    c = cueva(t)
    bat(c, t, 220, 1100, 0.7)
    pegar(c, bicho("polilla"), 860, 1050 + math.sin(t * 5) * 30, 0.9)
    ondas(c, 320, 1080, t, (61, 224, 230), 3, 560, 10, (-30, 30))
    if t > 1.2:
        ondas(c, 840, 1050, t - 1.2, (255, 212, 0), 3, 500, 8, (150, 210))  # el eco vuelve
        texto(c, "ECO", 700, 850, t - 1.2, 110, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def e_caza(t, d):
    c = cueva(t)
    c = Image.blend(c, Image.new("RGBA", (W, H), (0, 0, 0, 255)), 0.5)
    u = clamp01(t / (d * 0.7))
    x = 150 + 550 * ease_in_out(u)
    if u < 1:
        pegar(c, bicho("mosquito"), 760, 1100 + math.sin(t * 9) * 30, 0.7)
    bat(c, t, x, 1100, 0.8, vel=18)
    if u >= 1:
        texto(c, "¡ÑAM!", 760, 900, t - d * 0.7, 120, "#FFD400")
    texto(c, "A OSCURAS", 540, 1650, t - 0.2, 100, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_zorro(t, d):
    c = noche(t)
    img, dd = capa()
    dd.line([(0, 1250), (W, 1180)], fill=(60, 40, 30, 255), width=40)  # rama
    c.alpha_composite(img)
    pegar(c, bicho("mango"), 380, 1310, 1.1)
    bat(c, t, 640, 1050, 1.25, "#7A4B2A", 1.5, fruta=True, vel=5)
    texto(c, "ZORRO VOLADOR", 540, 1650, t - 0.3, 95, "#FFD400")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_giro(t, d):
    c = cueva(0.0)
    bandada(c, 0.0, 8, 1, 0.4)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def e_uv(t, d):
    c = noche(t)
    uv = clamp01((t - 0.8) / 0.6)
    if uv:
        c = Image.blend(c, Image.new("RGBA", (W, H), (60, 0, 120, 255)), 0.45 * uv)
    pegar(c, bicho("flor"), 540, 1250, 2.4)
    if uv:
        pegar(c, brillo(150, "#C77DFF", 0.8 * uv), 540, 1250)
        pegar(c, brillo(60, "#3DE0E6", 0.9 * uv), 540, 1250)
    bat(c, t, 820, 900, 0.6)
    tag(c, "UV", "ULTRAVIOLETA", 540, 1650, t - 0.4, 110)
    return c, dict(zoom=1.0 + 0.05 * t, t=t)


def e_dicho(t, d):
    c = cueva(t)
    bandada(c, t, 4, 7, 0.35)
    pegar(c, nico(t, "orgullo", 160, 160, ropa=ROPA), 540, 1880, 1.0, ancla="abajo")
    globo_texto(c, "«CIEGO COMO UN\nMURCIÉLAGO»", 540, 820, t - 0.2, 64)
    if t > 2.5:
        sello(c, "MITO", t - 2.5, "#FF4D6D", 1150, 170)
    return c, dict(zoom=1.0 + 0.03 * t, t=t)


def e_cta(t, d):
    c = cueva(t)
    bat(c, t, 820, 1150, 0.55)
    pegar(c, nico(t, "feliz", 10, 140 + 25 * math.sin(t * 10), ropa=ROPA), 330, 1880, 0.95, ancla="abajo")
    globo_texto(c, "¿QUÉ MITO\nDESMONTO AHORA?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto", "blip"]),
    (0, 0.5, e_nico, None, [("pop", 0.2)]),
    (1, 0.0, e_falso, None, [("buzz", 0.1), ("impacto", 0.12)]),
    (2, 0.0, e_ojos, "barrido", ["whoosh", ("boing", 0.8), ("pop", 1.0)]),
    (3, 0.0, e_ecolocalizacion, "barrido", ["whoosh", "blip", ("pop", 0.3)]),
    (4, 0.0, e_eco, None, ["blip", ("blip", 1.2), ("pop", 1.2)]),
    (5, 0.0, e_caza, None, ["whoosh_grave", ("bonk", 1.9)]),
    (6, 0.0, e_zorro, "barrido", ["whoosh", ("pop", 0.3)]),
    (7, 0.0, e_giro, None, ["scratch"]),
    (8, 0.0, e_uv, None, [("riser_corto", 0.2), ("ding", 0.9), ("pop", 0.4)]),
    (9, 0.0, e_dicho, "barrido", ["whoosh", ("pop", 0.2), ("impacto", 2.5)]),
    (10, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]
ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
