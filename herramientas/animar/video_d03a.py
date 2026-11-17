"""Día 03 · Video A: Un día en Venus dura más que un año."""
import math

from PIL import Image, ImageDraw

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-03/datos/01-venus-dia-mas-largo-que-ano.json"
VENUS, NUBES = "#E8B04B", "#F4D58A"
TRAJE = "#E8ECF2"


def venus(c, x, y, esc, t, giro=0.0, bandera=False):
    p = planeta(VENUS, 300, NUBES, 230)
    pegar(c, brillo(330 * esc, "#FFC870", 0.35), x, y)
    pegar(c, p, x, y, esc, rot=giro)
    if bandera:  # marca para ver la rotación
        a = math.radians(-90 - giro)
        bx, by = x + math.cos(a) * 300 * esc, y + math.sin(a) * 300 * esc
        img, d = capa()
        d.line([(bx, by), (bx + math.cos(a) * 90 * esc, by + math.sin(a) * 90 * esc)], fill=(255, 255, 255, 255), width=8)
        tx, ty = bx + math.cos(a) * 90 * esc, by + math.sin(a) * 90 * esc
        d.polygon([(tx, ty), (tx + math.cos(a + 1.57) * 50 * esc, ty + math.sin(a + 1.57) * 50 * esc),
                   (bx + math.cos(a) * 55 * esc, by + math.sin(a) * 55 * esc)], fill=(255, 77, 109, 255))
        c.alpha_composite(img)


def sol(c, x, y, esc=1.0, t=0):
    pegar(c, brillo(260 * esc, "#FFD45C", 0.8), x, y)
    pegar(c, prop("icono", "sol"), x, y, 1.4 * esc, rot=t * 10)


def orbita(c, cx, cy, rx, ry, color=(255, 255, 255, 110)):
    img, d = capa()
    for k in range(0, 360, 6):
        a0, a1 = math.radians(k), math.radians(k + 3)
        d.line([(cx + math.cos(a0) * rx, cy + math.sin(a0) * ry), (cx + math.cos(a1) * rx, cy + math.sin(a1) * ry)], fill=color, width=5)
    c.alpha_composite(img)


def suelo_venus(t, cielo_u=0.0):
    top = mezcla(hexrgb("#3A1E10"), hexrgb("#C9772E"), cielo_u)
    c = degradado(W, H, [(0, "#%02x%02x%02x" % top), (0.62, "#E8A24B"), (0.63, "#8A4B22"), (1, "#5A2E14")])
    particulas(c, t, 40, (255, 210, 150), 3, (2, 5), 10, 120)
    img, d = capa()
    for k in range(5):
        x = 80 + k * 240
        d.polygon([(x - 160, 1210), (x, 1080 - k % 2 * 60), (x + 160, 1210)], fill=(120, 60, 30, 255))
    c.alpha_composite(img)
    return c


def astronauta(c, t, x, y, esc, expr="feliz", bi=20, bd=20):
    pegar(c, nico(t, expr, bi, bd, traje=TRAJE, casco=True), x, y, esc, ancla="abajo")


def tarta(c, x, y, esc, t):
    m = Image.new("L", (360, 300), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 120, 360, 300], radius=30, fill=255)
    spr = sprite(m, "#F29BB0", 240)
    d = ImageDraw.Draw(spr)
    for k in range(3):
        xx = 100 + k * 80
        d.rectangle([xx - 8, 40, xx + 8, 120], fill=(255, 255, 255, 255))
    out = Image.new("RGBA", spr.size, (0, 0, 0, 0))
    out.alpha_composite(spr)
    pegar(c, out, x, y, esc, sombra=True)
    for k in range(3):
        xx = x + (100 + k * 80 - 180) * esc
        pegar(c, brillo(22 * esc, "#FFD45C", 0.95), xx, y + (30 - 150) * esc + math.sin(t * 12 + k) * 4)


# ----------------------------------------------------------------- escenas
def e01(t, d):
    c = cielo_estrellas(t)
    venus(c, 540, 1000, 1.1, t, giro=t * 3)
    texto(c, "1 DÍA > 1 AÑO", 540, 1560, t - 0.15, 120, "#FFD400")
    return c, dict(zoom=1.0 + 0.15 * ease_out(t / d), temblor=6 if t < 0.25 else 0, t=t)


