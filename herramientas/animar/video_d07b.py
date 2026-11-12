"""Día 07 · Video B (misterio): Las luces de Hessdalen."""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-07/datos/02-misterio-luces-de-hessdalen.json"


@lru_cache(maxsize=2)
def _valle():
    c = _cielo_noche()
    img, d = capa()
    for k, col in enumerate([(40, 50, 80), (28, 36, 60), (18, 24, 40)]):
        base = 1150 + k * 160
        pts = [(0, H)] + [(x, base - 260 + k * 60 + math.sin(x / 160 + k) * 120 + math.sin(x / 60) * 20) for x in range(0, W + 30, 30)] + [(W, H)]
        d.polygon(pts, fill=col + (255,))
    for k, (x, y) in enumerate([(220, 1500), (720, 1560), (880, 1440)]):  # casitas
        d.rectangle([x - 40, y - 40, x + 40, y + 20], fill=(70, 40, 40, 255))
        d.polygon([(x - 50, y - 40), (x, y - 80), (x + 50, y - 40)], fill=(90, 50, 50, 255))
        d.rectangle([x - 12, y - 20, x + 12, y], fill=(255, 210, 120, 255))
    c.alpha_composite(img)
    return c


def _cielo_noche():
    c = degradado(W, H, [(0, "#03060F"), (0.6, "#14203A"), (1, "#1E2A48")])
    img, d = capa()
    rng = random.Random(2)
    for _ in range(260):
        x, y, r = rng.uniform(0, W), rng.uniform(0, 1100), rng.choice([1, 1.5, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rng.randint(120, 255)))
    c.alpha_composite(img)
    return c


def valle(t):
    c = _valle().copy()
    particulas(c, t, 60, (255, 255, 255), 31, (2, 4), -25, 200)  # nieve
    return c


def orbe(c, x, y, color, esc=1.0, t=0):
    p = 1 + 0.15 * math.sin(t * 5 + x)
    pegar(c, brillo(110 * esc * p, color, 0.55), x, y)
    pegar(c, brillo(40 * esc, "#FFFFFF", 0.95), x, y)


def orbes(c, t, n=3, seed=1):
    rng = random.Random(seed)
    cols = ["#FFFFFF", "#FFE45C", "#FF6A5A"]
    for k in range(n):
        x0, y0 = rng.uniform(200, 880), rng.uniform(600, 1050)
        modo = k % 3
        if modo == 0:
            x, y = x0 + math.sin(t * 0.7 + k) * 60, y0 + math.cos(t * 0.5 + k) * 30
        elif modo == 1:
            x, y = x0, y0
        else:
            x, y = x0 + ((t * 400) % 1400) - 700, y0 - ((t * 120) % 400)
        orbe(c, x, y, cols[k % 3], rng.uniform(0.7, 1.2), t)


def e_gancho(t, d):
    c = valle(t)
    orbes(c, t, 3)
    texto(c, "NORUEGA", 540, 1780, t - 0.1, 130, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.12 * ease_out(t / d), temblor=5 if t < 0.25 else 0, t=t)


def e_nombre(t, d):
    c = valle(t)
    orbe(c, 540, 820, "#FFE45C", 1.3, t)
    texto(c, "HESSDALEN", 540, 1780, t - 0.1, 140, "#FFE45C")
    return c, dict(zoom=1.1, fy=0.45, t=t)


def e_colores(t, d):
    c = valle(t)
    orbes(c, t, 6, 4)
    texto(c, "FLOTAN, SE PARAN\nO SE DISPARAN", 540, 1760, t - 0.2, 90, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_oleada(t, d):
    c = valle(t)
    rng = random.Random(9)
    for k in range(18):
        if t > k * 0.12:
            orbe(c, rng.uniform(120, 960), rng.uniform(560, 1100), rng.choice(["#FFFFFF", "#FFE45C", "#FF6A5A"]), 0.6, t)
    tag(c, "AÑOS 80", "OLEADA", 540, 1780, t - 0.3, 120)
    return c, dict(zoom=1.0, t=t)


def radar(c, x, y, esc, t):
    img, dd = capa()
    dd.chord([x - 160 * esc, y - 160 * esc, x + 160 * esc, y + 160 * esc], 200, 340, fill=(220, 225, 235, 255))
    dd.line([(x, y - 60 * esc), (x, y + 140 * esc)], fill=(180, 185, 195, 255), width=int(16 * esc))
    c.alpha_composite(img)
    ondas(c, x, y - 100 * esc, t, (120, 255, 170), 3, 500, 6, (200, 340))


def e_proyecto(t, d):
    c = valle(t)
    orbes(c, t, 2, 11)
    radar(c, 300, 1450, 1.0, t)
    m = Image.new("L", (220, 150), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 220, 150], radius=26, fill=255)
    pegar(c, sprite(m, "#33333D", 920), 780, 1400, 1.0)
    pegar(c, brillo(30, "#88CCFF", 0.8), 850, 1400)
    tag(c, "1983", "PROYECTO HESSDALEN", 540, 1780, t - 0.3, 100)
    return c, dict(zoom=1.0, t=t)


