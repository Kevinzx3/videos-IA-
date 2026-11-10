"""Día 02 · Video B: ¿Solo usas el 10 % de tu cerebro? MITO."""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-02/datos/02-mito-10-por-ciento-cerebro.json"
ROSA = "#F29BB0"

# zonas del cerebro (coordenadas relativas al sprite de 700x520)
ZONAS = {"motora": (330, 120), "olfato": (170, 380), "musica": (420, 330), "vision": (600, 260),
         "frontal": (150, 210), "parietal": (500, 140), "cerebelo": (560, 420)}


@lru_cache(maxsize=4)
def _cerebro(cara=True):
    m = Image.new("L", (700, 520), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([20, 40, 680, 440], fill=255)
    d.ellipse([440, 330, 660, 500], fill=255)  # cerebelo
    d.rounded_rectangle([300, 380, 380, 520], radius=30, fill=255)  # tronco
    spr = sprite(m, ROSA, 180)
    dd = ImageDraw.Draw(spr)
    rng = random.Random(5)
    col = oscurecer(hexrgb(ROSA), 0.25) + (255,)
    for k in range(16):  # circunvoluciones
        x0, y0 = rng.uniform(80, 600), rng.uniform(90, 370)
        pts = [(x0 + j * 18, y0 + math.sin(j * 1.3 + k) * 22) for j in range(rng.randint(4, 8))]
        dd.line(pts, fill=col, width=7, joint="curve")
    dd.line([(350, 50), (350, 420)], fill=col, width=9)
    if cara:
        for s in (-1, 1):
            dd.ellipse([350 + s * 80 - 30, 230, 350 + s * 80 + 30, 290], fill=(255, 255, 255, 255))
            dd.ellipse([350 + s * 80 - 13, 248, 350 + s * 80 + 13, 274], fill=(30, 20, 30, 255))
        dd.arc([310, 285, 390, 335], 20, 160, fill=(80, 30, 40, 255), width=7)
    return spr


def cerebro(c, x, y, esc, t, zonas=(), todas=0.0, cara=True, latir=True):
    s = esc * (1 + (0.015 * math.sin(t * 3) if latir else 0))
    spr = _cerebro(cara)
    pegar(c, spr, x, y, s, sombra=True)
    for nombre, intensidad in list(zonas) + ([(z, todas) for z in ZONAS] if todas else []):
        zx, zy = ZONAS[nombre]
        px, py = x + (zx - 350) * s, y + (zy - 260) * s
        pegar(c, brillo(90 * s, "#FFE45C", 0.9 * intensidad), px, py)


def fondo(t, color1="#1A1440", color2="#3B2F6B"):
    c = _fondo(color1, color2).copy()
    particulas(c, t, 45, (200, 220, 255), 9, (2, 5), 20, 140)
    return c


@lru_cache(maxsize=4)
def _fondo(c1, c2):
    c = degradado(W, H, [(0, c1), (1, c2)])
    rng = random.Random(3)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for _ in range(12):
        pegar(img, brillo(rng.uniform(60, 150), rng.choice(["#3DE0E6", "#FF4D6D", "#FFD400"]), 0.18), rng.uniform(0, W), rng.uniform(0, H))
    c.alpha_composite(img)
    return c


def barra_uso(c, x, y, frac, ancho=760):
    img, d = capa()
    d.rounded_rectangle([x - ancho / 2, y, x + ancho / 2, y + 100], radius=50, fill=(30, 20, 40, 230), outline=(255, 255, 255, 255), width=6)
    if frac > 0.01:
        d.rounded_rectangle([x - ancho / 2 + 12, y + 12, x - ancho / 2 + 12 + (ancho - 24) * frac, y + 88], radius=38, fill=(255, 212, 0, 255))
    c.alpha_composite(img)


def sello(c, txt, t, color="#FF4D6D", y=1050):
    s = pop_scale(t, 0.25)
    if s:
        hud(rotulo(txt, 180, color, "#FFFFFF", 14, rot=-12), 540, y, (2.2 - 1.2 * s) if s < 1 else 1.0)


def objeto_libro():
    m = Image.new("L", (420, 560), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 420, 560], radius=24, fill=255)
    spr = sprite(m, "#3D7BE0", 181)
    ImageDraw.Draw(spr).rectangle([0, 0, 40, 560], fill=(30, 60, 140, 255))
    r = rotulo("10 %", 130, "#FFD400", "#1A1022", 8)
    spr.alpha_composite(r, (230 - r.width // 2, 200 - r.height // 2))
    r2 = rotulo("DESPIERTA\nTU MENTE", 44, "#FFFFFF", "#1A1022", 4)
    spr.alpha_composite(r2, (230 - r2.width // 2, 380 - r2.height // 2))
    return spr


def objeto_pantalla():
    m = Image.new("L", (760, 480), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 760, 480], radius=30, fill=255)
    spr = sprite(m, "#2B2440", 182)
    d = ImageDraw.Draw(spr)
    d.rounded_rectangle([30, 30, 730, 450], radius=20, fill=(20, 10, 30, 255))
    return spr


@lru_cache(maxsize=1)
def nota_musical():
    m = Image.new("L", (140, 200), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([0, 130, 70, 190], fill=255)
    d.rectangle([52, 20, 68, 160], fill=255)
    d.polygon([(52, 20), (130, 50), (130, 90), (68, 60)], fill=255)
    return sprite(m, "#FFD400", 186, costura=False)


@lru_cache(maxsize=1)
def rayo():
    m = Image.new("L", (120, 180), 0)
    ImageDraw.Draw(m).polygon([(70, 0), (10, 100), (55, 100), (40, 180), (110, 70), (65, 70), (95, 0)], fill=255)
    return sprite(m, "#FFD400", 187, costura=False)


# ----------------------------------------------------------------- escenas
def e_gancho(t, d):
    c = fondo(t)
    cerebro(c, 540, 950, 1.1, t, [("frontal", 1.0)])
    barra_uso(c, 540, 1350, 0.1 * ease_out(t / 0.4))
    texto(c, "10 %", 540, 1560, t - 0.1, 150, "#FFD400")
    return c, dict(zoom=1.0 + 0.12 * ease_out(t / d), temblor=6 if t < 0.25 else 0, t=t)


def e_mentira(t, d):
    c = fondo(t)
    cerebro(c, 540, 950, 1.1, t, todas=0.6)
    sello(c, "MENTIRA", t - 0.1)
    return c, dict(zoom=1.05, temblor=10 if 0.1 < t < 0.35 else 0, t=t)


def e_libro(t, d):
    c = fondo(t, "#2A1C10", "#6B4A2F")
    pegar(c, objeto_libro(), 540, 1000, pop_scale(t - 0.05) * 1.3, rot=math.sin(t * 2) * 4, sombra=True)
    texto(c, "AUTOAYUDA", 540, 1500, t - 0.25, 110, "#FFD400")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_pelicula(t, d):
    c = fondo(t, "#0E0A18", "#2A1C3A")
    pegar(c, objeto_pantalla(), 540, 950, 1.2)
    img, dd = capa()
    for k in range(3):
        dd.polygon([(160 + k * 380, 1500), (100 + k * 380, 1500), (540, 950)], fill=(255, 240, 200, 25))
    c.alpha_composite(img)
    cerebro(c, 540, 930, 0.6, t, [("frontal", 1.0)], cara=False)
    pegar(c, rotulo("10 %", 100, "#FFD400"), 540, 1120, pop_scale(t - 0.2))
    texto(c, "PELÍCULAS", 540, 1500, t - 0.3, 110, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_escaner(t, d):
    c = fondo(t, "#0F1E30", "#1F3B57")
    acostado = nico(t, "sorpresa", 10, -10).rotate(90, expand=True, resample=Image.BICUBIC)
    u = ease_in_out(t / d)
    pegar(c, acostado, 1150 - u * 600, 1150, 0.6)
    img, dd = capa()
    dd.ellipse([200, 650, 880, 1650], outline=(220, 225, 235, 255), width=110)
    c.alpha_composite(img)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([200, 650, 880, 1650], outline=255, width=110)
    c.alpha_composite(sprite(m.crop((0, 0, W, H)), "#DDE2EA", 183, sombreado=False))
    texto(c, "ESCÁNER", 540, 1780, t - 0.15, 110, "#7FD3FF")
    return c, dict(zoom=1.0, t=t)


def e_pantalla_todo(t, d):
    c = fondo(t, "#0F1E30", "#1F3B57")
    pegar(c, objeto_pantalla(), 540, 1000, 1.3)
    cerebro(c, 540, 990, 0.75, t, todas=clamp01(t / 0.6), cara=False)
    texto(c, "NADA DORMIDO", 540, 1500, t - 0.35, 110, "#FFE45C")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_reloj_dia(t, d):
    c = fondo(t)
    orden = list(ZONAS)
    zs = [(z, clamp01((t / d) * len(orden) - i)) for i, z in enumerate(orden)]
    cerebro(c, 540, 1000, 1.2, t, zs)
    pegar(c, prop("icono", "sol"), 180 + clamp01(t / d) * 720, 500 + math.sin(clamp01(t / d) * math.pi) * -150, 0.6)
    texto(c, "TODO SE ACTIVA", 540, 1520, t - 0.2, 110, "#FFE45C")
    return c, dict(zoom=1.05, t=t)


def e_dedo(t, d):
    c = fondo(t)
    cerebro(c, 540, 820, 0.9, t, [("motora", clamp01(t / 0.3))])
    pegar(c, nico(t, "aja", 5, 160 + 10 * math.sin(t * 10)), 540, 1880, 0.95, ancla="abajo")
    return c, dict(zoom=1.0, t=t)


def taza():
    m = Image.new("L", (360, 320), 0)
    dm = ImageDraw.Draw(m)
    dm.rounded_rectangle([20, 60, 280, 300], radius=50, fill=255)
    dm.ellipse([240, 110, 350, 230], fill=255)
    dm.ellipse([272, 142, 318, 198], fill=0)
    return sprite(m, "#FFFFFF", 184, color_costura=(200, 200, 210))


def e_cafe(t, d):
    c = fondo(t, "#2A1C10", "#6B4A2F")
    cerebro(c, 540, 820, 0.9, t, [("olfato", clamp01(t / 0.3))])
    pegar(c, taza(), 540, 1400, 1.1, sombra=True)
    img, dd = capa()
    for k in range(3):
        x = 470 + k * 60
        dd.line([(x + math.sin(t * 3 + j * 0.6 + k) * 18, 1260 - j * 20) for j in range(10)], fill=(255, 255, 255, 140), width=10)
    c.alpha_composite(img)
    return c, dict(zoom=1.0, t=t)


def e_cancion(t, d):
    c = fondo(t, "#1A1440", "#5A2F6B")
    cerebro(c, 540, 820, 0.9, t, [("musica", clamp01(t / 0.3))])
    for k in range(4):
        ph = (t * 0.8 + k / 4) % 1
        pegar(c, nota_musical(), 300 + k * 160, 1550 - ph * 400, 1, alfa=1 - ph)
    texto(c, "REGIONES DISTINTAS", 540, 1700, t - 0.3, 85, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_dano(t, d):
    c = fondo(t, "#2A0F1A", "#5A1F35")
    cerebro(c, 540, 1000, 1.2, t)
    rng = random.Random(8)
    for k, z in enumerate(ZONAS):
        if t > 0.2 + k * 0.25:
            zx, zy = ZONAS[z]
            hud(rotulo("!", 110, "#FFFFFF", "#FF4D6D", 12), 540 + (zx - 350) * 1.2, 1000 + (zy - 260) * 1.2, pop_scale(t - 0.2 - k * 0.25))
    texto(c, "CONSECUENCIAS", 540, 1560, t - 0.3, 110, "#FF8A9A")
    return c, dict(zoom=1.0 + 0.05 * t, t=t)


def e_golpe(t, d):
    c = fondo(t)
    golpe = t > 0.35
    pegar(c, nico(t, "espiral" if golpe else "sorpresa", 160, 160), 540, 1800 + (math.sin(t * 40) * 6 if golpe else 0), 1.0, ancla="abajo")
    if golpe:
        for k in range(5):
            a = t * 4 + k / 5 * math.tau
            pegar(c, brillo(18, "#FFD400", 1), 540 + math.cos(a) * 170, 960 + math.sin(a) * 40)
    texto(c, "SÍ IMPORTA", 540, 760, t - 0.4, 130, "#FFD400")
    return c, dict(zoom=1.15, fy=0.55, temblor=12 if 0.35 < t < 0.55 else 0, t=t)


def etiqueta_precio():
    m = Image.new("L", (520, 260), 0)
    dm = ImageDraw.Draw(m)
    dm.polygon([(0, 130), (110, 0), (520, 0), (520, 260), (110, 260)], fill=255)
    dm.ellipse([70, 105, 120, 155], fill=0)
    spr = sprite(m, "#FFD400", 185)
    r = rotulo("$$$", 120, "#3A2A20", "#FFFFFF", 6)
    spr.alpha_composite(r, (320 - r.width // 2, 130 - r.height // 2))
    return spr


def e_caro(t, d):
    c = fondo(t)
    cerebro(c, 540, 950, 1.0, t, todas=0.4)
    pegar(c, etiqueta_precio(), 760, 1320, pop_scale(t - 0.2) * 0.9, rot=-15 + math.sin(t * 4) * 5, sombra=True)
    texto(c, "ÓRGANO CARÍSIMO", 540, 1650, t - 0.3, 100, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_giro(t, d):
    c = fondo(0.0)
    cerebro(c, 540, 950, 1.0, 0.0, cara=True)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def e_peso(t, d):
    c = fondo(t)
    m = nico(0, "normal", 10, -10)
    sil = Image.new("RGBA", m.size, (61, 224, 230, 0))
    sil.putalpha(m.getchannel("A").point(lambda v: int(v * 0.5)))
    pegar(c, sil, 540, 1750, 1.3, ancla="abajo")
    cerebro(c, 540, 860, 0.32, t, cara=False)
    tag(c, "2–3 %", "DEL PESO", 540, 1450, t - 0.3, 130)
    return c, dict(zoom=1.0, t=t)


def e_energia(t, d):
    c = fondo(t)
    img, dd = capa()
    u = ease_out(clamp01((t - 0.15) / 0.6))
    dd.ellipse([240, 700, 840, 1300], fill=(60, 50, 90, 255), outline=(255, 255, 255, 255), width=8)
    dd.pieslice([240, 700, 840, 1300], -90, -90 + 72 * u, fill=(255, 212, 0, 255), outline=(255, 255, 255, 255), width=8)
    c.alpha_composite(img)
    cerebro(c, 640, 860, 0.22, t, cara=False)
    tag(c, "≈ 20 %", "ENERGÍA", 540, 1480, t - 0.6, 140)
    return c, dict(zoom=1.0, temblor=8 if 0.6 < t < 0.8 else 0, t=t)


def e_gloton(t, d):
    c = fondo(t, "#2A1C10", "#6B4A2F")
    cerebro(c, 540, 950, 1.1, t, todas=0.5 + 0.3 * math.sin(t * 6))
    for k in range(6):
        ph = (t * 1.2 + k / 6) % 1
        a = k / 6 * math.tau
        pegar(c, rayo(), 540 + math.cos(a) * 500 * (1 - ph), 950 + math.sin(a) * 500 * (1 - ph), 1, alfa=ph)
    texto(c, "GLOTÓN", 540, 1520, t - 0.2, 140, "#FFD400")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_duerme(t, d):
    c = fondo(t, "#0B1030", "#27306A")
    particulas(c, t, 25, (255, 240, 140), 6, (3, 6), 6, 200)
    pegar(c, prop("cama"), 540, 1550, 1.0)
    acostado = nico(t, "dormido", 10, -10).rotate(90, expand=True, resample=Image.BICUBIC)
    pegar(c, acostado, 470, 1420, 0.62)
    pegar(c, prop("manta"), 610, 1480, 1.0, sy=1 + 0.02 * math.sin(t * 2.5))
    cerebro(c, 540, 850, 0.65, t, todas=0.5 + 0.3 * math.sin(t * 3), cara=False)
    texto(c, "INCLUSO\nDURMIENDO", 540, 1120, t - 0.2, 95, "#BFD8FF")
    return c, dict(zoom=1.0, t=t)


def e_cta(t, d):
    c = fondo(t)
    pegar(c, nico(t, "feliz", 10, 140 + 25 * math.sin(t * 10)), 330, 1820, 0.95, ancla="abajo")
    cerebro(c, 790, 1350, 0.45, t)
    globo_texto(c, "¿QUÉ MITO\nDESTRUYO AHORA?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto"]),
    (0, 0.55, e_mentira, None, [("buzz", 0.1), ("impacto", 0.12)]),
    (1, 0.0, e_libro, "barrido", ["whoosh", ("pop", 0.05)]),
    (1, 0.5, e_pelicula, None, ["click", ("pop", 0.2)]),
    (2, 0.0, e_escaner, "barrido", ["whoosh_grave"]),
    (2, 0.55, e_pantalla_todo, None, ["riser_corto", ("ding", 0.6)]),
    (3, 0.0, e_reloj_dia, None, ["pop3"]),
    (4, 0.0, e_dedo, "barrido", ["whoosh", "blip"]),
    (4, 0.35, e_cafe, None, ["burbujas", "blip"]),
    (4, 0.68, e_cancion, None, ["ding", "blip"]),
    (5, 0.0, e_dano, "barrido", ["whoosh", ("impacto", 0.2), ("pop", 0.45), ("pop", 0.7)]),
    (6, 0.0, e_golpe, None, [("bonk", 0.35)]),
    (7, 0.0, e_caro, "barrido", ["whoosh", ("ding", 0.2)]),
    (8, 0.0, e_giro, None, ["scratch"]),
    (9, 0.0, e_peso, None, ["whoosh_grave", ("pop", 0.3)]),
    (10, 0.0, e_energia, None, ["riser_corto", ("impacto", 0.6)]),
    (11, 0.0, e_gloton, None, ["squish", ("pop", 0.2)]),
    (11, 0.5, e_duerme, None, ["whoosh_suave"]),
    (12, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]

ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
