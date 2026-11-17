"""Plantilla de videos por datos: cada video se describe con una lista de planos.

Plano = dict(seg, fr, fondo, el=[elementos], txt, color, tag=(valor, unidad), sello, sfx, tr, giro, cta, zoom)
Elemento = tupla ("tipo", ...parámetros). Ver ELEMENTOS más abajo.
"""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

from comun import *  # noqa
from comun import _comp  # noqa


# ----------------------------------------------------------------- fondos
@lru_cache(maxsize=16)
def _fondo_base(nombre):
    if nombre == "espacio":
        return _cielo_estrellas_fijo("#05040F", "#1A1440")
    if nombre == "tormenta":
        c = degradado(W, H, [(0, "#0A0E1A"), (0.55, "#1C2A3A"), (0.56, "#0E2A3A"), (1, "#061520")])
        return c
    if nombre in ("nieve_noche", "nieve_dia"):
        noche = nombre == "nieve_noche"
        c = _cielo_estrellas_fijo("#05081A", "#1E2A55") if noche else degradado(W, H, [(0, "#8FB4D9"), (1, "#E6F0F8")])
        img, d = capa()
        for k, col in enumerate([(200, 210, 230), (235, 240, 250)]):
            base = 1150 + k * 150
            pts = [(0, H)] + [(x, base - 300 + k * 80 + math.sin(x / 170 + k) * 140) for x in range(0, W + 30, 30)] + [(W, H)]
            d.polygon(pts, fill=(tuple(int(v * (0.55 if noche else 1)) for v in col)) + (255,))
        c.alpha_composite(img)
        return c
    if nombre == "laboratorio":
        c = degradado(W, H, [(0, "#0F2A3A"), (1, "#1F4A5A")])
        img, d = capa()
        d.rectangle([0, 1500, W, H], fill=(60, 70, 85, 255))
        c.alpha_composite(img)
        return c
    if nombre == "musgo":
        c = degradado(W, H, [(0, "#0E2A18"), (1, "#2E5A30")])
        rng = random.Random(3)
        img, d = capa()
        for _ in range(60):
            x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(30, 90)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(70, 130, 60, 70))
        c.alpha_composite(img.filter(ImageFilter.GaussianBlur(8)))
        return c
    if nombre == "papel":
        return degradado(W, H, [(0, "#2A1C10"), (1, "#5A3A20")])
    if nombre == "cocina":
        c = degradado(W, H, [(0, "#F6D9B0"), (0.7, "#E8B985"), (0.71, "#9A6A40"), (1, "#6A4628")])
        return c
    if nombre == "egipto":
        c = degradado(W, H, [(0, "#3A2A18"), (1, "#7A5A30")])
        img, d = capa()
        for k in range(0, W, 120):
            d.rectangle([k, 0, k + 110, H], outline=(150, 110, 60, 90), width=4)
        c.alpha_composite(img)
        return c
    if nombre == "mar_noche":
        c = degradado(W, H, [(0, "#0A1024"), (0.55, "#1E2A48"), (0.56, "#0E2A3A"), (1, "#061520")])
        return c
    if nombre == "amarillo":
        return degradado(W, H, [(0, "#FFD400"), (1, "#FFB000")])
    return degradado(W, H, [(0, "#14112B"), (1, "#2E2458")])


def _cielo_estrellas_fijo(c1, c2):
    c = degradado(W, H, [(0, c1), (1, c2)])
    img, d = capa()
    rng = random.Random(1)
    for _ in range(280):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.choice([1, 1.5, 2, 3])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rng.randint(110, 255)))
    c.alpha_composite(img)
    return c


def fondo(nombre, t):
    c = _fondo_base(nombre).copy()
    if nombre in ("tormenta", "mar_noche"):
        img, d = capa()
        for k in range(6):
            y = 1100 + k * 130
            d.line([(x, y + math.sin(x / 60 + t * 3 + k) * 22) for x in range(0, W + 20, 20)], fill=(120, 180, 200, 90), width=8)
        c.alpha_composite(img)
        if nombre == "tormenta":
            particulas(c, t, 120, (200, 220, 255), 21, (1, 2), -900, 140)
            if int(t * 2.3) % 5 == 0:
                c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, 50)))
    elif nombre.startswith("nieve"):
        particulas(c, t, 70, (255, 255, 255), 12, (3, 6), -40, 220)
    else:
        particulas(c, t, 35, (200, 220, 255), 9, (2, 5), 15, 120)
    return c


