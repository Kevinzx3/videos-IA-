"""Día 06 · Video B (misterio): Mary Celeste, el barco que apareció sin tripulación."""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-06/datos/02-misterio-mary-celeste.json"


def mar_niebla(t, sup=1150):
    c = degradado(W, H, [(0, "#3A4A5A"), (0.55, "#8A9AA8"), (0.6, "#2A4A5A"), (1, "#0E2230")])
    img, d = capa()
    for k in range(6):
        y = sup + 30 + k * 120
        d.line([(x, y + math.sin(x / 70 + t * 2 + k) * 14) for x in range(0, W + 20, 20)], fill=(160, 190, 200, 90), width=8)
    d.line([(x, sup + math.sin(x / 80 + t * 2) * 12) for x in range(0, W + 20, 20)], fill=(220, 230, 235, 200), width=8)
    c.alpha_composite(img)
    return c


def niebla(c, t, alfa=110):
    img, d = capa()
    for k in range(6):
        x = (k * 260 + t * 30) % (W + 600) - 300
        d.ellipse([x - 300, 900 + k * 60, x + 300, 1150 + k * 60], fill=(220, 225, 230, alfa))
    c.alpha_composite(img.filter(ImageFilter.GaussianBlur(40)))


@lru_cache(maxsize=4)
def velero(bote=True):
    img = Image.new("RGBA", (760, 820), (0, 0, 0, 0))
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    d.polygon([(40, 600), (720, 600), (640, 760), (120, 760)], fill=255)
    img.alpha_composite(sprite(m, "#5A3A28", 850))
    dd = ImageDraw.Draw(img)
    for x in (300, 500):
        dd.rectangle([x - 8, 80, x + 8, 610], fill=(70, 50, 35, 255))
    for x, ancho in ((300, 210), (500, 180)):
        for k, y in enumerate((120, 300, 450)):
            ms = Image.new("L", img.size, 0)
            ImageDraw.Draw(ms).polygon([(x - ancho + k * 20, y), (x + ancho - k * 20, y), (x + ancho - k * 10, y + 140), (x - ancho + k * 10, y + 140)], fill=255)
            img.alpha_composite(sprite(ms, "#E8E2D0", 851 + k))
    if bote:
        mb = Image.new("L", img.size, 0)
        ImageDraw.Draw(mb).chord([520, 540, 700, 620], 0, 180, fill=255)
        img.alpha_composite(sprite(mb, "#B04A3A", 855))
    return img


def barril(c, x, y, esc, vacio=False):
    m = Image.new("L", (160, 200), 0)
    ImageDraw.Draw(m).rounded_rectangle([10, 0, 150, 200], radius=50, fill=255)
    spr = sprite(m, "#9A6A40" if not vacio else "#B88A60", 860 + vacio)
    dd = ImageDraw.Draw(spr)
    for ya in (40, 160):
        dd.line([(12, ya), (148, ya)], fill=(60, 60, 70, 255), width=10)
    pegar(c, spr, x, y, esc)


def e_gancho(t, d):
    c = mar_niebla(t)
    pegar(c, velero(), 540, 920 + math.sin(t * 1.5) * 12, 0.9, rot=math.sin(t) * 3)
    niebla(c, t)
    texto(c, "1872", 540, 1650, t - 0.1, 150, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.12 * ease_out(t / d), temblor=5 if t < 0.25 else 0, t=t)


def e_sin_nadie(t, d):
    c = mar_niebla(t)
    pegar(c, velero(), 540, 920 + math.sin(t * 1.5) * 12, 0.9, rot=math.sin(t) * 3)
    niebla(c, t, 140)
    texto(c, "SIN NADIE\nA BORDO", 540, 1650, t - 0.1, 115, "#FF4D6D")
    return c, dict(zoom=1.1, t=t)


