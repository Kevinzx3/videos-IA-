"""Día 04 · Video B (mito): Triángulo de las Bermudas, el misterio que no lo es."""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-04/datos/02-mito-triangulo-bermudas.json"
PUNTOS = {"MIAMI": (230, 960), "BERMUDAS": (850, 840), "PUERTO RICO": (760, 1580)}


@lru_cache(maxsize=2)
def _mapa():
    c = degradado(W, H, [(0, "#0F3A5A"), (1, "#0A2540")])
    img, d = capa()
    for x in range(0, W, 90):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 18), width=2)
    for y in range(0, H, 90):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 18), width=2)
    c.alpha_composite(img)
    m = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(m)
    o = 200
    dm.polygon([(0, 300 + o), (260, 380 + o), (300, 600 + o), (250, 830 + o), (170, 900 + o), (120, 700 + o), (0, 650 + o)], fill=255)  # Florida/costa
    dm.ellipse([340, 1080 + o, 640, 1180 + o], fill=255)   # Cuba (aprox.)
    dm.ellipse([620, 1180 + o, 760, 1250 + o], fill=255)   # La Española
    dm.ellipse([730, 1350 + o, 800, 1400 + o], fill=255)   # Puerto Rico
    dm.ellipse([835, 625 + o, 870, 655 + o], fill=255)     # Bermudas
    c.alpha_composite(sprite(m, "#C9A86A", 500, grano=0.2))
    return c


def mapa(t, triangulo=1.0, puntos=True):
    c = _mapa().copy()
    particulas(c, t, 20, (200, 240, 255), 2, (2, 4), 5, 90)
    if triangulo > 0:
        img, d = capa()
        p = [PUNTOS[k] for k in ("MIAMI", "BERMUDAS", "PUERTO RICO")]
        n = 60
        segs = []
        for a, b in ((p[0], p[1]), (p[1], p[2]), (p[2], p[0])):
            segs += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
        k = int(len(segs) * triangulo)
        if k > 1:
            d.polygon(p, fill=(255, 77, 109, int(50 * triangulo)))
            for i in range(0, k - 1, 2):
                d.line([segs[i], segs[i + 1]], fill=(255, 212, 0, 255), width=10)
        c.alpha_composite(img)
    if puntos:
        for nom, (x, y) in PUNTOS.items():
            pegar(c, brillo(26, "#FFFFFF", 1), x, y)
            hud(rotulo(nom, 46, "#FFFFFF", "#1A1022", 4), min(max(x, 180), 900), y + 60, 1)
    return c


def barco(color="#E8E2D0", seed=510):
    m = Image.new("L", (360, 220), 0)
    d = ImageDraw.Draw(m)
    d.polygon([(0, 120), (360, 120), (300, 210), (50, 210)], fill=255)
    d.rectangle([120, 40, 260, 125], fill=255)
    d.rectangle([180, 0, 210, 45], fill=255)
    return sprite(m, color, seed)


def avion(seed=520):
    m = Image.new("L", (360, 200), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([20, 80, 340, 125], radius=22, fill=255)
    d.polygon([(150, 100), (230, 100), (170, 10), (130, 10)], fill=255)
    d.polygon([(150, 105), (230, 105), (170, 195), (130, 195)], fill=255)
    d.polygon([(30, 100), (80, 100), (40, 40), (20, 40)], fill=255)
    return sprite(m, "#DDE2EA", seed)


def tormenta(t):
    c = degradado(W, H, [(0, "#0A0E1A"), (0.5, "#1C2A3A"), (0.55, "#0E2A3A"), (1, "#061520")])
    img, d = capa()
    for k in range(6):
        y = 1000 + k * 130
        d.line([(x, y + math.sin(x / 60 + t * 3 + k) * 22) for x in range(0, W + 20, 20)], fill=(120, 180, 200, 90), width=8)
    c.alpha_composite(img)
    particulas(c, t, 120, (200, 220, 255), 21, (1, 2), -900, 140)
    if int(t * 2.3) % 5 == 0:
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, 60)))
    return c