# ---------------------------------------------------------------- sprites
@lru_cache(maxsize=4)
def avion(color="#7A8A6A"):
    m = Image.new("L", (420, 220), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([20, 90, 400, 140], radius=24, fill=255)
    d.polygon([(170, 115), (270, 115), (210, 10), (160, 10)], fill=255)
    d.polygon([(170, 120), (270, 120), (210, 215), (160, 215)], fill=255)
    d.polygon([(30, 112), (90, 112), (45, 50), (20, 50)], fill=255)
    spr = sprite(m, color, 900)
    ImageDraw.Draw(spr).ellipse([330, 98, 370, 128], fill=(160, 210, 240, 255))
    return spr


@lru_cache(maxsize=4)
def tardigrado(seco=False):
    m = Image.new("L", (520, 340), 0)
    d = ImageDraw.Draw(m)
    if seco:
        d.ellipse([140, 80, 380, 260], fill=255)
    else:
        d.rounded_rectangle([40, 60, 480, 230], radius=85, fill=255)
        for k in range(4):
            x = 110 + k * 100
            d.rounded_rectangle([x - 22, 190, x + 22, 320], radius=20, fill=255)
    spr = sprite(m, "#C9B49A" if seco else "#E8C8A8", 910, pelo=False)
    dd = ImageDraw.Draw(spr)
    if not seco:
        for k in range(4):
            x = 110 + k * 100
            for s in (-12, 0, 12):
                dd.line([(x + s, 318), (x + s * 1.6, 336)], fill=(60, 40, 30, 255), width=4)
        dd.ellipse([400, 110, 430, 140], fill=(30, 20, 30, 255))
        dd.ellipse([440, 130, 470, 160], fill=(30, 20, 30, 255))
        dd.ellipse([455, 165, 485, 190], fill=(120, 50, 60, 255))
    return spr


@lru_cache(maxsize=2)
def tienda(rota=False):
    m = Image.new("L", (600, 360), 0)
    ImageDraw.Draw(m).polygon([(0, 350), (300, 20), (600, 350)], fill=255)
    spr = sprite(m, "#C84A3A", 920)
    d = ImageDraw.Draw(spr)
    if rota:
        d.line([(300, 120), (260, 200), (320, 260), (280, 340)], fill=(20, 10, 10, 255), width=14)
    return spr


@lru_cache(maxsize=2)
def libro_voynich():
    m = Image.new("L", (760, 560), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 760, 560], radius=16, fill=255)
    spr = sprite(m, "#E8D8B0", 930)
    d = ImageDraw.Draw(spr)
    d.line([(380, 10), (380, 550)], fill=(150, 120, 80, 255), width=6)
    rng = random.Random(4)
    for pag in (0, 1):
        x0 = 40 + pag * 380
        for fila in range(7):
            for k in range(9):
                x, y = x0 + k * 34, 50 + fila * 40
                if rng.random() < 0.85:
                    d.arc([x, y, x + 22, y + 24], rng.choice([0, 90, 180]), rng.choice([270, 300, 360]), fill=(70, 50, 30, 255), width=4)
        cx, cy = x0 + 160, 420
        d.line([(cx, cy + 110), (cx, cy - 20)], fill=(60, 120, 50, 255), width=10)
        for a in range(5):
            ang = -math.pi / 2 + (a - 2) * 0.5
            d.ellipse([cx + math.cos(ang) * 60 - 26, cy + math.sin(ang) * 60 - 14, cx + math.cos(ang) * 60 + 26, cy + math.sin(ang) * 60 + 14], fill=(90, 160, 70, 255))
        d.ellipse([cx - 30, cy + 90, cx + 30, cy + 130], fill=(170, 80, 60, 255))
    return spr


