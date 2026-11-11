"""Utilidades compartidas por los guiones de escenas (texto, etiquetas, tiempos)."""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

from motor import *  # noqa
from motor import _comp  # noqa

RAIZ = Path(__file__).resolve().parents[2]


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


def capa():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def construir_escenas(guion_json, plan):
    """plan: lista de (segmento, fracción, función, transición, sfx).

    El inicio de cada escena = inicio del segmento + fracción · duración del segmento,
    con los tiempos reales (alineados con la voz) del JSON.
    """
    segs = json.load(open(guion_json, encoding="utf-8"))["segmentos"]
    dur = segs[-1][1]
    inicios = [segs[i][0] + fr * (segs[i][1] - segs[i][0]) for i, fr, *_ in plan]
    esc = []
    for k, (i, fr, f, tr, sfx) in enumerate(plan):
        fin = inicios[k + 1] if k + 1 < len(plan) else dur
        esc.append(dict(ini=inicios[k], fin=fin, f=f, tr=tr, sfx=sfx))
    return esc, dur


def giro(c, t, color="#FF4D6D"):
    """Congelado + rótulo EL GIRO (usar con fondo ya oscurecido)."""
    texto(c, "EL GIRO", 540, 1100, t, 170, color, rot=-6)


def boton_seguir(t, y=1330):
    late = 1 + 0.06 * math.sin(t * 8)
    hud(prop("seguir"), 540, y, pop_scale(t - 0.2) * late, True)


