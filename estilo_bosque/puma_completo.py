#!/usr/bin/env python3
"""Video completo: Qué hacer si te encuentras un puma (voz + música + efectos)."""
import math, os, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps

import puma as P
import sonido as S

W, H, FPS = P.W, P.H, P.FPS
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "salida")
HORIZ = P.HORIZ
GAP = 0.35

ESCENAS = [
    ("frente_gruñe", "Si alguna vez te encuentras cara a cara con un puma, lo que hagas en los próximos segundos puede salvarte la vida.", None),
    ("camina", "Es un felino de hasta *cien* kilos, y puede saltar más de cinco metros de un solo impulso.", "100 kg"),
    ("camina_izq", "Lo primero: *nunca* salgas corriendo. Si corres, activas su instinto de caza.", "NO CORRAS"),
    ("brazos", "Hazte lo más *grande* posible: levanta los brazos, abre tu chaqueta, y habla con voz fuerte.", None),
    ("mira", "Mírale a los ojos, y retrocede *despacio*, sin darle nunca la espalda.", "DESPACIO"),
    ("ataca", "Y si ataca, *defiéndete* con todo: piedras, palos, lo que tengas. Nunca te hagas el muerto.", "DEFIÉNDETE"),
    ("frente_calma", "Síguenos para más consejos que pueden salvarte la vida.", "SÍGUENOS"),
]


# ------------------------------------------------------------------ voz
def sintetizar():
    os.makedirs(OUT, exist_ok=True)
    partes, tiempos, t, sr = [], [], 0.6, 16000
    for i, (_, txt, _) in enumerate(ESCENAS):
        f = os.path.join(OUT, f"_l{i}.wav")
        subprocess.run(["python3", "-m", "piper", "-m", P.VOZ, "-f", f, "--length_scale", "1.0"],
                       input=txt.replace("*", "").encode(), check=True, capture_output=True)
        w = wave.open(f); sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16)
        os.remove(f)
        partes.append(x); d = len(x) / sr
        tiempos.append((t, t + d)); t += d + GAP
    total = t + 0.8
    pista = np.zeros(int(total * sr), np.int16)
    for x, (a, _) in zip(partes, tiempos):
        i = int(a * sr); pista[i:i + len(x)] = x
    crudo = os.path.join(OUT, "_voz_cruda.wav")
    with wave.open(crudo, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pista.tobytes())
    # limpiar y dar cuerpo a la voz: 44.1k, paso alto, compresor, un poco de graves
    limpia = os.path.join(OUT, "_voz.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", crudo, "-af",
                    "aresample=44100,highpass=f=70,equalizer=f=160:t=q:w=1:g=3,equalizer=f=3500:t=q:w=1.5:g=2,"
                    "acompressor=threshold=-20dB:ratio=3:attack=5:release=80,volume=1.6",
                    "-ac", "1", limpia], check=True)
    os.remove(crudo)
    w = wave.open(limpia); v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    os.remove(limpia)
    return v, tiempos, total


def mezcla(voz, tiempos, total):
    n = int(total * S.SR)
    voz = np.pad(voz, (0, max(0, n - len(voz))))[:n]
    mus = S.musica(total)[:n]
    amb = S.ambiente(total)[:n]
    # ducking: la música baja cuando habla el narrador
    e = np.abs(voz); k = int(0.25 * S.SR)
    e = np.convolve(e, np.ones(k) / k, mode="same"); e = np.clip(e / (np.percentile(e, 90) + 1e-9), 0, 1)
    sfx = np.zeros(n)
    for i, ((tipo, _, rot), (a, b)) in enumerate(zip(ESCENAS, tiempos)):
        ini = a - 0.25
        if i > 0: S.pegar(sfx, S.whoosh(), ini - 0.15, 0.55)
        if rot: S.pegar(sfx, S.pop(), ini + 0.9, 0.6)
        if tipo == "frente_gruñe":
            S.pegar(sfx, S.golpe_grave(), 0.05, 0.9); S.pegar(sfx, S.gruñido(1.8), 0.15, 0.7)
        if tipo.startswith("camina"):
            fin = tiempos[i + 1][0] - 0.25 if i + 1 < len(tiempos) else total
            tp = ini + 0.1
            while tp < fin:
                S.pegar(sfx, S.paso(), tp, 0.7); tp += 0.63 / 2
        if tipo == "ataca":
            S.pegar(sfx, S.subida(0.8), ini - 0.8, 0.5)
            S.pegar(sfx, S.gruñido(1.4), ini + 0.2, 0.75)
            fin = tiempos[i + 1][0] - 0.25
            tl = ini + 0.3
            while tl < fin:
                S.pegar(sfx, S.latido(), tl, 0.8); tl += 0.75
    m = voz * 1.0 + mus * 0.20 * (1 - 0.55 * e) + amb * 0.20 + sfx * 0.55
    m *= np.minimum(1, np.linspace(0, 40, n)) * np.minimum(1, np.linspace(40, 0, n) * 0.5 + 0.0 + 1e-9)
    m = m / (np.max(np.abs(m)) + 1e-9) * 0.93
    ruta = os.path.join(OUT, "_mezcla.wav")
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(S.SR)
        w.writeframes((m * 32767).astype(np.int16).tobytes())
    return ruta


