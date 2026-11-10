"""Día 02 · Video A: El pulpo tiene 3 corazones… y uno se apaga al nadar."""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

from comun import *  # noqa
from comun import _comp  # noqa

GUION = RAIZ / "dia-02/datos/01-pulpo-tres-corazones.json"
PULPO = "#E0607E"


# ------------------------------------------------------------------ fondos
@lru_cache(maxsize=2)
def _fondo_mar(frio=False):
    c = degradado(W, H, [(0, "#2A7FA8" if not frio else "#6FB7D6"), (0.5, "#0F4A6B" if not frio else "#2E6F96"), (1, "#06243A")])
    rayos = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(rayos)
    for k in range(6):
        x = 100 + k * 190
        d.polygon([(x, 0), (x + 90, 0), (x + 260, H), (x + 120, H)], fill=(255, 255, 255, 18))
    c.alpha_composite(rayos.filter(ImageFilter.GaussianBlur(20)))
    m = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(m)
    dm.polygon([(0, 1600), (300, 1560), (700, 1620), (W, 1570), (W, H), (0, H)], fill=255)
    c.alpha_composite(sprite(m, "#C9A86A", 150, costura=False, grano=0.25))
    rng = random.Random(4)
    for k in range(7):  # rocas y algas
        x = rng.uniform(0, W)
        r = Image.new("L", (260, 160), 0)
        ImageDraw.Draw(r).ellipse([0, 20, 260, 200], fill=255)
        pegar(c, sprite(r, "#5A5F73", 151 + k), x, 1600 + rng.uniform(0, 120), rng.uniform(0.5, 1.0))
    return c


def fondo_mar(t, frio=False):
    c = _fondo_mar(frio).copy()
    img, d = capa()
    for k in range(5):  # algas que se mecen
        x0 = 80 + k * 230
        pts = [(x0 + math.sin(t * 1.5 + k + j * 0.5) * j * 4, 1650 - j * 40) for j in range(10)]
        d.line(pts, fill=(60, 150, 90, 255), width=22, joint="curve")
    c.alpha_composite(img)
    if frio:
        particulas(c, t, 70, (255, 255, 255), 12, (3, 6), -40, 220)
    particulas(c, t, 35, (200, 240, 255), 3, (2, 5), 25, 150)
    return c


