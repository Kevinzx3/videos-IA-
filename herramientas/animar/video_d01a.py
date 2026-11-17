"""Día 01 · Video A: ¿Por qué eres más alto por la mañana?  (escenas animadas)

Las escenas se definen en el tiempo del guion original (dia-01/01-...md) y se
reajustan automáticamente a la locución real usando los tiempos del JSON alineado.
"""
import json
import math
import random
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from motor import *  # noqa
from motor import _comp

RAIZ = Path(__file__).resolve().parents[2]
GUION = RAIZ / "dia-01/datos/01-mas-alto-por-la-manana.json"

# inicios de segmento del guion original (para reajustar escenas a la voz)
ORIG = [0, 2.8, 5.0, 8.4, 11.0, 14.2, 17.6, 20.4, 24.4, 27.6, 30.0, 32.6, 35.8, 38.8, 42.8, 44.6, 48.4, 52.0, 54.4, 58.0]
_seg = json.load(open(GUION, encoding="utf-8"))["segmentos"]
NUEVO = [s[0] for s in _seg] + [_seg[-1][1]]
DURACION = NUEVO[-1]


def remap(t):
    for i in range(len(ORIG) - 1):
        if t <= ORIG[i + 1]:
            u = (t - ORIG[i]) / (ORIG[i + 1] - ORIG[i])
            return NUEVO[i] + u * (NUEVO[i + 1] - NUEVO[i])
    return NUEVO[-1]


# ------------------------------------------------------------------ fondos
SUELO_Y = 1500
REGLA_X, REGLA_TOP = 790, 440
PIES_Y = 1640


def y_regla(cm):
    return REGLA_TOP + 1060 - (cm - 150) * 22


@lru_cache(maxsize=4)
def fondo_cuarto(noche=False):
    if noche:
        c = degradado(W, H, [(0, "#1E2350"), (0.75, "#2E3A78"), (1, "#1A1E40")])
    else:
        c = degradado(W, H, [(0, "#F7D9B5"), (0.75, "#EDB98C"), (1, "#D99A6C")])
    pp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dpp = ImageDraw.Draw(pp)
    for x in range(0, W, 90):  # papel pintado
        dpp.line([(x, 0), (x, SUELO_Y)], fill=(255, 255, 255, 22 if not noche else 10), width=26)
        for y in range(40, SUELO_Y, 120):
            dpp.ellipse([x + 40, y, x + 52, y + 12], fill=(200, 90, 90, 50))
    c.alpha_composite(pp)
    d = ImageDraw.Draw(c)
    # ventana
    v = Image.new("RGBA", (400, 540), (0, 0, 0, 0))
    cielo = degradado(360, 500, [(0, "#2B1E3F"), (0.55, "#C2577A"), (1, "#F29E5C")] if not noche else [(0, "#0B1030"), (1, "#27306A")])
    v.alpha_composite(sprite(Image.new("L", (400, 540), 255), "#FFFFFF", 90))
    v.alpha_composite(cielo, (20, 20))
    dv = ImageDraw.Draw(v)
    dv.line([(200, 20), (200, 520)], fill=(255, 255, 255, 255), width=14)
    dv.line([(20, 270), (380, 270)], fill=(255, 255, 255, 255), width=14)
    if noche:
        pegar(v, prop("icono", "luna"), 110, 130, 0.6)
    else:
        pegar(v, prop("icono", "sol"), 110, 400, 0.55)
    pegar(c, v, 190, 700)
    # cortina
    m = Image.new("L", (130, 700), 0)
    ImageDraw.Draw(m).polygon([(0, 0), (130, 0), (90, 700), (0, 700)], fill=255)
    pegar(c, sprite(m, "#C94F6D" if not noche else "#7A3150", 91), 40, 760)
    # suelo de madera
    m = Image.new("L", (W, H - SUELO_Y), 255)
    pis = sprite(m, "#B9774A" if not noche else "#4E3A5C", 92, costura=False, grano=0.2)
    dp = ImageDraw.Draw(pis)
    for y in range(0, H - SUELO_Y, 70):
        dp.line([(0, y), (W, y)], fill=(80, 45, 25, 120), width=4)
    c.alpha_composite(pis, (0, SUELO_Y))
    d.line([(0, SUELO_Y), (W, SUELO_Y)], fill=(255, 240, 220, 160), width=5)
    pegar(c, prop("regla"), REGLA_X + 85, REGLA_TOP + 550, sombra=True)
    if noche:
        c.alpha_composite(Image.new("RGBA", (W, H), (20, 30, 90, 70)))
    return c


