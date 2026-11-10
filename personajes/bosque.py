#!/usr/bin/env python3
"""Video de prueba con personaje animado (Leo) en un bosque, con voz y lip-sync."""
import math, os, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "salida")
VOZ = os.environ.get("VOZ_MODELO", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "voces", "es-carlfm-x-low.onnx"))
F_SUB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
GAP = 0.35
GROUND = 1660

LINEAS = [
    ("camina", "¿Te perdiste en el bosque? No sigas caminando sin rumbo."),
    ("stop", "Detente, respira, y quédate en un solo lugar."),
    ("silbato", "Si tienes silbato, sopla tres veces. Es la señal de auxilio."),
    ("saluda", "Síguenos para más consejos."),
]

SKIN, SKIN_D = (242, 194, 155), (214, 160, 120)
SHIRT, PANTS = (46, 160, 90), (52, 70, 110)
CAP, BAG = (220, 50, 50), (170, 110, 60)
INK = (35, 30, 40)


# ---------------------------------------------------------------- audio
def sintetizar():
    os.makedirs(OUT, exist_ok=True)
    partes, tiempos, t, sr = [], [], 0.25, 16000
    for i, (_, txt) in enumerate(LINEAS):
        f = os.path.join(OUT, f"_l{i}.wav")
        subprocess.run(["python3", "-m", "piper", "-m", VOZ, "-f", f, "--length_scale", "0.95"],
                       input=txt.encode(), check=True, capture_output=True)
        w = wave.open(f); sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16)
        partes.append(x); d = len(x) / sr
        tiempos.append((t, t + d)); t += d + GAP + (1.7 if LINEAS[i][0] == 'silbato' else 0)
    total = t + 0.6
    pista = np.zeros(int(total * sr), np.int16)
    for x, (a, _) in zip(partes, tiempos):
        i = int(a * sr); pista[i:i + len(x)] = x
    ruta = os.path.join(OUT, "voz_bosque.wav")
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pista.tobytes())
    # envolvente por frame para mover la boca
    hop = sr // FPS
    env = np.array([np.sqrt(np.mean(pista[i:i + hop].astype(float) ** 2) + 1e-9)
                    for i in range(0, len(pista), hop)])
    env = np.clip(env / (np.percentile(env, 95) + 1e-9), 0, 1)
    return ruta, tiempos, total, env


