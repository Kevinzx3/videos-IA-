#!/usr/bin/env python3
"""Genera videos verticales (1080x1920) animados para Shorts / Reels / TikTok.

Uso:
  python3 generar.py                 # todos los videos de guiones.json
  python3 generar.py 02_perdido_bosque

Si existe audio/<id>.mp3 (la voz de Dan exportada de ElevenLabs), el video
se cronometra con la duración real del audio y se le pone ese audio.
Si no existe, se usa un ritmo estimado de Dan (~2.7 palabras/seg) y sale mudo.
"""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
FONT_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
PALABRAS_POR_SEG = 2.7
PAUSA_ESCENA = 0.25  # seg de respiro entre escenas


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ease_out_back(t):
    c1, c3 = 1.70158, 2.70158
    t = max(0.0, min(1.0, t))
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def duracion_audio(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", path])
    return float(out.strip())


def render_emoji(ch, size):
    f = ImageFont.truetype(FONT_EMOJI, 109)
    img = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((80, 80), ch, font=f, embedded_color=True, anchor="mm")
    img = img.crop(img.getbbox() or (0, 0, 160, 160))
    r = size / max(img.size)
    return img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)


def fondo(c1, c2):
    a, b = hex2rgb(c1), hex2rgb(c2)
    g = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / H
        g.putpixel((0, y), tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    g = g.resize((W, H))
    # viñeta suave
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse((-300, 200, W + 300, H - 200), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(220))
    oscuro = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(g, oscuro, v)


def trozos(palabras, n=3):
    """Agrupa palabras en bloques de subtítulo de hasta n palabras."""
    out, cur = [], []
    for p in palabras:
        cur.append(p)
        if len(cur) >= n or p[-1] in ".,?!:":
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def planificar(video, total=None):
    escenas = video["escenas"]
    pesos = [len(e["texto"].split()) for e in escenas]
    if total is None:
        dur = [p / PALABRAS_POR_SEG + PAUSA_ESCENA for p in pesos]
    else:
        util = total - 0.3
        dur = [util * p / sum(pesos) for p in pesos]
    plan, t = [], 0.0
    for e, d in zip(escenas, dur):
        palabras = e["texto"].split()
        bloques = trozos(palabras)
        habla = d - PAUSA_ESCENA if total is None else d
        tp = habla / len(palabras)
        tl, k = [], 0
        for b in bloques:
            tl.append((t + k * tp, b, tp))
            k += len(b)
        plan.append({"ini": t, "fin": t + d, "esc": e, "bloques": tl})
        t += d
    return plan, t + 0.3


def texto_con_borde(d, xy, txt, font, fill, borde=10, anchor="mm"):
    d.text(xy, txt, font=font, fill=fill, anchor=anchor,
           stroke_width=borde, stroke_fill=(0, 0, 0))


def generar(video):
    vid = video["id"]
    audio = os.path.join(BASE, "audio", vid + ".mp3")
    hay_audio = os.path.exists(audio)
    plan, total = planificar(video, duracion_audio(audio) if hay_audio else None)
    nframes = int(total * FPS)
    acento = hex2rgb(video["acento"])

    bg = fondo(*video["colores"])
    emojis = [render_emoji(p["esc"]["emoji"], 440) for p in plan]
    f_sub = ImageFont.truetype(FONT_BLACK, 92)
    f_sub_big = ImageFont.truetype(FONT_BLACK, 104)
    f_tag = ImageFont.truetype(FONT_BLACK, 54)
    f_tit = ImageFont.truetype(FONT_BOLD, 64)
    f_num = ImageFont.truetype(FONT_BLACK, 70)

    rnd = random.Random(vid)
    part = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(4, 14), rnd.uniform(20, 70))
            for _ in range(40)]
    items_lista = [i for i, p in enumerate(plan) if not p["esc"].get("intro")]

    salida = os.path.join(BASE, "salida", vid + ".mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if hay_audio:
        cmd += ["-i", audio, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", salida]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for fi in range(nframes):
        t = fi / FPS
        fr = bg.copy()
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)

        # partículas que suben
        for x, y, r, v in part:
            yy = (y - v * t) % H
            xx = x + 18 * math.sin(t * 0.8 + y)
            d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=acento + (45,))

        # etiqueta superior (entra deslizando)
        k = ease_out(t / 0.6)
        ty = int(-120 + (230 + 120) * k)
        tw = d.textlength(video["etiqueta"], font=f_tag) + 80
        d.rounded_rectangle((W / 2 - tw / 2, ty - 50, W / 2 + tw / 2, ty + 50),
                            radius=50, fill=acento + (255,))
        d.text((W / 2, ty), video["etiqueta"], font=f_tag, fill=(15, 15, 15), anchor="mm")
        texto_con_borde(d, (W / 2, ty + 110), video["titulo"], f_tit, (255, 255, 255), 8)

        # escena actual
        idx = next((i for i, p in enumerate(plan) if p["ini"] <= t < p["fin"]), len(plan) - 1)
        p = plan[idx]
        lt = t - p["ini"]
        em = emojis[idx]
        s = max(0.01, ease_out_back(lt / 0.45))
        bob = 18 * math.sin(lt * 3.2)
        rot = 6 * math.sin(lt * 2.1)
        e2 = em.resize((max(1, int(em.width * s)), max(1, int(em.height * s))), Image.LANCZOS)
        e2 = e2.rotate(rot, resample=Image.BICUBIC, expand=True)
        cx, cy = W // 2, int(800 + bob)
        # halo detrás del emoji
        hr = int(300 * s)
        d.ellipse((cx - hr, cy - hr, cx + hr, cy + hr), fill=(255, 255, 255, 28))
        capa.alpha_composite(e2, (cx - e2.width // 2, cy - e2.height // 2))

        # número de la lista (1/5...)
        if video.get("lista") and idx in items_lista:
            n = items_lista.index(idx) + 1
            ns = ease_out_back((lt - 0.15) / 0.4)
            if ns > 0:
                rr = int(70 * ns)
                bx, by = cx + 250, cy - 230
                d.ellipse((bx - rr, by - rr, bx + rr, by + rr), fill=acento + (255,),
                          outline=(0, 0, 0), width=6)
                if ns > 0.6:
                    d.text((bx, by), str(n), font=f_num, fill=(15, 15, 15), anchor="mm")

        # subtítulos palabra por palabra
        bloque = None
        for (bt, palabras, tp) in p["bloques"]:
            if bt <= t:
                bloque = (bt, palabras, tp)
        if bloque:
            bt, palabras, tp = bloque
            act = min(len(palabras) - 1, int((t - bt) / tp))
            pop = ease_out_back((t - bt) / 0.18)
            sp = 34
            anchos = [d.textlength(w.upper(), font=f_sub_big if i == act else f_sub) + 16
                      for i, w in enumerate(palabras)]
            # partir en 2 líneas si no cabe
            lineas = [list(range(len(palabras)))]
            if sum(anchos) + sp * (len(palabras) - 1) > W - 120 and len(palabras) > 1:
                m = len(palabras) // 2 + len(palabras) % 2
                lineas = [list(range(m)), list(range(m, len(palabras)))]
            y0 = 1380 - (len(lineas) - 1) * 60 + int((1 - pop) * 40)
            for li, lin in enumerate(lineas):
                lw = sum(anchos[i] for i in lin) + sp * (len(lin) - 1)
                x = W / 2 - lw / 2
                for i in lin:
                    w = palabras[i]
                    es_act = i == act
                    f = f_sub_big if es_act else f_sub
                    col = acento if es_act else (255, 255, 255)
                    texto_con_borde(d, (x + anchos[i] / 2, y0 + li * 120), w.upper(), f,
                                    col, 11)
                    x += anchos[i] + sp

        # barra de progreso
        d.rounded_rectangle((80, H - 150, W - 80, H - 132), radius=9, fill=(255, 255, 255, 60))
        d.rounded_rectangle((80, H - 150, 80 + (W - 160) * (t / total), H - 132), radius=9,
                            fill=acento + (255,))

        fr = fr.convert("RGBA")
        fr.alpha_composite(capa)
        ff.stdin.write(fr.convert("RGB").tobytes())

    ff.stdin.close()
    ff.wait()
    estado = "con voz" if hay_audio else "SIN voz (ritmo estimado)"
    print(f"✔ {salida}  ({total:.1f}s, {estado})")


def main():
    videos = json.load(open(os.path.join(BASE, "guiones.json"), encoding="utf-8"))
    filtro = set(sys.argv[1:])
    for v in videos:
        if not filtro or v["id"] in filtro:
            generar(v)
    # textos listos para pegar en ElevenLabs
    with open(os.path.join(BASE, "guiones_para_elevenlabs.txt"), "w", encoding="utf-8") as fh:
        for v in videos:
            fh.write(f"===== {v['id']}  →  guardar como audio/{v['id']}.mp3 =====\n")
            fh.write(" ".join(e["texto"] for e in v["escenas"]) + "\n\n")


if __name__ == "__main__":
    main()
