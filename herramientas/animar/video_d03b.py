"""Día 03 · Video B (misterio): La señal Wow! — 72 segundos que nadie ha explicado."""
import math
import random

from PIL import Image, ImageDraw, ImageFilter

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-03/datos/02-misterio-senal-wow.json"
VERDE = (120, 255, 170)


def noche(t):
    c = cielo_estrellas(t, "#03060F", "#14203A")
    img, d = capa()
    d.polygon([(0, 1450), (W, 1420), (W, H), (0, H)], fill=(16, 24, 30, 255))
    c.alpha_composite(img)
    return c


def big_ear(c, x, y, esc=1.0):
    """Radiotelescopio Big Ear: gran reflector plano inclinado + pantalla."""
    m = Image.new("L", (900, 420), 0)
    dm = ImageDraw.Draw(m)
    dm.polygon([(40, 360), (860, 360), (760, 120), (140, 120)], fill=255)
    spr = sprite(m, "#8C96A8", 300)
    dd = ImageDraw.Draw(spr)
    for k in range(1, 9):
        xx = 140 + k * 68
        dd.line([(xx - (k - 4.5) * 12, 125), (xx - (k - 4.5) * 20 - 30, 355)], fill=(200, 210, 225, 255), width=4)
    m2 = Image.new("L", (900, 420), 0)
    ImageDraw.Draw(m2).rectangle([60, 20, 840, 90], fill=255)
    pant = sprite(m2, "#5D667A", 301)
    spr.alpha_composite(pant)
    pegar(c, spr, x, y, esc, sombra=True)


def impresion(c, x, y, esc, t, resaltar=0.0, circulo=0.0):
    """Hoja de impresora de los 70 con columnas de caracteres; la columna 6EQUJ5 destaca."""
    rng = random.Random(7)
    w, h = 620, 1000
    m = Image.new("L", (w, h), 255)
    spr = sprite(m, "#F4F1E4", 302, costura=False)
    d = ImageDraw.Draw(spr)
    for yy in range(0, h, 80):
        d.rectangle([0, yy, w, yy + 40], fill=(214, 236, 214, 255))
    for k in range(0, h, 50):
        d.ellipse([10, k + 18, 26, k + 34], fill=(200, 200, 200, 255))
        d.ellipse([w - 26, k + 18, w - 10, k + 34], fill=(200, 200, 200, 255))
    f = fuente(46, False)
    col_wow = 3
    wow = "6EQUJ5"
    for fila in range(16):
        for col in range(6):
            if col == col_wow and 5 <= fila < 11:
                ch = wow[fila - 5]
                colr = mezcla((60, 60, 60), (200, 20, 40), resaltar)
            else:
                ch = rng.choice("11121 1  2 1 3 1")
                colr = (60, 60, 60)
            d.text((60 + col * 90, 40 + fila * 58), ch, font=f, fill=colr + (255,))
    if circulo > 0:
        cx, cy = 60 + col_wow * 90 + 14, 40 + 8 * 58 + 20
        d.arc([cx - 70, cy - 210, cx + 70, cy + 210], -90, -90 + 360 * circulo, fill=(220, 30, 40, 255), width=10)
    pegar(c, spr, x, y, esc, rot=-3, sombra=True)


def e_gancho(t, d):
    c = noche(t)
    big_ear(c, 540, 1330, 1.0)
    ondas(c, 540, 300, t * 1.3, VERDE, 5, 900, 12, (40, 140))
    texto(c, "1977", 540, 1700, t - 0.1, 150, "#78FFAA")
    return c, dict(zoom=1.0 + 0.12 * ease_out(t / d), temblor=6 if t < 0.25 else 0, t=t)


def e_nunca(t, d):
    c = noche(t)
    big_ear(c, 540, 1330, 1.0)
    sello(c, "NUNCA MÁS", t - 0.15, "#FF4D6D", 1000, 150)
    return c, dict(zoom=1.05, temblor=8 if 0.15 < t < 0.4 else 0, t=t)


