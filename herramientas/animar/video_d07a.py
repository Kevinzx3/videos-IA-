"""Día 07 · Video A: ¿Y si caes por un agujero que atraviesa la Tierra?"""
import math

from PIL import Image, ImageDraw

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-07/datos/01-agujero-que-atraviesa-la-tierra.json"
CX, CY, R = 540, 1100, 520


def tierra_corte(t, tubo=True):
    c = cielo_estrellas(t)
    img, d = capa()
    for r, col in ((R, (60, 130, 200)), (R * 0.93, (150, 90, 50)), (R * 0.55, (230, 120, 40)), (R * 0.2, (255, 220, 90))):
        d.ellipse([CX - r, CY - r, CX + r, CY + r], fill=col + (255,))
    d.ellipse([CX - R, CY - R, CX + R, CY + R], outline=(200, 230, 255, 255), width=10)
    if tubo:
        d.rectangle([CX - 26, CY - R - 10, CX + 26, CY + R + 10], fill=(30, 30, 45, 255), outline=(220, 220, 230, 255), width=5)
    c.alpha_composite(img)
    pegar(c, brillo(R * 0.3, "#FFE45C", 0.6), CX, CY)
    return c


def nico_tubo(c, t, y, esc=0.18, expr="sorpresa", rot=0):
    pegar(c, nico(t, expr, 160, 160, -15, 15), CX, y, esc, rot=rot)


def e_gancho(t, d):
    c = tierra_corte(t)
    nico_tubo(c, t, CY - R - 60, 0.2, "esceptico")
    texto(c, "¿CUÁNTO TARDAS?", 540, 1780, t - 0.1, 105, "#FFD400")
    return c, dict(zoom=1.0 + 0.1 * ease_out(t / d), temblor=5 if t < 0.25 else 0, t=t)


def e_tubo(t, d):
    c = tierra_corte(t)
    texto(c, "TUBO SIN AIRE", 540, 1780, t - 0.2, 105, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def pos(u):
    """Posición en el tubo para fase u (0 arriba, 0.5 abajo), movimiento armónico."""
    return CY - R * math.cos(u * math.tau)


def e_salta(t, d):
    c = tierra_corte(t)
    u = 0.12 * ease_in(clamp01(t / d)) if False else 0.12 * clamp01(t / d) ** 2
    y = pos(u)
    nico_tubo(c, t, y, 0.18, "sorpresa", rot=t * 60)
    for k in range(4):
        pegar(c, brillo(14, "#FFFFFF", 0.8), CX + (k - 1.5) * 18, y - 80 - k * 25)
    texto(c, "LA GRAVEDAD TE JALA", 540, 1780, t - 0.2, 90, "#FFFFFF")
    return c, dict(zoom=1.3, fy=0.5, t=t)


def bala(c, x, y, esc):
    m = Image.new("L", (300, 110), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 10, 230, 100], radius=10, fill=255)
    ImageDraw.Draw(m).pieslice([160, 10, 300, 100], 270, 90, fill=255)
    pegar(c, sprite(m, "#C8A040", 900), x, y, esc)


