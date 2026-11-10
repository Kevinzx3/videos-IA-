#!/usr/bin/env python3
"""Video de prueba estilo 'ilustración con textura' – Qué hacer si te encuentras un puma."""
import math, os, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "salida")
VOZ = os.environ.get("VOZ_MODELO", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "voces", "es-carlfm-x-low.onnx"))
F_REG = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"
F_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
HORIZ = 1080
GAP = 0.3

ESCENAS = [
    ("camina", "Si te encuentras con un puma, *nunca* salgas corriendo.", "NO CORRAS"),
    ("brazos", "Hazte lo más *grande* posible: levanta los brazos.", None),
    ("mira", "Mírale a los ojos, y retrocede *despacio*, sin darle la espalda.", "DESPACIO"),
    ("ataca", "Y si ataca, *defiéndete* con todo. Nunca te hagas el muerto.", "DEFIÉNDETE"),
]

RNG = np.random.default_rng(5)


# ------------------------------------------------------------------ voz
def sintetizar():
    os.makedirs(OUT, exist_ok=True)
    partes, tiempos, t, sr = [], [], 0.3, 16000
    for i, (_, txt, _) in enumerate(ESCENAS):
        f = os.path.join(OUT, f"_l{i}.wav")
        subprocess.run(["python3", "-m", "piper", "-m", VOZ, "-f", f, "--length_scale", "1.0"],
                       input=txt.replace("*", "").encode(), check=True, capture_output=True)
        w = wave.open(f); sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16)
        partes.append(x); d = len(x) / sr
        tiempos.append((t, t + d)); t += d + GAP
        os.remove(f)
    total = t + 0.5
    pista = np.zeros(int(total * sr), np.int16)
    for x, (a, _) in zip(partes, tiempos):
        i = int(a * sr); pista[i:i + len(x)] = x
    ruta = os.path.join(OUT, "voz_puma.wav")
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pista.tobytes())
    return ruta, tiempos, total