def e_estacion(t, d):
    c = valle(t)
    m = Image.new("L", (300, 260), 0)
    ImageDraw.Draw(m).rectangle([0, 60, 300, 260], fill=255)
    pegar(c, sprite(m, "#C9CED8", 930), 540, 1450, 1.0, sombra=True)
    img, dd = capa()
    dd.line([(540, 1330), (540, 1050)], fill=(200, 200, 210, 255), width=10)
    c.alpha_composite(img)
    ondas(c, 540, 1050, t, (255, 228, 92), 3, 400, 6, (0, 360))
    if int(t * 2) % 2 == 0:
        pegar(c, brillo(18, "#FF2020", 1), 640, 1360)
    tag(c, "1998", "ESTACIÓN AUTOMÁTICA", 540, 1780, t - 0.3, 100)
    return c, dict(zoom=1.0, t=t)


def e_por_ano(t, d):
    c = valle(t)
    orbes(c, t, 4, 17)
    tag(c, "10–20", "VECES AL AÑO", 540, 1780, t - 0.2, 130)
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_giro(t, d):
    c = valle(0.0)
    orbes(c, 0.0, 3)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def e_foto(t, d):
    c = valle(t)
    img, dd = capa()
    dd.rectangle([140, 640, 940, 1340], fill=(240, 240, 235, 255))
    c.alpha_composite(img)
    foto = _valle().crop((0, 500, W, 1300)).resize((760, 560))
    _comp(c, foto, 160, 660)
    orbe(c, 540, 860, "#FFE45C", 1.0, 0)
    hud(rotulo("FOTOGRAFIADAS\nY MEDIDAS", 90, "#FFFFFF"), 540, 1700, pop_scale(t - 0.3))
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_plasma(t, d):
    c = valle(t)
    rng = random.Random(4)
    for k in range(16):
        ph = (t * 0.4 + k / 16) % 1
        x = rng.uniform(150, 930)
        pegar(c, brillo(12, "#9CFFC8", 0.9 * (1 - ph)), x, 1500 - ph * 700)
    orbe(c, 540, 820, "#C8B4FF", 1.4, t)
    texto(c, "¿PLASMA\nPOR RADÓN?", 540, 1760, t - 0.2, 100, "#9CFFC8")
    return c, dict(zoom=1.0, t=t)


def e_sin(t, d):
    c = valle(t)
    pegar(c, rotulo("?", 520, "#FFE45C", "#2A2000", 20), 540, 950, 1 + 0.05 * math.sin(t * 4))
    texto(c, "SIN EXPLICACIÓN", 540, 1700, t - 0.2, 110, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_cta(t, d):
    c = valle(t)
    orbes(c, t, 2, 21)
    pegar(c, nico(t, "esceptico", 10, 140 + 25 * math.sin(t * 10)), 330, 1880, 0.95, ancla="abajo")
    globo_texto(c, "¿TÚ QUÉ CREES\nQUE SON?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto", "riser_suave"]),
    (1, 0.0, e_nombre, None, [("pop", 0.1)]),
    (2, 0.0, e_colores, None, ["whoosh", "blip"]),
    (3, 0.0, e_oleada, "barrido", ["whoosh", "pop3"]),
    (4, 0.0, e_proyecto, None, ["click", ("pop", 0.3)]),
    (5, 0.0, e_estacion, None, ["blip", ("pop", 0.3)]),
    (6, 0.0, e_por_ano, None, [("pop", 0.2)]),
    (7, 0.0, e_giro, None, ["scratch"]),
    (8, 0.0, e_foto, None, ["click", ("ding", 0.3)]),
    (9, 0.0, e_plasma, "barrido", ["whoosh_grave", "burbujas"]),
    (10, 0.0, e_sin, None, [("pop", 0.1)]),
    (11, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]
ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
