"""Biblioteca de dibujo reutilizable (estilo ilustración con textura).

Personajes y escenarios para generar clips animados de cada escena.
"""
import math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "estilo_bosque"))
import puma as P  # noqa: E402  (peludo, capsula, escenario, puma, excursionista)

W, H, FPS = 1080, 1920, 30
peludo, capsula = P.peludo, P.capsula
eio, eob = P.eio, P.eob


# ------------------------------------------------------------------ utilidades
def cielo(h=1080, stops=None):
    stops = stops or [(0, (34, 24, 58)), (0.45, (92, 48, 92)), (0.78, (196, 98, 92)), (1, (240, 150, 96))]
    y = np.linspace(0, 1, h)[:, None]
    c = np.zeros((h, W, 3))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (y >= a) & (y <= b); k = np.clip((y - a) / (b - a), 0, 1)
        for i in range(3):
            c[:, :, i] = np.where(m, ca[i] + (cb[i] - ca[i]) * k, c[:, :, i])
    img = Image.new("RGBA", (W, H)); img.paste(Image.fromarray(c.astype(np.uint8)).convert("RGBA"), (0, 0))
    d = ImageDraw.Draw(img); rnd = random.Random(9)
    for _ in range(60):
        x, yy, r = rnd.uniform(0, W), rnd.uniform(0, h * 0.55), rnd.uniform(1, 2.5)
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=(255, 240, 230, rnd.randint(80, 190)))
    return img


def textura(w, h, col_arriba, col_abajo, seed=3, vertical=True, fuerza=0.45):
    v = P.vetas(w, h, seed, vertical=vertical)
    y = np.linspace(0, 1, h)[:, None, None]
    a, b = np.array(col_arriba, float), np.array(col_abajo, float)
    base = a + (b - a) * y
    out = np.clip(base * (1 - fuerza / 2 + fuerza * v[:, :, None]), 0, 255).astype(np.uint8)
    return Image.fromarray(out).convert("RGBA")


def sombra(capa, cx, cy, rx, ry=24, a=110):
    g = Image.new("RGBA", (int(rx * 2 + 60), int(ry * 2 + 60)), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((30, 30, 30 + rx * 2, 30 + ry * 2), fill=(10, 15, 10, a))
    g = g.filter(ImageFilter.GaussianBlur(12))
    capa.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))


def pegar(fondo, sprite, cx, base_y, escala=1.0):
    """Pega un sprite centrado en x con sus 'pies' (borde inferior) en base_y."""
    if escala != 1.0:
        sprite = sprite.resize((max(1, int(sprite.width * escala)), max(1, int(sprite.height * escala))), Image.BILINEAR)
    fondo.alpha_composite(sprite, (int(cx - sprite.width / 2), int(base_y - sprite.height)))


def luz_calida(fr, fuerza=60):
    g = Image.new("RGBA", (W, H), (255, 190, 120, 0))
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse((-200, 700, W + 200, 1500), fill=fuerza)
    g.putalpha(m.filter(ImageFilter.GaussianBlur(160)))
    fr.alpha_composite(g)


class Clip:
    """Escribe un mp4 mudo frame a frame."""

    def __init__(self, ruta, dur):
        self.n = max(1, int(round(dur * FPS)))
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        self.ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                    "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18",
                                    "-preset", "fast", "-pix_fmt", "yuv420p", ruta], stdin=subprocess.PIPE)

    def frames(self):
        for i in range(self.n):
            yield i / FPS, i / max(1, self.n - 1)

    def escribir(self, img):
        self.ff.stdin.write(img.convert("RGB").tobytes())

    def cerrar(self):
        self.ff.stdin.close(); self.ff.wait()


# ------------------------------------------------------------------ árboles
_arbol_cache = {}