# ------------------------------------------------------------------ puma de frente
def puma_frente(t, gr):
    img = Image.new("RGBA", (1000, 1100), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    TAN, TAN_D, CREMA, CLARO = (196, 146, 92), (150, 104, 64), (232, 212, 182), (214, 172, 122)
    resp = math.sin(t * 2.2) * 6
    d.rounded_rectangle((140, 560 + resp, 860, 1160), radius=260, fill=TAN)
    for x in (360, 640):
        P.capsula(d, (x, 760), (x + (x - 500) * 0.08, 1060), 160, TAN)
        d.ellipse((x - 100, 1010, x + 100, 1100), fill=TAN)
    d.ellipse((380, 600 + resp, 620, 960), fill=CLARO)
    # orejas
    for sgn in (-1, 1):
        cx = 500 + sgn * 190
        d.polygon([(cx - 75 * sgn * -1 if False else cx - 85, 300), (cx + sgn * 30, 110), (cx + 85, 300)], fill=TAN)
    d.ellipse((220, 160 + resp * 0.3, 780, 660 + resp * 0.3), fill=TAN)
    for sgn in (-1, 1):
        cx = 500 + sgn * 130
        d.ellipse((cx - 150, 400, cx + 150, 640), fill=TAN)
    for sgn in (-1, 1):
        cx = 500 + sgn * 62
        d.ellipse((cx - 72, 450, cx + 72, 590), fill=CREMA)
    d.ellipse((420, 540, 580, 660), fill=CREMA)
    s = P.peludo(img); d = ImageDraw.Draw(s)
    oy = resp * 0.3
    # interior de orejas
    for sgn in (-1, 1):
        cx = 500 + sgn * 190
        d.polygon([(cx - 45, 290 + oy), (cx + sgn * 25, 165 + oy), (cx + 45, 290 + oy)], fill=(90, 60, 45))
    # ojos ámbar
    parp = (t % 3.7) < 0.12
    for sgn in (-1, 1):
        ex, ey = 500 + sgn * 105, 375 + oy
        if parp:
            d.line((ex - 45, ey, ex + 45, ey), fill=(30, 20, 15), width=8); continue
        d.ellipse((ex - 50, ey - 38, ex + 50, ey + 38), fill=(214, 160, 50), outline=(30, 20, 15), width=7)
        pw = 10 if gr > 0.3 else 16
        d.ellipse((ex - pw, ey - 32, ex + pw, ey + 32), fill=(15, 10, 8))
        d.ellipse((ex - 22, ey - 22, ex - 10, ey - 10), fill=(255, 255, 240))
        # cejas fruncidas al gruñir
        if gr > 0.1:
            d.line((ex - sgn * 55, ey - 40 + 14 * gr, ex + sgn * 45, ey - 50 - 16 * gr), fill=(70, 45, 30), width=10)
        # marcas oscuras (lagrimal)
        d.line((ex - sgn * 40, ey + 30, 500 + sgn * 55, 500 + oy), fill=(80, 55, 40), width=9)
    # nariz
    d.polygon([(458, 455 + oy), (542, 455 + oy), (500, 505 + oy)], fill=(170, 100, 100), outline=(60, 35, 30))
    d.line((500, 505 + oy, 500, 535 + oy), fill=(60, 35, 30), width=6)
    if gr > 0.05:
        h = 120 * gr
        d.ellipse((410, 520 + oy, 590, 530 + h + oy), fill=(110, 25, 35), outline=(50, 25, 20), width=6)
        for fx in (445, 555):
            d.polygon([(fx - 14, 528 + oy), (fx + 14, 528 + oy), (fx, 528 + 55 * gr + oy)], fill=(250, 248, 235))
            d.polygon([(fx - 12, 528 + h + oy), (fx + 12, 528 + h + oy), (fx, 528 + h - 40 * gr + oy)], fill=(250, 248, 235))
        d.ellipse((460, 520 + h * 0.6 + oy, 540, 530 + h + oy), fill=(200, 90, 100))
    else:
        d.arc((440, 505 + oy, 500, 555 + oy), 20, 160, fill=(60, 35, 30), width=6)
        d.arc((500, 505 + oy, 560, 555 + oy), 20, 160, fill=(60, 35, 30), width=6)
    # bigotes
    for sgn in (-1, 1):
        for k in range(3):
            d.line((500 + sgn * 90, 520 + k * 14 + oy, 500 + sgn * 230, 500 + k * 26 + oy), fill=(250, 245, 235, 200), width=3)
    return s


# ------------------------------------------------------------------ cachés de sprites
_cache = {}


def sprite_puma(t, anda, ag=0.0):
    T = 2 * math.pi / 5 * 2
    tq = round((t % T) * 15) / 15
    key = ("p", anda, tq, round(ag, 1))
    if key not in _cache: _cache[key] = P.puma(tq, anda=anda, agazapado=round(ag, 1))
    return _cache[key]


def sprite_frente(t, gr):
    key = ("f", round((t % 7.4) * 10) / 10, round(gr, 1))
    if key not in _cache: _cache[key] = puma_frente(key[1], key[2])
    return _cache[key]


def sprite_hiker(b):
    key = ("h", round(b, 2))
    if key not in _cache: _cache[key] = P.excursionista(key[1])
    return _cache[key]


def sombra(capa, cx, cy, rx):
    key = ("s", int(rx))
    if key not in _cache:
        g = Image.new("RGBA", (int(rx * 2 + 80), 132), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((40, 40, 40 + rx * 2, 92), fill=(10, 20, 10, 120))
        _cache[key] = g.filter(ImageFilter.GaussianBlur(14))
    g = _cache[key]
    capa.alpha_composite(g, (int(cx - g.width / 2), int(cy - 66)))


def chip_img(texto, k, f):
    key = ("c", texto, round(k, 2))
    if key in _cache: return _cache[key]
    capa = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    P.chip(capa, texto, k, 150, f)
    _cache[key] = capa
    return capa


def subs_plan(tiempos):
    out = []
    for (a, b), (_, txt, _) in zip(tiempos, ESCENAS):
        pal = txt.split(); tot = sum(len(p.strip("*")) + 2 for p in pal); t = a; grupo = []
        for p in pal:
            dur = (b - a) * (len(p.strip("*")) + 2) / tot
            grupo.append((t, t + dur, p.replace("*", ""), p.startswith("*"))); t += dur
            if len(grupo) >= 5 or p.rstrip("*")[-1] in ".,:?!":
                out.append(grupo); grupo = []
        if grupo: out.append(grupo)
    return out


# ------------------------------------------------------------------ main
def main():
    voz, tiempos, total = sintetizar()
    audio = mezcla(voz, tiempos, total)
    fondo = P.escenario()
    f_reg = ImageFont.truetype(P.F_REG, 58); f_bold = ImageFont.truetype(P.F_BOLD, 60)
    f_chip = ImageFont.truetype(P.F_BOLD, 66)
    subs = subs_plan(tiempos)
    rnd = random.Random(3)
    luci = [(rnd.uniform(0, W), rnd.uniform(500, 1800), rnd.uniform(0, 6.3), rnd.uniform(10, 30)) for _ in range(26)]
    # máscara de viñeta roja precalculada
    m = Image.new("L", (W, H), 255); ImageDraw.Draw(m).ellipse((-100, 150, W + 100, H - 150), fill=0)
    m = m.filter(ImageFilter.GaussianBlur(120))
    salida = os.path.join(OUT, "puma_completo.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", audio,
                           "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", salida],
                          stdin=subprocess.PIPE)
    for fi in range(int(total * FPS)):
        t = fi / FPS
        esc = max([0] + [i for i, (a, b) in enumerate(tiempos) if a - 0.25 <= t])
        tipo, _, rotulo = ESCENAS[esc]
        a0 = 0 if esc == 0 else tiempos[esc][0] - 0.25
        fin = tiempos[esc + 1][0] - 0.25 if esc + 1 < len(tiempos) else total
        lt = t - a0; pr = lt / (fin - a0)
        fr = fondo.copy()
        mundo = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        if tipo.startswith("frente"):
            gr = 0.0
            if tipo == "frente_gruñe":
                gr = P.eio((lt - 0.1) / 0.3) * (1 - P.eio((lt - 2.2) / 0.5))
            sp = sprite_frente(t, gr)
            mundo.alpha_composite(sp, (40, 830))
        elif tipo.startswith("camina"):
            sp = sprite_puma(t, True)
            izq = tipo == "camina_izq"
            sc = 1.1 if izq else 0.95
            sp = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.BILINEAR)
            if izq:
                sp = ImageOps.mirror(sp); x = int(W - 200 - 420 * pr) - sp.width // 2
                y = 1150
            else:
                x = int(-300 + 420 * pr); y = 1110
            sombra(mundo, x + sp.width * 0.5, y + sp.height - 40, sp.width * 0.42)
            mundo.alpha_composite(sp, (x, y))
        elif tipo == "brazos":
            sp = sprite_puma(t, False).resize((300, 186), Image.BILINEAR)
            sombra(mundo, 790, HORIZ + 210, 110)
            mundo.alpha_composite(sp, (640, HORIZ + 40))
            hk = sprite_hiker(P.eio((lt - 0.6) / 0.8))
            sombra(mundo, W / 2, 1830, 210)
            mundo.alpha_composite(hk, (int(W / 2 - hk.width / 2), 880 - 220))
        elif tipo == "mira":
            sp = sprite_puma(t, False)
            sc = 1.25; sp = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.BILINEAR)
            x = int(W - sp.width + 120 - 60 * pr)
            sombra(mundo, x + sp.width * 0.5, 1050 + sp.height - 50, sp.width * 0.42)
            mundo.alpha_composite(sp, (x, 1050))
        else:  # ataca
            sp = sprite_puma(t, False, P.eio(lt / 1.2))
            sc = 1.3; sp = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.BILINEAR)
            x = int(-330 + 30 * math.sin(t * 3))
            sombra(mundo, x + sp.width * 0.5, 1020 + sp.height - 60, sp.width * 0.42)
            mundo.alpha_composite(sp, (x, 1020))
        fr.alpha_composite(mundo)

        d = ImageDraw.Draw(fr)
        for x, y, ph, v in luci:
            yy = y - (v * t) % 300; xx = x + 25 * math.sin(t * 0.7 + ph)
            al = int(110 + 100 * math.sin(t * 2 + ph))
            d.ellipse((xx - 3, yy - 3, xx + 3, yy + 3), fill=(255, 250, 220, max(0, al)))

        # cámara
        z = 1.0 + 0.07 * P.eio(pr)
        if tipo == "frente_gruñe": z = 1.12 - 0.08 * P.eio(pr) + 0.03 * math.exp(-lt * 4) * math.sin(lt * 40)
        if tipo == "ataca": z += 0.02 * abs(math.sin(t * 6))
        cw, ch = W / z, H / z
        cx = W / 2 + (40 if tipo == "mira" else 0) * pr
        cy = H / 2 + 600 * (z - 1)
        fr = fr.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BILINEAR)

        if tipo == "ataca":
            v = Image.new("RGBA", (W, H), (180, 20, 20, 0))
            v.putalpha(m.point(lambda p, a=(0.45 + 0.25 * math.sin(t * 7)): int(p * a)))
            fr.alpha_composite(v)

        du = ImageDraw.Draw(fr)
        g = None
        for gr_ in subs:
            if gr_[0][0] <= t: g = gr_
        if g and t <= g[-1][1] + 0.4:
            P.dibujar_subs(du, g, t, f_reg, f_bold)
        if rotulo:
            k = P.eob((lt - 0.9) / 0.35)
            if k > 0: fr.alpha_composite(chip_img(rotulo, k, f_chip), (0, 560 - 150))
        if lt < 0.1 and esc > 0:
            fr.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(200 * (1 - lt / 0.1)))))
        ff.stdin.write(fr.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    os.remove(audio)
    print("✔", salida, f"{total:.1f}s")


if __name__ == "__main__":
    main()
