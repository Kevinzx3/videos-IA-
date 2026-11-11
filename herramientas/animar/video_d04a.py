"""Día 04 · Video A (misterio resuelto): Las piedras que se mueven solas."""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-04/datos/01-piedras-que-se-mueven-solas.json"
HORIZ = 900


@lru_cache(maxsize=4)
def _playa(noche=False):
    if noche:
        c = degradado(W, H, [(0, "#0B1030"), (0.46, "#2E3A78"), (0.47, "#4A4F6E"), (1, "#3A3E58")])
    else:
        c = degradado(W, H, [(0, "#4F8FD1"), (0.44, "#F6C28B"), (0.47, "#D9C29A"), (1, "#C8AE82")])
    img, d = capa()
    for k, col in enumerate([(150, 110, 90, 255), (120, 85, 70, 255)] if not noche else [(40, 40, 70, 255), (30, 30, 55, 255)]):
        pts = [(0, HORIZ)] + [(x, HORIZ - 120 - k * 40 + math.sin(x / 120 + k * 2) * 60 + math.sin(x / 47) * 20) for x in range(0, W + 30, 30)] + [(W, HORIZ)]
        d.polygon(pts, fill=col)
    rng = random.Random(3)  # grietas hexagonales del barro seco
    for _ in range(260):
        x, y = rng.uniform(0, W), rng.uniform(HORIZ + 10, H)
        r = 18 + (y - HORIZ) / 9
        pts = [(x + math.cos(a / 6 * math.tau) * r, y + math.sin(a / 6 * math.tau) * r * 0.45) for a in range(7)]
        d.line(pts, fill=(140, 115, 80, 120) if not noche else (80, 80, 110, 120), width=3)
    c.alpha_composite(img)
    return c


def playa(t, noche=False):
    c = _playa(noche).copy()
    particulas(c, t, 25, (255, 240, 210), 3, (2, 4), 6, 100)
    return c


@lru_cache(maxsize=8)
def roca(seed=0, tam=220):
    rng = random.Random(seed)
    m = Image.new("L", (tam, int(tam * 0.75)), 0)
    pts = [(tam / 2 + math.cos(a) * tam * rng.uniform(0.38, 0.48), tam * 0.4 + math.sin(a) * tam * rng.uniform(0.25, 0.33)) for a in [k / 9 * math.tau for k in range(9)]]
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return sprite(m, "#5E5650", 400 + seed)