# ------------------------------------------------------------------- pulpo
def pulpo(t, expr="feliz", color=PULPO, nado=0.0, cansado=False, rayosx=False, caminar=0.0):
    """Pulpo de fieltro (~700 px). nado>0 junta los brazos (propulsión)."""
    S = 760
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    cx, cy = S // 2, 300
    for k in range(8):  # brazos
        base_ang = math.pi * (0.15 + 0.7 * k / 7)
        ang0 = base_ang * (1 - nado) + math.pi / 2 * nado
        x, y = cx + (k - 3.5) * 30, cy + 110
        w = 74
        for j in range(16):
            ola = math.sin(t * 3 + k * 0.8 + j * 0.45) * (0.35 - 0.25 * nado)
            if caminar:
                ola += math.sin(t * 6 + k * math.pi / 2) * 0.3 * caminar * (j / 16)
            a = ang0 + ola * (j / 16) * 1.5
            x += math.cos(a) * 25
            y += math.sin(a) * 25 * (1 + 0.6 * nado)
            r = w * (1 - j / 18) / 2
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    d.ellipse([cx - 175, cy - 260, cx + 175, cy + 160], fill=255)  # manto
    spr = sprite(m, color, 160)
    dd = ImageDraw.Draw(spr)
    if rayosx:
        dd.ellipse([cx - 170, cy - 255, cx + 170, cy + 155], fill=(70, 40, 110, 255))
        dd.ellipse([cx - 120, cy - 215, cx + 120, cy - 20], fill=(95, 60, 140, 255))
    else:
        rng = random.Random(2)
        for _ in range(14):
            x, y, r = cx + rng.uniform(-130, 130), cy + rng.uniform(-220, 60), rng.uniform(8, 18)
            dd.ellipse([x - r, y - r, x + r, y + r], fill=aclarar(hexrgb(color), 0.25) + (255,))
    for s in (-1, 1):  # ojos
        ex, ey = cx + s * 70, cy + 40
        dd.ellipse([ex - 46, ey - 40, ex + 46, ey + 40], fill=(255, 255, 255, 255))
        if expr == "cansado" or cansado:
            dd.ellipse([ex - 18, ey, ex + 18, ey + 30], fill=(30, 20, 30, 255))
            dd.rectangle([ex - 48, ey - 42, ex + 48, ey + 4], fill=hexrgb(color) + (255,))
            dd.line([(ex - 46, ey + 4), (ex + 46, ey + 4)], fill=(30, 20, 30, 255), width=6)
        elif expr == "sorpresa":
            dd.ellipse([ex - 14, ey - 14, ex + 14, ey + 14], fill=(30, 20, 30, 255))
        else:
            dd.ellipse([ex - 22, ey - 22, ex + 22, ey + 22], fill=(30, 20, 30, 255))
            dd.ellipse([ex - 8, ey - 16, ex + 4, ey - 4], fill=(255, 255, 255, 255))
    by = cy + 105
    if expr == "sorpresa":
        dd.ellipse([cx - 14, by - 14, cx + 14, by + 18], fill=(90, 30, 40, 255))
    elif expr == "cansado" or cansado:
        dd.arc([cx - 26, by, cx + 26, by + 26], 200, 340, fill=(60, 20, 30, 255), width=6)
    else:
        dd.arc([cx - 30, by - 22, cx + 30, by + 14], 20, 160, fill=(60, 20, 30, 255), width=7)
    return spr


def corazones_pulpo(c, x, y, esc, t, latido=True, principal_parado=False, brillo_branq=False):
    """Dos corazones branquiales + uno sistémico sobre el pulpo (vista rayos X)."""
    p = 1 + 0.12 * max(0, math.sin(t * 9)) if latido else 1
    for s in (-1, 1):
        if brillo_branq:
            pegar(c, brillo(60 * esc, "#3DE0E6", 0.7), x + s * 95 * esc, y + 20 * esc)
        pegar(c, corazon("#7FB8FF", 141 + s), x + s * 95 * esc, y + 20 * esc, 0.32 * esc * p)
    pp = 1 if principal_parado else p
    pegar(c, corazon("#3D7BE0", 143), x, y - 80 * esc, 0.5 * esc * pp)


def gota_color(color, esc=1.0):
    m, d = nueva_mascara(60, 80)
    d.ellipse([8 * SS, 28 * SS, 52 * SS, 76 * SS], fill=255)
    d.polygon([(30 * SS, 0), (10 * SS, 46 * SS), (50 * SS, 46 * SS)], fill=255)
    return sprite(cerrar_mascara(m), color, 165)


# ----------------------------------------------------------------- escenas
def e_gancho(t, d):
    c = fondo_mar(t)
    a = clamp01(t / 0.4)
    pegar(c, pulpo(t, "feliz", rayosx=True), 540, 1050, 1.0, alfa=0.4 + 0.6 * a)
    corazones_pulpo(c, 540, 880, 1.0, t)
    texto(c, "3 CORAZONES", 540, 1500, t - 0.2, 125, "#FFD400")
    return c, dict(zoom=1.0 + 0.15 * ease_out(t / d), fy=0.5, temblor=6 if t < 0.25 else 0, t=t)


def e_sangre(t, d):
    c = fondo_mar(t)
    u = ease_in_out((t - 0.3) / 0.6)
    pegar(c, gota_color("#E23B4E"), 540, 1000, 4.0, alfa=1 - u)
    pegar(c, gota_color("#3D7BE0"), 540, 1000, 4.0, alfa=u)
    texto(c, "SANGRE AZUL", 540, 1500, t - 0.6, 125, "#7FB8FF")
    return c, dict(zoom=1.05, t=t)


