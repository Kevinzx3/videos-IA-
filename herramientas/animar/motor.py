"""Motor de animación 2.5D "recortable de fieltro" para Shorts 9:16.

Todo se dibuja por código con Pillow: texturas de fieltro, bordes cosidos,
personajes (Nico y Chispa), props, fondos con parallax, rótulos y cámara.
"""
import math
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
SS = 2  # supersampling para máscaras

FUENTE_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FUENTE_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"


# ---------------------------------------------------------------- utilidades
def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mezcla(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def aclarar(c, t):
    return mezcla(c, (255, 255, 255), t)


def oscurecer(c, t):
    return mezcla(c, (0, 0, 0), t)


def ease_out(u):
    u = max(0.0, min(1.0, u))
    return 1 - (1 - u) ** 3


def ease_in_out(u):
    u = max(0.0, min(1.0, u))
    return 3 * u * u - 2 * u * u * u


def back_out(u, s=1.9):
    u = max(0.0, min(1.0, u))
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def pop_scale(t, dur=0.28):
    """0 -> 1.15 -> 1 en `dur` segundos."""
    if t <= 0:
        return 0.0
    return back_out(t / dur, 2.6) if t < dur else 1.0


def clamp01(u):
    return max(0.0, min(1.0, u))


@lru_cache(maxsize=4)
def _ruido(seed, w=1200, h=2100):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (h // 2, w // 2)).astype(np.float32)
    img = Image.fromarray(np.uint8(np.clip(128 + n * 40, 0, 255)), "L").resize((w, h), Image.BILINEAR)
    fino = Image.fromarray(np.uint8(np.clip(128 + rng.normal(0, 1, (h, w)) * 30, 0, 255)), "L")
    return Image.blend(img, fino, 0.5)


def textura(size, seed=1, fuerza=0.13):
    """Multiplicador de grano tipo fieltro (L, ~128 = neutro)."""
    r = _ruido(seed)
    w, h = size
    ox = (seed * 97) % max(1, r.width - w) if r.width > w else 0
    oy = (seed * 61) % max(1, r.height - h) if r.height > h else 0
    crop = r.crop((ox, oy, ox + w, oy + h)) if (w <= r.width and h <= r.height) else r.resize((w, h))
    a = np.asarray(crop, np.float32) / 128.0
    return 1 + (a - 1) * (fuerza / 0.3)


# ------------------------------------------------------------- sprites fieltro
def nueva_mascara(w, h):
    m = Image.new("L", (w * SS, h * SS), 0)
    return m, ImageDraw.Draw(m)


def cerrar_mascara(m):
    return m.resize((m.width // SS, m.height // SS), Image.LANCZOS)


def sprite(mask, color, seed=3, costura=True, pelo=False, sombreado=True, color_costura=None, grano=0.13):
    """Convierte una máscara L en sprite RGBA de fieltro con borde cosido."""
    color = hexrgb(color) if isinstance(color, str) else color
    w, h = mask.size
    if pelo:  # borde irregular tipo pelaje
        rng = np.random.default_rng(seed)
        n = Image.fromarray(np.uint8(rng.integers(0, 255, (h, w))), "L").filter(ImageFilter.GaussianBlur(1.2))
        m2 = mask.filter(ImageFilter.GaussianBlur(3))
        a = np.asarray(m2, np.float32) + (np.asarray(n, np.float32) - 128) * 1.6
        mask = Image.fromarray(np.uint8(np.clip((a - 110) * 4, 0, 255)), "L")
    base = np.ones((h, w, 3), np.float32) * np.array(color, np.float32)
    tex = textura((w, h), seed, grano)[..., None]
    base *= tex
    if sombreado:
        grad = np.linspace(1.08, 0.82, h, dtype=np.float32)[:, None, None]
        base *= grad
        # oclusión suave en el borde
        inner = np.asarray(mask.filter(ImageFilter.GaussianBlur(10)), np.float32)[..., None] / 255
        base *= 0.78 + 0.22 * inner
    if pelo:
        rng = random.Random(seed)
        img = Image.fromarray(np.uint8(np.clip(base, 0, 255)), "RGB")
        d = ImageDraw.Draw(img)
        for _ in range(int(w * h / 90)):
            x, y = rng.randrange(w), rng.randrange(h)
            L = rng.randint(5, 13)
            ang = math.radians(rng.uniform(70, 110))
            c = aclarar(color, 0.25) if rng.random() < 0.5 else oscurecer(color, 0.25)
            d.line([(x, y), (x + math.cos(ang) * L * 0.4, y + math.sin(ang) * L)], fill=c, width=1)
        base = np.asarray(img, np.float32)
    rgb = Image.fromarray(np.uint8(np.clip(base, 0, 255)), "RGB")
    out = rgb.convert("RGBA")
    out.putalpha(mask)
    if costura and min(w, h) > 30:
        e1 = mask.filter(ImageFilter.MinFilter(9))
        e2 = e1.filter(ImageFilter.MinFilter(5))
        anillo = ImageChops.subtract(e1, e2)
        yy, xx = np.mgrid[0:h, 0:w]
        rayas = ((xx + yy) // 9) % 2 == 0
        a = np.asarray(anillo, np.float32) * rayas
        cc = color_costura or aclarar(color, 0.55)
        capa = Image.new("RGBA", (w, h), cc + (0,))
        capa.putalpha(Image.fromarray(np.uint8(a * 0.85), "L"))
        out = Image.alpha_composite(out, capa)
    return out


def pegar(lienzo, spr, cx, cy, escala=1.0, rot=0.0, alfa=1.0, sombra=False, sx=None, sy=None, ancla="centro"):
    """Pega un sprite centrado (o anclado abajo) con escala/rotación/alfa."""
    if spr is None:
        return
    ex = escala * (sx if sx is not None else 1.0)
    ey = escala * (sy if sy is not None else 1.0)
    if ex <= 0.01 or ey <= 0.01 or alfa <= 0.01:
        return
    s = spr
    if abs(ex - 1) > 1e-3 or abs(ey - 1) > 1e-3:
        s = s.resize((max(1, int(s.width * ex)), max(1, int(s.height * ey))), Image.BILINEAR)
    if abs(rot) > 0.05:
        s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alfa < 0.999:
        a = s.getchannel("A").point(lambda v: int(v * alfa))
        s = s.copy()
        s.putalpha(a)
    x = int(cx - s.width / 2)
    y = int(cy - s.height / 2) if ancla == "centro" else int(cy - s.height)
    if sombra:
        sh = Image.new("RGBA", s.size, (20, 10, 30, 0))
        sh.putalpha(s.getchannel("A").point(lambda v: int(v * 0.35)))
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        _comp(lienzo, sh, x + 12, y + 18)
    _comp(lienzo, s, x, y)


def _comp(lienzo, s, x, y):
    W0, H0 = lienzo.size
    if x >= W0 or y >= H0 or x + s.width <= 0 or y + s.height <= 0:
        return
    cx0, cy0 = max(0, -x), max(0, -y)
    cx1, cy1 = min(s.width, W0 - x), min(s.height, H0 - y)
    lienzo.alpha_composite(s.crop((cx0, cy0, cx1, cy1)), (x + cx0, y + cy0))


def sombra_suelo(lienzo, cx, cy, ancho, alfa=0.35):
    m = Image.new("RGBA", (int(ancho * 1.4), int(ancho * 0.4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(m)
    d.ellipse([ancho * 0.2, ancho * 0.08, ancho * 1.2, ancho * 0.32], fill=(15, 10, 25, int(255 * alfa)))
    m = m.filter(ImageFilter.GaussianBlur(12))
    _comp(lienzo, m, int(cx - m.width / 2), int(cy - m.height / 2))


def brillo(radio, color, intensidad=0.8):
    color = hexrgb(color) if isinstance(color, str) else color
    s = int(radio * 4)
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).ellipse([s * 0.3, s * 0.3, s * 0.7, s * 0.7], fill=int(255 * intensidad))
    m = m.filter(ImageFilter.GaussianBlur(radio * 0.45))
    out = Image.new("RGBA", (s, s), color + (0,))
    out.putalpha(m)
    return out


# ------------------------------------------------------------------- rótulos
HUD = []  # elementos en espacio de pantalla (se pegan después de la cámara)


def hud(spr, x, y, escala=1.0, sombra=False):
    HUD.append((spr, x, y, escala, sombra))


def pintar_hud(img):
    for spr, x, y, e, sh in HUD:
        pegar(img, spr, x, y, e, sombra=sh)
    HUD.clear()

@lru_cache(maxsize=64)
def fuente(tam, negra=True):
    return ImageFont.truetype(FUENTE_BLACK if negra else FUENTE_XB, tam)


@lru_cache(maxsize=256)
def rotulo(texto, tam=120, color="#FFFFFF", borde="#1A1022", grosor=10, rot=0):
    """Texto grande con contorno grueso y sombra (sprite RGBA)."""
    f = fuente(tam)
    lineas = texto.split("\n")
    anchos = [f.getbbox(l, stroke_width=grosor) for l in lineas]
    w = max(b[2] - b[0] for b in anchos) + grosor * 4
    lh = int(tam * 1.12)
    h = lh * len(lineas) + grosor * 4
    img = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lineas):
        b = f.getbbox(l, stroke_width=grosor)
        x = (w + 30 - (b[2] - b[0])) / 2 - b[0]
        y = 10 + i * lh - b[1] + grosor
        d.text((x + 6, y + 10), l, font=f, fill=(10, 5, 20, 140), stroke_width=grosor, stroke_fill=(10, 5, 20, 140))
        d.text((x, y), l, font=f, fill=hexrgb(color), stroke_width=grosor, stroke_fill=hexrgb(borde))
    if rot:
        img = img.rotate(rot, resample=Image.BICUBIC, expand=True)
    return img


@lru_cache(maxsize=64)
def etiqueta(valor, unidad="", tam=130):
    """Píldora de dato: número amarillo + unidad pequeña (como la del '300 kg')."""
    f1, f2 = fuente(tam), fuente(int(tam * 0.42))
    b1 = f1.getbbox(valor)
    b2 = f2.getbbox(unidad) if unidad else (0, 0, 0, 0)
    w = (b1[2] - b1[0]) + ((b2[2] - b2[0]) + 18 if unidad else 0) + 90
    h = int(tam * 1.25)
    img = Image.new("RGBA", (w + 20, h + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([14, 22, w + 14, h + 22], radius=h // 2, fill=(5, 0, 15, 90))
    d.rounded_rectangle([4, 8, w + 4, h + 8], radius=h // 2, fill=(26, 20, 34, 215), outline=(255, 212, 0, 255), width=5)
    x = 49 - b1[0]
    y = 8 + (h - (b1[3] - b1[1])) / 2 - b1[1]
    d.text((x, y), valor, font=f1, fill=(255, 212, 0))
    if unidad:
        x2 = 49 + (b1[2] - b1[0]) + 14 - b2[0]
        d.text((x2, y + (b1[3] - b1[1]) - (b2[3] - b2[1]) - b2[1] + b1[1]), unidad, font=f2, fill=(255, 255, 255))
    return img


# ------------------------------------------------------------------ fondos
def degradado(w, h, paradas):
    """paradas: [(pos, '#hex'), ...] vertical."""
    ys = np.linspace(0, 1, h, dtype=np.float32)
    out = np.zeros((h, 3), np.float32)
    pos = [p for p, _ in paradas]
    cols = [np.array(hexrgb(c), np.float32) for _, c in paradas]
    for i in range(3):
        out[:, i] = np.interp(ys, pos, [c[i] for c in cols])
    arr = np.repeat(out[:, None, :], w, axis=1)
    arr *= textura((w, h), 11, 0.04)[..., None]
    arr += np.random.default_rng(1).uniform(-2, 2, arr.shape)
    return Image.fromarray(np.uint8(np.clip(arr, 0, 255)), "RGB").convert("RGBA")


def capa_pinos(w, h, color, seed, base_y, alto, n):
    m, d = nueva_mascara(w, h)
    rng = random.Random(seed)
    s = SS
    xs = sorted(rng.uniform(-80, w + 80) for _ in range(n))
    for x in xs:
        a = alto * rng.uniform(0.7, 1.15)
        ancho = a * 0.38
        for k in range(4):  # pisos del pino
            y0 = base_y - a + k * a * 0.22
            ww = ancho * (0.45 + k * 0.2)
            d.polygon([((x) * s, y0 * s), ((x - ww) * s, (y0 + a * 0.32) * s), ((x + ww) * s, (y0 + a * 0.32) * s)], fill=255)
    d.rectangle([0, base_y * s - 2, w * s, h * s], fill=255)
    return sprite(cerrar_mascara(m), color, seed, costura=False, sombreado=False, grano=0.08)


def capa_edificios(w, h, color, seed, base_y, alto, ventanas=None):
    m, d = nueva_mascara(w, h)
    rng = random.Random(seed)
    s = SS
    x = -40
    rects = []
    while x < w + 40:
        bw = rng.uniform(110, 220)
        bh = alto * rng.uniform(0.5, 1.1)
        d.rectangle([x * s, (base_y - bh) * s, (x + bw - 8) * s, h * s], fill=255)
        if rng.random() < 0.3:
            d.polygon([(x * s, (base_y - bh) * s), ((x + bw / 2) * s, (base_y - bh - 50) * s), ((x + bw - 8) * s, (base_y - bh) * s)], fill=255)
        rects.append((x, base_y - bh, bw - 8, bh))
        x += bw
    d.rectangle([0, base_y * s, w * s, h * s], fill=255)
    spr = sprite(cerrar_mascara(m), color, seed, costura=False, sombreado=False, grano=0.08)
    if ventanas:
        dd = ImageDraw.Draw(spr)
        for (x0, y0, bw, bh) in rects:
            for yy in range(int(y0 + 30), int(base_y - 30), 56):
                for xx in range(int(x0 + 18), int(x0 + bw - 30), 46):
                    if rng.random() < 0.45:
                        dd.rectangle([xx, yy, xx + 20, yy + 28], fill=hexrgb(ventanas) + (230,))
    return spr


def suelo_hierba(w, h, y0, color="#6E8A2E"):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rectangle([0, y0, w, h], fill=255)
    spr = sprite(m, color, 21, costura=False, grano=0.25)
    d = ImageDraw.Draw(spr)
    rng = random.Random(5)
    c = hexrgb(color)
    for _ in range(4000):
        x, y = rng.uniform(0, w), rng.uniform(y0, h)
        L = 6 + (y - y0) / (h - y0) * 18
        d.line([(x, y), (x + rng.uniform(-3, 3), y - L)], fill=aclarar(c, rng.uniform(0, .3)) if rng.random() < .5 else oscurecer(c, rng.uniform(0, .3)), width=2)
    d.line([(0, y0), (w, y0)], fill=(255, 245, 220, 200), width=3)
    return spr


def particulas(lienzo, t, n=40, color=(255, 230, 180), seed=7, tam=(2, 5), vel=18, alfa=150):
    rng = random.Random(seed)
    capa = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    w, h = lienzo.size
    for i in range(n):
        x0, y0 = rng.uniform(0, w), rng.uniform(0, h)
        sp = rng.uniform(0.4, 1.2) * vel
        r = rng.uniform(*tam)
        ph = rng.uniform(0, 6.28)
        x = (x0 + math.sin(t * 0.7 + ph) * 25) % w
        y = (y0 - t * sp) % h
        a = int(alfa * (0.5 + 0.5 * math.sin(t * 2 + ph)))
        d.ellipse([x - r, y - r, x + r, y + r], fill=color + (a,))
    lienzo.alpha_composite(capa)


# ---------------------------------------------------------------- personajes
PIEL = "#F2C29B"
MOSTAZA = "#E8A93B"
ROJO = "#D64545"
VERDE = "#4E8F4A"
MARINO = "#2C3E66"
BOTAS = "#7A4B2A"
OSCURO = (40, 28, 30)


@lru_cache(maxsize=64)
def _parte(nombre, traje=MOSTAZA):
    """Partes de Nico en coordenadas locales (sprites cacheados)."""
    if nombre == "cabeza":
        m, d = nueva_mascara(250, 250)
        d.ellipse([10 * SS, 10 * SS, 240 * SS, 240 * SS], fill=255)
        return sprite(cerrar_mascara(m), PIEL, 31)
    if nombre == "oreja":
        m, d = nueva_mascara(60, 70)
        d.ellipse([4 * SS, 4 * SS, 56 * SS, 66 * SS], fill=255)
        return sprite(cerrar_mascara(m), oscurecer(hexrgb(PIEL), 0.05), 32, costura=False)
    if nombre == "gorro":
        m, d = nueva_mascara(280, 210)
        d.pieslice([20 * SS, 30 * SS, 260 * SS, 330 * SS], 180, 360, fill=255)
        return sprite(cerrar_mascara(m), ROJO, 33)
    if nombre == "doblez":
        m, d = nueva_mascara(290, 70)
        d.rounded_rectangle([5 * SS, 8 * SS, 285 * SS, 62 * SS], radius=26 * SS, fill=255)
        return sprite(cerrar_mascara(m), oscurecer(hexrgb(ROJO), 0.12), 34)
    if nombre == "pompon":
        m, d = nueva_mascara(90, 90)
        d.ellipse([8 * SS, 8 * SS, 82 * SS, 82 * SS], fill=255)
        return sprite(cerrar_mascara(m), "#F4EDE4", 35, pelo=True, costura=False)
    if nombre == "torso":
        m, d = nueva_mascara(300, 290)
        d.rounded_rectangle([30 * SS, 10 * SS, 270 * SS, 280 * SS], radius=70 * SS, fill=255)
        d.polygon([(20 * SS, 280 * SS), (40 * SS, 120 * SS), (260 * SS, 120 * SS), (280 * SS, 280 * SS)], fill=255)
        spr = sprite(cerrar_mascara(m), traje, 36)
        d2 = ImageDraw.Draw(spr)
        c = oscurecer(hexrgb(traje), 0.25)
        d2.line([(150, 40), (150, 270)], fill=c + (255,), width=5)
        for y in (110, 170, 230):
            d2.ellipse([128, y - 9, 146, y + 9], fill=(60, 40, 30, 255))
        return spr
    if nombre == "mochila":
        m, d = nueva_mascara(340, 260)
        d.rounded_rectangle([10 * SS, 10 * SS, 330 * SS, 250 * SS], radius=60 * SS, fill=255)
        return sprite(cerrar_mascara(m), VERDE, 37)
    if nombre == "tirante":
        m, d = nueva_mascara(40, 200)
        d.rounded_rectangle([4 * SS, 0, 36 * SS, 200 * SS], radius=14 * SS, fill=255)
        return sprite(cerrar_mascara(m), oscurecer(hexrgb(VERDE), 0.15), 38, costura=False)
    if nombre == "brazo":
        m, d = nueva_mascara(80, 210)
        d.rounded_rectangle([8 * SS, 0, 72 * SS, 170 * SS], radius=32 * SS, fill=255)
        spr = sprite(cerrar_mascara(m), traje, 39)
        mano = Image.new("L", (80 * SS, 210 * SS), 0)
        ImageDraw.Draw(mano).ellipse([10 * SS, 140 * SS, 70 * SS, 205 * SS], fill=255)
        ms = sprite(cerrar_mascara(mano), PIEL, 40, costura=False)
        out = Image.new("RGBA", (80, 210), (0, 0, 0, 0))
        out.alpha_composite(ms)
        out.alpha_composite(spr)
        return out
    if nombre == "pierna":
        m, d = nueva_mascara(80, 160)
        d.rounded_rectangle([10 * SS, 0, 70 * SS, 130 * SS], radius=24 * SS, fill=255)
        pierna = sprite(cerrar_mascara(m), MARINO, 41)
        b, db = nueva_mascara(80, 160)
        db.rounded_rectangle([0, 110 * SS, 80 * SS, 158 * SS], radius=22 * SS, fill=255)
        bota = sprite(cerrar_mascara(b), BOTAS, 42, costura=False)
        out = Image.new("RGBA", (80, 160), (0, 0, 0, 0))
        out.alpha_composite(pierna)
        out.alpha_composite(bota)
        return out
    raise KeyError(nombre)


def _cara(d, cx, cy, expr, t):
    """Dibuja gafas, ojos, cejas y boca según la expresión."""
    ojo_dx, ojo_y = 50, cy - 5
    parpadeo = (t % 3.1) < 0.1 and expr in ("normal", "feliz_ojos")
    for s in (-1, 1):
        ex = cx + s * ojo_dx
        # gafas
        d.ellipse([ex - 40, ojo_y - 38, ex + 40, ojo_y + 38], fill=(255, 255, 255, 235), outline=OSCURO + (255,), width=7)
        if expr == "espiral":
            for k in range(26):
                a = k * 0.55 + t * 9 * s
                r = 2 + k * 1.2
                d.ellipse([ex + math.cos(a) * r - 3, ojo_y + math.sin(a) * r - 3, ex + math.cos(a) * r + 3, ojo_y + math.sin(a) * r + 3], fill=OSCURO + (255,))
        elif expr in ("feliz", "orgullo", "dormido"):
            d.arc([ex - 18, ojo_y - 10, ex + 18, ojo_y + 18], 200 if expr != "dormido" else 20, 340 if expr != "dormido" else 160, fill=OSCURO + (255,), width=7)
        elif expr == "cansado":
            d.ellipse([ex - 13, ojo_y - 6, ex + 13, ojo_y + 20], fill=OSCURO + (255,))
            d.rectangle([ex - 34, ojo_y - 34, ex + 34, ojo_y + 2], fill=hexrgb(PIEL) + (255,))
            d.line([(ex - 32, ojo_y + 2), (ex + 32, ojo_y + 2)], fill=OSCURO + (255,), width=6)
        elif parpadeo:
            d.line([(ex - 16, ojo_y), (ex + 16, ojo_y)], fill=OSCURO + (255,), width=7)
        else:
            r = 10 if expr == "sorpresa" else 15
            d.ellipse([ex - r, ojo_y - r, ex + r, ojo_y + r], fill=OSCURO + (255,))
            d.ellipse([ex - r * 0.5 + 4, ojo_y - r * 0.6, ex + 4, ojo_y - r * 0.1], fill=(255, 255, 255, 255))
        # cejas
        cy_ceja = ojo_y - 50 - (12 if expr in ("sorpresa", "espiral") else 0)
        inc = {"normal": 0, "sorpresa": -6, "espiral": -6, "feliz": -4, "orgullo": 8, "aja": -10,
               "cansado": 10, "esceptico": -14 if s < 0 else 6, "dormido": 4}.get(expr, 0)
        ang = math.radians(inc * s)
        x0, x1 = ex - 30, ex + 30
        y0, y1 = cy_ceja - math.sin(ang) * 30, cy_ceja + math.sin(ang) * 30
        d.line([(x0, y0), (x1, y1)], fill=(70, 40, 25, 255), width=15)
    d.line([(cx - 10, ojo_y - 6), (cx + 10, ojo_y - 6)], fill=OSCURO + (255,), width=6)
    # mejillas
    for s in (-1, 1):
        d.ellipse([cx + s * 78 - 18, cy + 45 - 10, cx + s * 78 + 18, cy + 45 + 10], fill=(235, 120, 110, 110))
    by = cy + 70
    if expr in ("sorpresa", "espiral"):
        d.ellipse([cx - 18, by - 22, cx + 18, by + 22], fill=(90, 30, 35, 255))
    elif expr in ("feliz", "orgullo", "aja"):
        d.chord([cx - 42, by - 30, cx + 42, by + 30], 0, 180, fill=(90, 30, 35, 255))
        d.chord([cx - 30, by + 6, cx + 30, by + 30], 0, 180, fill=(230, 110, 120, 255))
    elif expr == "cansado":
        d.arc([cx - 30, by, cx + 30, by + 30], 200, 340, fill=OSCURO + (255,), width=6)
    elif expr == "dormido":
        d.ellipse([cx - 8, by - 6, cx + 8, by + 10], fill=(90, 30, 35, 255))
    elif expr == "esfuerzo":
        d.rounded_rectangle([cx - 34, by - 12, cx + 34, by + 12], radius=10, fill=(255, 255, 255, 255), outline=OSCURO + (255,), width=5)
        d.line([(cx - 34, by), (cx + 34, by)], fill=OSCURO + (255,), width=3)
    else:
        d.arc([cx - 34, by - 26, cx + 34, by + 18], 20, 160, fill=OSCURO + (255,), width=7)


def _pivote(dst, spr, piv, pos, ang):
    """Rota `spr` alrededor de su punto `piv` y lo coloca con ese punto en `pos`."""
    R = int(max(spr.size) * 1.1)
    lien = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    lien.alpha_composite(spr, (R - piv[0], R - piv[1]))
    if abs(ang) > 0.1:
        lien = lien.rotate(ang, resample=Image.BICUBIC)
    _comp(dst, lien, int(pos[0] - R), int(pos[1] - R))


def nico(t=0.0, expr="normal", brazo_i=10, brazo_d=-10, pierna_i=0, pierna_d=0,
         traje=MOSTAZA, casco=False, respirar=True):
    """Devuelve sprite RGBA de Nico (pies en el borde inferior), ~760 px de alto."""
    Wn, Hn = 560, 800
    img = Image.new("RGBA", (Wn, Hn), (0, 0, 0, 0))
    cx = Wn // 2
    pie = Hn - 10
    resp = 1 + (0.012 * math.sin(t * 3.2) if respirar else 0)
    # piernas
    for s, ang in ((-1, pierna_i), (1, pierna_d)):
        _pivote(img, _parte("pierna"), (40, 6), (cx + s * 50, pie - 154), ang)
    torso_y = pie - 150 - 280
    # mochila detrás
    mo = _parte("mochila")
    img.alpha_composite(mo, (cx - mo.width // 2, torso_y + 20))
    # brazos (pivote en hombro)
    hombro_y = torso_y + 45
    for s, ang in ((-1, brazo_i), (1, brazo_d)):
        _pivote(img, _parte("brazo", traje), (40, 22), (cx + s * 122, hombro_y), ang * s)
    to = _parte("torso", traje)
    if abs(resp - 1) > 1e-3:
        to = to.resize((to.width, int(to.height * resp)), Image.BILINEAR)
    img.alpha_composite(to, (cx - to.width // 2, torso_y + 290 - to.height))
    for s in (-1, 1):
        tir = _parte("tirante")
        img.alpha_composite(tir, (cx + s * 70 - 20, torso_y + 10))
    # cabeza
    hy = torso_y - 200
    for s in (-1, 1):
        o = _parte("oreja")
        img.alpha_composite(o, (cx + s * 118 - 30, hy + 110))
    ca = _parte("cabeza")
    img.alpha_composite(ca, (cx - 125, hy))
    capa = Image.new("RGBA", img.size, (0, 0, 0, 0))
    _cara(ImageDraw.Draw(capa), cx, hy + 130, expr, t)
    img.alpha_composite(capa)
    # gorro
    g = _parte("gorro")
    img.alpha_composite(g, (cx - 140, hy - 112))
    dob = _parte("doblez")
    img.alpha_composite(dob, (cx - 145, hy + 6))
    pp = _parte("pompon")
    img.alpha_composite(pp, (cx - 45 + int(4 * math.sin(t * 5)), hy - 140))
    if casco:
        c = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dc = ImageDraw.Draw(c)
        dc.ellipse([cx - 175, hy - 40, cx + 175, hy + 310], fill=(200, 235, 255, 60), outline=(240, 245, 255, 255), width=14)
        dc.arc([cx - 130, hy, cx + 40, hy + 200], 200, 260, fill=(255, 255, 255, 200), width=12)
        img.alpha_composite(c)
    return img


def chispa(t, tam=1.0):
    """Luciérnaga cian con alas que aletean y brillo."""
    s = int(260 * tam)
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    g = brillo(s * 0.3, "#3DE0E6", 0.6 + 0.2 * math.sin(t * 6))
    img.alpha_composite(g.resize((s, s)), (0, 0))
    alas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(alas)
    c = s / 2
    aleteo = abs(math.sin(t * 22))
    for k in (-1, 1):
        wx = c + k * s * 0.17
        hh = s * 0.17 * (0.3 + 0.7 * aleteo)
        d.ellipse([wx - s * 0.12, c - s * 0.2 - hh, wx + s * 0.12, c - s * 0.2 + hh * 0.4], fill=(240, 255, 255, 170), outline=(255, 255, 255, 230), width=2)
    img.alpha_composite(alas)
    d = ImageDraw.Draw(img)
    _cuerpo = _chispa_cuerpo(int(s * 0.36))
    img.alpha_composite(_cuerpo, (int(c - _cuerpo.width / 2), int(c - _cuerpo.height / 2)))
    d.ellipse([c - s * 0.07, c + s * 0.12, c + s * 0.07, c + s * 0.22], fill=(255, 230, 80, 255))
    for k in (-1, 1):
        d.ellipse([c + k * s * 0.05 - 7 * tam, c - 10 * tam, c + k * s * 0.05 + 7 * tam, c + 6 * tam], fill=OSCURO + (255,))
    return img


@lru_cache(maxsize=8)
def _chispa_cuerpo(r):
    m, d = nueva_mascara(r, r)
    d.ellipse([2 * SS, 2 * SS, (r - 2) * SS, (r - 2) * SS], fill=255)
    return sprite(cerrar_mascara(m), "#3DE0E6", 51)


# ---------------------------------------------------------------------- props
@lru_cache(maxsize=None)
def prop(nombre, *args):
    f = globals()["_prop_" + nombre]
    return f(*args)


def _prop_regla():
    m = Image.new("L", (170, 1100), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 170, 1100], radius=20, fill=255)
    spr = sprite(m, "#E9C27A", 61)
    d = ImageDraw.Draw(spr)
    f = fuente(34, False)
    for i in range(0, 46):
        y = 1060 - i * 22
        largo = 70 if i % 5 == 0 else 35
        d.line([(0, y), (largo, y)], fill=(90, 55, 25, 255), width=5 if i % 5 == 0 else 3)
        if i % 5 == 0:
            d.text((85, y - 20), str(150 + i), font=f, fill=(90, 55, 25, 255))
    return spr


def _prop_marca():
    img = Image.new("RGBA", (130, 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 30), (40, 4), (40, 56)], fill=(214, 69, 69, 255))
    d.rounded_rectangle([36, 12, 128, 48], radius=12, fill=(214, 69, 69, 255))
    return img


def _prop_vertebra(cara=True):
    m, d = nueva_mascara(300, 150)
    d.rounded_rectangle([60 * SS, 15 * SS, 240 * SS, 135 * SS], radius=40 * SS, fill=255)
    d.polygon([(10 * SS, 60 * SS), (70 * SS, 40 * SS), (70 * SS, 100 * SS), (10 * SS, 85 * SS)], fill=255)
    d.polygon([(290 * SS, 60 * SS), (230 * SS, 40 * SS), (230 * SS, 100 * SS), (290 * SS, 85 * SS)], fill=255)
    spr = sprite(cerrar_mascara(m), "#F3E6D0", 62)
    if cara:
        dd = ImageDraw.Draw(spr)
        for s in (-1, 1):
            dd.ellipse([150 + s * 30 - 9, 62, 150 + s * 30 + 9, 80], fill=OSCURO + (255,))
        dd.arc([130, 78, 170, 104], 20, 160, fill=OSCURO + (255,), width=5)
    return spr


def _prop_disco():
    m, d = nueva_mascara(220, 70)
    d.rounded_rectangle([4 * SS, 4 * SS, 216 * SS, 66 * SS], radius=30 * SS, fill=255)
    return sprite(cerrar_mascara(m), "#4FA8E8", 63)


def _prop_esponja(cara=True):
    m, d = nueva_mascara(380, 260)
    d.rounded_rectangle([10 * SS, 10 * SS, 370 * SS, 250 * SS], radius=50 * SS, fill=255)
    spr = sprite(cerrar_mascara(m), "#F5C842", 64)
    dd = ImageDraw.Draw(spr)
    rng = random.Random(4)
    for _ in range(22):
        x, y, r = rng.uniform(40, 340), rng.uniform(40, 220), rng.uniform(7, 17)
        if cara and 140 < x < 240 and 80 < y < 180:
            continue
        dd.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=(200, 150, 30, 255))
    if cara:
        for s in (-1, 1):
            dd.ellipse([190 + s * 38 - 13, 105, 190 + s * 38 + 13, 131], fill=OSCURO + (255,))
            dd.ellipse([190 + s * 38 - 5, 108, 190 + s * 38 + 3, 116], fill=(255, 255, 255, 255))
        dd.chord([160, 130, 220, 175], 0, 180, fill=(90, 30, 35, 255))
    return spr


def _prop_gota():
    m, d = nueva_mascara(60, 80)
    d.ellipse([8 * SS, 28 * SS, 52 * SS, 76 * SS], fill=255)
    d.polygon([(30 * SS, 0), (10 * SS, 46 * SS), (50 * SS, 46 * SS)], fill=255)
    return sprite(cerrar_mascara(m), "#7FD3FF", 65, costura=False)


def _prop_pan():
    m, d = nueva_mascara(620, 300)
    d.rounded_rectangle([10 * SS, 60 * SS, 610 * SS, 290 * SS], radius=60 * SS, fill=255)
    d.ellipse([10 * SS, 0, 220 * SS, 180 * SS], fill=255)
    d.ellipse([400 * SS, 0, 610 * SS, 180 * SS], fill=255)
    spr = sprite(cerrar_mascara(m), "#D99A4E", 66, costura=True)
    inner = Image.new("L", spr.size, 0)
    di = ImageDraw.Draw(inner)
    di.rounded_rectangle([40, 85, 580, 265], radius=45, fill=255)
    di.ellipse([40, 30, 200, 160], fill=255)
    di.ellipse([420, 30, 580, 160], fill=255)
    miga = sprite(inner, "#F6DDAF", 67, costura=False)
    spr.alpha_composite(miga)
    return spr


def _prop_flecha(texto="GRAVEDAD"):
    m, d = nueva_mascara(420, 620)
    d.rectangle([120 * SS, 0, 300 * SS, 380 * SS], fill=255)
    d.polygon([(10 * SS, 360 * SS), (410 * SS, 360 * SS), (210 * SS, 610 * SS)], fill=255)
    spr = sprite(cerrar_mascara(m), "#FF4D6D", 68)
    r = rotulo(texto, 64, rot=90)
    spr.alpha_composite(r, (210 - r.width // 2, 190 - r.height // 2))
    return spr


def _prop_reloj():
    m, d = nueva_mascara(420, 460)
    d.ellipse([40 * SS, 60 * SS, 380 * SS, 400 * SS], fill=255)
    d.ellipse([20 * SS, 20 * SS, 130 * SS, 120 * SS], fill=255)
    d.ellipse([290 * SS, 20 * SS, 400 * SS, 120 * SS], fill=255)
    d.rectangle([90 * SS, 380 * SS, 120 * SS, 450 * SS], fill=255)
    d.rectangle([300 * SS, 380 * SS, 330 * SS, 450 * SS], fill=255)
    spr = sprite(cerrar_mascara(m), "#FF4D6D", 69)
    dd = ImageDraw.Draw(spr)
    dd.ellipse([80, 100, 340, 360], fill=(255, 250, 240, 255))
    for k in range(12):
        a = k / 12 * math.tau
        dd.line([(210 + math.sin(a) * 110, 230 - math.cos(a) * 110), (210 + math.sin(a) * 125, 230 - math.cos(a) * 125)], fill=OSCURO + (255,), width=6)
    return spr


def _prop_boton():
    m, d = nueva_mascara(420, 300)
    d.ellipse([10 * SS, 120 * SS, 410 * SS, 290 * SS], fill=255)
    base = sprite(cerrar_mascara(m), "#3B3550", 70)
    m2, d2 = nueva_mascara(420, 300)
    d2.ellipse([60 * SS, 30 * SS, 360 * SS, 230 * SS], fill=255)
    cima = sprite(cerrar_mascara(m2), "#FFD400", 71)
    dd = ImageDraw.Draw(cima)
    dd.arc([150, 70, 270, 190], 40, 330, fill=(60, 40, 30, 255), width=16)
    dd.polygon([(255, 70), (290, 110), (240, 120)], fill=(60, 40, 30, 255))
    return base, cima


def _prop_cama():
    img = Image.new("RGBA", (900, 520), (0, 0, 0, 0))
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 60, 70, 520], radius=20, fill=255)
    d.rounded_rectangle([830, 200, 900, 520], radius=20, fill=255)
    d.rectangle([40, 330, 860, 430], fill=255)
    img.alpha_composite(sprite(m, "#8A5A3B", 72))
    m2 = Image.new("L", img.size, 0)
    ImageDraw.Draw(m2).rounded_rectangle([60, 250, 850, 350], radius=30, fill=255)
    img.alpha_composite(sprite(m2, "#F2EFE6", 73))
    m3 = Image.new("L", img.size, 0)
    ImageDraw.Draw(m3).rounded_rectangle([80, 180, 290, 270], radius=40, fill=255)
    img.alpha_composite(sprite(m3, "#FFFFFF", 74))
    return img


def _prop_manta():
    m = Image.new("L", (620, 200), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 620, 200], radius=60, fill=255)
    spr = sprite(m, "#5B6CC9", 75)
    d = ImageDraw.Draw(spr)
    for x in range(40, 620, 80):
        for y in range(30, 200, 80):
            d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(255, 212, 0, 200))
    return spr


def _prop_medalla():
    img = Image.new("RGBA", (220, 330), (0, 0, 0, 0))
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    d.polygon([(50, 0), (100, 0), (130, 170), (80, 170)], fill=255)
    d.polygon([(170, 0), (120, 0), (90, 170), (140, 170)], fill=255)
    img.alpha_composite(sprite(m, "#3D7BE0", 76, costura=False))
    m2 = Image.new("L", img.size, 0)
    ImageDraw.Draw(m2).ellipse([30, 130, 190, 290], fill=255)
    med = sprite(m2, "#F2B630", 77)
    ImageDraw.Draw(med).regular_polygon((110, 210, 45), 5, rotation=0, fill=(255, 235, 130, 255))
    img.alpha_composite(med)
    return img


def _prop_tierra():
    s = 1400
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).ellipse([0, 0, s, s], fill=255)
    spr = sprite(m, "#2F7FD1", 78)
    rng = random.Random(9)
    cont = Image.new("L", (s, s), 0)
    dc = ImageDraw.Draw(cont)
    for _ in range(14):
        x, y, r = rng.uniform(150, 1250), rng.uniform(150, 1250), rng.uniform(80, 220)
        dc.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=255)
    cont = ImageChops.multiply(cont.filter(ImageFilter.GaussianBlur(20)).point(lambda v: 255 if v > 120 else 0), m)
    spr.alpha_composite(sprite(cont, "#5BAA4E", 79, costura=False))
    halo = brillo(s * 0.55, "#9FD8FF", 0.5).resize((int(s * 1.25), int(s * 1.25)))
    out = Image.new("RGBA", halo.size, (0, 0, 0, 0))
    out.alpha_composite(halo)
    out.alpha_composite(spr, ((halo.width - s) // 2, (halo.height - s) // 2))
    return out


def _prop_estacion():
    img = Image.new("RGBA", (900, 360), (0, 0, 0, 0))
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([330, 120, 570, 240], radius=40, fill=255)
    d.rectangle([180, 170, 720, 190], fill=255)
    img.alpha_composite(sprite(m, "#C9CED8", 80))
    for x0 in (20, 720):
        p = Image.new("L", img.size, 0)
        ImageDraw.Draw(p).rectangle([x0, 60, x0 + 160, 300], fill=255)
        pan = sprite(p, "#2B4FA8", 81)
        dp = ImageDraw.Draw(pan)
        for k in range(1, 4):
            dp.line([(x0 + k * 40, 60), (x0 + k * 40, 300)], fill=(160, 190, 255, 200), width=3)
        img.alpha_composite(pan)
    return img


def _prop_capsula():
    img = Image.new("RGBA", (600, 900), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for k in range(6):
        d.line([(300, 640), (60 + k * 96, 300)], fill=(240, 240, 240, 255), width=4)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).pieslice([20, 20, 580, 560], 180, 360, fill=255)
    para = sprite(m, "#FF4D6D", 82)
    dp = ImageDraw.Draw(para)
    for k in range(1, 6, 2):
        dp.pieslice([20, 20, 580, 560], 180 + k * 30, 180 + (k + 1) * 30, fill=(250, 245, 235, 255))
    img.alpha_composite(para)
    m2 = Image.new("L", img.size, 0)
    ImageDraw.Draw(m2).polygon([(230, 620), (370, 620), (430, 860), (170, 860)], fill=255)
    cap = sprite(m2, "#E6E9EF", 83)
    ImageDraw.Draw(cap).ellipse([270, 680, 330, 740], fill=(60, 120, 200, 255), outline=(40, 40, 50, 255), width=5)
    img.alpha_composite(cap)
    return img


def _prop_globo():
    m, d = nueva_mascara(860, 330)
    d.rounded_rectangle([10 * SS, 10 * SS, 850 * SS, 270 * SS], radius=80 * SS, fill=255)
    d.polygon([(150 * SS, 250 * SS), (110 * SS, 325 * SS), (250 * SS, 255 * SS)], fill=255)
    return sprite(cerrar_mascara(m), "#FFFFFF", 84, color_costura=(200, 200, 210))


def _prop_seguir():
    m, d = nueva_mascara(640, 170)
    d.rounded_rectangle([5 * SS, 5 * SS, 635 * SS, 165 * SS], radius=80 * SS, fill=255)
    spr = sprite(cerrar_mascara(m), "#FF4D6D", 85)
    r = rotulo("+ SEGUIR", 78, borde="#9E1F3A", grosor=4)
    spr.alpha_composite(r, (320 - r.width // 2, 85 - r.height // 2))
    return spr


def _prop_icono(tipo):
    m, d = nueva_mascara(220, 220)
    if tipo == "sol":
        d.ellipse([50 * SS, 50 * SS, 170 * SS, 170 * SS], fill=255)
        for k in range(10):
            a = k / 10 * math.tau
            d.line([((110 + math.cos(a) * 75) * SS, (110 + math.sin(a) * 75) * SS), ((110 + math.cos(a) * 105) * SS, (110 + math.sin(a) * 105) * SS)], fill=255, width=14 * SS)
        return sprite(cerrar_mascara(m), "#FFC93C", 86)
    d.ellipse([30 * SS, 30 * SS, 190 * SS, 190 * SS], fill=255)
    d.ellipse([75 * SS, 10 * SS, 225 * SS, 160 * SS], fill=0)
    return sprite(cerrar_mascara(m), "#F4F0D8", 87)


def _prop_charco():
    m = Image.new("L", (380, 110), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 380, 110], fill=255)
    return sprite(m, "#5EB7E0", 88, costura=False)


def _prop_ventana(noche=False):
    img = Image.new("RGBA", (380, 520), (0, 0, 0, 0))
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 380, 520], radius=24, fill=255)
    img.alpha_composite(sprite(m, "#FFFFFF", 89))
    return img


# ---------------------------------------------------------------------- cámara
def camara(img, zoom=1.0, fx=0.5, fy=0.5, dx=0.0, dy=0.0, rot=0.0, temblor=0.0, t=0.0):
    """Recorta/escala el fotograma: zoom centrado en (fx, fy) + desplazamiento."""
    if temblor:
        zoom = max(zoom, 1.04)
        dx += math.sin(t * 61) * temblor
        dy += math.cos(t * 47) * temblor
    zoom = max(zoom, 1.0)
    if zoom == 1.0 and not dx and not dy and not rot:
        return img
    w, h = img.size
    cw, ch = w / zoom, h / zoom
    cx = fx * w + dx
    cy = fy * h + dy
    x0 = min(max(cx - cw / 2, 0), w - cw)
    y0 = min(max(cy - ch / 2, 0), h - ch)
    out = img.transform((w, h), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    if rot:
        out = out.rotate(rot, resample=Image.BILINEAR, fillcolor=(0, 0, 0))
    return out


def barrido(img, fuerza):
    """Desenfoque de movimiento horizontal para whip-pans."""
    if fuerza <= 0.01:
        return img
    k = max(2, int(fuerza * 40))
    pequeño = img.resize((max(1, img.width // k), img.height), Image.BILINEAR)
    return pequeño.resize(img.size, Image.BILINEAR)


def vineta(img, fuerza=0.35):
    return Image.alpha_composite(img, _vineta(img.size, fuerza))


@lru_cache(maxsize=4)
def _vineta(size, fuerza):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w * 0.75)) ** 2 + ((yy - h / 2) / (h * 0.7)) ** 2)
    a = np.clip((r - 0.55) * 1.6, 0, 1) * 255 * fuerza
    a = np.clip(a + np.random.default_rng(0).uniform(0, 1.5, a.shape) * (a > 0), 0, 255)  # tramado contra bandas
    out = Image.new("RGBA", size, (15, 5, 25, 0))
    out.putalpha(Image.fromarray(np.uint8(a), "L"))
    return out