def e_gancho(t, d):
    c = tormenta(t)
    hunde = ease_in_out(t / d)
    pegar(c, barco("#C9CED8"), 380, 1050 + hunde * 200, 1.0, rot=-10 - hunde * 25, alfa=1 - hunde * 0.6)
    pegar(c, avion(), 760 + t * 60, 480, 0.8, alfa=1 - hunde)
    texto(c, "¿ES REAL?", 540, 1650, t - 0.2, 140, "#FF4D6D")
    return c, dict(zoom=1.0 + 0.12 * ease_out(t / d), temblor=6 if t < 0.25 else 0, t=t)


def e_mapa(t, d):
    c = mapa(t, ease_in_out(clamp01((t - 0.2) / 1.2)))
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_fama(t, d):
    c = mapa(t, 1.0, False)
    c = Image.blend(c, Image.new("RGBA", (W, H), (20, 10, 30, 255)), 0.45)
    for k, (txt, col) in enumerate([("LIBROS", "#3D7BE0"), ("DOCUMEN-\nTALES", "#FF4D6D"), ("ATLÁNTIDA", "#4E8F4A"), ("OVNIS", "#8A4FD0"), ("PORTALES", "#E08A3C")]):
        s = pop_scale(t - 0.1 - k * 0.3)
        if s:
            x = 200 + (k % 3) * 340
            y = 950 + (k // 3) * 380
            hud(icono_carta(txt, col, 280, 530 + k), x + (170 if k >= 3 else 0), y, s * 0.95, True)
    texto(c, "FAMA ENORME", 540, 1720, t - 0.05, 120, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def e_noaa(t, d):
    c = degradado(W, H, [(0, "#0F3A5A"), (1, "#0A2540")])
    particulas(c, t, 25, (200, 240, 255), 4, (2, 4), 8, 100)
    tag(c, "NOAA", "", 540, 900, t - 0.05, 170)
    texto(c, "AGENCIA DEL OCÉANO\nDE EE. UU.", 540, 1180, t - 0.3, 75, "#FFFFFF")
    texto(c, "LO DICE CLARO", 540, 1600, t - 0.6, 110, "#FFD400")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_pruebas(t, d):
    c = degradado(W, H, [(0, "#0F3A5A"), (1, "#0A2540")])
    barras(c, [10, 10, 10], ["TRIÁNGULO", "ZONA A", "ZONA B"], ["#FF4D6D", "#3DE0E6", "#3DE0E6"], t, x0=90, ancho=900, maximo=12)
    texto(c, "SIN DIFERENCIA", 540, 1680, t - 0.7, 110, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def e_trafico(t, d):
    c = mapa(t, 1.0, False)
    rng = random.Random(5)
    for k in range(14):
        x0, y0 = rng.uniform(-100, W), rng.uniform(500, 1500)
        vx = rng.uniform(40, 120) * (1 if k % 2 else -1)
        x = (x0 + t * vx) % (W + 200) - 100
        if k % 3 == 0:
            pegar(c, avion(), x, y0 - 200, 0.35, rot=0 if vx > 0 else 180)
        else:
            pegar(c, barco(), x, y0, 0.3)
    texto(c, "MUCHO TRÁFICO", 540, 1780, t - 0.2, 110, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_huracan(t, d):
    c = mapa(t, 1.0, False)
    img, dd = capa()
    cx, cy = 600, 1200
    for k in range(4):
        pts = [(cx + math.cos(a + t * 3 + k * 1.57) * (20 + a * 40), cy + math.sin(a + t * 3 + k * 1.57) * (20 + a * 40)) for a in [j * 0.15 for j in range(40)]]
        dd.line(pts, fill=(255, 255, 255, 200), width=14, joint="curve")
    for k in range(5):  # corriente del Golfo
        ph = (t * 0.6 + k / 5) % 1
        y = 1300 - ph * 700
        dd.polygon([(300 + ph * 120, y - 40), (280 + ph * 120, y + 10), (330 + ph * 120, y + 10)], fill=(61, 224, 230, int(230 * (1 - ph))))
    c.alpha_composite(img)
    texto(c, "HURACANES Y\nCORRIENTES", 540, 1760, t - 0.2, 100, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_fisicas(t, d):
    c = degradado(W, H, [(0, "#0F3A5A"), (1, "#0A2540")])
    m = Image.new("L", (520, 520), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 520, 520], fill=255)
    chk = sprite(m, "#4E8F4A", 540)
    ImageDraw.Draw(chk).line([(130, 270), (230, 370), (400, 170)], fill=(255, 255, 255, 255), width=50)
    pegar(c, chk, 540, 1000, pop_scale(t - 0.1) * 0.9, sombra=True)
    texto(c, "CAUSAS FÍSICAS", 540, 1560, t - 0.4, 110, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_oficial(t, d):
    c = mapa(t, 1.0, True)
    sello(c, "NO OFICIAL", t - 0.3, "#FF4D6D", 1250, 140, -10)
    return c, dict(zoom=1.0, temblor=8 if 0.3 < t < 0.5 else 0, t=t)


def e_giro(t, d):
    c = tormenta(0.0)
    pegar(c, barco("#C9CED8"), 380, 1050, 1.0, rot=-10)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def revista():
    m = Image.new("L", (560, 760), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 560, 760], radius=20, fill=255)
    spr = sprite(m, "#F2E6C8", 550)
    d = ImageDraw.Draw(spr)
    d.rectangle([0, 0, 560, 150], fill=(180, 40, 50, 255))
    r = rotulo("REVISTA", 80, "#FFFFFF", "#6A1020", 4)
    spr.alpha_composite(r, (280 - r.width // 2, 75 - r.height // 2))
    r = rotulo("EL MORTAL\nTRIÁNGULO", 70, "#1A1022", "#FFFFFF", 4)
    spr.alpha_composite(r, (280 - r.width // 2, 330 - r.height // 2))
    d.polygon([(280, 460), (160, 680), (400, 680)], outline=(180, 40, 50, 255), width=12)
    return spr


def e_1964(t, d):
    c = degradado(W, H, [(0, "#2A1C10"), (1, "#5A3A20")])
    particulas(c, t, 20, (255, 230, 200), 3, (2, 4), 8, 90)
    pegar(c, revista(), 540, 1080, pop_scale(t - 0.05) * 0.85, rot=-6 + math.sin(t * 2) * 2, sombra=True)
    tag(c, "1964", "", 540, 1560, t - 0.4, 150)
    texto(c, "VINCENT GADDIS", 540, 1740, t - 0.7, 85, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_titular(t, d):
    c = degradado(W, H, [(0, "#2A1C10"), (1, "#5A3A20")])
    u = ease_out(t / 0.7)
    pegar(c, revista(), 540, 1080, 0.3 + 0.6 * u, rot=(1 - u) * 720, sombra=True)
    texto(c, "UN BUEN TITULAR", 540, 1650, t - 0.7, 115, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def e_cta(t, d):
    c = mapa(t, 1.0, False)
    pegar(c, nico(t, "esceptico", 10, 140 + 25 * math.sin(t * 10)), 330, 1880, 0.95, ancla="abajo")
    globo_texto(c, "¿QUÉ MISTERIO\nINVESTIGO AHORA?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto", "ola", "riser_suave"]),
    (1, 0.0, e_mapa, "barrido", ["whoosh", ("pop", 0.3)]),
    (2, 0.0, e_fama, None, [("pop", 0.1), ("pop", 0.4), ("pop", 0.7), ("pop", 1.0), ("pop", 1.3)]),
    (3, 0.0, e_noaa, "barrido", ["whoosh", ("pop", 0.05)]),
    (4, 0.0, e_pruebas, None, ["riser_corto", ("ding", 0.8)]),
    (5, 0.0, e_trafico, None, ["whoosh"]),
    (6, 0.0, e_huracan, None, ["whoosh_grave", "ola"]),
    (7, 0.0, e_fisicas, None, [("ding", 0.2)]),
    (8, 0.0, e_oficial, None, [("buzz", 0.3), ("impacto", 0.32)]),
    (9, 0.0, e_giro, None, ["scratch"]),
    (10, 0.0, e_1964, None, [("pop", 0.05), ("impacto", 0.4)]),
    (11, 0.0, e_titular, None, ["whoosh", ("ding", 0.7)]),
    (12, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]
ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