def e_nico_buzo(t, d):
    c = fondo_mar(t)
    pegar(c, nico(t, "sorpresa", 40, 120, traje="#2D3E5C", casco=True), 300, 1700 + math.sin(t * 2) * 10, 0.8, ancla="abajo")
    pegar(c, pulpo(t, "feliz"), 780, 1250, 0.7)
    texto(c, "EL PULPO", 540, 1780, t - 0.15, 120, "#FFFFFF")
    return c, dict(zoom=1.05 + 0.04 * t, t=t)


def e_ovni(t, d):
    c = fondo_espacio_simple(t)
    u = ease_out(t / d)
    img, dd = capa()
    dd.polygon([(440, 560), (640, 560), (820, 1500), (260, 1500)], fill=(160, 255, 200, 70))
    c.alpha_composite(img)
    m = Image.new("L", (460, 200), 0)
    dm = ImageDraw.Draw(m)
    dm.ellipse([0, 70, 460, 180], fill=255)
    dm.ellipse([130, 0, 330, 140], fill=255)
    pegar(c, sprite(m, "#B8C2D6", 170), 540, 470 + math.sin(t * 3) * 10, 1.0)
    pegar(c, pulpo(t, "sorpresa"), 540, 1350 - u * 400, 0.55, rot=math.sin(t * 4) * 10)
    texto(c, "¿ALIENÍGENA?", 540, 1650, t - 0.2, 105, "#9CFFC8")
    return c, dict(zoom=1.0, t=t)


@lru_cache(maxsize=1)
def _espacio():
    c = degradado(W, H, [(0, "#05040F"), (1, "#1A1440")])
    img, d = capa()
    rng = random.Random(1)
    for _ in range(300):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.choice([1, 1.5, 2, 3])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rng.randint(120, 255)))
    c.alpha_composite(img)
    return c


def fondo_espacio_simple(t):
    c = _espacio().copy()
    particulas(c, t, 20, (255, 255, 255), 4, (1, 2.5), 6, 200)
    return c


def e_rayosx(t, d):
    c = fondo_mar(t)
    pegar(c, pulpo(t, "feliz", rayosx=True), 540, 1050, 1.1)
    corazones_pulpo(c, 540, 860, 1.1, t, brillo_branq=True)
    texto(c, "2 PARA LAS\nBRANQUIAS", 540, 1560, t - 0.2, 105, "#7FB8FF")
    return c, dict(zoom=1.0 + 0.1 * ease_out(t / d), fy=0.48, t=t)


def e_branquias(t, d):
    c = fondo_mar(t)
    pegar(c, pulpo(t, "feliz", rayosx=True), 540, 1150, 1.9)
    p = 1 + 0.15 * max(0, math.sin(t * 9))
    for s in (-1, 1):
        pegar(c, corazon("#7FB8FF", 141 + s), 540 + s * 180, 880, 0.6 * p)
        for k in range(5):  # sangre que pasa por la branquia y se ilumina
            ph = (t * 0.9 + k / 5) % 1
            col = mezcla(hexrgb("#3B4A7A"), hexrgb("#7FD3FF"), ph)
            pegar(c, brillo(20, col, 0.9), 540 + s * (180 + ph * 260), 880 - math.sin(ph * math.pi) * 160, 1)
    return c, dict(zoom=1.0, t=t)


def e_oxigeno(t, d):
    c = fondo_mar(t)
    pegar(c, pulpo(t, "feliz", rayosx=True), 540, 1150, 1.9)
    for k in range(10):
        ph = (t * 0.7 + k / 10) % 1
        x = 300 + (k * 53) % 480
        pegar(c, rotulo("O₂", 54, "#FFFFFF", "#1F6F8B", 5), x, 1500 - ph * 700, 1, alfa=1 - ph)
    texto(c, "OXÍGENO", 540, 600 + 1000, t - 0.15, 120, "#7FD3FF")
    return c, dict(zoom=1.0, t=t)