# ------------------------------------------------------------------ texturas
def ruido(w, h, escala, seed):
    r = np.random.default_rng(seed).random((max(2, h // escala), max(2, w // escala)))
    return np.asarray(Image.fromarray((r * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), float) / 255


def vetas(w, h, seed, vertical=False):
    """Textura de pelo/hierba: ruido estirado en una dirección."""
    r = np.random.default_rng(seed).random((h, w))
    img = Image.fromarray((r * 255).astype(np.uint8))
    img = img.filter(ImageFilter.BoxBlur(1))
    img = img.resize((w // 3, h // 14) if vertical else (w // 14, h // 3), Image.BILINEAR)
    img = img.resize((w, h), Image.BICUBIC)
    return np.asarray(img, float) / 255


def escenario(seed=1):
    # cielo
    y = np.linspace(0, 1, HORIZ)[:, None]
    stops = [(0, (34, 24, 58)), (0.45, (92, 48, 92)), (0.78, (196, 98, 92)), (1, (240, 150, 96))]
    cielo = np.zeros((HORIZ, W, 3))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (y >= a) & (y <= b); k = np.clip((y - a) / (b - a), 0, 1)
        for c in range(3):
            cielo[:, :, c] = np.where(m, ca[c] + (cb[c] - ca[c]) * k, cielo[:, :, c])
    img = Image.fromarray(cielo.astype(np.uint8)).convert("RGBA")
    full = Image.new("RGBA", (W, H)); full.paste(img, (0, 0))
    d = ImageDraw.Draw(full); rnd = random.Random(seed)
    for _ in range(70):
        x, yy = rnd.uniform(0, W), rnd.uniform(0, 650); r = rnd.uniform(1, 2.6)
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=(255, 240, 230, rnd.randint(90, 200)))
    # montañas
    x = -100
    while x < W + 100:
        w = rnd.uniform(300, 500); h = rnd.uniform(140, 240)
        d.polygon([(x, HORIZ), (x + w / 2, HORIZ - h), (x + w, HORIZ)], fill=(96, 72, 130))
        x += w * 0.55
    # dos capas de pinos
    for capa, (col, hmin, hmax, n, base) in enumerate([((44, 70, 78), 330, 480, 13, HORIZ + 10),
                                                       ((28, 52, 56), 460, 640, 7, HORIZ + 20)]):
        for _ in range(n):
            px = rnd.uniform(-60, W + 60); ph = rnd.uniform(hmin, hmax); pw = ph * 0.32
            pisos = 5
            for k in range(pisos):
                top = base - ph + k * ph * 0.16
                bw = pw * (0.35 + 0.65 * (k + 1) / pisos)
                d.polygon([(px, top), (px - bw, top + ph * 0.24), (px + bw, top + ph * 0.24)], fill=col)
    # pradera con textura
    gh = H - HORIZ
    v = vetas(W, gh, seed + 9, vertical=True)
    yy = np.linspace(0, 1, gh)[:, None]
    base_c = np.stack([150 - 90 * yy, 160 - 70 * yy, 60 - 30 * yy], -1)
    pasto = base_c * (0.72 + 0.5 * v[:, :, None])
    pasto = np.clip(pasto + 30 * (1 - yy[:, :, None]) ** 6, 0, 255).astype(np.uint8)
    full.paste(Image.fromarray(pasto).convert("RGBA"), (0, HORIZ))
    # línea de luz en el horizonte
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rectangle((0, HORIZ - 3, W, HORIZ + 3), fill=(255, 230, 170, 255))
    full.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
    full.alpha_composite(glow.filter(ImageFilter.GaussianBlur(2)))
    return full


# ------------------------------------------------------------------ pelaje
FUR_N = None


def peludo(img):
    """Convierte un sprite plano en uno con borde peludo y textura de pelo."""
    global FUR_N
    w, h = img.size
    if FUR_N is None or FUR_N[0].shape != (h, w):
        FUR_N = (ruido(w, h, 2, 11), vetas(w, h, 12))
    n1, n2 = FUR_N
    a = np.asarray(img.split()[3].filter(ImageFilter.GaussianBlur(3.5)), float) / 255
    a2 = ((a + (n1 - 0.5) * 0.6) > 0.5).astype(float)
    rgb = np.asarray(img.convert("RGB"), float)
    # rellenar color del borde extendido
    rgb_b = np.asarray(img.convert("RGB").filter(ImageFilter.MaxFilter(7)), float)
    orig_a = np.asarray(img.split()[3], float)[:, :, None] / 255
    rgb = rgb * orig_a + rgb_b * (1 - orig_a)
    rgb *= (0.78 + 0.42 * n2[:, :, None])
    # sombreado inferior suave
    rgb *= np.linspace(1.08, 0.82, h)[:, None, None]
    out = np.dstack([np.clip(rgb, 0, 255), a2 * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def capsula(d, p1, p2, wd, col):
    d.line([p1, p2], fill=col, width=int(wd))
    r = wd / 2
    for x, y in (p1, p2):
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def puma(t, anda=True, agazapado=0.0):
    """Puma de perfil mirando a la derecha. Devuelve sprite RGBA 1000x620."""
    img = Image.new("RGBA", (1000, 620), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    TAN, TAN_D, CREMA = (196, 146, 92), (150, 104, 64), (218, 184, 140)
    ag = agazapado * 70
    fase = t * 5.0 if anda else 0
    by = 250 + ag  # altura del lomo
    # patas lejanas (más oscuras)
    for hx, off in ((300, math.pi), (650, 0)):
        a = math.sin(fase + off + 1.2) * 0.38 if anda else -0.15 * agazapado
        top = (hx, by + 90); rod = (top[0] + 150 * math.sin(a) * 0.6, top[1] + 120)
        pata = (rod[0] + 30 * math.sin(a), 520)
        capsula(d, top, rod, 64, TAN_D); capsula(d, rod, pata, 52, TAN_D)
        d.ellipse((pata[0] - 34, pata[1] - 20, pata[0] + 40, pata[1] + 16), fill=TAN_D)
    # cola
    sw = math.sin(t * 2.6) * 30
    pts = [(230, by + 10), (150, by + 60), (100, by + 160), (80 + sw * 0.4, by + 240), (40 + sw, by + 230 - ag * 0.5)]
    for p, q in zip(pts, pts[1:]):
        capsula(d, p, q, 34, TAN)
    d.ellipse((pts[-1][0] - 26, pts[-1][1] - 22, pts[-1][0] + 26, pts[-1][1] + 22), fill=(60, 40, 30))
    # cuerpo
    d.ellipse((200, by - 20, 420, by + 170), fill=TAN)
    d.rounded_rectangle((260, by - 5, 720, by + 160), radius=80, fill=TAN)
    d.ellipse((580, by - 30, 760, by + 170), fill=TAN)
    # cuello y cabeza
    hy = by - 60 + ag * 0.9
    d.polygon([(640, by + 10), (720, hy + 40), (800, hy + 70), (760, by + 140)], fill=TAN)
    d.ellipse((720, hy - 50, 890, hy + 100), fill=TAN)
    d.ellipse((820, hy + 25, 935, hy + 105), fill=CREMA)
    d.polygon([(760, hy - 20), (775, hy - 85), (815, hy - 30)], fill=TAN)
    d.polygon([(772, hy - 32), (780, hy - 66), (802, hy - 34)], fill=(110, 70, 50))
    # patas cercanas
    for hx, off in ((330, 0), (680, math.pi)):
        a = math.sin(fase + off) * 0.38 if anda else -0.2 * agazapado
        top = (hx, by + 80); rod = (top[0] + 150 * math.sin(a) * 0.6, top[1] + 125 - ag * 0.3)
        pata = (rod[0] + 30 * math.sin(a), 540)
        capsula(d, top, rod, 76, TAN); capsula(d, rod, pata, 58, TAN)
        d.ellipse((pata[0] - 38, pata[1] - 22, pata[0] + 46, pata[1] + 18), fill=TAN)
    s = peludo(img)
    d = ImageDraw.Draw(s)
    # detalles nítidos (ojo, nariz, marcas)
    d.ellipse((842, hy + 12, 862, hy + 32), fill=(20, 16, 14))
    d.ellipse((849, hy + 15, 855, hy + 21), fill=(255, 255, 255))
    d.polygon([(912, hy + 40), (934, hy + 44), (920, hy + 58)], fill=(120, 70, 70))
    d.line((905, hy + 70, 880, hy + 85), fill=(60, 40, 30), width=5)
    d.line((838, hy + 50, 860, hy + 82), fill=(90, 60, 40), width=6)
    return s


def excursionista(brazos):
    """Persona vista de espaldas. brazos: 0 (abajo) .. 1 (arriba).
    Lienzo con margen (OX, OY) para que las manos nunca se corten."""
    OX, OY = 160, 220
    img = Image.new("RGBA", (520 + 2 * OX, 980 + OY), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    P_ = lambda x, y: (x + OX, y + OY)
    TEAL, TEAL_D, JEAN, NAR = (38, 160, 160), (30, 132, 134), (40, 78, 150), (238, 120, 40)
    PIEL = (150, 100, 70)
    # piernas
    capsula(d, P_(215, 560), P_(200, 900), 66, JEAN); capsula(d, P_(305, 560), P_(320, 900), 66, JEAN)
    for x in (195, 325):
        d.ellipse((*P_(x - 40, 890), *P_(x + 40, 940)), fill=(110, 70, 40))
    # torso
    d.rounded_rectangle((*P_(150, 230), *P_(370, 600)), radius=60, fill=TEAL)
    # brazos: el hombro sube y el codo se abre hacia fuera (forma de V)
    for sgn in (-1, 1):
        hom = P_(260 + sgn * 92, 275 - 20 * brazos)
        a1 = sgn * (0.12 + brazos * 2.55)            # brazo superior
        a2 = sgn * (0.05 + brazos * 2.85)            # antebrazo (algo más vertical arriba)
        codo = (hom[0] + 150 * math.sin(a1), hom[1] + 150 * math.cos(a1))
        mano = (codo[0] + 135 * math.sin(a2), codo[1] + 135 * math.cos(a2))
        d.ellipse((hom[0] - 42, hom[1] - 42, hom[0] + 42, hom[1] + 42), fill=TEAL)   # hombro
        capsula(d, hom, codo, 72, TEAL); capsula(d, codo, mano, 62, TEAL_D)
        d.ellipse((codo[0] - 33, codo[1] - 33, codo[0] + 33, codo[1] + 33), fill=TEAL)
        # puño de la manga + mano
        cx_, cy_ = codo[0] + 0.85 * (mano[0] - codo[0]), codo[1] + 0.85 * (mano[1] - codo[1])
        d.ellipse((cx_ - 33, cy_ - 33, cx_ + 33, cy_ + 33), fill=(26, 112, 116))
        d.ellipse((mano[0] - 31, mano[1] - 31, mano[0] + 31, mano[1] + 31), fill=PIEL)
    # cabeza y gorro (encima de los hombros)
    d.ellipse((*P_(205, 110), *P_(315, 230)), fill=(110, 70, 45))
    d.chord((*P_(200, 90), *P_(320, 200)), 180, 360, fill=(250, 200, 40))
    d.rectangle((*P_(200, 140), *P_(320, 160)), fill=(230, 175, 30))
    # mochila
    d.rounded_rectangle((*P_(170, 250), *P_(350, 520)), radius=40, fill=NAR)
    d.rounded_rectangle((*P_(200, 380), *P_(320, 490)), radius=24, fill=(214, 98, 30))
    d.line((*P_(230, 425), *P_(290, 425)), fill=(120, 50, 20), width=8)
    d.rounded_rectangle((*P_(175, 240), *P_(345, 290)), radius=24, fill=(40, 70, 170))
    return peludo(img)


# ------------------------------------------------------------------ texto
def subtitulos_plan(tiempos):
    out = []
    for (a, b), (_, txt, _) in zip(tiempos, ESCENAS):
        pal = txt.split(); tot = sum(len(p.strip("*")) + 2 for p in pal); t = a; grupo = []
        for p in pal:
            dur = (b - a) * (len(p.strip("*")) + 2) / tot
            grupo.append((t, t + dur, p.replace("*", ""), p.startswith("*")))
            t += dur
            if len(grupo) >= 5 or p.rstrip("*")[-1] in ".,:?!":
                out.append(grupo); grupo = []
        if grupo: out.append(grupo)
    return out


def dibujar_subs(d, grupo, t, f_reg, f_bold):
    # hasta 2 líneas centradas; palabras ya dichas tenues, actual en negrita blanca
    words = []
    for (a, b, p, clave) in grupo:
        act = a <= t < b; dicha = t >= a
        f = f_bold if (act or clave) else f_reg
        words.append((p, f, act, dicha, clave, d.textlength(p, font=f)))
    sp = 18; lines = [[]]; lw = 0
    for w in words:
        if lw + w[5] > W - 160 and lines[-1]:
            lines.append([]); lw = 0
        lines[-1].append(w); lw += w[5] + sp
    for li, line in enumerate(lines):
        tw = sum(w[5] for w in line) + sp * (len(line) - 1); x = W / 2 - tw / 2
        y = 330 + li * 78
        for (p, f, act, dicha, clave, wd) in line:
            if clave and dicha:
                d.rounded_rectangle((x - 12, y - 40, x + wd + 12, y + 40), radius=10,
                                    fill=(40, 60, 120, 200), outline=(140, 180, 255, 255), width=3)
            alpha = 255 if (act or (clave and dicha)) else (150 if dicha else 0)
            if alpha:
                d.text((x, y), p, font=f, fill=(255, 255, 255, alpha), anchor="lm")
            x += wd + sp


def chip(capa, texto, k, cy, f):
    if k <= 0: return
    d = ImageDraw.Draw(capa)
    tw = d.textlength(texto, font=f); pw, ph = (tw + 70) * k, 110 * k
    cx = W / 2
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).rounded_rectangle((cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2), radius=int(28 * k),
                                        fill=(255, 200, 120, 90))
    capa.alpha_composite(g.filter(ImageFilter.GaussianBlur(18)))
    d.rounded_rectangle((cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2), radius=int(28 * k),
                        fill=(30, 26, 30, 230), outline=(90, 80, 70, 255), width=2)
    if k > 0.85:
        d.text((cx, cy), texto, font=f, fill=(255, 226, 170), anchor="mm")


def eob(t):
    t = max(0.0, min(1.0, t)); return 1 + 2.70158 * (t - 1) ** 3 + 1.70158 * (t - 1) ** 2


def eio(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ main
def main():
    voz, tiempos, total = sintetizar()
    fondo = escenario()
    f_reg = ImageFont.truetype(F_REG, 58); f_bold = ImageFont.truetype(F_BOLD, 60)
    f_chip = ImageFont.truetype(F_BOLD, 66)
    subs = subtitulos_plan(tiempos)
    rnd = random.Random(3)
    luci = [(rnd.uniform(0, W), rnd.uniform(500, 1800), rnd.uniform(0, 6.3), rnd.uniform(10, 30)) for _ in range(26)]
    salida = os.path.join(OUT, "puma_prueba.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", voz,
                           "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", salida],
                          stdin=subprocess.PIPE)
    hiker_cache = {}
    for fi in range(int(total * FPS)):
        t = fi / FPS
        esc = max([0] + [i for i, (a, b) in enumerate(tiempos) if a - 0.2 <= t])
        tipo, _, rotulo = ESCENAS[esc]
        a0 = tiempos[esc][0] - (0.3 if esc == 0 else 0.2)
        fin = tiempos[esc + 1][0] - 0.2 if esc + 1 < len(tiempos) else total
        lt = t - a0; dur = fin - a0; pr = lt / dur
        fr = fondo.copy()
        mundo = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        if tipo == "camina":
            sp = puma(t, anda=True)
            x = int(-300 + 420 * pr); sc = 0.95
            sp = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.BILINEAR)
            sombra(mundo, x + sp.width * 0.5, 1110 + sp.height - 40, sp.width * 0.42)
            mundo.alpha_composite(sp, (x, 1110))
        elif tipo == "brazos":
            sp = puma(t, anda=False).resize((300, 186), Image.BILINEAR)
            sombra(mundo, 790, HORIZ + 210, 110)
            mundo.alpha_composite(sp, (640, HORIZ + 40))
            br = round(eio((lt - 0.6) / 0.8), 2)
            if br not in hiker_cache: hiker_cache[br] = excursionista(br)
            hk = hiker_cache[br]
            sombra(mundo, W / 2, 1830, 210)
            mundo.alpha_composite(hk, (int(W / 2 - hk.width / 2), 880 - 220))
        elif tipo == "mira":
            sp = puma(t, anda=False)
            sc = 1.25; sp = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.BILINEAR)
            x = int(W - sp.width + 120 - 60 * pr)
            sombra(mundo, x + sp.width * 0.5, 1050 + sp.height - 50, sp.width * 0.42)
            mundo.alpha_composite(sp, (x, 1050))
        else:  # ataca
            ag = eio(lt / 1.2)
            sp = puma(t, anda=False, agazapado=ag)
            sc = 1.3; sp = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.BILINEAR)
            x = int(-330 + 30 * math.sin(t * 3))
            sombra(mundo, x + sp.width * 0.5, 1020 + sp.height - 60, sp.width * 0.42)
            mundo.alpha_composite(sp, (x, 1020))
        fr.alpha_composite(mundo)

        # luciérnagas
        cap = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(cap)
        for x, y, ph, v in luci:
            yy = y - (v * t) % 300; xx = x + 25 * math.sin(t * 0.7 + ph)
            al = int(110 + 100 * math.sin(t * 2 + ph))
            d.ellipse((xx - 3, yy - 3, xx + 3, yy + 3), fill=(255, 250, 220, max(0, al)))
        fr.alpha_composite(cap)

        # cámara: zoom lento por escena
        z = 1.0 + 0.07 * eio(pr)
        if tipo == "ataca": z += 0.02 * abs(math.sin(t * 6))
        cw, ch = W / z, H / z
        cx = W / 2 + (40 if tipo == "mira" else 0) * pr
        fr = fr.crop((int(cx - cw / 2), int(H / 2 - ch / 2 + 60 * (z - 1) * 10), int(cx + cw / 2),
                      int(H / 2 + ch / 2 + 60 * (z - 1) * 10))).resize((W, H), Image.BILINEAR)

        if tipo == "ataca":  # pulso rojo en los bordes
            v = Image.new("RGBA", (W, H), (180, 20, 20, int(70 + 50 * math.sin(t * 7))))
            m = Image.new("L", (W, H), 255)
            ImageDraw.Draw(m).ellipse((-100, 150, W + 100, H - 150), fill=0)
            v.putalpha(ImageChops.multiply(v.split()[3], m.filter(ImageFilter.GaussianBlur(120))))
            fr.alpha_composite(v)

        # texto encima (sin zoom)
        ui = Image.new("RGBA", (W, H), (0, 0, 0, 0)); du = ImageDraw.Draw(ui)
        g = None
        for gr in subs:
            if gr[0][0] <= t: g = gr
        if g and t <= g[-1][1] + 0.4:
            dibujar_subs(du, g, t, f_reg, f_bold)
        if rotulo:
            chip(ui, rotulo, eob((lt - 0.9) / 0.35), 560, f_chip)
        # fundido en los cortes
        if lt < 0.12 and esc > 0:
            ui.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - lt / 0.12)))))
        fr.alpha_composite(ui)
        ff.stdin.write(fr.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    print("✔", salida, f"{total:.1f}s")


def sombra(capa, cx, cy, rx):
    g = Image.new("RGBA", capa.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((cx - rx, cy - 26, cx + rx, cy + 26), fill=(10, 20, 10, 120))
    capa.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)))


if __name__ == "__main__":
    main()