@lru_cache(maxsize=2)
def fondo_calle_capas():
    cielo = degradado(W, H, [(0, "#2B1E3F"), (0.45, "#C2577A"), (0.7, "#F29E5C"), (1, "#F29E5C")])
    lejos = capa_edificios(W + 400, H, "#7A4A78", 5, 1280, 520, ventanas="#FFD98A")
    medio = capa_edificios(W + 600, H, "#3E2D5C", 8, 1380, 640, ventanas="#FFC56B")
    m = Image.new("L", (W + 800, H - 1380), 255)
    acera = sprite(m, "#8F7F8F", 93, costura=False, grano=0.2)
    da = ImageDraw.Draw(acera)
    for x in range(0, W + 800, 180):
        da.line([(x, 0), (x - 60, H - 1380)], fill=(60, 50, 70, 140), width=5)
    return cielo, lejos, medio, acera


def fondo_calle(t, vel=60):
    cielo, lejos, medio, acera = fondo_calle_capas()
    c = cielo.copy()
    particulas(c, t, 25, (255, 220, 180), 3, (2, 4), 10, 110)
    _comp(c, lejos, int(-(t * vel * 0.25) % 400), 0)
    _comp(c, medio, int(-(t * vel * 0.55) % 600), 0)
    _comp(c, acera, int(-(t * vel) % 180) - 180, 1380)
    return c


@lru_cache(maxsize=2)
def fondo_cuerpo_base():
    c = degradado(W, H, [(0, "#14112B"), (0.5, "#2A2152"), (1, "#3B2F6B")])
    rng = random.Random(3)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for _ in range(14):
        b = brillo(rng.uniform(60, 160), rng.choice(["#3DE0E6", "#FF4D6D", "#7A6CFF"]), 0.25)
        pegar(capa, b, rng.uniform(0, W), rng.uniform(0, H))
    c.alpha_composite(capa)
    return c


def fondo_cuerpo(t):
    c = fondo_cuerpo_base().copy()
    particulas(c, t, 50, (160, 240, 255), 9, (2, 5), 25, 140)
    return c


@lru_cache(maxsize=2)
def fondo_espacio_base():
    c = degradado(W, H, [(0, "#05040F"), (1, "#16123A")])
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    rng = random.Random(1)
    for _ in range(420):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.choice([1, 1, 1.5, 2, 3])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rng.randint(120, 255)))
    c.alpha_composite(capa)
    return c


def fondo_espacio(t, tierra=True, tierra_y=1900, tierra_esc=1.0):
    c = fondo_espacio_base().copy()
    particulas(c, t, 30, (255, 255, 255), 4, (1, 2.5), 6, 200)
    if tierra:
        pegar(c, prop("tierra"), W / 2, tierra_y + 200, tierra_esc, rot=t * 2)
    return c


@lru_cache(maxsize=2)
def fondo_amarillo():
    c = degradado(W, H, [(0, "#FFD400"), (1, "#FFB000")])
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for k in range(-H, W, 160):
        d.line([(k, H), (k + H, 0)], fill=(255, 255, 255, 28), width=50)
    c.alpha_composite(capa)
    return c


# ------------------------------------------------------------ helpers escena
def nico_en(c, t, x=480, y=PIES_Y, esc=1.0, sombra=True, rot=0.0, sy=1.0, **kw):
    if sombra:
        sombra_suelo(c, x, y - 8, 340 * esc)
    spr = nico(t, **kw)
    if rot:
        spr = spr.rotate(rot, resample=Image.BICUBIC, expand=True)
    pegar(c, spr, x, y, esc, sy=sy, ancla="abajo")


def texto(c, txt, x, y, tl, tam=120, color="#FFFFFF", rot=0):
    """Rótulo grande en espacio de pantalla (no le afecta el zoom de cámara)."""
    s = pop_scale(tl)
    if s > 0:
        hud(rotulo(txt, tam, color, rot=rot), x, y, s)


def tag(c, val, uni, x, y, tl, tam=130):
    s = pop_scale(tl)
    if s > 0:
        hud(etiqueta(val, uni, tam), x, y, s, True)


def chispa_en(c, t, x, y, tam=1.0):
    pegar(c, chispa(t, tam), x, y + math.sin(t * 4) * 12)


def marca(c, cm):
    pegar(c, prop("marca"), REGLA_X - 30, y_regla(cm))


def columna(c, cx, top, t, n=6, aplastar=1.0, separar=0.0, ola=None, esc=1.0, cara=True):
    """Dibuja una columna de vértebras y discos. aplastar<1 comprime los discos."""
    v = prop("vertebra", cara)
    dsc = prop("disco")
    y = top
    for i in range(n):
        dy = 0
        if ola is not None:
            ph = clamp01((ola - i * 0.12) / 0.3)
            dy = -math.sin(ph * math.pi) * 40
        pegar(c, v, cx, y + dy, esc)
        y += (75 + 4) * esc
        if i < n - 1:
            hdisc = 70 * aplastar * esc
            pegar(c, dsc, cx, y + hdisc / 2 - 4 * esc, esc, sy=aplastar)
            y += hdisc + separar * esc + 75 * esc - 8 * esc
    return y


def gotas_lado(c, cx, cy, t, n=6, ancho=160):
    for k in range(n):
        ph = (t * 1.4 + k / n) % 1
        for s in (-1, 1):
            pegar(c, prop("gota"), cx + s * (ancho + ph * 160), cy + ph * ph * 220, 0.6, alfa=1 - ph)