def e_sistemico(t, d):
    c = fondo_mar(t)
    pegar(c, pulpo(t, "feliz", rayosx=True), 540, 1050, 1.1)
    p = 1 + 0.15 * max(0, math.sin(t * 9))
    pegar(c, brillo(140, "#3D7BE0", 0.6), 540, 780)
    pegar(c, corazon("#3D7BE0", 143), 540, 780, 0.75 * p)
    texto(c, "CORAZÓN\nSISTÉMICO", 540, 1560, t - 0.15, 110, "#7FB8FF")
    return c, dict(zoom=1.2, fy=0.45, t=t)


def e_reparte(t, d):
    c = fondo_mar(t)
    pegar(c, pulpo(t, "feliz", rayosx=True), 540, 1050, 1.1)
    corazones_pulpo(c, 540, 860, 1.1, t)
    for k in range(8):  # pulsos que viajan a los brazos
        a = math.pi * (0.15 + 0.7 * k / 7)
        ph = (t * 1.2 + k * 0.1) % 1
        r = 60 + ph * 330
        pegar(c, brillo(18, "#7FB8FF", 1), 540 + math.cos(a) * r, 1080 + math.sin(a) * r * 0.9, 1, alfa=1 - ph)
    texto(c, "A TODO EL CUERPO", 540, 1600, t - 0.15, 95, "#FFFFFF")
    return c, dict(zoom=1.05, t=t)


def e_azul(t, d):
    c = fondo_mar(t)
    pegar(c, nico(t, "esceptico", 10, 160, traje="#2D3E5C", casco=True), 540, 1750, 1.0, ancla="abajo")
    texto(c, "¿AZUL?", 540, 800, t - 0.1, 140, "#7FB8FF")
    return c, dict(zoom=1.25, fy=0.45, t=t)


def e_cobre(t, d):
    c = fondo_mar(t)
    pegar(c, brillo(260, "#E08A3C", 0.5), 540, 1000)
    pegar(c, elemento("Cu", "COBRE", "#C8743A"), 540, 1000, pop_scale(t - 0.05) * 1.5, rot=math.sin(t * 3) * 4, sombra=True)
    return c, dict(zoom=1.0 + 0.05 * t, temblor=6 if 0.05 < t < 0.3 else 0, t=t)