# ---------------------------------------------------------------- escenario
def capa_arboles(seed, n, ancho, ytop, ybase, tam, col, col2):
    rnd = random.Random(seed)
    img = Image.new("RGBA", (ancho, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x = rnd.uniform(0, ancho); h = rnd.uniform(*tam); w = h * 0.42
        yb = ybase + rnd.uniform(-15, 15)
        d.rectangle((x - w * 0.07, yb - h * 0.15, x + w * 0.07, yb), fill=(90, 60, 40, 255))
        for k in range(3):  # pino en 3 pisos
            top = yb - h + k * h * 0.22; bw = w * (0.55 + k * 0.22)
            d.polygon([(x, top), (x - bw, top + h * 0.42), (x + bw, top + h * 0.42)],
                      fill=col if k % 2 == 0 else col2)
    return img


def escenario():
    cielo = Image.new("RGB", (1, H))
    for y in range(H):
        t = min(1, y / 1300)
        cielo.putpixel((0, y), (int(120 + 90 * t), int(190 + 45 * t), int(245 - 10 * t)))
    cielo = cielo.resize((W, H)).convert("RGBA")
    d = ImageDraw.Draw(cielo)
    d.ellipse((760, 180, 930, 350), fill=(255, 236, 140))
    sol = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sol).ellipse((700, 120, 990, 410), fill=(255, 240, 160, 90))
    cielo.alpha_composite(sol.filter(ImageFilter.GaussianBlur(40)))
    anchoL = W * 3
    mont = Image.new("RGBA", (anchoL, H), (0, 0, 0, 0))
    dm = ImageDraw.Draw(mont); rnd = random.Random(3)
    x = -200
    while x < anchoL + 200:
        w = rnd.uniform(380, 650); h = rnd.uniform(380, 600)
        dm.polygon([(x, 1250), (x + w / 2, 1250 - h), (x + w, 1250)], fill=(120, 150, 185))
        dm.polygon([(x + w / 2, 1250 - h), (x + w / 2 - w * 0.12, 1250 - h * 0.78),
                    (x + w / 2 + w * 0.12, 1250 - h * 0.78)], fill=(240, 245, 250))
        x += w * 0.6
    capas = [
        (mont, 0.1),
        (capa_arboles(1, 40, anchoL, 0, 1330, (260, 380), (60, 120, 95, 255), (70, 132, 104, 255)), 0.3),
        (capa_arboles(2, 26, anchoL, 0, 1460, (420, 560), (34, 100, 62, 255), (42, 114, 72, 255)), 0.6),
    ]
    suelo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(suelo)
    ds.rectangle((0, 1450, W, H), fill=(92, 160, 70))
    ds.polygon([(380, 1450), (700, 1450), (W + 200, H), (-200, H)], fill=(196, 160, 110))
    frente = capa_arboles(4, 7, anchoL, 0, H + 80, (900, 1100), (20, 74, 44, 255), (26, 86, 50, 255))
    return cielo, capas, suelo, frente


def pegar_capa(base, capa, off):
    off = int(off) % capa.width
    base.alpha_composite(capa.crop((off, 0, off + W, H)) if off + W <= capa.width else
                         _envuelto(capa, off))


def _envuelto(capa, off):
    a = capa.crop((off, 0, capa.width, H)); b = capa.crop((0, 0, W - a.width, H))
    out = Image.new("RGBA", (W, H)); out.paste(a, (0, 0)); out.paste(b, (a.width, 0))
    return out


# ---------------------------------------------------------------- personaje
def miembro(d, p1, p2, ancho, col):
    d.line([p1, p2], fill=col, width=ancho)
    r = ancho / 2
    for (x, y) in (p1, p2):
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def polar(o, ang, l):
    return (o[0] + l * math.sin(ang), o[1] + l * math.cos(ang))


def dibujar_leo(d, cx, s, st):
    """st: fase, anda, boca(0-1), parpadeo, cejas, brazo, mira, sonrisa, sopla"""
    S = lambda v: v * s
    bob = abs(math.sin(st["fase"])) * S(-14) if st["anda"] else math.sin(st["t"] * 2) * S(4)
    cadera = (cx, GROUND - S(190) + bob)
    hombro = (cx, cadera[1] - S(210))
    ang_p = math.sin(st["fase"]) * 0.55 if st["anda"] else 0.0

    # pierna y brazo traseros
    for sgn, col in ((-1, (40, 56, 92)),):
        cb = (cadera[0] - S(30), cadera[1])
        rod = polar(cb, -ang_p, S(100))
        pie = polar(rod, -ang_p - (0.25 if st["anda"] else 0), S(95))
        miembro(d, cb, rod, int(S(46)), col); miembro(d, rod, pie, int(S(42)), col)
        d.ellipse((pie[0] - S(40), pie[1] - S(16), pie[0] + S(44), pie[1] + S(22)), fill=INK)
    if st["brazo"] in ("balanceo", "pecho", "silbato", "saluda"):
        a = -ang_p * 0.9 if st["anda"] else 0.12
        codo = polar((hombro[0] - S(55), hombro[1] + S(20)), a, S(95))
        mano = polar(codo, a - 0.1, S(85))
        miembro(d, (hombro[0] - S(55), hombro[1] + S(20)), codo, int(S(36)), (36, 136, 76))
        miembro(d, codo, mano, int(S(32)), SKIN_D)

    # mochila
    d.rounded_rectangle((cx - S(120), hombro[1] + S(5), cx - S(30), cadera[1] - S(15)),
                        radius=int(S(30)), fill=BAG, outline=INK, width=int(S(5)))
    # pierna delantera
    cf = (cadera[0] + S(30), cadera[1])
    rod = polar(cf, ang_p, S(100))
    pie = polar(rod, ang_p - (0.25 if st["anda"] else 0), S(95))
    miembro(d, cf, rod, int(S(48)), PANTS); miembro(d, rod, pie, int(S(44)), PANTS)
    d.ellipse((pie[0] - S(40), pie[1] - S(16), pie[0] + S(46), pie[1] + S(24)), fill=INK)
    # torso
    d.rounded_rectangle((cx - S(78), hombro[1] - S(10), cx + S(78), cadera[1] + S(20)),
                        radius=int(S(55)), fill=SHIRT, outline=INK, width=int(S(5)))
    d.rectangle((cx - S(78), cadera[1] - S(10), cx + S(78), cadera[1] + S(20)), fill=PANTS)
    d.line((cx - S(30), hombro[1], cx - S(55), cadera[1] - S(20)), fill=(120, 80, 40), width=int(S(14)))

    # brazo delantero
    sh = (cx + S(60), hombro[1] + S(20))
    if st["brazo"] == "balanceo":
        a = ang_p * 0.9 if st["anda"] else -0.12
        codo = polar(sh, a, S(95)); mano = polar(codo, a + 0.15, S(85))
    elif st["brazo"] == "pecho":  # mano al pecho, respirando
        codo = polar(sh, -0.5, S(90)); mano = (cx + S(10), hombro[1] + S(70) + math.sin(st["t"] * 3) * S(5))
    elif st["brazo"] == "silbato":
        codo = (cx + S(130), hombro[1] - S(10)); mano = (cx + S(55), hombro[1] - S(110))
    else:  # saluda
        codo = (cx + S(150), hombro[1] - S(40))
        mano = polar(codo, math.pi - 0.3 + 0.45 * math.sin(st["t"] * 9), S(95))
    miembro(d, sh, codo, int(S(38)), SHIRT); miembro(d, codo, mano, int(S(34)), SKIN)
    d.ellipse((mano[0] - S(24), mano[1] - S(24), mano[0] + S(24), mano[1] + S(24)), fill=SKIN)

    # cabeza
    hc = (cx + st["mira"] * S(8), hombro[1] - S(130))
    R = S(125)
    d.ellipse((hc[0] - R - S(18), hc[1] - S(10), hc[0] - R + S(22), hc[1] + S(40)), fill=SKIN_D)
    d.ellipse((hc[0] + R - S(22), hc[1] - S(10), hc[0] + R + S(18), hc[1] + S(40)), fill=SKIN_D)
    d.ellipse((hc[0] - R, hc[1] - R, hc[0] + R, hc[1] + R), fill=SKIN, outline=INK, width=int(S(5)))
    # gorra
    d.chord((hc[0] - R - S(4), hc[1] - R - S(20), hc[0] + R + S(4), hc[1] + R * 0.6), 180, 360,
            fill=CAP, outline=INK, width=int(S(5)))
    d.rounded_rectangle((hc[0] - S(20), hc[1] - S(42), hc[0] + R + S(70), hc[1] - S(18)),
                        radius=int(S(12)), fill=(190, 35, 35), outline=INK, width=int(S(4)))
    # ojos
    ex = st["mira"] * S(14)
    for dx in (-S(48), S(48)):
        ox, oy = hc[0] + dx, hc[1] + S(38)
        if st["parpadeo"]:
            d.line((ox - S(22), oy, ox + S(22), oy), fill=INK, width=int(S(7)))
        else:
            d.ellipse((ox - S(26), oy - S(32), ox + S(26), oy + S(32)), fill="white", outline=INK, width=int(S(4)))
            d.ellipse((ox + ex - S(13), oy - S(13), ox + ex + S(13), oy + S(17)), fill=INK)
            d.ellipse((ox + ex - S(5), oy - S(9), ox + ex + S(3), oy - S(1)), fill="white")
        # cejas
        k = {"preocupado": 1, "tranquilo": 0, "feliz": 0.35}[st["cejas"]]
        lado = -1 if dx < 0 else 1
        d.line((ox - S(26), oy - S(46) - lado * k * S(10), ox + S(26), oy - S(46) + lado * k * S(10)),
               fill=INK, width=int(S(9)))
    # mejillas
    for dx in (-S(80), S(80)):
        d.ellipse((hc[0] + dx - S(20), hc[1] + S(72), hc[0] + dx + S(20), hc[1] + S(92)), fill=(240, 150, 140))
    # boca
    my = hc[1] + S(96)
    if st["sopla"]:
        d.ellipse((hc[0] - S(14), my - S(14), hc[0] + S(14), my + S(14)), fill=(120, 30, 40), outline=INK, width=int(S(4)))
        d.rounded_rectangle((hc[0] - S(12), my - S(14), hc[0] + S(70), my + S(10)), radius=int(S(6)),
                            fill=(250, 200, 30), outline=INK, width=int(S(4)))
    else:
        ab = st["boca"]
        if ab < 0.12:
            if st["sonrisa"]:
                d.arc((hc[0] - S(38), my - S(30), hc[0] + S(38), my + S(18)), 20, 160, fill=INK, width=int(S(7)))
            else:
                d.line((hc[0] - S(20), my, hc[0] + S(20), my), fill=INK, width=int(S(7)))
        else:
            h = S(8 + 34 * ab); w = S(26 + 10 * ab)
            d.rounded_rectangle((hc[0] - w, my - h / 2, hc[0] + w, my + h / 2), radius=int(min(w, h) / 2),
                                fill=(120, 30, 40), outline=INK, width=int(S(5)))
            if h > S(22):
                d.rectangle((hc[0] - w * 0.6, my - h / 2 + S(4), hc[0] + w * 0.6, my - h / 2 + S(10)), fill="white")
    return hc


# ---------------------------------------------------------------- utilidades
def eob(t):
    t = max(0.0, min(1.0, t)); return 1 + 2.70158 * (t - 1) ** 3 + 1.70158 * (t - 1) ** 2


def octagono(d, c, r, fill):
    pts = [(c[0] + r * math.cos(math.pi / 8 + k * math.pi / 4), c[1] + r * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    d.polygon(pts, fill=fill, outline="white", width=max(1, int(r * 0.08)))


def main():
    ruta_voz, tiempos, total, env = sintetizar()
    cielo, capas, suelo, frente = escenario()
    f_sub = ImageFont.truetype(F_SUB, 88); f_big = ImageFont.truetype(F_SUB, 98)
    f_stop = ImageFont.truetype(F_SUB, 70); f_btn = ImageFont.truetype(F_SUB, 56)
    salida = os.path.join(OUT, "bosque_prueba.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", ruta_voz,
                           "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", salida],
                          stdin=subprocess.PIPE)
    # tiempos por palabra para subtítulos
    subs = []
    for (a, b), (_, txt) in zip(tiempos, LINEAS):
        pal = txt.split(); tot = sum(len(p) + 2 for p in pal); t = a; grupo = []
        for p in pal:
            dur = (b - a) * (len(p) + 2) / tot
            grupo.append((t, t + dur, p)); t += dur
            if len(grupo) == 3 or p[-1] in ".,?!":
                subs.append(grupo); grupo = []
        if grupo: subs.append(grupo)
    rnd = random.Random(7)
    hojas = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(40, 90), rnd.uniform(0, 6)) for _ in range(14)]
    parpadeos = set()
    tt = 1.2
    while tt < total:
        parpadeos.update(range(int(tt * FPS), int(tt * FPS) + 4)); tt += rnd.uniform(2.2, 3.8)

    cam = 0.0
    for fi in range(int(total * FPS)):
        t = fi / FPS
        esc = max([0] + [i for i, (a, b) in enumerate(tiempos) if a - 0.15 <= t])
        tipo = LINEAS[esc][0]; lt = t - tiempos[esc][0]
        anda = tipo == "camina"
        if anda: cam += 9
        fr = cielo.copy()
        for capa, k in capas: pegar_capa(fr, capa, cam * k)
        fr.alpha_composite(suelo)
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
        # sombra
        d.ellipse((W / 2 - 170, GROUND - 25, W / 2 + 170, GROUND + 30), fill=(0, 0, 0, 60))
        st = dict(t=t, fase=cam / 36, anda=anda, boca=float(env[min(fi, len(env) - 1)]),
                  parpadeo=fi in parpadeos, sopla=False, sonrisa=False,
                  mira=math.sin(t * 2.4) if anda else 0.0,
                  cejas={"camina": "preocupado", "stop": "tranquilo", "silbato": "tranquilo", "saluda": "feliz"}[tipo],
                  brazo={"camina": "balanceo", "stop": "pecho", "silbato": "balanceo", "saluda": "saluda"}[tipo],
                  sonrisa_=None)
        st["sonrisa"] = tipo in ("saluda", "stop")
        if tipo == "silbato":
            # habla primero, luego sopla 3 veces al final de la frase
            fin = tiempos[esc][1] - tiempos[esc][0]
            if lt > fin * 0.45:
                st["brazo"] = "silbato"
            sopl = lt > fin + 0.0
            st["sopla"] = sopl
            if sopl: st["boca"] = 0
        hc = dibujar_leo(d, W / 2, 1.15, st)

        if tipo == "stop":  # señal STOP
            k = eob(lt / 0.45); r = 120 * k
            if r > 2:
                octagono(d, (W / 2 + 300, 1010), r, (215, 30, 40))
                if k > 0.7: d.text((W / 2 + 300, 1010), "STOP", font=f_stop, fill="white", anchor="mm")
        if tipo == "silbato" and st["sopla"]:
            ls = lt - (tiempos[esc][1] - tiempos[esc][0])
            for n in range(3):
                p = (ls * 2.2 - n * 0.33) % 1.0
                for j in range(3):
                    rr = 60 + 260 * p + j * 40
                    a = int(255 * (1 - p))
                    d.arc((hc[0] + 100 - rr, hc[1] + 90 - rr, hc[0] + 100 + rr, hc[1] + 90 + rr), -40, 40,
                          fill=(255, 255, 255, a), width=10)
        if tipo == "saluda":
            k = eob(lt / 0.4)
            if k > 0.05:
                bw, bh = 420 * k, 110 * k
                d.rounded_rectangle((W / 2 - bw / 2, 760 - bh / 2, W / 2 + bw / 2, 760 + bh / 2), radius=int(bh / 2),
                                    fill=(230, 30, 60), outline="white", width=6)
                if k > 0.8: d.text((W / 2, 760), "SÍGUENOS", font=f_btn, fill="white", anchor="mm")

        fr.alpha_composite(capa)
        pegar_capa(fr, frente, cam * 1.4)
        # hojas cayendo
        cap2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(cap2)
        for x, y, v, ph in hojas:
            yy = (y + v * t) % H; xx = (x + 40 * math.sin(t + ph) - cam * 0.8) % W
            d2.ellipse((xx - 14, yy - 7, xx + 14, yy + 7), fill=(230, 150, 40, 220))
        # subtítulos
        actual = None
        for g in subs:
            if g[0][0] <= t <= g[-1][1] + 0.25: actual = g
        if actual:
            pop = eob((t - actual[0][0]) / 0.16)
            ws = []
            for (a, b, p) in actual:
                act = a <= t < b
                f = f_big if act else f_sub
                ws.append((p.upper(), f, act, d2.textlength(p.upper(), font=f) + 16))
            lw = sum(w[3] for w in ws) + 28 * (len(ws) - 1)
            lineas = [ws] if lw < W - 100 else [ws[:2], ws[2:]]
            for li, lin in enumerate(lineas):
                lw = sum(w[3] for w in lin) + 28 * (len(lin) - 1); x = W / 2 - lw / 2
                y = 430 + li * 115 + (1 - pop) * 30
                for (p, f, act, wd) in lin:
                    d2.text((x + wd / 2, y), p, font=f, anchor="mm", fill=(255, 214, 0) if act else "white",
                            stroke_width=11, stroke_fill=(0, 0, 0))
                    x += wd + 28
        fr.alpha_composite(cap2)
        ff.stdin.write(fr.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    print("✔", salida, f"{total:.1f}s")


if __name__ == "__main__":
    main()