# ------------------------------------------------------------------ escenas
# Cada escena: f(t_local, dur) -> (imagen RGBA, parámetros de cámara)

def e01(t, d):  # Nico asustado frente a la regla, push-in
    c = fondo_cuarto().copy()
    particulas(c, t, 30, (255, 240, 210), 2, (2, 4), 12, 120)
    marca(c, 178)
    nico_en(c, t, expr="sorpresa", brazo_i=25, brazo_d=25)
    texto(c, "¿MÁS BAJO?", 540, 1250, t - 0.05, 120)
    return c, dict(zoom=1.0 + 0.18 * ease_out(t / d), fx=0.47, fy=0.55, temblor=6 if t < 0.25 else 0, t=t)


def e02(t, d):  # detalle de la regla: la marca baja
    c = fondo_cuarto().copy()
    nico_en(c, t, expr="sorpresa", brazo_i=25, brazo_d=25)
    caida = ease_out((t - 0.2) / 0.25)
    marca(c, 178 - caida)
    if t > 0.45:
        tag(c, "-1", "cm", 540, 1300, t - 0.45, 170)
    return c, dict(zoom=2.4, fx=(REGLA_X - 60) / W, fy=y_regla(177.5) / H + 0.04, temblor=8 if 0.2 < t < 0.4 else 0, t=t)


def e03(t, d):  # primer plano, ojos en espiral, entra Chispa
    c = fondo_cuarto().copy()
    marca(c, 177)
    nico_en(c, t, expr="espiral", brazo_i=150, brazo_d=150)
    x = 1150 - ease_out(t / 0.6) * 380
    chispa_en(c, t, x, 820)
    return c, dict(zoom=1.9, fx=0.47, fy=0.5, t=t)


def e04(t, d):  # Chispa gira alrededor de Nico
    c = fondo_cuarto().copy()
    marca(c, 177)
    a = t * 5
    detras = math.sin(a) < 0
    x, y = 480 + math.cos(a) * 300, 1050 + math.sin(a) * 60
    if detras:
        chispa_en(c, t, x, y, 0.8)
    nico_en(c, t, expr="esceptico", brazo_i=5, brazo_d=-5)
    if not detras:
        chispa_en(c, t, x, y, 1.1)
    texto(c, "NO ES\nILUSIÓN", 540, 1300, t - 0.15, 120, "#FFD400")
    return c, dict(zoom=1.25 + 0.05 * t, fx=0.46, fy=0.55, t=t)


def e05(t, d):  # zoom-through a la espalda -> columna
    u = t / d
    if u < 0.45:
        c = fondo_cuarto().copy()
        nico_en(c, t, expr="normal")
        return c, dict(zoom=1.0 + 6 * ease_in_out(u / 0.45) ** 2, fx=0.45, fy=0.62, t=t)
    c = fondo_cuerpo(t)
    columna(c, 540, 700, t, 5, esc=1.1)
    texto(c, "TU COLUMNA", 540, 1500, t - 0.45 * d, 120, "#3DE0E6")
    return c, dict(zoom=1.6 - 0.6 * ease_out((u - 0.45) / 0.55), fx=0.5, fy=0.55, t=t)


def e06(t, d):  # paneo vertical por la columna, vértebras saludan en ola
    c = fondo_cuerpo(t)
    columna(c, 540, 380, t, 7, ola=t / d * 1.6, esc=1.0)
    return c, dict(zoom=1.15, fx=0.5, fy=0.35 + 0.3 * ease_in_out(t / d), t=t)


def e07(t, d):  # detalle: Chispa ilumina el disco
    c = fondo_cuerpo(t)
    pegar(c, prop("vertebra", True), 540, 820, 1.8)
    gl = 0.5 + 0.5 * math.sin(t * 8)
    pegar(c, brillo(260, "#3DE0E6", 0.5 + 0.3 * gl), 540, 1010)
    pegar(c, prop("disco"), 540, 1010, 1.8)
    pegar(c, prop("vertebra", True), 540, 1200, 1.8, rot=180)
    chispa_en(c, t, 860 - ease_out(t / 0.5) * 80, 1000, 0.9)
    tag(c, "DISCO", "", 540, 1400, t - 0.3, 110)
    return c, dict(zoom=1.0 + 0.06 * t, fx=0.5, fy=0.53, t=t)


def e08(t, d):  # match cut: disco -> esponja
    c = fondo_cuerpo(t)
    u = ease_in_out(t / 0.5)
    pegar(c, prop("disco"), 540, 1000, 1.8 + u, alfa=1 - u)
    pegar(c, prop("esponja", True), 540, 1000, 0.6 + 0.9 * u, alfa=u)
    if t > 0.4:
        for k in range(3):
            ph = ((t - 0.4) * 1.2 + k / 3) % 1
            pegar(c, prop("gota"), 450 + k * 90, 1130 + ph * 300, 0.8, alfa=1 - ph)
    texto(c, "= ESPONJA", 540, 1450, t - 0.4, 120, "#FFD400")
    return c, dict(zoom=1.0, t=t)