@lru_cache(maxsize=2)
def tarro_miel(cristal=False):
    img = Image.new("RGBA", (420, 520), (0, 0, 0, 0))
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([30, 110, 390, 510], radius=70, fill=255)
    img.alpha_composite(sprite(m, "#F2EBD8" if cristal else "#F2A51A", 940))
    m2 = Image.new("L", img.size, 0)
    ImageDraw.Draw(m2).rounded_rectangle([50, 40, 370, 130], radius=26, fill=255)
    img.alpha_composite(sprite(m2, "#C84A3A", 941))
    r = rotulo("MIEL", 70, "#FFFFFF", "#6A3A10", 6)
    img.alpha_composite(r, (210 - r.width // 2, 300 - r.height // 2))
    return img


def rayo(c, x, y, esc, t):
    img, d = capa()
    rng = random.Random(int(t * 12))
    pts, xx, yy = [], x, y
    for k in range(12):
        pts.append((xx, yy))
        xx += rng.uniform(-60, 60) * esc
        yy += 90 * esc
    d.line(pts, fill=(255, 255, 220, 255), width=int(14 * esc), joint="curve")
    c.alpha_composite(img.filter(ImageFilter.GaussianBlur(10)))
    c.alpha_composite(img)
    pegar(c, brillo(220 * esc, "#B8D8FF", 0.6), x, y + 500 * esc)


def termometro(c, x, y, frac, color="#FF4D6D"):
    img, d = capa()
    d.rounded_rectangle([x - 40, y - 420, x + 40, y + 60], radius=40, fill=(240, 240, 245, 255))
    d.ellipse([x - 75, y - 10, x + 75, y + 140], fill=hexrgb(color) + (255,))
    d.rounded_rectangle([x - 22, y - 400 + 400 * (1 - frac), x + 22, y + 60], radius=20, fill=hexrgb(color) + (255,))
    c.alpha_composite(img)


def dibujar_elemento(c, e, t, d):
    tipo = e[0]
    if tipo == "nico":
        _, x, y, esc, expr, bi, bd, *rest = e
        traje = rest[0] if rest else MOSTAZA
        casco = rest[1] if len(rest) > 1 else False
        pegar(c, nico(t, expr, bi, bd, traje=traje, casco=casco), x, y, esc, ancla="abajo")
    elif tipo == "chispa":
        chispa_en(c, t, e[1], e[2], e[3] if len(e) > 3 else 1.0)
    elif tipo == "planeta":
        _, color, bandas, x, y, esc = e
        pegar(c, planeta(color, 300, bandas, 950), x, y, esc, rot=t * 4)
    elif tipo == "carta":
        _, txt, color, x, y, esc, t0 = e
        s = pop_scale(t - t0)
        if s:
            hud(icono_carta(txt, color, 300, 960 + len(txt)), x, y, s * esc, True)
    elif tipo == "cal":
        _, dia, mes, anio, x, y, esc = e
        pegar(c, calendario(dia, mes, anio), x, y, pop_scale(t - 0.05) * esc, sombra=True)
    elif tipo == "ondas":
        ondas(c, e[1], e[2], t, e[3] if len(e) > 3 else (160, 255, 200), 4, 600, 10, (0, 360))
    elif tipo == "avion":
        _, x, y, esc, vx, vy, *rest = e
        rot = rest[0] if rest else 0
        pegar(c, avion(), x + vx * t, y + vy * t + math.sin(t * 2) * 10, esc, rot=rot + math.sin(t * 1.5) * 3, sombra=True)
    elif tipo == "escuadron":
        _, x, y, esc = e
        for k in range(5):
            pegar(c, avion(), x + (k % 3) * 220 * esc - (k // 3) * 110 * esc + t * 40, y + (k // 3) * 170 * esc + math.sin(t * 2 + k) * 8, esc)
    elif tipo == "tardigrado":
        _, x, y, esc, seco = e
        pegar(c, tardigrado(seco), x + (0 if seco else math.sin(t * 2) * 20), y, esc * (1 + 0.02 * math.sin(t * 4)), sombra=True)
    elif tipo == "tienda":
        pegar(c, tienda(e[4] if len(e) > 4 else False), e[1], e[2], e[3], sombra=True)
    elif tipo == "huellas":
        img, dd = capa()
        for k in range(14):
            yy = 1350 + k * 40
            xx = 540 + math.sin(k * 0.7) * 140 + (k % 2) * 40
            dd.ellipse([xx - 16, yy - 24, xx + 16, yy + 24], fill=(120, 130, 160, 200))
        c.alpha_composite(img)
    elif tipo == "rayo":
        if int(t * 8) % 3 != 2:
            rayo(c, e[1], e[2], e[3], t)
    elif tipo == "nube_tormenta":
        for k in range(6):
            pegar(c, brillo(180, "#3A4458", 0.9), 140 + k * 160, 420 + (k % 2) * 60)
    elif tipo == "termometro":
        termometro(c, e[1], e[2], ease_out(clamp01(t / 0.8)) * e[3], e[4] if len(e) > 4 else "#FF4D6D")
    elif tipo == "sol":
        pegar(c, brillo(260, "#FFD45C", 0.8), e[1], e[2])
        pegar(c, prop("icono", "sol"), e[1], e[2], e[3], rot=t * 10)
    elif tipo == "libro":
        pegar(c, libro_voynich(), e[1], e[2], e[3] * (1 + 0.01 * math.sin(t * 2)), rot=e[4] if len(e) > 4 else 0, sombra=True)
    elif tipo == "tarro":
        pegar(c, tarro_miel(e[4] if len(e) > 4 else False), e[1], e[2], e[3], sombra=True)
    elif tipo == "bacteria_seca":
        for k in range(5):
            ph = (t * 0.8 + k / 5) % 1
            pegar(c, brillo(30, "#7BD88F", 0.8 * (1 - ph)), e[1] + math.cos(k) * 200 * (1 - ph), e[2] + math.sin(k) * 200 * (1 - ph))
    elif tipo == "barras":
        _, vals, labs, cols = e
        barras(c, vals, labs, cols, t, x0=140, ancho=800, maximo=max(vals) * 1.1)
    elif tipo == "luna":
        pegar(c, planeta("#B8B8C0", 300, None, 970), e[1], e[2], e[3])
    elif tipo == "explosion":
        if t > e[3]:
            u = clamp01((t - e[3]) / 0.6)
            pegar(c, brillo(80 + 300 * u, "#FFB040", 1 - u * 0.6), e[1], e[2])


# ----------------------------------------------------------------- planos
def hacer_plano(p):
    def f(t, d):
        c = fondo(p.get("fondo", "oscuro"), 0.0 if p.get("giro") else t)
        for e in p.get("el", []):
            dibujar_elemento(c, e, 0.0 if p.get("giro") else t, d)
        if p.get("giro"):
            c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
            giro(c, t)
            return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)
        if p.get("cta"):
            pegar(c, nico(t, "feliz", 10, 140 + 25 * math.sin(t * 10)), 330, 1880, 0.95, ancla="abajo")
            globo_texto(c, p["cta"], 540, 900, t - 0.1)
            boton_seguir(t, 1200)
            return c, dict(zoom=1.0, t=t)
        if p.get("txt"):
            texto(c, p["txt"], 540, p.get("ty", 1660), t - p.get("tt", 0.2), p.get("tam", 105), p.get("color", "#FFFFFF"))
        if p.get("tag"):
            v, u = p["tag"]
            tag(c, v, u, 540, p.get("tagy", 1500), t - 0.3, p.get("tagtam", 130))
        if p.get("sello"):
            sello(c, p["sello"], t - 0.15, p.get("sellocolor", "#FF4D6D"), p.get("selloy", 1100), 150)
        z = p.get("zoom", "in")
        zoom = {"in": 1.0 + 0.08 * ease_out(t / d), "out": 1.12 - 0.1 * ease_out(t / d), "none": 1.0}[z]
        return c, dict(zoom=zoom, fy=p.get("fy", 0.5), temblor=p.get("temblor", 0) if t < 0.3 else 0, t=t)
    return f


def construir(guion_rel, planos):
    plan = [(p["seg"], p.get("fr", 0.0), hacer_plano(p), p.get("tr"), p.get("sfx", [])) for p in planos]
    escenas, dur = construir_escenas(RAIZ / guion_rel, plan)
    g = [e for e, p in zip(escenas, planos) if p.get("giro")]
    corte = (g[0]["ini"], g[0]["ini"] + 0.45) if g else (dur - 1, dur - 0.9)
    return escenas, dur, corte