def e_bala(t, d):
    c = cielo_estrellas(t)
    u = clamp01(t / d)
    bala(c, 100 + u * 500, 800, 1.0)
    pegar(c, nico(t, "espiral", 160, 160), 100 + u * 900, 1250, 0.6, rot=-80)
    for k in range(6):
        img, dd = capa()
        y = 1150 + k * 40
        dd.line([(100 + u * 900 - 300 - k * 30, y), (100 + u * 900 - 120, y)], fill=(255, 255, 255, 160), width=6)
        c.alpha_composite(img)
    texto(c, "MÁS RÁPIDO\nQUE UNA BALA", 540, 1700, t - 0.2, 100, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def e_frena(t, d):
    c = tierra_corte(t)
    u = 0.25 + 0.15 * clamp01(t / d)
    y = pos(u)
    nico_tubo(c, t, y, 0.18, "esfuerzo", rot=180)
    img, dd = capa()
    dd.polygon([(CX + 70, y - 60), (CX + 110, y), (CX + 30, y)], fill=(255, 77, 109, 255))
    dd.line([(CX + 70, y), (CX + 70, y - 140)], fill=(255, 77, 109, 255), width=12)
    c.alpha_composite(img)
    texto(c, "AHORA TE FRENA", 540, 1780, t - 0.2, 100, "#FF4D6D")
    return c, dict(zoom=1.2, fy=0.6, t=t)


def e_llega(t, d):
    c = tierra_corte(t)
    u = 0.42 + 0.08 * ease_out(clamp01(t / (d * 0.6)))
    nico_tubo(c, t, pos(u) + 60, 0.2, "feliz", rot=180)
    texto(c, "QUIETO UN INSTANTE", 540, 400 + 1400, t - 0.3, 90, "#FFFFFF")
    return c, dict(zoom=1.25, fy=0.72, t=t)


def e_tiempo(t, d):
    c = cielo_estrellas(t)
    img, dd = capa()
    dd.ellipse([290, 700, 790, 1200], fill=(240, 240, 245, 255), outline=(255, 77, 109, 255), width=30)
    a = -math.pi / 2 + clamp01(t / 1.2) * math.tau * 38 / 60
    dd.pieslice([320, 730, 760, 1170], -90, math.degrees(a), fill=(255, 212, 0, 200))
    dd.line([(540, 950), (540 + math.cos(a) * 200, 950 + math.sin(a) * 200)], fill=(30, 20, 30, 255), width=14)
    dd.rectangle([510, 640, 570, 700], fill=(255, 77, 109, 255))
    c.alpha_composite(img)
    tag(c, "≈38", "MINUTOS", 540, 1450, t - 0.6, 150)
    return c, dict(zoom=1.0, t=t)


def e_yoyo(t, d):
    c = tierra_corte(t)
    u = (t / d * 1.0) % 1
    nico_tubo(c, t, pos(u), 0.18, "espiral", rot=t * 120)
    texto(c, "PARA SIEMPRE", 540, 1780, t - 0.3, 110, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def e_giro(t, d):
    c = tierra_corte(0.0)
    nico_tubo(c, 0.0, CY - R - 60, 0.2, "sorpresa")
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def e_antipoda(t, d):
    c = cielo_estrellas(t)
    pegar(c, prop("tierra"), 540, 1100, 0.6, rot=t * 3)
    img, dd = capa()
    u = ease_in_out(clamp01((t - 0.2) / 1.0))
    p0, p1 = (380, 820), (700, 1380)
    dd.line([p0, (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)], fill=(255, 212, 0, 255), width=10)
    c.alpha_composite(img)
    pegar(c, brillo(26, "#FFD400", 1), *p0)
    hud(rotulo("CARIBE", 54, "#FFFFFF"), p0[0] - 20, p0[1] - 70, 1)
    if u > 0.95:
        pegar(c, brillo(30, "#3DE0E6", 1), *p1)
        hud(rotulo("OCÉANO ÍNDICO", 60, "#3DE0E6"), 620, p1[1] + 80, pop_scale(t - 1.2))
    texto(c, "NO EN CHINA", 540, 1780, t - 0.4, 110, "#FF4D6D")
    return c, dict(zoom=1.0, t=t)


def e_flotador(t, d):
    c = degradado(W, H, [(0, "#3E7CB1"), (0.45, "#9FD3FF"), (0.46, "#1F6F8B"), (1, "#0B2A44")])
    img, dd = capa()
    dd.line([(x, 880 + math.sin(x / 70 + t * 3) * 14) for x in range(0, W + 20, 20)], fill=(232, 244, 242, 255), width=10)
    c.alpha_composite(img)
    sal = ease_out(clamp01(t / 0.6))
    pegar(c, nico(t, "feliz", 160, 160), 540, 1300 - sal * 120, 0.8, ancla="abajo")
    m = Image.new("L", (300, 300), 0)
    dm = ImageDraw.Draw(m)
    dm.ellipse([10, 10, 290, 290], fill=255)
    dm.ellipse([90, 90, 210, 210], fill=0)
    pegar(c, sprite(m, "#FF4D6D", 910), 540, 1100 - sal * 120, 1.0)
    texto(c, "LLEVA FLOTADOR", 540, 1650, t - 0.3, 105, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def e_cta(t, d):
    c = tierra_corte(t)
    pegar(c, nico(t, "feliz", 10, 140 + 25 * math.sin(t * 10)), 330, 1880, 0.95, ancla="abajo")
    globo_texto(c, "¿TE ATREVERÍAS\nA SALTAR?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto", "riser_suave"]),
    (1, 0.0, e_tubo, None, ["whoosh_grave"]),
    (2, 0.0, e_salta, None, ["whoosh", "riser_corto"]),
    (3, 0.0, e_bala, "barrido", ["whoosh", ("impacto", 0.3)]),
    (4, 0.0, e_frena, None, ["squish"]),
    (5, 0.0, e_llega, None, ["boing"]),
    (6, 0.0, e_tiempo, "barrido", ["tictac", ("impacto", 0.6)]),
    (7, 0.0, e_yoyo, None, ["boing", ("whoosh", 0.5)]),
    (8, 0.0, e_giro, None, ["scratch"]),
    (9, 0.0, e_antipoda, None, ["whoosh", ("pop", 1.2), ("buzz", 0.4)]),
    (10, 0.0, e_flotador, None, ["ola", ("ding", 0.3)]),
    (11, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]
ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