def e09(t, d):  # la esponja respira
    c = fondo_cuerpo(t)
    r = 1 + 0.08 * math.sin(t * 5)
    pegar(c, prop("esponja", True), 540, 1000, 1.5, sx=r, sy=2 - r)
    rng = random.Random(2)
    for k in range(10):
        ph = (t * 0.6 + k / 10) % 1
        x = 380 + rng.uniform(0, 320)
        pegar(c, brillo(14, "#BFF2FF", 0.9), x + math.sin(t * 3 + k) * 20, 1150 - ph * 600, 1, alfa=1 - ph)
    return c, dict(zoom=1.1 - 0.06 * t / d, fx=0.5, fy=0.52, t=t)


def e10(t, d):  # calle: Nico camina, cae la flecha GRAVEDAD
    c = fondo_calle(t)
    paso = math.sin(t * 9)
    nico_en(c, t, 540, 1700, 0.95, brazo_i=8 + paso * 12, brazo_d=8 - paso * 12, pierna_i=paso * 14, pierna_d=-paso * 14, expr="normal")
    yf = -500 + ease_out((t - 0.2) / 0.35) * 820
    if t > 0.2:
        pegar(c, prop("flecha", "GRAVEDAD"), 540, yf, 0.75, sombra=True)
    return c, dict(zoom=1.05, fx=0.5, fy=0.52, temblor=10 if 0.5 < t < 0.75 else 0, t=t)


def e11(t, d):  # aplastado como un sándwich
    c = fondo_calle(t, 0)
    sq = 1 - 0.18 * ease_out((t - 0.15) / 0.3)
    pegar(c, prop("pan"), 540, 1700 + 60, 1.25)
    nico_en(c, t, 540, 1690, 0.95, sombra=False, sy=sq, expr="esfuerzo", brazo_i=60, brazo_d=60)
    ytop = 1690 - 780 * sq - 140
    pegar(c, prop("pan"), 540, ytop - 40 + (1 - ease_out(t / 0.25)) * -600, 1.25, rot=180)
    texto(c, "¡ÑAM!", 830, 1000, t - 0.3, 90, "#FFD400", rot=12)
    return c, dict(zoom=1.0, temblor=7 if 0.15 < t < 0.4 else 0, t=t)


def e12(t, d):  # cada paso: polvo
    c = fondo_calle(t, 120)
    paso = math.sin(t * 10)
    nico_en(c, t, 540, 1700, 0.95, brazo_i=8 + paso * 18, brazo_d=8 - paso * 18, pierna_i=paso * 20, pierna_d=-paso * 20)
    for k in range(5):
        ph = (t * 2 + k / 5) % 1
        pegar(c, brillo(30, "#E8D8C8", 0.7), 480 - ph * 120 + k * 20, 1690 - ph * 40, 1 + ph, alfa=1 - ph)
    return c, dict(zoom=1.7, fx=0.5, fy=0.8, t=t)


def e13(t, d):  # salto sobre un charco
    c = fondo_calle(t, 80)
    pegar(c, prop("charco"), 540, 1720, 1.4)
    u = clamp01(t / d)
    salto = math.sin(u * math.pi) * 260
    nico_en(c, t, 300 + u * 480, 1700 - salto, 0.9, sombra=False, brazo_i=120, brazo_d=120, pierna_i=-25, pierna_d=25, expr="feliz")
    sombra_suelo(c, 300 + u * 480, 1700, 300 * (1 - salto / 600))
    return c, dict(zoom=1.15, fx=0.5, fy=0.65, t=t)


def e14(t, d):  # se carga la mochila con esfuerzo
    c = fondo_calle(t, 0)
    tiemb = math.sin(t * 40) * 3
    nico_en(c, t, 540 + tiemb, 1700, 1.0, expr="esfuerzo", brazo_i=150, brazo_d=150, sy=0.97)
    for k in range(3):
        ph = (t * 1.5 + k / 3) % 1
        pegar(c, prop("gota"), 400 + k * 140, 900 + ph * 120, 0.5, alfa=1 - ph)
    return c, dict(zoom=1.35, fx=0.5, fy=0.55, t=t)


def e15(t, d):  # rayos X: discos se aplastan y sueltan gotitas
    c = fondo_cuerpo(t)
    ap = 1 - 0.35 * (0.5 + 0.5 * math.sin(t * 7 - 1.6))
    y = columna(c, 540, 520, t, 5, aplastar=ap, esc=1.05)
    gotas_lado(c, 540, 900, t, 5, 150)
    return c, dict(zoom=1.05, fx=0.5, fy=0.5, t=t)


