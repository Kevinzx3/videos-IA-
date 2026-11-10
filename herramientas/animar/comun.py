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
