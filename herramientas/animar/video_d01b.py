"""Día 01 · Video B: Qué hacer si el mar te arrastra (corriente de resaca)."""
import json
import math
import random
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw

from motor import *  # noqa
from motor import _comp

RAIZ = Path(__file__).resolve().parents[2]
GUION = RAIZ / "dia-01/datos/02-corriente-de-resaca.json"
ORIG = [0, 3.4, 5.8, 9.2, 12.2, 17.0, 19.6, 20.8, 23.0, 24.2, 29.0, 30.2, 33.2, 37.0, 40.6, 44.2, 46.0, 49.4, 52.6, 55.6, 59.0]
_seg = json.load(open(GUION, encoding="utf-8"))["segmentos"]
NUEVO = [s[0] for s in _seg] + [_seg[-1][1]]
DURACION = NUEVO[-1]


def remap(t):
    for i in range(len(ORIG) - 1):
        if t <= ORIG[i + 1]:
            u = (t - ORIG[i]) / (ORIG[i + 1] - ORIG[i])
            return NUEVO[i] + u * (NUEVO[i + 1] - NUEVO[i])
    return NUEVO[-1]


TRAJE = "#3DB2E0"
AGUA = "#1F6F8B"
AGUA_OSC = "#0E3A4F"
ESPUMA = (232, 244, 242)
ARENA = "#E2C58F"


# ------------------------------------------------------------------ helpers
def texto(c, txt, x, y, tl, tam=120, color="#FFFFFF", rot=0):
    s = pop_scale(tl)
    if s > 0:
        hud(rotulo(txt, tam, color, rot=rot), x, y, s)


def tag(c, val, uni, x, y, tl, tam=130):
    s = pop_scale(tl)
    if s > 0:
        hud(etiqueta(val, uni, tam), x, y, s, True)


def chispa_en(c, t, x, y, tam=1.0):
    pegar(c, chispa(t, tam), x, y + math.sin(t * 4) * 12)


@lru_cache(maxsize=2)
def cielo_mar():
    return degradado(W, H, [(0, "#1B2A4A"), (0.35, "#3E7CB1"), (0.6, "#F6C28B"), (1, "#F6C28B")])


def mar_lateral(t, superficie=1150, costa=True):
    """Vista lateral: cielo, playa al fondo, mar con olas animadas."""
    c = cielo_mar().copy()
    particulas(c, t, 20, (255, 240, 210), 2, (2, 4), 8, 100)
    if costa:
        m = Image.new("L", (W, 200), 0)
        ImageDraw.Draw(m).ellipse([-200, 60, W + 200, 400], fill=255)
        pegar(c, sprite(m, ARENA, 120, costura=False), W / 2, superficie - 40)
        pegar(c, prop("torre"), 820, superficie - 120, 0.45)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    pts = [(x, superficie + math.sin(x / 70 + t * 3) * 14) for x in range(0, W + 20, 20)]
    d.polygon(pts + [(W, H), (0, H)], fill=hexrgb(AGUA) + (255,))
    for k in range(6):
        y = superficie + 80 + k * 120
        d.line([(x, y + math.sin(x / 90 + t * 2 + k) * 10) for x in range(0, W + 20, 20)], fill=(120, 200, 220, 70), width=6)
    d.line(pts, fill=ESPUMA + (255,), width=10)
    c.alpha_composite(capa)
    return c