def e_humano(t, d):
    c = degradado(W, H, [(0, "#3A1020"), (1, "#7A2035")])
    particulas(c, t, 30, (255, 180, 180), 5, (2, 5), 15, 120)
    pegar(c, elemento("Fe", "HIERRO", "#8A8F9E"), 330, 950, pop_scale(t - 0.1) * 1.1, sombra=True)
    pegar(c, gota_color("#E23B4E"), 760, 950, pop_scale(t - 0.3) * 3.2)
    texto(c, "HEMOGLOBINA", 540, 1450, t - 0.4, 110, "#FF8A9A")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_hemocianina(t, d):
    c = fondo_mar(t)
    pegar(c, elemento("Cu", "COBRE", "#C8743A"), 330, 950, 1.1, sombra=True)
    u = ease_in_out((t - 0.4) / 0.8)
    pegar(c, gota_color("#C9D6E0"), 760, 950, 3.2, alfa=1 - u)
    pegar(c, gota_color("#3D7BE0"), 760, 950, 3.2, alfa=u)
    for k in range(4):
        ph = clamp01((t - 0.2 - k * 0.12) / 0.4)
        if ph > 0:
            pegar(c, rotulo("O₂", 60, "#FFFFFF", "#1F6F8B", 5), 1000 - ph * 220, 700 + k * 120 + ph * 80, 1, alfa=1 - ph * 0.8)
    texto(c, "HEMOCIANINA", 540, 1450, t - 0.2, 110, "#7FB8FF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_comparacion(t, d):
    izq = degradado(W // 2, H, [(0, "#3A1020"), (1, "#7A2035")])
    der = fondo_mar(t).crop((270, 0, 270 + W // 2, H))
    c = Image.new("RGBA", (W, H))
    c.alpha_composite(izq, (0, 0))
    c.alpha_composite(der, (W // 2, 0))
    pegar(c, gota_color("#E23B4E"), 270, 1000, 2.6)
    pegar(c, gota_color("#3D7BE0"), 810, 1000, 2.6)
    pegar(c, rotulo("TÚ", 90), 270, 700, pop_scale(t - 0.05))
    pegar(c, rotulo("PULPO", 90), 810, 700, pop_scale(t - 0.2))
    img, dd = capa()
    dd.line([(W // 2, 0), (W // 2, H)], fill=(255, 255, 255, 255), width=12)
    c.alpha_composite(img)
    return c, dict(zoom=1.0 + 0.03 * t, t=t)


def e_frio(t, d):
    c = fondo_mar(t, frio=True)
    pegar(c, pulpo(t, "feliz", color="#D9708C"), 540, 1150, 0.95)
    texto(c, "AGUA FRÍA,\nPOCO OXÍGENO", 540, 1650, t - 0.2, 95, "#FFFFFF")
    return c, dict(zoom=1.05 + 0.04 * t, t=t)


def e_giro(t, d):
    c = fondo_mar(0.0, frio=True)
    pegar(c, pulpo(0.0, "sorpresa"), 540, 1150, 0.95)
    c = Image.blend(c, Image.new("RGBA", (W, H), (40, 30, 60, 255)), 0.4)
    giro(c, t)
    return c, dict(zoom=1.1 + 0.1 * t, temblor=8 if t < 0.3 else 0, t=t)


def e_nada(t, d):
    c = fondo_mar(t)
    u = ease_in_out(t / d)
    y = 1400 - u * 700
    for k in range(10):
        ph = (t * 2 + k / 10) % 1
        pegar(c, brillo(16 + k % 3 * 4, "#E8F4FF", 0.9), 540 + math.sin(k * 7) * 40, y + 380 + ph * 400, 1, alfa=1 - ph)
    pegar(c, pulpo(t, "sorpresa", nado=0.9), 540, y, 0.8)
    texto(c, "PROPULSIÓN", 540, 1650, t - 0.15, 105, "#FFFFFF")
    return c, dict(zoom=1.0, t=t)


def e_para(t, d):
    c = degradado(W, H, [(0, "#081A28"), (1, "#0F3047")])
    pegar(c, corazon("#3D7BE0", 143), 540, 760, 0.9 * (1 + (0.12 * max(0, math.sin(t * 9)) if t < 0.5 else 0)))
    plano = ease_out((t - 0.5) / 0.4)
    ecg(c, t, 80, 1000, 1180, plano, (90, 255, 140) if plano < 0.5 else (255, 77, 109))
    if t > 0.6:
        texto(c, "SE DETIENE", 540, 1500, t - 0.6, 125, "#FF4D6D")
    return c, dict(zoom=1.0, t=t)


def e_agotado(t, d):
    c = fondo_mar(t)
    pegar(c, pulpo(t, "cansado", cansado=True), 540, 1350 + math.sin(t * 2) * 10, 0.95, sy=0.9)
    for k in range(3):
        ph = (t * 0.8 + k / 3) % 1
        pegar(c, gota_color("#BFE6FF"), 380 + k * 140, 900 + ph * 150, 0.6, alfa=1 - ph)
    texto(c, "AGOTADO", 540, 1700, t - 0.15, 110, "#FFD400")
    return c, dict(zoom=1.2, fy=0.6, t=t)


def e_camina(t, d):
    c = fondo_mar(t)
    x = 200 + clamp01(t / d) * 600
    pegar(c, pulpo(t, "feliz", caminar=1.0), x, 1350 + abs(math.sin(t * 6)) * -20, 0.75)
    texto(c, "MEJOR CAMINAR", 540, 1720, t - 0.15, 100, "#FFFFFF")
    return c, dict(zoom=1.05, fy=0.6, t=t)


def e_cardio(t, d):
    c = degradado(W, H, [(0, "#FFD400"), (1, "#FFB000")])
    pegar(c, pulpo(t, "cansado"), 540, 1150, 0.8)
    m = Image.new("L", (520, 160), 0)
    dm = ImageDraw.Draw(m)
    dm.rounded_rectangle([0, 0, 120, 160], radius=24, fill=255)
    dm.rounded_rectangle([400, 0, 520, 160], radius=24, fill=255)
    dm.rectangle([110, 60, 410, 100], fill=255)
    pegar(c, sprite(m, "#3B3550", 171), 540, 600, 0.9, rot=math.sin(t * 3) * 6)
    img, dd = capa()
    u = clamp01((t - 0.3) / 0.25)
    if u:
        s = 200 * back_out(u)
        dd.line([(540 - s, 600 - s * 0.6), (540 + s, 600 + s * 0.6)], fill=(255, 77, 109, 255), width=36)
        dd.line([(540 - s, 600 + s * 0.6), (540 + s, 600 - s * 0.6)], fill=(255, 77, 109, 255), width=36)
    c.alpha_composite(img)
    texto(c, "CERO CARDIO", 540, 1650, t - 0.35, 115, "#FFFFFF")
    return c, dict(zoom=1.0 + 0.04 * t, t=t)


def e_cta(t, d):
    c = fondo_mar(t)
    pegar(c, nico(t, "feliz", 10, 140 + 25 * math.sin(t * 10), traje="#2D3E5C", casco=True), 330, 1800, 0.85, ancla="abajo")
    pegar(c, pulpo(t, "feliz"), 790, 1350, 0.55)
    globo_texto(c, "¿QUÉ ANIMAL\nEXPLICO AHORA?", 540, 900, t - 0.1)
    boton_seguir(t, 1200)
    return c, dict(zoom=1.0, t=t)


PLAN = [
    (0, 0.0, e_gancho, None, ["impacto", ("pop", 0.2)]),
    (0, 0.55, e_sangre, None, [("pop", 0.6)]),
    (1, 0.0, e_nico_buzo, "barrido", ["whoosh", "burbujas"]),
    (1, 0.5, e_ovni, None, ["riser_suave"]),
    (2, 0.0, e_rayosx, "barrido", ["whoosh_grave", ("blip", 0.2)]),
    (2, 0.55, e_branquias, None, ["latido"]),
    (3, 0.0, e_oxigeno, None, ["burbujas"]),
    (4, 0.0, e_sistemico, None, ["latido", ("pop", 0.15)]),
    (4, 0.55, e_reparte, None, ["whoosh"]),
    (5, 0.0, e_azul, "barrido", ["blip"]),
    (5, 0.5, e_cobre, None, [("impacto", 0.05), ("pop", 0.05)]),
    (6, 0.0, e_humano, "barrido", ["whoosh", ("pop", 0.1), ("pop", 0.3)]),
    (7, 0.0, e_hemocianina, None, ["burbujas", ("ding", 1.0)]),
    (7, 0.6, e_comparacion, None, ["whoosh", ("pop", 0.05), ("pop", 0.2)]),
    (8, 0.0, e_frio, None, ["riser_suave"]),
    (9, 0.0, e_giro, None, ["scratch"]),
    (10, 0.0, e_nada, None, ["whoosh_grave", "burbujas"]),
    (10, 0.5, e_para, None, ["latido", ("alarma", 0.6)]),
    (11, 0.0, e_agotado, None, ["squish"]),
    (11, 0.5, e_camina, None, ["paso"]),
    (12, 0.0, e_cardio, "barrido", ["whoosh", ("buzz", 0.3)]),
    (13, 0.0, e_cta, "barrido", ["whoosh", ("pop", 0.1), ("ding", 0.3)]),
]

ESCENAS, DURACION = construir_escenas(GUION, PLAN)
_g = [e for e in ESCENAS if e["f"] is e_giro][0]
CORTE_MUSICA = (_g["ini"], _g["ini"] + 0.45)