def e02(t, d):
    c = suelo_venus(t)
    astronauta(c, t, 540, 1750, 1.0, "esceptico", 10, 165)
    texto(c, "¿CÓMO?", 540, 800, t - 0.1, 140, "#FFFFFF")
    return c, dict(zoom=1.15, fy=0.55, t=t)


def e_orbita(t, d):
    c = cielo_estrellas(t)
    sol(c, 540, 1000, 0.8, t)
    orbita(c, 540, 1000, 400, 400)
    a = t * 1.8
    venus(c, 540 + math.cos(a) * 400, 1000 + math.sin(a) * 400, 0.28, t)
    tag(c, "225", "días = AÑO", 540, 1560, t - 0.3, 120)
    return c, dict(zoom=1.0, t=t)


def e_giro_lento(t, d):
    c = cielo_estrellas(t)
    venus(c, 540, 980, 1.0, t, giro=t * 8, bandera=True)
    tag(c, "243", "días = DÍA", 540, 1560, t - 0.3, 120)
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_barras(t, d):
    c = cielo_estrellas(t, "#120A26", "#3A1E4A")
    barras(c, [225, 243], ["AÑO", "DÍA"], ["#3DE0E6", "#FF4D6D"], t, maximo=260)
    texto(c, "GIRA LENTÍSIMO", 540, 1680, t - 0.7, 105, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_cumple(t, d):
    c = suelo_venus(t, 0.5)
    astronauta(c, t, 360, 1760, 0.9, "feliz", 120, 150)
    tarta(c, 760, 1500, 0.9, t)
    texto(c, "¡FELIZ CUMPLE!", 540, 820, t - 0.2, 110, "#FFD400")
    for k in range(10):
        ph = (t * 0.8 + k / 10) % 1
        pegar(c, brillo(12, ["#FF4D6D", "#3DE0E6", "#FFD400"][k % 3], 1), 120 + k * 90, 650 + ph * 900, 1, alfa=1 - ph)
    return c, dict(zoom=1.05, t=t)


def e_reves(t, d):
    c = cielo_estrellas(t)
    cols = ["#9AA3B5", "#E8B04B", "#3D7BE0", "#D9603B"]
    nombres = ["MERCURIO", "VENUS", "TIERRA", "MARTE"]
    for k, (col, nom) in enumerate(zip(cols, nombres)):
        x = 180 + k * 240
        rv = nom == "VENUS"
        pegar(c, planeta(col, 120, None, 250 + k), x, 1000, 0.75, rot=(t * 40) * (-1 if rv else 1))
        img, dd = capa()
        dd.arc([x - 120, 880, x + 120, 1120], 200, 340, fill=(255, 77, 109, 255) if rv else (255, 255, 255, 200), width=10)
        ax, ay = (x + 112, 960) if not rv else (x - 112, 960)
        dd.polygon([(ax, ay - 30), (ax - 20 if not rv else ax + 20, ay + 10), (ax + 25 if not rv else ax - 25, ay + 5)], fill=(255, 77, 109, 255) if rv else (255, 255, 255, 200))
        c.alpha_composite(img)
        hud(rotulo(nom, 42, "#FFD400" if rv else "#FFFFFF", "#1A1022", 4), x, 1190, 1)
    texto(c, "GIRA AL REVÉS", 540, 1500, t - 0.3, 115, "#FF4D6D")
    return c, dict(zoom=1.0, t=t)


def e_oeste(t, d):
    u = ease_in_out(t / d)
    c = suelo_venus(t, u)
    sol(c, 240 + u * 120, 1150 - u * 450, 0.7, t)
    c2, dd = capa()
    c.alpha_composite(c2)
    hud(rotulo("OESTE", 70, "#FFD400"), 230, 1290, 1)
    hud(rotulo("ESTE", 70, "#FFFFFF"), 850, 1290, 1)
    texto(c, "SALE POR EL OESTE", 540, 1560, t - 0.2, 95, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_choque(t, d):
    c = cielo_estrellas(t)
    venus(c, 600, 1050, 0.9, t, giro=t * 5)
    u = clamp01(t / 0.5)
    if u < 1:
        pegar(c, planeta("#7A6A5A", 70, None, 260), 100 + u * 300, 450 + u * 330, 1.0)
    else:
        pegar(c, brillo(260, "#FFFFFF", clamp01(1.5 - (t - 0.5) * 2)), 400, 780)
    texto(c, "¿UN CHOQUE?", 540, 1650, t - 0.4, 110, "#FFD400")
    return c, dict(zoom=1.0, temblor=12 if 0.5 < t < 0.7 else 0, t=t)


def e_atmosfera(t, d):
    c = cielo_estrellas(t)
    venus(c, 540, 1000, 1.05, t, giro=t * 25)
    ondas(c, 540, 1000, t, (255, 220, 150), 4, 520, 14, (0, 360))
    texto(c, "¿SU ATMÓSFERA?", 540, 1650, t - 0.2, 100, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def e_giro(t, d):
    c = suelo_venus(0.0, 0.3)
    astronauta(c, 0.0, 540, 1750, 1.0, "sorpresa")
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def e_amanecer(t, d):
    u = (t / d) % 1
    c = suelo_venus(t, 0.2 + 0.6 * math.sin(u * math.pi))
    sol(c, 300 + u * 300, 1150 - math.sin(u * math.pi) * 450, 0.6, t)
    astronauta(c, t, 760, 1780, 0.8, "dormido", 10, 10)
    tag(c, "≈117", "días", 540, 1560, t - 0.3, 130)
    return c, dict(zoom=1.0, t=t)


def e_explica(t, d):
    c = cielo_estrellas(t)
    sol(c, 540, 1000, 0.7, t)
    orbita(c, 540, 1000, 380, 380)
    a = -math.pi / 2 + t * 0.6
    vx, vy = 540 + math.cos(a) * 380, 1000 + math.sin(a) * 380
    venus(c, vx, vy, 0.3, t, giro=-t * 40, bandera=True)
    img, dd = capa()
    dd.line([(540, 1000), (vx, vy)], fill=(255, 220, 120, 120), width=6)
    c.alpha_composite(img)
    texto(c, "ÓRBITA + GIRO AL REVÉS", 540, 1560, t - 0.2, 80, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_eterno(t, d):
    c = cielo_estrellas(t, "#120A26", "#3A1E4A")
    barras(c, [117, 225], ["DÍA SOLAR", "AÑO"], ["#FFD400", "#3DE0E6"], t, maximo=260)
    texto(c, "...PERO ETERNO", 540, 1680, t - 0.8, 110, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_cta(t, d):
    c = cielo_estrellas(t)
    venus(c, 820, 1450, 0.35, t, giro=t * 5)
    astronauta(c, t, 330, 1820, 0.9, "feliz", 10, 140 + 25 * math.sin(t * 10))
    globo_texto(c, "¿QUÉ PLANETA\nEXPLICO AHORA?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e01, None, ["impacto"]), (0, 0.6, e02, None, ["blip"]),
    (1, 0.0, e_orbita, "barrido", ["whoosh", ("pop", 0.3)]),
    (2, 0.0, e_giro_lento, None, ["whoosh_grave", ("pop", 0.3)]),
    (3, 0.0, e_barras, None, ["riser_corto", ("impacto", 0.6)]),
    (4, 0.0, e_cumple, "barrido", ["whoosh", ("ding", 0.2)]),
    (5, 0.0, e_reves, "barrido", ["whoosh", ("buzz", 0.3)]),
    (6, 0.0, e_oeste, None, ["riser_suave"]),
    (7, 0.0, e_choque, None, ["whoosh", ("impacto", 0.5)]), (7, 0.55, e_atmosfera, None, ["whoosh_grave"]),
    (8, 0.0, e_giro, None, ["scratch"]),
    (9, 0.0, e_amanecer, None, ["riser_suave", ("pop", 0.3)]),
    (10, 0.0, e_explica, "barrido", ["whoosh"]),
    (11, 0.0, e_eterno, None, ["pop3"]),
    (12, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]
ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