def e_dei_gratia(t, d):
    c = mar_niebla(t)
    pegar(c, velero(), 760, 980, 0.5)
    pegar(c, velero(), 220 + t * 30, 1000, 0.6)
    hud(rotulo("DEI GRATIA", 50, "#FFD400"), 230 + t * 30, 760, 1)
    hud(rotulo("MARY CELESTE", 50, "#FFFFFF"), 760, 800, 1)
    texto(c, "CERCA DE LAS AZORES", 540, 1650, t - 0.3, 90, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def cubierta(t):
    c = degradado(W, H, [(0, "#6A7A88"), (0.4, "#A8B4BE"), (0.41, "#7A5238"), (1, "#4A3020")])
    img, d = capa()
    for y in range(800, H, 70):
        d.line([(0, y), (W, y)], fill=(50, 32, 20, 160), width=5)
    d.rectangle([0, 760, W, 800], fill=(60, 40, 28, 255))
    c.alpha_composite(img)
    return c


def e_nadie(t, d):
    c = cubierta(t)
    pegar(c, nico(t, "sorpresa", 30, 150), 540, 1900, 1.0, ancla="abajo")
    texto(c, "¿HOLA?", 540, 820, t - 0.2, 140, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.05 * t, t=t)


def e_diez(t, d):
    c = mar_niebla(t)
    for k in range(10):
        a = clamp01(1 - (t - 0.3 - k * 0.12) / 0.4)
        sil = nico(0, "normal", 10, -10)
        s2 = Image.new("RGBA", sil.size, (20, 30, 40, 0))
        s2.putalpha(sil.getchannel("A").point(lambda v: int(v * 0.85)))
        pegar(c, s2, 120 + (k % 5) * 210, 1100 + (k // 5) * 380, 0.38, alfa=a, ancla="abajo")
    tag(c, "10", "PERSONAS", 540, 1650, t - 0.2, 140)
    return c, dict(zoom=1.0, t=t)


def e_comida(t, d):
    c = cubierta(t)
    for k in range(4):
        barril(c, 240 + k * 200, 1300, 0.9)
    texto(c, "COMIDA Y AGUA\nPARA MESES", 540, 850, t - 0.2, 100, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_barriles(t, d):
    c = degradado(W, H, [(0, "#2A1C10"), (1, "#4A3020")])
    for fila in range(4):
        for col in range(6):
            barril(c, 130 + col * 165, 760 + fila * 200, 0.75 * pop_scale(t - (fila * 6 + col) * 0.03))
    tag(c, "≈1700", "BARRILES DE ALCOHOL", 540, 1650, t - 0.6, 110)
    return c, dict(zoom=1.0, t=t)


def e_bote(t, d):
    c = mar_niebla(t)
    pegar(c, velero(False), 540, 920, 1.1)
    img, dd = capa()
    u = clamp01((t - 0.2) / 0.3)
    dd.ellipse([780 - 80 * u, 810 - 50 * u, 780 + 80 * u, 810 + 50 * u], outline=(255, 77, 109, 255), width=10)
    c.alpha_composite(img)
    texto(c, "FALTA EL BOTE", 540, 1650, t - 0.3, 120, "#FF4D6D")
    return c, dict(zoom=1.15, fx=0.6, fy=0.45, t=t)


def e_giro(t, d):
    c = mar_niebla(0.0)
    pegar(c, velero(), 540, 920, 0.9)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def e_vacios(t, d):
    c = degradado(W, H, [(0, "#2A1C10"), (1, "#4A3020")])
    for k in range(9):
        barril(c, 160 + (k % 5) * 190, 900 + (k // 5) * 260, 0.85, vacio=True)
    for k in range(8):
        ph = (t * 0.6 + k / 8) % 1
        pegar(c, brillo(50, "#E8F0D8", 0.4 * (1 - ph)), 200 + k * 100, 1000 - ph * 400)
    tag(c, "9", "BARRILES VACÍOS", 540, 1650, t - 0.2, 130)
    return c, dict(zoom=1.0, t=t)


def e_huyen(t, d):
    c = mar_niebla(t)
    pegar(c, velero(False), 760, 900, 0.7)
    u = clamp01(t / d)
    m = Image.new("L", (260, 110), 0)
    ImageDraw.Draw(m).chord([0, 0, 260, 110], 0, 180, fill=255)
    pegar(c, sprite(m, "#B04A3A", 870), 400 - u * 300, 1250, 1.0)
    niebla(c, t, int(80 + 120 * u))
    texto(c, "¿HUYERON AL BOTE?", 540, 1700, t - 0.2, 100, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_doyle(t, d):
    c = degradado(W, H, [(0, "#2A1C10"), (1, "#5A3A20")])
    m = Image.new("L", (540, 720), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 540, 720], radius=20, fill=255)
    libro = sprite(m, "#2E4A6A", 880)
    r = rotulo("CUENTO\n1884", 80, "#FFD400", "#1A1022", 4)
    libro.alpha_composite(r, (270 - r.width // 2, 220 - r.height // 2))
    r = rotulo("A. CONAN\nDOYLE", 60, "#FFFFFF", "#1A1022", 4)
    libro.alpha_composite(r, (270 - r.width // 2, 520 - r.height // 2))
    pegar(c, libro, 540, 1080, pop_scale(t - 0.05) * 0.9, rot=-4, sombra=True)
    texto(c, "LEYENDA INVENTADA", 540, 1700, t - 0.5, 100, "#FFD400")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_cta(t, d):
    c = mar_niebla(t)
    pegar(c, velero(), 820, 1250, 0.35)
    pegar(c, nico(t, "esceptico", 10, 140 + 25 * math.sin(t * 10)), 330, 1880, 0.95, ancla="abajo")
    globo_texto(c, "¿TÚ QUÉ CREES\nQUE PASÓ?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto", "ola", "riser_suave"]), (0, 0.6, e_sin_nadie, None, [("buzz", 0.1)]),
    (1, 0.0, e_dei_gratia, "barrido", ["whoosh", "ola"]),
    (2, 0.0, e_nadie, None, ["squish", ("blip", 0.2)]),
    (3, 0.0, e_diez, None, ["whoosh_suave", ("pop", 0.2)]),
    (4, 0.0, e_comida, "barrido", ["whoosh", ("pop", 0.2)]),
    (5, 0.0, e_barriles, None, ["pop3", ("pop", 0.6)]),
    (6, 0.0, e_bote, None, [("buzz", 0.3)]),
    (7, 0.0, e_giro, None, ["scratch"]),
    (8, 0.0, e_vacios, None, [("pop", 0.2), "burbujas"]), (8, 0.5, e_huyen, None, ["whoosh", "ola"]),
    (9, 0.0, e_doyle, "barrido", ["whoosh", ("pop", 0.05), ("ding", 0.5)]),
    (10, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]
ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