def e_fecha(t, d):
    c = noche(t)
    pegar(c, calendario("15", "AGOSTO", "1977"), 540, 1000, pop_scale(t - 0.05) * 1.3, sombra=True)
    texto(c, "OHIO, EE. UU.", 540, 1560, t - 0.3, 100, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_oreja(t, d):
    c = noche(t)
    big_ear(c, 540, 1330, 1.0)
    m = Image.new("L", (300, 420), 0)
    dm = ImageDraw.Draw(m)
    dm.ellipse([0, 0, 300, 420], fill=255)
    dm.ellipse([90, 90, 230, 330], fill=0)
    dm.rectangle([0, 200, 140, 420], fill=255)
    texto(c, "BIG EAR =\nGRAN OREJA", 540, 1700, t - 0.3, 95, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def e_alguien(t, d):
    c = cielo_estrellas(t, "#03060F", "#14203A")
    pegar(c, planeta("#6A4FB0", 160, "#9D85E0", 310), 760, 760, 1.0)
    ondas(c, 760, 760, t, VERDE, 4, 600, 10, (100, 260))
    pegar(c, planeta("#2F7FD1", 220, "#5BAA4E", 311), 260, 1500, 1.0)
    texto(c, "¿HAY ALGUIEN?", 540, 1180, t - 0.2, 110, "#78FFAA")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_ehman(t, d):
    c = degradado(W, H, [(0, "#2A2238"), (1, "#4A3A55")])
    particulas(c, t, 20, (255, 230, 200), 2, (2, 4), 8, 90)
    img, dd = capa()
    dd.rectangle([0, 1450, W, H], fill=(110, 75, 50, 255))
    c.alpha_composite(img)
    pegar(c, nico(t, "normal", 60, 60), 540, 1780, 1.05, ancla="abajo")
    impresion(c, 540, 1640, 0.42, t)
    texto(c, "JERRY EHMAN", 540, 800, t - 0.15, 100, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_6equj5(t, d):
    c = degradado(W, H, [(0, "#2A2238"), (1, "#4A3A55")])
    impresion(c, 540, 1100, 1.25, t, resaltar=clamp01((t - 0.3) / 0.6))
    if t > 1.2:
        tag(c, "6EQUJ5", "", 540, 1680, t - 1.2, 120)
    return c, dict(zoom=1.0 + 0.25 * ease_in_out(t / d), fy=0.55, t=t)


def e_wow(t, d):
    c = degradado(W, H, [(0, "#2A2238"), (1, "#4A3A55")])
    impresion(c, 540, 1100, 1.25, t, resaltar=1.0, circulo=clamp01(t / 0.8))
    if t > 0.8:
        hud(rotulo("Wow!", 190, "#DC1E28", "#FFFFFF", 10, rot=12), 740, 900, pop_scale(t - 0.8))
    return c, dict(zoom=1.2, fy=0.55, temblor=8 if 0.8 < t < 1.0 else 0, t=t)


def e_72(t, d):
    c = noche(t)
    big_ear(c, 540, 1330, 0.9)
    img, dd = capa()
    dd.polygon([(500, 1200), (580, 1200), (700, 0), (380, 0)], fill=(120, 255, 170, 35))
    c.alpha_composite(img)
    u = clamp01(t / d)
    pegar(c, brillo(70, "#78FFAA", 1.0), -100 + u * 1280, 500, 1)
    n = int(72 * u)
    hud(etiqueta(f"{n}", "s", 150), 540, 1650, 1, True)
    return c, dict(zoom=1.0, t=t)


def e_hidrogeno(t, d):
    c = cielo_estrellas(t, "#03060F", "#14203A")
    img, dd = capa()
    dd.arc([190, 700, 890, 1400], 180, 360, fill=(255, 255, 255, 255), width=14)
    for k in range(0, 181, 15):
        a = math.radians(180 + k)
        dd.line([(540 + math.cos(a) * 330, 1050 + math.sin(a) * 330), (540 + math.cos(a) * 300, 1050 + math.sin(a) * 300)], fill=(255, 255, 255, 255), width=6)
    ang = math.radians(180 + 120 + 6 * math.sin(t * 3) * (1 - clamp01(t / 0.8)))
    dd.line([(540, 1050), (540 + math.cos(ang) * 290, 1050 + math.sin(ang) * 290)], fill=(255, 77, 109, 255), width=14)
    dd.ellipse([520, 1030, 560, 1070], fill=(255, 255, 255, 255))
    c.alpha_composite(img)
    tag(c, "1420", "MHz", 540, 1250, t - 0.3, 120)
    texto(c, "HIDRÓGENO", 540, 1500, t - 0.5, 115, "#78FFAA")
    return c, dict(zoom=1.0, t=t)


def e_buscan(t, d):
    c = noche(t)
    big_ear(c, 540, 1330, 0.9)
    ondas(c, 540, 1150, t, (160, 200, 255), 3, 900, 8, (190, 350))
    sello(c, "NO SE REPITIÓ", t - 0.6, "#FF4D6D", 800, 120, -8)
    return c, dict(zoom=1.0 + 0.03 * t, t=t)


def e_giro(t, d):
    c = degradado(W, H, [(0, "#2A2238"), (1, "#4A3A55")])
    impresion(c, 540, 1100, 1.25, 0.0, resaltar=1.0, circulo=1.0)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.45)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def nube_h(c, x, y, esc, intensidad, t):
    rng = random.Random(4)
    for k in range(14):
        dx, dy, r = rng.uniform(-260, 260), rng.uniform(-160, 160), rng.uniform(90, 170)
        pegar(c, brillo(r * esc, mezcla(hexrgb("#3A5FB0"), hexrgb("#9FF0FF"), intensidad), 0.35 + 0.5 * intensidad),
              x + dx * esc + math.sin(t + k) * 8, y + dy * esc)


def e_nube(t, d):
    c = cielo_estrellas(t, "#03060F", "#14203A")
    nube_h(c, 540, 950, 1.1, 0.15, t)
    texto(c, "NUBE DE HIDRÓGENO", 540, 1560, t - 0.2, 95, "#9FF0FF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_magnetar(t, d):
    c = cielo_estrellas(t, "#03060F", "#14203A")
    fl = clamp01((t - 0.4) / 0.3)
    nube_h(c, 650, 1150, 0.9, fl, t)
    img, dd = capa()
    for k in range(5):  # líneas de campo magnético
        r = 60 + k * 35
        dd.ellipse([250 - r * 0.6, 600 - r, 250 + r * 0.6, 600 + r], outline=(200, 160, 255, 140), width=5)
    c.alpha_composite(img)
    pegar(c, brillo(90 + fl * 200, "#E0C8FF", 0.9), 250, 600)
    if fl > 0:
        img, dd = capa()
        dd.line([(250, 600), (650, 1150)], fill=(255, 255, 255, int(220 * (1 - abs(fl - 0.5) * 2) + 30)), width=int(10 + 20 * fl))
        c.alpha_composite(img)
    texto(c, "MAGNETAR", 540, 1650, t - 0.5, 120, "#E0C8FF")
    return c, dict(zoom=1.0, temblor=8 if 0.4 < t < 0.6 else 0, t=t)


def e_hipotesis(t, d):
    c = cielo_estrellas(t, "#03060F", "#14203A")
    pegar(c, rotulo("?", 600, "#78FFAA", "#0A2A1A", 20), 540, 950, 1 + 0.05 * math.sin(t * 4))
    sello(c, "HIPÓTESIS", t - 0.1, "#FFD400", 1450, 130, -6)
    texto(c, "MISTERIO ABIERTO", 540, 1700, t - 0.9, 95, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_cta(t, d):
    c = noche(t)
    big_ear(c, 760, 1400, 0.45)
    pegar(c, nico(t, "esceptico", 10, 140 + 25 * math.sin(t * 10)), 330, 1820, 0.95, ancla="abajo")
    globo_texto(c, "¿TÚ QUÉ CREES\nQUE FUE?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto", "riser_suave"]), (0, 0.6, e_nunca, None, [("buzz", 0.15)]),
    (1, 0.0, e_fecha, "barrido", ["whoosh", ("pop", 0.05)]), (1, 0.55, e_oreja, None, [("pop", 0.2)]),
    (2, 0.0, e_alguien, None, ["blip"]),
    (3, 0.0, e_ehman, "barrido", ["whoosh"]),
    (4, 0.0, e_6equj5, None, ["tictac", ("impacto", 1.2)]),
    (5, 0.0, e_wow, None, ["squish", ("ding", 0.8)]),
    (6, 0.0, e_72, "barrido", ["whoosh", "tictac"]),
    (7, 0.0, e_hidrogeno, None, [("pop", 0.3), ("blip", 0.5)]),
    (8, 0.0, e_buscan, None, ["riser_suave", ("buzz", 0.6)]),
    (9, 0.0, e_giro, None, ["scratch"]),
    (10, 0.0, e_nube, None, ["whoosh_grave"]), (10, 0.45, e_magnetar, None, [("impacto", 0.4)]),
    (11, 0.0, e_hipotesis, None, [("pop", 0.1), ("pop", 0.9)]),
    (12, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]
ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