def arbol(tipo=0, seed=0):
    """Árbol frondoso con textura. tipo 0: copa redonda, 1: bambú."""
    key = (tipo, seed)
    if key in _arbol_cache: return _arbol_cache[key]
    rnd = random.Random(seed)
    img = Image.new("RGBA", (600, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    verdes = [(46, 110, 62), (60, 132, 70), (36, 92, 54), (74, 146, 80)]
    if tipo == 0:
        d.polygon([(280, 900), (320, 900), (312, 420), (288, 420)], fill=(92, 62, 40))
        d.line((300, 560, 220, 470), fill=(92, 62, 40), width=22); d.line((300, 520, 390, 440), fill=(92, 62, 40), width=20)
        for _ in range(9):
            r = rnd.uniform(110, 170); x = 300 + rnd.uniform(-140, 140); y = 330 + rnd.uniform(-170, 90)
            d.ellipse((x - r, y - r, x + r, y + r), fill=rnd.choice(verdes))
    else:
        for k in range(7):
            x = 230 + k * 22 + rnd.uniform(-8, 8); top = rnd.uniform(60, 200)
            d.line((x, 900, x + rnd.uniform(-30, 30), top), fill=(98, 140, 60), width=16)
            for yy in range(int(top), 860, 70):
                d.line((x - 10, yy, x + 10, yy), fill=(70, 100, 40), width=4)
                lado = rnd.choice((-1, 1))
                d.polygon([(x, yy), (x + lado * 90, yy - 30), (x + lado * 80, yy - 10)], fill=rnd.choice(verdes))
    s = peludo(img)
    _arbol_cache[key] = s
    return s


def brote():
    img = Image.new("RGBA", (200, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.line((100, 260, 100, 90), fill=(90, 130, 50), width=12)
    for lado, y in ((-1, 140), (1, 110), (-1, 90)):
        d.ellipse((100 + (lado < 0) * -80, y - 25, 100 + (lado > 0) * 80, y + 25), fill=(88, 160, 70))
    return peludo(img)


# ------------------------------------------------------------------ persona de frente
def persona(pose="de_pie", t=0.0, viejo=False, piel=(150, 98, 64), camisa=(236, 232, 220),
            pantalon=(70, 64, 60), sonrisa=False, triste=False):
    """Persona de frente. pose: de_pie | arrodillado | cubos | saluda."""
    img = Image.new("RGBA", (700, 1200), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    cx = 350; pelo = (235, 235, 230) if viejo else (25, 20, 18)
    resp = math.sin(t * 2.2) * 4
    arrod = pose == "arrodillado"
    cadera_y = 860 if arrod else 700
    # piernas
    if arrod:
        capsula(d, (cx - 50, cadera_y), (cx - 70, 1000), 74, pantalon); capsula(d, (cx - 70, 1000), (cx - 10, 1150), 66, pantalon)
        capsula(d, (cx + 50, cadera_y), (cx + 120, 1050), 74, pantalon); capsula(d, (cx + 120, 1050), (cx + 110, 1150), 66, pantalon)
    else:
        capsula(d, (cx - 50, cadera_y), (cx - 60, 1130), 76, pantalon); capsula(d, (cx + 50, cadera_y), (cx + 60, 1130), 76, pantalon)
        for x in (cx - 62, cx + 62):
            d.ellipse((x - 48, 1120, x + 48, 1165), fill=(60, 45, 35))
    hy = cadera_y - 400 + resp  # hombros
    # torso
    d.rounded_rectangle((cx - 120, hy, cx + 120, cadera_y + 40), radius=70, fill=camisa)
    # brazos
    def brazo(sgn, codo, mano):
        hom = (cx + sgn * 110, hy + 50)
        capsula(d, hom, codo, 64, camisa); capsula(d, codo, mano, 54, piel)
        d.ellipse((mano[0] - 30, mano[1] - 30, mano[0] + 30, mano[1] + 30), fill=piel)
    if pose == "cubos":
        for sgn in (-1, 1):
            brazo(sgn, (cx + sgn * 160, hy + 200), (cx + sgn * 175, hy + 360))
    elif pose == "arrodillado":
        k = math.sin(t * 3)
        brazo(-1, (cx - 150, hy + 200), (cx - 60, hy + 330 + 20 * k))
        brazo(1, (cx + 150, hy + 200), (cx + 60, hy + 330 - 20 * k))
    elif pose == "saluda":
        brazo(-1, (cx - 160, hy + 210), (cx - 170, hy + 380))
        a = math.sin(t * 8) * 0.35
        brazo(1, (cx + 210, hy - 20), (cx + 230 + 90 * math.sin(a), hy - 170))
    else:
        brazo(-1, (cx - 155, hy + 210), (cx - 165, hy + 390)); brazo(1, (cx + 155, hy + 210), (cx + 165, hy + 390))
    # cuello y cabeza
    d.rectangle((cx - 35, hy - 60, cx + 35, hy + 20), fill=piel)
    hc = (cx, hy - 150)
    d.ellipse((hc[0] - 112, hc[1] - 125, hc[0] + 112, hc[1] + 120), fill=piel)
    d.ellipse((hc[0] - 128, hc[1] - 20, hc[0] - 92, hc[1] + 40), fill=piel)
    d.ellipse((hc[0] + 92, hc[1] - 20, hc[0] + 128, hc[1] + 40), fill=piel)
    d.chord((hc[0] - 118, hc[1] - 140, hc[0] + 118, hc[1] + 30), 180, 360, fill=pelo)
    if viejo:
        d.chord((hc[0] - 100, hc[1] - 10, hc[0] + 100, hc[1] + 175), 0, 180, fill=pelo)
    s = peludo(img); d = ImageDraw.Draw(s)
    # cara nítida
    parp = (t % 3.3) < 0.12
    for dx in (-42, 42):
        ex, ey = hc[0] + dx, hc[1] + 5
        if parp: d.line((ex - 16, ey, ex + 16, ey), fill=(25, 18, 15), width=6)
        else:
            d.ellipse((ex - 14, ey - 16, ex + 14, ey + 16), fill=(25, 18, 15))
            d.ellipse((ex - 6, ey - 10, ex, ey - 4), fill=(255, 255, 255))
        if triste: d.line((ex - 20, ey - 30 + (8 if dx < 0 else -8), ex + 20, ey - 30 - (8 if dx < 0 else -8)), fill=(30, 22, 18), width=6)
        else: d.line((ex - 20, ey - 32, ex + 20, ey - 34), fill=(30, 22, 18) if not viejo else (220, 220, 215), width=6)
    my = hc[1] + 62
    if sonrisa: d.arc((hc[0] - 34, my - 26, hc[0] + 34, my + 16), 20, 160, fill=(80, 30, 30), width=7)
    elif triste: d.arc((hc[0] - 26, my, hc[0] + 26, my + 30), 200, 340, fill=(80, 30, 30), width=6)
    else: d.line((hc[0] - 18, my, hc[0] + 18, my), fill=(80, 30, 30), width=6)
    if pose == "cubos":  # palo sobre los hombros y cubos
        d.line((cx - 330, hy + 20, cx + 330, hy + 20), fill=(120, 84, 50), width=18)
        for sgn in (-1, 1):
            bx = cx + sgn * 300
            d.line((bx, hy + 20, bx - 40, hy + 260), fill=(60, 50, 40), width=4); d.line((bx, hy + 20, bx + 40, hy + 260), fill=(60, 50, 40), width=4)
            d.polygon([(bx - 60, hy + 255), (bx + 60, hy + 255), (bx + 48, hy + 380), (bx - 48, hy + 380)], fill=(120, 130, 140), outline=(60, 60, 70))
    return s


# ------------------------------------------------------------------ animales
def elefante(t):
    img = Image.new("RGBA", (1100, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    G, GD = (130, 128, 134), (104, 100, 108)
    f = t * 3.0
    for hx, off in ((330, math.pi), (720, 0)):
        a = math.sin(f + off + 1) * 0.22
        capsula(d, (hx, 520), (hx + 160 * math.sin(a), 860), 120, GD)
    d.ellipse((200, 250, 860, 660), fill=G)
    d.line((210, 420, 150, 600 + 20 * math.sin(t * 2)), fill=GD, width=16)
    d.ellipse((760, 200, 1010, 470), fill=G)
    # trompa
    pts = [(960, 380)]
    for k in range(1, 6):
        ang = 0.25 * k + 0.25 * math.sin(t * 2 + k * 0.6)
        pts.append((pts[-1][0] + 45 * math.sin(ang * 0.6), pts[-1][1] + 70 * math.cos(ang * 0.3)))
    for p_, q in zip(pts, pts[1:]): capsula(d, p_, q, 70 - 8 * pts.index(p_), G)
    d.ellipse((700, 230 + 5 * math.sin(t * 3), 870, 480), fill=GD)  # oreja
    for hx, off in ((380, 0), (770, math.pi)):
        a = math.sin(f + off) * 0.22
        capsula(d, (hx, 520), (hx + 160 * math.sin(a), 870), 130, G)
    s = peludo(img); d = ImageDraw.Draw(s)
    d.ellipse((900, 290, 918, 308), fill=(20, 18, 18))
    d.polygon([(930, 400), (1000, 440), (935, 430)], fill=(245, 240, 225))  # colmillo
    return s


def tigre(t, anda=True):
    s = P.puma(t, anda=anda)
    a = np.asarray(s, float)
    rgb = a[:, :, :3]
    lum = rgb.mean(axis=2, keepdims=True) / 160
    naranja = np.array([232, 128, 40.0])
    rgb2 = np.clip(naranja * lum * 1.05, 0, 255)
    # rayas
    h, w = rgb.shape[:2]
    xx = np.arange(w)[None, :]; yy = np.arange(h)[:, None]
    rayas = (np.sin((xx + 0.35 * yy) / 11.0) > 0.72) & (yy > 180)
    rgb2[rayas] *= 0.18
    out = np.dstack([rgb2, a[:, :, 3]]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def ciervo(t):
    img = Image.new("RGBA", (700, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    C = (170, 112, 70)
    for hx in (210, 260, 440, 490):
        capsula(d, (hx, 380), (hx + 10 * math.sin(t * 2 + hx), 660), 40, C if hx in (210, 440) else (140, 92, 58))
    d.ellipse((170, 260, 530, 430), fill=C)
    d.polygon([(470, 300), (520, 160), (560, 170), (540, 320)], fill=C)
    d.ellipse((500, 110, 610, 200), fill=C)
    d.polygon([(560, 150), (650, 140), (575, 175)], fill=C)
    for k in (-1, 1):
        d.line((540 + k * 10, 115, 520 + k * 40, 30), fill=(110, 80, 50), width=8)
        d.line((530 + k * 25, 70, 500 + k * 55, 50), fill=(110, 80, 50), width=6)
    s = peludo(img); d = ImageDraw.Draw(s)
    d.ellipse((568, 140, 580, 152), fill=(15, 12, 10))
    return s


def gato(t, pose="sentado", rot=0.0):
    """Gato naranja. pose: sentado | cayendo (rot en radianes) | paracaidas."""
    img = Image.new("RGBA", (800, 800), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    N, ND, B = (232, 146, 60), (196, 112, 40), (250, 236, 214)
    if pose == "sentado":
        d.ellipse((240, 330, 560, 760), fill=N)
        d.ellipse((330, 420, 470, 740), fill=B)
        cola = [(520, 700), (640, 690), (690, 600 + 30 * math.sin(t * 2)), (660, 520 + 40 * math.sin(t * 2))]
        for p_, q in zip(cola, cola[1:]): capsula(d, p_, q, 50, N)
        d.ellipse((260, 130, 540, 390), fill=N)
        for sgn in (-1, 1):
            d.polygon([(400 + sgn * 120, 200), (400 + sgn * 130, 70), (400 + sgn * 40, 150)], fill=N)
        d.ellipse((330, 260, 470, 380), fill=B)
    else:
        # cuerpo estirado de lado con patas
        abre = 1.0 if pose == "paracaidas" else 0.3
        d.ellipse((200, 330, 620, 520), fill=N)
        for hx, sgn in ((260, -1), (330, -1), (500, 1), (570, 1)):
            capsula(d, (hx, 470), (hx + sgn * 120 * abre, 470 + 150 * (1 - 0.4 * abre)), 46, N)
        cola = [(210, 420), (110, 360), (60, 260)]
        for p_, q in zip(cola, cola[1:]): capsula(d, p_, q, 44, N)
        d.ellipse((540, 230, 760, 440), fill=N)
        for sgn in (-1, 1):
            d.polygon([(650 + sgn * 80, 280), (650 + sgn * 90, 170), (650 + sgn * 20, 250)], fill=N)
        d.ellipse((600, 330, 720, 430), fill=B)
    s = peludo(img); d = ImageDraw.Draw(s)
    # rayas y cara
    hcx, hcy = (400, 270) if pose == "sentado" else (650, 330)
    for k in (-1, 0, 1):
        d.line((hcx + k * 40, hcy - 110, hcx + k * 30, hcy - 60), fill=ND, width=12)
    for sgn in (-1, 1):
        ex, ey = hcx + sgn * 50, hcy - 10
        d.ellipse((ex - 24, ey - 26, ex + 24, ey + 26), fill=(120, 190, 90))
        d.ellipse((ex - 8, ey - 22, ex + 8, ey + 22), fill=(15, 12, 10))
        d.ellipse((ex - 14, ey - 16, ex - 6, ey - 8), fill="white")
    d.polygon([(hcx - 14, hcy + 40), (hcx + 14, hcy + 40), (hcx, hcy + 56)], fill=(220, 120, 130))
    for sgn in (-1, 1):
        for k in range(2):
            d.line((hcx + sgn * 40, hcy + 60 + k * 14, hcx + sgn * 150, hcy + 45 + k * 28), fill=(255, 255, 255, 210), width=3)
    if rot:  # recortar al contenido y rotar con margen para que nunca se corte
        s = s.crop(s.getbbox()).rotate(math.degrees(rot), resample=Image.BICUBIC, expand=True)
    return s