def rastro(c, pts, ancho=18, alfa=200):
    img, d = capa()
    d.line(pts, fill=(110, 90, 65, alfa), width=ancho, joint="curve")
    d.line(pts, fill=(235, 215, 180, alfa // 2), width=max(2, ancho // 4), joint="curve")
    c.alpha_composite(img)


def camino(seed, x0, y0, largo, n=40):
    rng = random.Random(seed)
    pts, x, y, a = [], x0, y0, rng.uniform(-2.2, -0.9)
    for k in range(n):
        a += rng.uniform(-0.25, 0.25)
        x += math.cos(a) * largo / n
        y += math.sin(a) * largo / n * 0.5
        pts.append((x, y))
    return pts


def e_gancho(t, d):
    c = playa(t)
    pts = camino(1, 520, 1500, 900)
    u = 0.85 + 0.15 * ease_in_out(t / d)
    k = int(len(pts) * u)
    rastro(c, pts[:k], 26)
    pegar(c, roca(1, 260), pts[k - 1][0], pts[k - 1][1] - 40, 1.0, sombra=True)
    texto(c, "SE MUEVEN SOLAS", 540, 1700, t - 0.15, 105, "#FFD400")
    return c, dict(zoom=1.0 + 0.1 * ease_out(t / d), temblor=6 if t < 0.25 else 0, t=t)


def e_racetrack(t, d):
    c = playa(t)
    for s in range(5):
        pts = camino(10 + s, 150 + s * 190, 1800, 700)
        rastro(c, pts, 10)
        pegar(c, roca(s, 120), pts[-1][0], pts[-1][1] - 20, 1.0)
    texto(c, "RACETRACK PLAYA", 540, 1100, t - 0.15, 105, "#FFFFFF")
    texto(c, "VALLE DE LA MUERTE", 540, 1240, t - 0.35, 75, "#FFD400")
    return c, dict(zoom=1.1 - 0.08 * t / d, t=t)


def e_roca(t, d):
    c = playa(t)
    pts = camino(2, 540, 1900, 1000)
    rastro(c, pts, 40)
    pegar(c, roca(2, 360), 540, 1450, 1.0, sombra=True)
    tag(c, "DECENAS", "DE KILOS", 540, 1750, t - 0.3, 110)
    return c, dict(zoom=1.0 + 0.05 * t, t=t)


def e_nadie(t, d):
    c = playa(t)
    for s in range(3):
        pts = camino(20 + s, 250 + s * 280, 1850, 900, 60)
        rastro(c, pts, 16)
        pegar(c, roca(5 + s, 150), pts[-1][0], pts[-1][1] - 25, 1.0)
    pegar(c, nico(t, "esceptico", 120, 120), 540, 1900, 0.9, ancla="abajo")
    texto(c, "NADIE LAS VIO", 540, 820, t - 0.2, 110, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_teorias(t, d):
    c = playa(t)
    c = Image.blend(c, Image.new("RGBA", (W, H), (30, 20, 40, 255)), 0.35)
    for k, (txt, col) in enumerate([("VIENTO\nHURACANADO", "#3D7BE0"), ("ALGAS\nRESBALADIZAS", "#4E8F4A"), ("¿OVNIS?", "#8A4FD0")]):
        s = pop_scale(t - 0.2 - k * 0.45)
        if s:
            hud(icono_carta(txt, col, 300, 410 + k), 200 + k * 340, 1150 + (k % 2) * 120, s * 0.95, True)
    texto(c, "TEORÍAS", 540, 800, t - 0.05, 130, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def camara_tripode(c, x, y, esc, t, rec=False):
    img, d = capa()
    for dx in (-60, 0, 60):
        d.line([(x, y), (x + dx * esc, y + 260 * esc)], fill=(60, 60, 70, 255), width=int(10 * esc))
    c.alpha_composite(img)
    m = Image.new("L", (220, 150), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 220, 150], radius=26, fill=255)
    pegar(c, sprite(m, "#33333D", 420), x, y - 40 * esc, esc)
    pegar(c, brillo(30 * esc, "#88CCFF", 0.8), x + 70 * esc, y - 40 * esc)
    if rec and int(t * 3) % 2 == 0:
        pegar(c, brillo(20 * esc, "#FF2020", 1.0), x - 70 * esc, y - 80 * esc)


def e_camaras(t, d):
    c = playa(t)
    for k in range(3):
        camara_tripode(c, 200 + k * 340, 1150, 0.8, t)
    for k in range(3):
        x = 250 + k * 300
        pegar(c, roca(10 + k, 160), x, 1650, 1.0, sombra=True)
        pegar(c, rotulo("GPS", 44, "#FFFFFF", "#1A1022", 4), x, 1560, pop_scale(t - 0.3 - k * 0.2))
    return c, dict(zoom=1.0, t=t)


def e_grabadas(t, d):
    c = playa(t)
    pegar(c, calendario("DIC", "2013"), 300, 1200, pop_scale(t - 0.05) * 0.9, sombra=True)
    camara_tripode(c, 760, 1200, 1.1, t, rec=True)
    texto(c, "¡GRABADAS!", 540, 1700, t - 0.4, 125, "#FF4D6D")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_hielo_noche(t, d):
    c = playa(t, True)
    pegar(c, prop("icono", "luna"), 820, 400, 0.9)
    img, dd = capa()
    u = clamp01(t / 1.0)
    dd.rectangle([0, HORIZ + 20, W, H], fill=(170, 210, 255, int(110 * u)))
    for k in range(25):
        x = (k * 97) % W
        y = HORIZ + 60 + (k * 53) % (H - HORIZ - 80)
        dd.line([(x, y), (x + 60, y - 10)], fill=(255, 255, 255, int(160 * u)), width=3)
    c.alpha_composite(img)
    pegar(c, roca(3, 260), 540, 1500, 1.0)
    texto(c, "AGUA QUE\nSE CONGELA", 540, 1750, t - 0.2, 95, "#BFE6FF")
    return c, dict(zoom=1.0, t=t)


def placas(c, t, desplaza=0.0, u_romper=1.0):
    rng = random.Random(9)
    img, d = capa()
    for fila in range(6):
        for col in range(5):
            x = col * 230 + 60 + rng.uniform(-30, 30) + desplaza
            y = HORIZ + 120 + fila * 160 + rng.uniform(-20, 20)
            sep = 16 * u_romper
            pts = [(x + sep, y), (x + 200 - sep, y + 10), (x + 210 - sep, y + 130 - sep), (x + 10 + sep, y + 140 - sep)]
            d.polygon(pts, fill=(190, 225, 255, 120), outline=(255, 255, 255, 220))
    c.alpha_composite(img)


def e_placas(t, d):
    c = playa(t)
    placas(c, t, 0, ease_out(t / 0.8))
    pegar(c, roca(3, 260), 540, 1500, 1.0)
    tag(c, "POCOS", "mm", 540, 1780, t - 0.4, 120)
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_brisa(t, d):
    c = playa(t)
    u = clamp01(t / d)
    rastro(c, [(240, 1520), (240 + u * 300, 1520 - u * 30)], 30)
    placas(c, t, u * 300, 1.0)
    pegar(c, roca(3, 260), 240 + u * 300, 1480 - u * 30, 1.0)
    for k in range(4):
        ph = (t * 1.5 + k / 4) % 1
        img, dd = capa()
        y = 1150 + k * 60
        dd.line([(ph * W - 200, y), (ph * W, y)], fill=(255, 255, 255, int(200 * (1 - ph))), width=8)
        c.alpha_composite(img)
    texto(c, "UNA BRISA SUAVE", 540, 1780, t - 0.2, 100, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_giro(t, d):
    c = playa(0.0)
    pegar(c, roca(1, 260), 540, 1400, 1.0)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def e_lento(t, d):
    c = playa(t)
    u = clamp01(t / d)
    rastro(c, [(300, 1450), (300 + u * 80, 1450)], 30)
    pegar(c, roca(4, 260), 300 + u * 80, 1410, 1.0, sombra=True)
    tag(c, "2–6", "m/min", 540, 1050, t - 0.2, 150)
    pegar(c, nico(t, "cansado", 10, 10), 800, 1900, 0.8, ancla="abajo")
    texto(c, "CASI NI SE NOTA", 540, 1780, t - 0.6, 90, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_cta(t, d):
    c = playa(t)
    pegar(c, roca(1, 200), 800, 1600, 1.0, sombra=True)
    pegar(c, nico(t, "feliz", 10, 140 + 25 * math.sin(t * 10)), 330, 1880, 0.95, ancla="abajo")
    globo_texto(c, "¿QUÉ MISTERIO\nRESUELVO AHORA?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto", "riser_suave"]),
    (1, 0.0, e_racetrack, "barrido", ["whoosh", ("pop", 0.15), ("pop", 0.35)]),
    (2, 0.0, e_roca, None, [("pop", 0.3)]),
    (3, 0.0, e_nadie, None, ["blip"]),
    (4, 0.0, e_teorias, "barrido", ["whoosh", ("pop", 0.2), ("pop", 0.65), ("pop", 1.1)]),
    (5, 0.0, e_camaras, None, ["click", ("blip", 0.3)]),
    (6, 0.0, e_grabadas, None, [("pop", 0.05), ("ding", 0.4)]),
    (7, 0.0, e_hielo_noche, "barrido", ["whoosh_suave"]),
    (8, 0.0, e_placas, None, ["squish3", ("pop", 0.4)]),
    (9, 0.0, e_brisa, None, ["whoosh"]),
    (10, 0.0, e_giro, None, ["scratch"]),
    (11, 0.0, e_lento, None, [("pop", 0.2), "tictac"]),
    (12, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]
ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