def agua_delante(c, t, superficie, alfa=150):
    """Capa de agua semitransparente por delante (para cuerpos sumergidos)."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    pts = [(x, superficie + math.sin(x / 70 + t * 3) * 14) for x in range(0, W + 20, 20)]
    d.polygon(pts + [(W, H), (0, H)], fill=hexrgb(AGUA) + (alfa,))
    d.line(pts, fill=ESPUMA + (255,), width=10)
    c.alpha_composite(capa)


def nico_nadando(c, t, x, sup, esc=0.8, expr="sorpresa", brazos=(150, 150), agitado=0):
    bi, bd = brazos
    if agitado:
        bi += math.sin(t * 22) * agitado
        bd += math.sin(t * 22 + 1.5) * agitado
    spr = nico(t, expr, bi, bd, traje=TRAJE)
    pegar(c, spr, x, sup + 420 * esc + math.sin(t * 3) * 8, esc, ancla="abajo")
    agua_delante(c, t, sup)


@lru_cache(maxsize=4)
def _cenital_base(canal=True):
    c = Image.new("RGBA", (W, H))
    agua = degradado(W, H, [(0, "#0E4A66"), (0.6, "#1F6F8B"), (0.78, "#3FA6B8"), (1, "#3FA6B8")])
    c.alpha_composite(agua)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(0, 1500), (W, 1460), (W, H), (0, H)], fill=255)
    c.alpha_composite(sprite(m, ARENA, 121, costura=False, grano=0.25))
    if canal:
        m2 = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m2).polygon([(470, 1480), (610, 1480), (650, 500), (430, 500)], fill=255)
        from PIL import ImageFilter
        m2 = m2.filter(ImageFilter.GaussianBlur(25))
        oscuro = Image.new("RGBA", (W, H), hexrgb(AGUA_OSC) + (0,))
        oscuro.putalpha(m2.point(lambda v: int(v * 0.8)))
        c.alpha_composite(oscuro)
    return c


def mar_cenital(t, canal=True, flechas=True):
    """Vista desde arriba: arena abajo, rompientes de espuma con hueco en el canal."""
    c = _cenital_base(canal).copy()
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for k in range(4):  # líneas de espuma que avanzan hacia la orilla
        y0 = 950 + ((t * 90 + k * 140) % 560)
        for x in range(0, W, 14):
            if canal and 400 < x < 680:
                continue
            y = y0 + math.sin(x / 60 + k) * 18
            d.ellipse([x - 12, y - 7, x + 12, y + 7], fill=ESPUMA + (200,))
    if canal and flechas:
        for k in range(5):
            ph = (t * 0.6 + k / 5) % 1
            y = 1450 - ph * 900
            d.polygon([(540, y - 40), (510, y + 10), (570, y + 10)], fill=(255, 255, 255, int(200 * (1 - ph))))
            d.rectangle([530, y + 10, 550, y + 50], fill=(255, 255, 255, int(200 * (1 - ph))))
    c.alpha_composite(capa)
    particulas(c, t, 25, (255, 255, 255), 5, (2, 4), 6, 90)
    return c


@lru_cache(maxsize=4)
def cabeza_nico(expr="sorpresa"):
    """Nico visto desde arriba: solo cabeza y hombros (para vistas cenitales)."""
    spr = nico(0.3, expr, 120, 120, traje=TRAJE)
    return spr.crop((60, 0, 500, 470))


def nadador_cenital(c, t, x, y, esc=0.45, expr="sorpresa", rot=0):
    s = cabeza_nico(expr)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = 130 * esc * 2
    d.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.9], fill=ESPUMA + (90,))
    c.alpha_composite(capa)
    pegar(c, s, x, y, esc, rot=rot)


def flecha_plana(c, x0, y0, x1, y1, color, ancho=36, alfa=255):
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    col = hexrgb(color) + (alfa,)
    ang = math.atan2(y1 - y0, x1 - x0)
    xb, yb = x1 - math.cos(ang) * ancho * 1.6, y1 - math.sin(ang) * ancho * 1.6
    d.line([(x0, y0), (xb, yb)], fill=col, width=ancho)
    px, py = -math.sin(ang), math.cos(ang)
    d.polygon([(x1, y1), (xb + px * ancho * 1.4, yb + py * ancho * 1.4), (xb - px * ancho * 1.4, yb - py * ancho * 1.4)], fill=col)
    c.alpha_composite(capa)


def cruz(c, x, y, tam, u):
    if u <= 0:
        return
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    s = tam * back_out(u)
    for a, b in (((-1, -1), (1, 1)), ((-1, 1), (1, -1))):
        d.line([(x + a[0] * s, y + a[1] * s), (x + b[0] * s, y + b[1] * s)], fill=(255, 77, 109, 255), width=int(tam * 0.35))
    c.alpha_composite(capa)


def tarjeta_paso(t, n):
    c = degradado(W, H, [(0, "#FFD400"), (1, "#FFB000")])
    pegar(c, brillo(420, "#FFFFFF", 0.35), W / 2, H / 2)
    s = pop_scale(t, 0.3)
    hud(rotulo("PASO", 130, "#3A2A20", "#FFFFFF", 8), 540, 820, s)
    hud(rotulo(str(n), 520, "#FFFFFF", "#3A2A20", 22), 540 + (1 - ease_out(t / 0.3)) * 600, 1220, 1)
    chispa_en(c, t, 540 + (1 - ease_out(t / 0.3)) * 600 + 260, 1300, 0.9)
    return c, dict(zoom=1.0 + 0.05 * t, t=t)


def barra_energia(c, x, y, nivel, ancho=420):
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.rounded_rectangle([x - ancho / 2, y, x + ancho / 2, y + 90], radius=22, fill=(30, 20, 40, 230), outline=(255, 255, 255, 255), width=6)
    d.rectangle([x + ancho / 2, y + 25, x + ancho / 2 + 20, y + 65], fill=(255, 255, 255, 255))
    col = (90, 220, 120) if nivel > 0.5 else (255, 200, 0) if nivel > 0.25 else (255, 77, 109)
    if nivel > 0.01:
        d.rounded_rectangle([x - ancho / 2 + 12, y + 12, x - ancho / 2 + 12 + (ancho - 24) * nivel, y + 78], radius=14, fill=col + (255,))
    c.alpha_composite(capa)


# --------------------------------------------------------------- props mar
def _prop_torre():
    img = Image.new("RGBA", (500, 700), (0, 0, 0, 0))
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    for x0 in (80, 380):
        d.rectangle([x0, 300, x0 + 40, 700], fill=255)
    d.rectangle([60, 300, 440, 340], fill=255)
    img.alpha_composite(sprite(m, "#E8E2D0", 122))
    m2 = Image.new("L", img.size, 0)
    ImageDraw.Draw(m2).rounded_rectangle([90, 120, 410, 310], radius=20, fill=255)
    img.alpha_composite(sprite(m2, "#FF4D6D", 123))
    m3 = Image.new("L", img.size, 0)
    ImageDraw.Draw(m3).polygon([(40, 130), (250, 20), (460, 130)], fill=255)
    img.alpha_composite(sprite(m3, "#FFFFFF", 124))
    ImageDraw.Draw(img).line([(250, 150), (250, 280)], fill=(255, 255, 255, 255), width=20)
    ImageDraw.Draw(img).line([(185, 215), (315, 215)], fill=(255, 255, 255, 255), width=20)
    return img


def _prop_flotador():
    m = Image.new("L", (300, 300), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([10, 10, 290, 290], fill=255)
    d.ellipse([90, 90, 210, 210], fill=0)
    spr = sprite(m, "#FF4D6D", 125)
    dd = ImageDraw.Draw(spr)
    for a in (0, 90, 180, 270):
        dd.pieslice([10, 10, 290, 290], a + 20, a + 50, fill=(255, 255, 255, 255))
    dd.ellipse([90, 90, 210, 210], fill=(0, 0, 0, 0))
    return spr


def _prop_nadador_olimpico():
    m = Image.new("L", (700, 220), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([480, 60, 620, 180], fill=255)
    d.rounded_rectangle([140, 90, 520, 170], radius=40, fill=255)
    d.line([(520, 110), (660, 40)], fill=255, width=40)
    d.line([(160, 130), (20, 110)], fill=255, width=36)
    spr = sprite(m, "#F2C29B", 126)
    dd = ImageDraw.Draw(spr)
    dd.chord([470, 50, 630, 190], 180, 360, fill=(255, 212, 0, 255))
    dd.rounded_rectangle([540, 100, 600, 125], radius=10, fill=(40, 40, 60, 255))
    return spr


def _prop_marcador():
    m = Image.new("L", (520, 640), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 520, 640], radius=40, fill=255)
    return sprite(m, "#FFFFFF", 127, color_costura=(200, 200, 210))


for _n, _f in list(globals().items()):
    if _n.startswith("_prop_"):
        import motor
        setattr(motor, _n, _f)


# ------------------------------------------------------------------ escenas
SUP = 1150


def e01(t, d):  # Nico flota mar adentro, la playa se aleja
    c = mar_lateral(t, SUP)
    nico_nadando(c, t, 540, SUP, 0.85, "sorpresa", (150, 150), 25)
    texto(c, "¿TE ARRASTRA?", 540, 1500, t - 0.05, 120)
    return c, dict(zoom=1.0 + 0.2 * ease_out(t / d), fx=0.5, fy=0.5, temblor=6 if t < 0.25 else 0, t=t)


def e02(t, d):  # nada como loco hacia la orilla sin avanzar
    c = mar_lateral(t, SUP)
    nico_nadando(c, t, 540, SUP, 1.1, "espiral", (170, 170), 60)
    for k in range(8):
        ph = (t * 3 + k / 8) % 1
        a = k / 8 * math.pi + math.pi
        pegar(c, prop("gota"), 540 + math.cos(a) * 300 * ph, SUP - math.sin(-a) * 250 * ph - 50, 0.8, alfa=1 - ph)
    return c, dict(zoom=1.5, fx=0.5, fy=0.45, temblor=4, t=t)


def e03(t, d):  # flecha a la orilla con X
    c = mar_cenital(t, True, False)
    nadador_cenital(c, t, 540, 820, 0.45)
    flecha_plana(c, 540, 930, 540, 1400, "#FF4D6D", 40)
    cruz(c, 540, 1170, 130, (t - 0.3) / 0.3)
    texto(c, "NO A LA ORILLA", 540, 1650, t - 0.35, 100, "#FF4D6D")
    return c, dict(zoom=1.05, t=t)


def e04(t, d):  # Chispa lo detiene tirando del pompón
    c = mar_lateral(t, SUP)
    nico_nadando(c, t, 540, SUP, 1.1, "sorpresa", (40, 40))
    chispa_en(c, t, 1100 - ease_out(t / 0.5) * 560, 330, 1.0)
    return c, dict(zoom=1.6, fx=0.5, fy=0.38, t=t)


def e05(t, d):  # vista cenital alta: el canal oscuro
    c = mar_cenital(t)
    return c, dict(zoom=1.15 - 0.1 * t / d, fx=0.5, fy=0.55, t=t)


def e06(t, d):  # el canal se ilumina
    c = mar_cenital(t)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = int(255 * clamp01(t / 0.3))
    dd = ImageDraw.Draw(capa)
    for k in range(0, 60, 2):  # contorno discontinuo amarillo (cosido)
        y0 = 500 + k * 16.5
        dd.line([(430 + (k * 16.5) / 980 * 40, y0), (430 + ((k + 1) * 16.5) / 980 * 40, y0 + 16)], fill=(255, 212, 0, a), width=10)
        dd.line([(650 - (k * 16.5) / 980 * 40, y0), (650 - ((k + 1) * 16.5) / 980 * 40, y0 + 16)], fill=(255, 212, 0, a), width=10)
    c.alpha_composite(capa)
    texto(c, "CORRIENTE\nDE RESACA", 540, 1650, t - 0.2, 105, "#FFD400")
    return c, dict(zoom=1.1, fx=0.5, fy=0.55, t=t)


def diorama(t, flechas_a_playa=True, agitadas=False):
    c = cielo_mar().copy()
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.polygon([(0, 900), (W, 900), (W, H), (0, H)], fill=hexrgb(AGUA) + (255,))
    d.polygon([(600, 900), (W, 760), (W, H), (300, H)], fill=hexrgb(ARENA) + (255,))
    c.alpha_composite(capa)
    for k in range(3):  # olas de fieltro
        ph = (t * 0.5 + k / 3) % 1
        x = 80 + ph * 520
        m = Image.new("L", (200, 160), 0)
        ImageDraw.Draw(m).pieslice([0, 0, 200, 320], 180, 360, fill=255)
        pegar(c, sprite(m, "#3FA6B8", 130 + k), x, 880, 1.0, alfa=1 - ph * 0.6)
    if flechas_a_playa:
        for k in range(3):
            ph = (t * 0.8 + k / 3) % 1
            flecha_plana(c, 60 + ph * 380, 1000 + k * 120, 200 + ph * 380, 1000 + k * 120, "#FFFFFF", 22, int(220 * (1 - ph)))
    if agitadas:
        for k in range(4):
            yy = 1050 + k * 90
            dx = math.sin(t * 9 + k) * 40
            flecha_plana(c, 560 + dx, yy, 400 + dx, yy, "#FFFFFF", 22, 230)
    return c


def e07(t, d):
    c = diorama(t, True)
    return c, dict(zoom=1.05 + 0.03 * t, t=t)


def e08(t, d):
    c = diorama(t, False, True)
    texto(c, "TIENE QUE\nVOLVER", 540, 1650, t - 0.15, 115, "#FFD400")
    return c, dict(zoom=1.05, t=t)


def e09(t, d):  # flechas confluyen en el canal
    c = mar_cenital(t)
    u = ease_out(t / 0.8)
    for s in (-1, 1):
        for k in range(2):
            x0 = 540 + s * (380 - k * 120)
            flecha_plana(c, x0, 1400, 540 + s * 40 + (x0 - 540) * (1 - u) * 0.3, 1400 - 260 * u, "#FFFFFF", 22, 200)
    return c, dict(zoom=1.1, fx=0.5, fy=0.62, t=t)


def e10(t, d):  # match cut: canal -> río con orillas de hierba
    c = mar_cenital(t)
    u = ease_in_out(t / 0.5)
    if u > 0:
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(capa)
        a = int(255 * u)
        dd.polygon([(0, 500), (420, 500), (460, 1480), (0, 1480)], fill=(110, 138, 46, a))
        dd.polygon([(W, 500), (660, 500), (620, 1480), (W, 1480)], fill=(110, 138, 46, a))
        c.alpha_composite(capa)
    texto(c, "= RÍO EN EL MAR", 540, 1680, t - 0.4, 100, "#FFFFFF")
    return c, dict(zoom=1.05, t=t)


def carrera(t, adelanta=0.0):
    c = mar_lateral(t, 900, False)
    for k in range(6):  # corriente: flechas veloces
        ph = (t * 1.6 + k / 6) % 1
        flecha_plana(c, -200 + ph * 1500, 1250 + (k % 3) * 160, -40 + ph * 1500, 1250 + (k % 3) * 160, "#FFFFFF", 26, 200)
    pegar(c, prop("nadador_olimpico"), 520 - adelanta * 260 + math.sin(t * 8) * 10, 960, 1.0)
    agua_delante(c, t, 900, 90)
    return c


def e11(t, d):
    return carrera(t, ease_in_out(t / d) * 0.5), dict(zoom=1.05, t=t)


def e12(t, d):
    c = carrera(t, 0.5)
    chispa_en(c, t, 1150 - ease_out(t / 0.4) * 400, 700)
    tag(c, "≈ 2,4", "m/s", 540, 1550, t - 0.3, 150)
    return c, dict(zoom=1.0, t=t)


def e13(t, d):
    c = carrera(t, 0.5 + ease_out(t / d) * 0.5)
    texto(c, "MÁS RÁPIDO QUE\nUN OLÍMPICO", 540, 1580, t - 0.1, 90, "#FFD400")
    return c, dict(zoom=1.0, temblor=6 if t < 0.25 else 0, t=t)


def e14(t, d):  # nada contra la corriente, la energía baja
    c = mar_lateral(t, SUP)
    nico_nadando(c, t, 540, SUP, 0.95, "esfuerzo", (160, 160), 40)
    barra_energia(c, 540, 380, 0.9 - 0.6 * clamp01(t / d))
    return c, dict(zoom=1.1, fx=0.5, fy=0.45, t=t)


def e15(t, d):
    c = mar_lateral(t, SUP)
    nico_nadando(c, t, 540, SUP, 1.05, "cansado", (30, 30))
    barra_energia(c, 540, 380, 0.12)
    if int(t * 6) % 2 == 0:
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 40, 60, 40)))
    texto(c, "PELIGRO", 540, 1600, t - 0.1, 140, "#FF4D6D")
    return c, dict(zoom=1.25, fx=0.5, fy=0.45, t=t)


def e16(t, d):
    return tarjeta_paso(t, 1)


def e17(t, d):  # flota en estrella
    c = mar_cenital(t, False)
    pegar(c, nico(t, "feliz", 120, 120, -25, 25, traje=TRAJE), 540, 980 + math.sin(t * 2) * 15, 0.75, rot=math.sin(t) * 4)
    agua_delante(c, t, 1240, 70)
    for k in range(6):
        ph = (t * 0.7 + k / 6) % 1
        pegar(c, brillo(14, "#FFFFFF", 0.9), 420 + k * 50, 1200 - ph * 500, 1, alfa=1 - ph)
    texto(c, "CALMA · FLOTA", 540, 1640, t - 0.2, 105, "#FFFFFF")
    return c, dict(zoom=1.05, t=t)


def e18(t, d):
    return tarjeta_paso(t, 2)


def e19(t, d):  # nada en paralelo
    c = mar_cenital(t)
    u = clamp01(t / d)
    x = 540 + u * 330
    nadador_cenital(c, t, x, 820, 0.42, "esfuerzo", rot=-8)
    flecha_plana(c, 560, 960, 560 + 120 + u * 300, 960, "#5AD27A", 34)
    texto(c, "EN PARALELO", 540, 1650, t - 0.2, 110, "#5AD27A")
    return c, dict(zoom=1.1, fx=0.55, fy=0.5, t=t)


def e20(t, d):  # el canal es estrecho: < 25 m
    c = mar_cenital(t)
    nadador_cenital(c, t, 870, 820, 0.4, "feliz")
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(capa)
    w = ease_out(t / 0.4)
    dd.rounded_rectangle([420, 700, 420 + 240 * w, 760], radius=10, fill=(255, 212, 0, 255))
    for k in range(int(12 * w)):
        dd.line([(430 + k * 20, 700), (430 + k * 20, 725)], fill=(60, 40, 30, 255), width=4)
    c.alpha_composite(capa)
    tag(c, "< 25", "m", 540, 1600, t - 0.3, 150)
    return c, dict(zoom=1.15 - 0.1 * ease_out(t / d), fx=0.5, fy=0.45, t=t)


def e21(t, d):
    return tarjeta_paso(t, 3)


def e22(t, d):  # vuelve en diagonal
    c = mar_cenital(t)
    u = clamp01(t / d)
    nadador_cenital(c, t, 870 + u * 40, 820 + u * 300, 0.4, "feliz")
    flecha_plana(c, 870, 900, 980, 1380, "#5AD27A", 34)
    texto(c, "EN DIAGONAL", 540, 1650, t - 0.2, 110, "#5AD27A")
    return c, dict(zoom=1.1, fx=0.6, fy=0.6, t=t)


def e23(t, d):  # llega a la arena, Chispa lo abanica
    c = degradado(W, H, [(0, "#3E7CB1"), (0.5, "#F6C28B"), (0.62, "#3FA6B8"), (0.7, "#E2C58F"), (1, "#D9B57A")])
    rot = 90
    acostado = nico(t, "feliz", 10, -10, traje=TRAJE).rotate(rot, expand=True, resample=Image.BICUBIC)
    pegar(c, acostado, 540, 1480, 0.7)
    chispa_en(c, t, 330, 1200 + math.sin(t * 12) * 20, 0.9)
    return c, dict(zoom=1.15, fx=0.5, fy=0.7, t=t)


def e24(t, d):
    c = mar_lateral(t, SUP)
    nico_nadando(c, t, 540, SUP, 0.85, "sorpresa", (60, 60))
    texto(c, "¿NO PUEDES\nSALIR?", 540, 1550, t - 0.1, 110, "#FFD400")
    return c, dict(zoom=1.1, t=t)


def e25(t, d):  # levanta el brazo y grita; el socorrista silba
    c = mar_lateral(t, SUP)
    nico_nadando(c, t, 420, SUP, 0.95, "sorpresa", (20, 175 + math.sin(t * 9) * 10))
    if t > 0.6:
        for k in range(3):
            r = 30 + ((t - 0.6) * 200 + k * 40) % 120
            capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(capa).arc([820 - r, 960 - r, 820 + r, 960 + r], 200, 340, fill=(255, 255, 255, 200), width=8)
            c.alpha_composite(capa)
    texto(c, "FLOTA Y\nPIDE AYUDA", 540, 1560, t - 0.2, 110, "#FFFFFF")
    return c, dict(zoom=1.15 + 0.05 * t, fx=0.5, fy=0.45, t=t)


def orilla_pov(t, foco=False, oscuro=False, espuma=False):
    c = cielo_mar().copy()
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.polygon([(0, 780), (W, 780), (W, H), (0, H)], fill=hexrgb("#2A8FA5") + (255,))
    d.polygon([(380, 780), (700, 780), (820, 1500), (260, 1500)], fill=hexrgb(AGUA_OSC if oscuro else "#2380A0") + (255,))
    for k in range(4):  # olas que rompen excepto en el hueco
        y = 830 + k * 170 + (t * 60 % 170)
        for x in range(0, W, 16):
            hueco = 360 - k * 30 < x < 720 + k * 30
            if not hueco:
                d.ellipse([x - 14, y - 8 + math.sin(x / 40 + t * 3) * 6, x + 14, y + 8], fill=ESPUMA + (230,))
    d.polygon([(0, 1500), (W, 1500), (W, H), (0, H)], fill=hexrgb(ARENA) + (255,))
    if espuma:
        for k in range(10):
            ph = (t * 0.5 + k / 10) % 1
            x = 470 + (k % 4) * 40
            y = 1450 - ph * 650
            d.ellipse([x - 16, y - 10, x + 16, y + 10], fill=ESPUMA + (int(230 * (1 - ph)),))
    c.alpha_composite(capa)
    if foco:
        from PIL import ImageFilter
        m = Image.new("L", (W, H), 150)
        ImageDraw.Draw(m).polygon([(380, 780), (700, 780), (820, 1500), (260, 1500)], fill=0)
        m = m.filter(ImageFilter.GaussianBlur(20))
        sombra = Image.new("RGBA", (W, H), (10, 10, 30, 0))
        sombra.putalpha(m)
        c.alpha_composite(sombra)
    return c


def e26(t, d):
    c = orilla_pov(t)
    texto(c, "¿CÓMO\nDETECTARLA?", 540, 1720, t - 0.1, 105, "#FFD400")
    return c, dict(zoom=1.05, t=t)


def e27(t, d):
    c = orilla_pov(t, foco=True)
    chispa_en(c, t, 540, 1100, 1.0)
    texto(c, "OLAS QUE\nNO ROMPEN", 540, 1720, t - 0.2, 105, "#FFFFFF")
    return c, dict(zoom=1.1, fx=0.5, fy=0.55, t=t)


def e28(t, d):
    c = orilla_pov(t, foco=True, oscuro=True)
    texto(c, "AGUA MÁS\nOSCURA", 540, 1720, t - 0.15, 105, "#FFFFFF")
    return c, dict(zoom=1.4, fx=0.5, fy=0.6, t=t)


def e29(t, d):
    c = orilla_pov(t, oscuro=True, espuma=True)
    texto(c, "ESPUMA HACIA\nMAR ADENTRO", 540, 1720, t - 0.15, 95, "#FFFFFF")
    return c, dict(zoom=1.2, fx=0.5, fy=0.6, t=t)


def e30(t, d):  # EL GIRO
    c = orilla_pov(0.0, oscuro=True)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    texto(c, "EL GIRO", 540, 1100, t, 170, "#FF4D6D", rot=-6)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def submarino(t):
    c = degradado(W, H, [(0, "#3FA6B8"), (0.15, "#1F6F8B"), (1, "#081E2C")])
    particulas(c, t, 40, (200, 240, 255), 6, (3, 7), 30, 150)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(capa).line([(x, 300 + math.sin(x / 70 + t * 3) * 14) for x in range(0, W + 20, 20)], fill=ESPUMA + (255,), width=10)
    c.alpha_composite(capa)
    return c


def e31(t, d):  # mano de agua intenta hundir a Nico
    c = submarino(t)
    tira = ease_out(t / d) * 120
    pegar(c, nico(t, "sorpresa", 160, 160, traje=TRAJE), 540, 1100 + tira, 0.75, ancla="abajo")
    m = Image.new("L", (400, 600), 0)
    dm = ImageDraw.Draw(m)
    dm.rounded_rectangle([60, 200, 340, 600], radius=80, fill=255)
    for k in range(4):
        dm.rounded_rectangle([60 + k * 72, 60 + abs(k - 1.5) * 30, 120 + k * 72, 260], radius=30, fill=255)
    pegar(c, sprite(m, "#2D8FB0", 131), 540, 1400 + tira, 0.9, alfa=0.85)
    texto(c, "«TE HUNDE»", 540, 1700, t - 0.1, 110, "#FFFFFF")
    return c, dict(zoom=1.05, t=t)


def e32(t, d):  # sello FALSO
    c = submarino(t)
    pegar(c, nico(t, "esceptico", 20, 20, traje=TRAJE), 540, 1220, 0.75, ancla="abajo")
    s = pop_scale(t - 0.1, 0.25)
    if s:
        hud(rotulo("FALSO", 200, "#FF4D6D", "#FFFFFF", 14, rot=-12), 540, 1150, (2.2 - 1.2 * s) if s < 1 else 1.0)
    return c, dict(zoom=1.0, temblor=10 if 0.1 < t < 0.35 else 0, t=t)


def e33(t, d):  # flota y se desliza mar adentro, sin hundirse
    c = mar_lateral(t, SUP, costa=True)
    x = 380 + clamp01(t / d) * 380
    nico_nadando(c, t, x, SUP, 0.7, "normal", (40, 40))
    flecha_plana(c, x + 160, SUP - 200, x + 360, SUP - 200, "#FFD400", 30)
    texto(c, "NO HACIA ABAJO", 540, 1560, t - 0.15, 100, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e34(t, d):
    c = mar_cenital(t)
    u = clamp01(t / d)
    nadador_cenital(c, t, 540, 1200 - u * 300, 0.4, "normal")
    flecha_plana(c, 540, 1050 - u * 300, 540, 700 - u * 300, "#FFD400", 34)
    texto(c, "TE ALEJA\nDE LA ORILLA", 540, 1640, t - 0.15, 100, "#FFD400")
    return c, dict(zoom=1.05, t=t)


def e35(t, d):  # pánico = agotamiento
    c = mar_lateral(t, SUP)
    nico_nadando(c, t, 540, SUP, 1.1, "espiral", (170, 170), 50)
    barra_energia(c, 540, 380, max(0.05, 0.5 - t * 0.4))
    texto(c, "PÁNICO =\nAGOTAMIENTO", 540, 1560, t - 0.15, 105, "#FF4D6D")
    return c, dict(zoom=1.3, fx=0.5, fy=0.45, t=t)


def e36(t, d):  # flota tranquilo con un flotador
    c = mar_lateral(t, SUP)
    u = ease_out(t / 0.6)
    pegar(c, prop("flotador"), 540, SUP - 300 + u * 330, 0.9)
    nico_nadando(c, t, 540, SUP, 0.85, "feliz", (60, 60))
    chispa_en(c, t, 800, 600, 0.9)
    texto(c, "SABERLO\nTE SALVA", 540, 1560, t - 0.3, 115, "#FFD400")
    return c, dict(zoom=1.1, fx=0.5, fy=0.5, t=t)


def icono_guardar(c, x, y, s):
    if s <= 0:
        return
    m = Image.new("L", (220, 280), 0)
    ImageDraw.Draw(m).polygon([(20, 0), (200, 0), (200, 270), (110, 200), (20, 270)], fill=255)
    hud(sprite(m, "#FFD400", 132), x, y, s, True)


def icono_compartir(c, x, y, s):
    if s <= 0:
        return
    img = Image.new("RGBA", (300, 260), (0, 0, 0, 0))
    m = Image.new("L", (300, 260), 0)
    ImageDraw.Draw(m).polygon([(0, 240), (60, 110), (180, 110), (180, 40), (300, 140), (180, 240), (180, 170), (80, 170)], fill=255)
    img.alpha_composite(sprite(m, "#3DE0E6", 133))
    hud(img, x, y, s, True)


def e37(t, d):
    c = degradado(W, H, [(0, "#3E7CB1"), (0.45, "#F6C28B"), (0.55, "#3FA6B8"), (0.62, "#E2C58F"), (1, "#D9B57A")])
    particulas(c, t, 25, (255, 240, 210), 3, (2, 4), 10, 110)
    pegar(c, nico(t, "feliz", 10, 100, traje=TRAJE), 540, 1880, 1.15, ancla="abajo")
    icono_guardar(c, 300, 760, pop_scale(t - 0.15))
    icono_compartir(c, 780, 760, pop_scale(t - 0.45))
    texto(c, "GUARDA · COMPARTE", 540, 1000, t - 0.2, 85, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e38(t, d):
    c = degradado(W, H, [(0, "#3E7CB1"), (0.45, "#F6C28B"), (0.55, "#3FA6B8"), (0.62, "#E2C58F"), (1, "#D9B57A")])
    particulas(c, t, 40, (255, 230, 160), 5, (2, 5), 18, 150)
    sal = 140 + 25 * math.sin(t * 10)
    sombra_suelo(c, 400, 1630, 340)
    pegar(c, nico(t, "feliz", 10, sal, traje=TRAJE), 400, 1640, 1.0, ancla="abajo")
    chispa_en(c, t, 820, 1000, 1.0)
    late = 1 + 0.06 * math.sin(t * 8)
    hud(prop("seguir"), 540, 1330, pop_scale(t - 0.2) * late, True)
    return c, dict(zoom=1.0, t=t)


_ESCENAS = [
    (0.0, e01, None, ["impacto", "ola"]), (0.8, e02, None, ["chapoteo"]), (1.7, e03, None, [("buzz", 0.3)]),
    (2.6, e04, None, ["blip"]), (3.4, e05, "barrido", ["whoosh"]), (4.6, e06, None, ["pop", "impacto"]),
    (5.8, e07, None, ["ola"]), (7.5, e08, None, ["burbujas"]), (9.2, e09, None, ["whoosh"]),
    (10.7, e10, None, [("ding", 0.4)]), (12.2, e11, "barrido", ["whoosh"]), (14.0, e12, None, [("pop", 0.3), ("impacto", 0.35)]),
    (15.5, e13, None, ["scratch"]), (17.0, e14, None, ["latido"]), (18.3, e15, None, ["alarma"]),
    (19.6, e16, "barrido", ["impacto", "pop"]), (20.8, e17, None, [("ding", 0.2)]), (23.0, e18, "barrido", ["impacto", "pop"]),
    (24.2, e19, None, ["chapoteo"]), (26.6, e20, None, [("pop", 0.3)]), (29.0, e21, "barrido", ["impacto", "pop"]),
    (30.2, e22, None, ["whoosh"]), (31.7, e23, None, ["ding", "ola"]), (33.2, e24, "barrido", ["riser_corto"]),
    (34.6, e25, None, [("silbato", 0.6)]), (37.0, e26, "barrido", ["whoosh", "ola"]), (38.8, e27, None, ["blip", ("pop", 0.2)]),
    (40.6, e28, None, [("pop", 0.15)]), (42.4, e29, None, ["burbujas"]), (44.2, e30, None, ["scratch"]),
    (46.0, e31, None, ["burbujas"]), (47.7, e32, None, [("buzz", 0.1), ("impacto", 0.12)]), (49.4, e33, "barrido", ["whoosh"]),
    (51.0, e34, None, [("pop", 0.15)]), (52.6, e35, None, ["latido"]), (54.1, e36, None, [("ding", 0.5)]),
    (55.6, e37, "barrido", [("pop", 0.15), ("pop", 0.45)]), (57.3, e38, None, ["whoosh", ("ding", 0.2)]),
]

ESCENAS = []
for i, (t0, f, tr, sfx) in enumerate(_ESCENAS):
    ini = remap(t0)
    fin = remap(_ESCENAS[i + 1][0]) if i + 1 < len(_ESCENAS) else DURACION
    ESCENAS.append(dict(ini=ini, fin=fin, f=f, tr=tr, sfx=sfx))
CORTE_MUSICA = (remap(44.2), remap(44.2) + 0.45)