def e16(t, d):  # esponja exprimida: gota a gota
    c = fondo_cuerpo(t)
    ap = ease_out(t / 0.5)
    pegar(c, prop("esponja", True), 540, 950, 1.4, sx=1 - 0.35 * ap, sy=1 + 0.1 * ap)
    for s in (-1, 1):
        m = Image.new("L", (260, 360), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, 260, 360], radius=120, fill=255)
        pegar(c, sprite(m, PIEL, 95), 540 + s * (520 - 120 * ap), 950, 1.0)
    for k in range(4):
        ph = (t * 1.5 + k / 4) % 1
        pegar(c, prop("gota"), 470 + k * 45, 1150 + ph * 450, 0.9, alfa=1 - ph)
    texto(c, "GOTA A GOTA", 540, 1500, t - 0.3, 110, "#7FD3FF")
    return c, dict(zoom=1.0, t=t)


def e17(t, d):  # pantalla dividida mañana / noche
    izq = fondo_cuarto(False).copy()
    der = fondo_cuarto(True).copy()
    nico_en(izq, t, 540, PIES_Y, 1.0, expr="feliz")
    nico_en(der, t, 540, PIES_Y, 0.95, expr="cansado")
    c = Image.new("RGBA", (W, H))
    c.alpha_composite(izq.crop((270, 0, 270 + W // 2, H)), (0, 0))
    c.alpha_composite(der.crop((270, 0, 270 + W // 2, H)), (W // 2, 0))
    ImageDraw.Draw(c).line([(W // 2, 0), (W // 2, H)], fill=(255, 255, 255, 255), width=12)
    pegar(c, prop("icono", "sol"), 270, 1150, pop_scale(t - 0.1) * 0.9)
    pegar(c, prop("icono", "luna"), 810, 1150, pop_scale(t - 0.3) * 0.9)
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e18(t, d):  # Chispa trae la etiqueta 1–2 cm
    c = fondo_cuarto(True).copy()
    marca(c, 178)
    pegar(c, prop("marca"), REGLA_X - 30, y_regla(176.5), alfa=0.6)
    xx = 1200 - ease_out(t / 0.5) * 520
    chispa_en(c, t, xx, 1000)
    tag(c, "1–2", "cm", 540, 1250, t - 0.35, 140)
    return c, dict(zoom=1.5, fx=0.55, fy=0.55, t=t)


def e19(t, d):  # despertador saltando, agujas girando
    c = fondo_amarillo().copy()
    salto = abs(math.sin(t * 14)) * 30
    reloj = prop("reloj").copy()
    dr = ImageDraw.Draw(reloj)
    h = 7 + clamp01(t / d) * 1
    for ang, L, wd in ((h / 12 * math.tau, 70, 12), ((h % 1) * math.tau, 100, 8)):
        dr.line([(210, 230), (210 + math.sin(ang) * L, 230 - math.cos(ang) * L)], fill=OSCURO + (255,), width=wd)
    pegar(c, reloj, 540 + math.sin(t * 30) * 8, 1000 - salto, 1.6, rot=math.sin(t * 30) * 5, sombra=True)
    texto(c, "1.ª HORA", 540, 1500, t - 0.2, 130)
    return c, dict(zoom=1.0 + 0.05 * t, t=t)


def e20(t, d):  # barra de progreso hasta casi la mitad
    c = fondo_amarillo().copy()
    d0 = ImageDraw.Draw(c)
    x0, x1, y0 = 140, 940, 1000
    d0.rounded_rectangle([x0, y0, x1, y0 + 110], radius=55, fill=(60, 40, 30, 255))
    p = 0.45 * ease_out(clamp01((t - 0.1) / 0.5))
    if p > 0.02:
        d0.rounded_rectangle([x0 + 12, y0 + 12, x0 + 12 + (x1 - x0 - 24) * p, y0 + 98], radius=45, fill=(255, 77, 109, 255))
    pegar(c, rotulo("ALTURA PERDIDA", 70, "#3A2A20", "#FFFFFF", 6), 540, 900)
    texto(c, "≈ MITAD", 540, 1300, t - 0.6, 140, "#FFFFFF")
    return c, dict(zoom=1.0, temblor=6 if 0.6 < t < 0.8 else 0, t=t)


def e21(t, d):  # "¡ajá!"
    c = fondo_cuarto().copy()
    marca(c, 177)
    nico_en(c, t, expr="aja", brazo_i=5, brazo_d=165)
    return c, dict(zoom=1.8, fx=0.47, fy=0.48, t=t)


def e22(t, d):  # Chispa pulsa el botón de REINICIO
    c = fondo_amarillo().copy()
    base, cima = prop("boton")
    pres = 1 if 0.35 < t < 0.6 else 0
    pegar(c, base, 540, 1150, 1.6, sombra=True)
    pegar(c, cima, 540, 1150 + pres * 40, 1.6)
    chispa_en(c, t, 540, 820 - (1 - ease_out(t / 0.35)) * 400 + pres * 60, 1.0)
    texto(c, "REINICIO", 540, 1500, t - 0.4, 130, "#FFFFFF")
    return c, dict(zoom=1.0, temblor=8 if 0.35 < t < 0.5 else 0, t=t)


def e23(t, d):  # noche: Nico se acuesta, la gravedad se desvanece
    c = fondo_cuarto(True).copy()
    particulas(c, t, 25, (255, 240, 140), 6, (3, 6), 6, 200)
    pegar(c, prop("cama"), 540, 1500, 1.0)
    acostado = nico(t, "dormido", 10, -10, respirar=True).rotate(90, expand=True, resample=Image.BICUBIC)
    pegar(c, acostado, 470, 1370, 0.62)
    r = 1 + 0.02 * math.sin(t * 2.5)
    pegar(c, prop("manta"), 610, 1430, 1.0, sy=r)
    a = 1 - clamp01(t / (d * 0.7))
    if a > 0:
        pegar(c, prop("flecha", "GRAVEDAD"), 540, 700, 0.55, alfa=a)
    texto(c, "SIN PRESIÓN", 540, 1080, t - d * 0.55, 110, "#BFD8FF")
    for k in range(3):
        ph = (t * 0.7 + k / 3) % 1
        pegar(c, rotulo("Z", 60 + k * 10, "#FFFFFF"), 300 + ph * 100, 1330 - ph * 140 - k * 20, 1, alfa=1 - ph)
    return c, dict(zoom=1.25 - 0.1 * t / d, fx=0.5, fy=0.7, t=t)


def e25(t, d):  # rayos X: los discos se hinchan de nuevo
    c = fondo_cuerpo(t)
    ap = 0.65 + 0.35 * ease_out(t / d)
    columna(c, 540, 520, t, 5, aplastar=ap, esc=1.05)
    for k in range(8):
        ph = (t * 0.8 + k / 8) % 1
        for s in (-1, 1):
            pegar(c, prop("gota"), 540 + s * (400 - ph * 230), 700 + k * 80, 0.5, alfa=ph)
    return c, dict(zoom=1.05, t=t)


def e26(t, d):  # time-lapse ventana: luna baja, sale el sol
    u = ease_in_out(t / d)
    top = mezcla(hexrgb("#0B1030"), hexrgb("#2B1E3F"), u)
    mid = mezcla(hexrgb("#1B2560"), hexrgb("#C2577A"), u)
    bot = mezcla(hexrgb("#27306A"), hexrgb("#F29E5C"), u)
    c = degradado(W, H, [(0, "#%02x%02x%02x" % top), (0.55, "#%02x%02x%02x" % mid), (1, "#%02x%02x%02x" % bot)])
    pegar(c, prop("icono", "luna"), 300, 500 + u * 900, 1.3, alfa=1 - u)
    pegar(c, prop("icono", "sol"), 760, 1500 - u * 900, 1.5, alfa=u)
    c.alpha_composite(capa_pinos(W, H, "#1F2340", 4, 1650, 450, 8))
    # marco de ventana
    d0 = ImageDraw.Draw(c)
    d0.rectangle([0, 0, W, H], outline=(255, 255, 255, 255), width=60)
    d0.line([(W // 2, 0), (W // 2, H)], fill=(255, 255, 255, 255), width=40)
    d0.line([(0, H // 2), (W, H // 2)], fill=(255, 255, 255, 255), width=40)
    return c, dict(zoom=1.05, t=t)


def e27(t, d):  # se despierta y se estira
    c = fondo_cuarto().copy()
    marca(c, 177)
    u = ease_out(t / 0.6)
    nico_en(c, t, expr="feliz", brazo_i=20 + 150 * u, brazo_d=20 + 150 * u, sy=1 + 0.03 * math.sin(clamp01(t / 0.6) * math.pi))
    return c, dict(zoom=1.2, fx=0.47, fy=0.55, t=t)


def e28(t, d):  # la marca sube +1 cm
    c = fondo_cuarto().copy()
    nico_en(c, t, expr="feliz", brazo_i=170, brazo_d=170)
    marca(c, 177 + ease_out((t - 0.15) / 0.3))
    if t > 0.4:
        tag(c, "+1", "cm", 540, 1300, t - 0.4, 170)
    return c, dict(zoom=2.4, fx=(REGLA_X - 60) / W, fy=y_regla(177.5) / H + 0.04, t=t)


def e29(t, d):  # orgulloso: "MÍDETE AL DESPERTAR"
    c = fondo_cuarto().copy()
    particulas(c, t, 30, (255, 240, 200), 8, (2, 4), 15, 130)
    marca(c, 178)
    nico_en(c, t, expr="orgullo", brazo_i=-35, brazo_d=-35)
    texto(c, "MÍDETE AL\nDESPERTAR", 540, 1300, t - 0.15, 115, "#FFD400")
    return c, dict(zoom=1.0 + 0.08 * t / d, fx=0.5, fy=0.55, t=t)


def e30(t, d):  # Chispa le pone una medalla
    c = fondo_cuarto().copy()
    marca(c, 178)
    nico_en(c, t, expr="feliz", brazo_i=-35, brazo_d=-35)
    u = ease_out(t / 0.6)
    pegar(c, prop("medalla"), 480, 400 + u * 730, 0.9, rot=(1 - u) * 30)
    chispa_en(c, t, 480, 300 + u * 600, 0.8)
    if t > 0.7:
        for k in range(8):
            a = k / 8 * math.tau
            r = 120 + (t - 0.7) * 300
            pegar(c, brillo(18, "#FFD400", 0.9), 480 + math.cos(a) * r, 1150 + math.sin(a) * r, 1, alfa=clamp01(1.5 - (t - 0.7) * 2))
    return c, dict(zoom=1.35, fx=0.45, fy=0.58, t=t)


def e31(t, d):  # EL GIRO: congelado + salto al espacio
    if t < 0.35:
        c = fondo_cuarto().copy()
        marca(c, 178)
        nico_en(c, 0.0, expr="sorpresa", brazo_i=25, brazo_d=25)
        c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.35)
        texto(c, "EL GIRO", 540, 1250, t, 160, "#FF4D6D", rot=-6)
        return c, dict(zoom=1.15, temblor=10, t=t)
    u = ease_in_out((t - 0.35) / (d - 0.35))
    c = fondo_espacio(t, True, 1900 - u * 800, 0.3 + 0.7 * u)
    texto(c, "EL GIRO", 540, 1250 - u * 600, 1, 160, "#FF4D6D", rot=-6)
    return c, dict(zoom=1.6 - 0.6 * u, t=t)


def e32(t, d):  # Nico astronauta flotando junto a la estación
    c = fondo_espacio(t, True, 1700, 1.0)
    pegar(c, prop("estacion"), 600 - t * 30, 760, 0.9, rot=-6)
    flot = math.sin(t * 2) * 30
    spr = nico(t, "feliz", 120, 120, -15, 15, traje="#E8ECF2", casco=True)
    pegar(c, spr, 500 + t * 20, 1250 + flot, 0.85, rot=10 * math.sin(t * 1.3))
    return c, dict(zoom=1.05 + 0.04 * t, t=t)


def e33(t, d):  # columna flotando, vértebras separadas: +3 %
    c = fondo_espacio(t, False)
    sep = 30 * ease_out(t / 1.0)
    columna(c, 540, 420, t, 6, separar=sep, esc=0.95)
    tag(c, "+3", "%", 540, 1550, t - 0.45, 150)
    return c, dict(zoom=1.05, fy=0.5, t=t)


def e34(t, d):  # silueta 1,80 -> 1,85
    c = fondo_espacio(t, False)
    u = ease_out((t - 0.2) / 0.8)
    m = nico(0, "normal", 10, -10)
    sil = Image.new("RGBA", m.size, (61, 224, 230, 0))
    sil.putalpha(m.getchannel("A"))
    pegar(c, brillo(400, "#3DE0E6", 0.25), 540, 1100)
    pegar(c, sil, 540, 1550, 1.0, sy=1 + 0.06 * u, ancla="abajo")
    pegar(c, rotulo("1,80 m → ≈1,85 m", 90, "#FFFFFF"), 540, 1700, pop_scale(t - 0.3))
    return c, dict(zoom=1.0, t=t)


def e35(t, d):  # se estira tanto que choca con el techo: +5 cm
    c = fondo_espacio(t, True, 1800, 1.0)
    d0 = ImageDraw.Draw(c)
    d0.rectangle([0, 0, W, 330], fill=(170, 176, 190, 255))
    d0.rectangle([0, 300, W, 340], fill=(110, 116, 130, 255))
    subida = ease_out(t / 0.5) * 220
    golpe = t > 0.5
    spr = nico(t, "espiral" if golpe else "orgullo", 160, 160, traje="#E8ECF2", casco=True)
    pegar(c, spr, 540, 1400 - subida + (math.sin((t - 0.5) * 30) * 6 if golpe else 0), 0.9, ancla="abajo")
    if golpe:
        for k in range(5):
            a = t * 4 + k / 5 * math.tau
            pegar(c, brillo(16, "#FFD400", 1), 540 + math.cos(a) * 160, 480 + math.sin(a) * 40)
    tag(c, "+5", "cm", 540, 1580, t - 0.3, 140)
    return c, dict(zoom=1.0, temblor=12 if 0.5 < t < 0.7 else 0, t=t)


def e36(t, d):  # cápsula bajando con paracaídas
    c = degradado(W, H, [(0, "#3E7CB1"), (0.7, "#F6C28B"), (1, "#F29E5C")])
    for k, (x, y) in enumerate([(200, 400), (800, 650), (400, 1300)]):
        nube = Image.new("L", (360, 160), 0)
        dn = ImageDraw.Draw(nube)
        for cx, r in ((90, 60), (180, 80), (270, 60)):
            dn.ellipse([cx - r, 120 - r, cx + r, 120 + r * 0.6], fill=255)
        pegar(c, sprite(nube, "#FFFFFF", 100 + k), x, (y + t * 300) % 2100 - 100, 1.0, alfa=0.9)
    pegar(c, prop("capsula"), 540 + math.sin(t * 2) * 30, 900 + t * 60, 1.1, rot=math.sin(t * 2) * 6)
    return c, dict(zoom=1.0, t=t)


def e37(t, d):  # vuelve: la marca baja otra vez
    c = fondo_cuarto().copy()
    nico_en(c, t, expr="esceptico", brazo_i=10, brazo_d=-10)
    marca(c, 183 - 5 * ease_out((t - 0.2) / 0.4))
    return c, dict(zoom=1.3, fx=0.55, fy=0.5, t=t)


def e38(t, d):  # Nico señala a cámara + globo de comentario
    c = fondo_cuarto().copy()
    particulas(c, t, 25, (255, 240, 210), 4, (2, 4), 12, 120)
    nico_en(c, t, 540, PIES_Y + 300, 1.25, expr="feliz", brazo_i=10, brazo_d=100)
    s = pop_scale(t - 0.15, 0.35)
    if s:
        g = prop("globo").copy()
        r = rotulo("¿A QUÉ HORA\nTE MEDIRÁS?", 74, "#1A1022", "#FFFFFF", 4)
        g.alpha_composite(r, (430 - r.width // 2, 140 - r.height // 2))
        pegar(c, g, 540, 900, s * 1.0, sombra=True)
    return c, dict(zoom=1.0 + 0.05 * t, t=t)


def e39(t, d):  # final: saludo + botón seguir
    c = fondo_cuarto().copy()
    particulas(c, t, 40, (255, 230, 160), 5, (2, 5), 18, 150)
    sal = 140 + 25 * math.sin(t * 10)
    nico_en(c, t, 400, PIES_Y, 1.0, expr="feliz", brazo_i=10, brazo_d=sal)
    chispa_en(c, t, 820, 1000, 1.0)
    late = 1 + 0.06 * math.sin(t * 8)
    pegar(c, prop("seguir"), 540, 1330, pop_scale(t - 0.2) * late, sombra=True)
    texto(c, "+ CIENCIA", 540, 1500, t - 0.5, 90, "#FFD400")
    return c, dict(zoom=1.0, t=t)


# (inicio en guion original, función, transición de entrada, SFX al inicio)
_ESCENAS = [
    (0.0, e01, None, ["impacto"]), (0.9, e02, None, ["squish"]), (1.9, e03, None, ["blip"]),
    (2.8, e04, "barrido", ["whoosh"]), (3.9, e05, None, ["whoosh_grave"]), (5.0, e06, None, ["pop3"]),
    (6.6, e07, None, ["blip"]), (8.4, e08, None, ["ding"]), (9.7, e09, None, ["burbujas"]),
    (11.0, e10, "barrido", ["whoosh", ("impacto", 0.55)]), (12.6, e11, None, [("squish", 0.2)]),
    (14.2, e12, None, ["paso"]), (15.3, e13, None, ["boing"]), (16.4, e14, None, ["esfuerzo"]),
    (17.6, e15, None, ["squish3"]), (19.0, e16, None, ["goteo"]), (20.4, e17, "barrido", ["whoosh"]),
    (22.4, e18, None, [("pop", 0.35), ("impacto", 0.4)]), (24.4, e19, None, ["tictac"]),
    (26.0, e20, None, ["riser_corto", ("impacto", 0.6)]), (27.6, e21, None, ["ding"]),
    (28.8, e22, None, [("click", 0.35), ("whoosh", 0.45)]), (30.0, e23, "barrido", ["whoosh_suave"]),
    (32.6, e25, None, ["burbujas"]), (34.2, e26, None, ["riser_suave"]), (35.8, e27, None, ["estirar"]),
    (37.3, e28, None, [("ding", 0.2)]), (38.8, e29, None, [("pop", 0.15)]), (40.8, e30, None, [("ding", 0.6), ("ding", 0.8)]),
    (42.8, e31, None, ["scratch", ("whoosh_grave", 0.35)]), (44.6, e32, None, ["espacio"]),
    (46.4, e33, None, [("pop", 0.45), ("impacto", 0.5)]), (48.4, e34, None, [("estirar", 0.2)]),
    (50.2, e35, None, [("bonk", 0.5)]), (52.0, e36, "barrido", ["whoosh_bajada"]), (53.2, e37, None, [("squish", 0.2)]),
    (54.4, e38, None, [("pop", 0.15)]), (56.2, e39, "barrido", ["whoosh", ("ding", 0.2)]),
]

ESCENAS = []
for i, (t0, f, tr, sfx) in enumerate(_ESCENAS):
    ini = remap(t0)
    fin = remap(_ESCENAS[i + 1][0]) if i + 1 < len(_ESCENAS) else DURACION
    ESCENAS.append(dict(ini=ini, fin=fin, f=f, tr=tr, sfx=sfx))