def globo_texto(c, txt, x, y, tl, tam=74):
    s = pop_scale(tl, 0.35)
    if s:
        g = prop("globo").copy()
        r = rotulo(txt, tam, "#1A1022", "#FFFFFF", 4)
        g.alpha_composite(r, (430 - r.width // 2, 140 - r.height // 2))
        hud(g, x, y, s, True)


def corazon(color="#FF4D6D", seed=140):
    m, d = nueva_mascara(240, 220)
    s = SS
    d.ellipse([0, 0, 130 * s, 130 * s], fill=255)
    d.ellipse([110 * s, 0, 240 * s, 130 * s], fill=255)
    d.polygon([(8 * s, 90 * s), (232 * s, 90 * s), (120 * s, 215 * s)], fill=255)
    return sprite(cerrar_mascara(m), color, seed)


def elemento(simbolo, nombre, color):
    """Casilla de tabla periódica."""
    m = Image.new("L", (300, 340), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 300, 340], radius=30, fill=255)
    spr = sprite(m, color, 141)
    r = rotulo(simbolo, 150, "#FFFFFF", "#1A1022", 8)
    spr.alpha_composite(r, (150 - r.width // 2, 150 - r.height // 2))
    n = rotulo(nombre, 46, "#FFFFFF", "#1A1022", 4)
    spr.alpha_composite(n, (150 - n.width // 2, 285 - n.height // 2))
    return spr


def ecg(c, t, x0, x1, y, plano=0.0, color=(90, 255, 140)):
    """Línea de electrocardiograma; plano=1 la aplana."""
    img, d = capa()
    pts = []
    for x in range(int(x0), int(x1), 6):
        ph = ((x - x0) / 260 - t * 1.2) % 1
        v = 0
        if 0.40 < ph < 0.45:
            v = -160
        elif 0.45 < ph < 0.50:
            v = 90
        elif 0.30 < ph < 0.36:
            v = -25
        pts.append((x, y + v * (1 - plano)))
    d.line(pts, fill=color + (255,), width=10)
    c.alpha_composite(img)


# ------------------------------------------------------------ extras (día 3-4)
import random as _random
from functools import lru_cache as _lru


@_lru(maxsize=4)
def _cielo_estrellas(c1="#05040F", c2="#1A1440", n=320, seed=1):
    c = degradado(W, H, [(0, c1), (1, c2)])
    img, d = capa()
    rng = _random.Random(seed)
    for _ in range(n):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.choice([1, 1.5, 2, 3])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rng.randint(110, 255)))
    c.alpha_composite(img)
    return c


def cielo_estrellas(t, c1="#05040F", c2="#1A1440"):
    c = _cielo_estrellas(c1, c2).copy()
    particulas(c, t, 25, (255, 255, 255), 4, (1, 2.5), 6, 200)
    return c


@_lru(maxsize=16)
def planeta(color, r=300, bandas=None, seed=200):
    """Esfera de fieltro con bandas de nubes."""
    m = Image.new("L", (2 * r, 2 * r), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 2 * r, 2 * r], fill=255)
    spr = sprite(m, color, seed)
    if bandas:
        rng = _random.Random(seed)
        capa_b = Image.new("L", (2 * r, 2 * r), 0)
        db = ImageDraw.Draw(capa_b)
        for k in range(7):
            y = rng.uniform(0.15, 0.85) * 2 * r
            db.line([(x, y + math.sin(x / 50 + k) * 18) for x in range(0, 2 * r, 10)], fill=255, width=int(r * 0.09))
        from PIL import ImageChops
        capa_b = ImageChops.multiply(capa_b, m)
        spr.alpha_composite(sprite(capa_b, bandas, seed + 1, costura=False))
    # sombreado esférico
    sh = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.ellipse([r * 0.5, r * 0.3, 2.4 * r, 2.4 * r], fill=(10, 0, 30, 110))
    from PIL import ImageFilter as _F, ImageChops as _C
    sh = sh.filter(_F.GaussianBlur(r * 0.25))
    a = _C.multiply(sh.getchannel("A"), m)
    sh.putalpha(a)
    spr.alpha_composite(sh)
    return spr


def calendario(dia, mes, anio=None):
    m = Image.new("L", (420, 470), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 420, 470], radius=36, fill=255)
    spr = sprite(m, "#FFFFFF", 210, color_costura=(200, 200, 210))
    d = ImageDraw.Draw(spr)
    d.rounded_rectangle([0, 0, 420, 130], radius=36, fill=(255, 77, 109, 255))
    d.rectangle([0, 90, 420, 130], fill=(255, 77, 109, 255))
    r = rotulo(mes, 70, "#FFFFFF", "#9E1F3A", 4)
    spr.alpha_composite(r, (210 - r.width // 2, 65 - r.height // 2))
    r = rotulo(dia, 190, "#1A1022", "#FFFFFF", 4)
    spr.alpha_composite(r, (210 - r.width // 2, 290 - r.height // 2))
    if anio:
        r = rotulo(anio, 56, "#FF4D6D", "#FFFFFF", 4)
        spr.alpha_composite(r, (210 - r.width // 2, 420 - r.height // 2))
    return spr


def sello(c, txt, t, color="#FF4D6D", y=1050, tam=170, rot=-12):
    s = pop_scale(t, 0.25)
    if s:
        hud(rotulo(txt, tam, color, "#FFFFFF", 14, rot=rot), 540, y, (2.2 - 1.2 * s) if s < 1 else 1.0)


def barras(c, valores, etiquetas, colores, t, x0=180, y0=1450, ancho=720, alto_max=650, maximo=None):
    """Gráfico de barras animado (crecen al entrar)."""
    maximo = maximo or max(valores)
    n = len(valores)
    w = ancho / n * 0.6
    img, d = capa()
    for k, (v, col) in enumerate(zip(valores, colores)):
        u = ease_out(clamp01((t - k * 0.15) / 0.6))
        h = alto_max * v / maximo * u
        x = x0 + (k + 0.5) * ancho / n
        d.rounded_rectangle([x - w / 2, y0 - h, x + w / 2, y0], radius=18, fill=hexrgb(col) + (255,), outline=(255, 255, 255, 255), width=5)
    c.alpha_composite(img)
    for k, (v, et) in enumerate(zip(valores, etiquetas)):
        x = x0 + (k + 0.5) * ancho / n
        u = ease_out(clamp01((t - k * 0.15) / 0.6))
        hud(rotulo(et, 64 if n < 3 else 46), x, y0 + 60, 1)
        if u > 0.6:
            hud(rotulo(str(v), 80, "#FFD400"), x, y0 - alto_max * v / maximo - 60, pop_scale((u - 0.6) * 2))


def icono_carta(txt, color, tam=300, seed=220):
    """Tarjeta cuadrada con texto grande (para listas de teorías, iconos, etc.)."""
    m = Image.new("L", (tam, tam), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, tam, tam], radius=tam // 6, fill=255)
    spr = sprite(m, color, seed)
    r = rotulo(txt, int(tam * 0.22), "#FFFFFF", "#1A1022", 6)
    if r.width > tam * 0.92:  # ajustar al ancho de la tarjeta
        f = tam * 0.92 / r.width
        r = r.resize((int(r.width * f), int(r.height * f)), Image.LANCZOS)
    spr.alpha_composite(r, (tam // 2 - r.width // 2, tam // 2 - r.height // 2))
    return spr


def ondas(c, x, y, t, color=(160, 255, 200), n=4, r_max=420, grosor=10, ang=(200, 340)):
    img, d = capa()
    for k in range(n):
        r = ((t * 160 + k * r_max / n) % r_max) + 20
        a = int(230 * (1 - r / r_max))
        d.arc([x - r, y - r, x + r, y + r], ang[0], ang[1], fill=color + (a,), width=grosor)
    c.alpha_composite(img)
