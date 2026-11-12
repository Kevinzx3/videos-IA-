#!/usr/bin/env python3
"""Recopilatorio horizontal (16:9) para YouTube a partir de Shorts ya hechos.

- Cada Short se recorta antes de su cierre («sígueme…») usando el JSON del guion.
- Se coloca en el centro sobre un fondo desenfocado del propio video.
- Entre videos se insertan tarjetas de cuenta atrás (#6 … #1) animadas con música y SFX.
No necesita voz nueva.

Uso: python3 compilacion.py salida.mp4
"""
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
import audio as A  # noqa: E402
from motor import back_out, brillo, clamp01, degradado, ease_out, fuente, nico, pegar, particulas, rotulo  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
TMP = Path("/tmp/claude-0/-home-user-videos-IA-/c40b1534-d684-59d2-9175-3f8c177d3c05/scratchpad/compilacion")
TMP.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30

LISTA = [  # (número, título de tarjeta, carpeta/nombre)
    (6, "EL BLOOP", "dia-05/02-misterio-bloop"),
    (5, "LAS PIEDRAS QUE\nSE MUEVEN SOLAS", "dia-04/01-piedras-que-se-mueven-solas"),
    (4, "EL TRIÁNGULO\nDE LAS BERMUDAS", "dia-04/02-mito-triangulo-bermudas"),
    (3, "LAS LUCES\nDE HESSDALEN", "dia-07/02-misterio-luces-de-hessdalen"),
    (2, "EL MARY CELESTE", "dia-06/02-misterio-mary-celeste"),
    (1, "LA SEÑAL WOW!", "dia-03/02-misterio-senal-wow"),
]


def fondo(t):
    c = degradado(W, H, [(0, "#03060F"), (1, "#1E1438")])
    particulas(c, t, 70, (160, 220, 255), 3, (2, 5), 25, 150)
    return c


def render_tarjeta(nombre, dur, dibujar):
    """Renderiza un clip de tarjeta (imagen) a mp4 sin audio."""
    out = TMP / f"{nombre}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", str(out)],
                          stdin=subprocess.PIPE)
    for n in range(int(dur * FPS)):
        t = n / FPS
        ff.stdin.write(dibujar(t).convert("RGB").tobytes())
    ff.stdin.close()
    ff.wait()
    return out


def tarjeta_numero(num, titulo):
    def dib(t):
        c = fondo(t)
        pegar(c, brillo(420, "#FF4D6D", 0.35), W / 2, H / 2)
        s = back_out(clamp01(t / 0.35), 2.2) if t < 0.35 else 1.0
        pegar(c, rotulo(f"#{num}", 300, "#FFD400", "#1A1022", 16), W / 2, 380, s * (1 + 0.03 * t))
        if t > 0.35:
            pegar(c, rotulo(titulo, 110, "#FFFFFF", "#1A1022", 10), W / 2, 760, ease_out((t - 0.35) / 0.3))
        return c
    return dib


def tarjeta_intro(t):
    c = fondo(t)
    pegar(c, nico(t, "esceptico", 10, 165), 300, 1180, 0.95, ancla="abajo")
    pegar(c, rotulo("TOP 6", 200, "#FFD400", "#1A1022", 14), 1150, 300, back_out(clamp01(t / 0.4)))
    if t > 0.5:
        pegar(c, rotulo("MISTERIOS\nINCREÍBLES", 120, "#FFFFFF", "#1A1022", 10), 1150, 690, ease_out((t - 0.5) / 0.4))
    return c


def tarjeta_final(t):
    c = fondo(t)
    pegar(c, nico(t, "feliz", 10, 140 + 25 * math.sin(t * 10)), 420, 1180, 0.95, ancla="abajo")
    pegar(c, rotulo("¿CUÁL TE DIO\nMÁS MIEDO?", 110, "#FFFFFF", "#1A1022", 10), 1200, 360, back_out(clamp01(t / 0.4)))
    if t > 0.6:
        pegar(c, rotulo("SUSCRÍBETE PARA MÁS", 80, "#FFD400", "#1A1022", 8), 1200, 700, ease_out((t - 0.6) / 0.4) * (1 + 0.04 * math.sin(t * 8)))
    return c


def audio_tarjeta(dur, sfx):
    """Música de misterio + SFX para una tarjeta (WAV estéreo 48 kHz)."""
    m = A.musica(dur, 90, "misterio") * 0.35
    s = np.zeros(len(m))
    for t0, nombre in sfx:
        x = A.SFX[nombre]()
        A._sumar(s, int(t0 * A.SR), x)
    out = TMP / f"aud_{abs(hash((dur, tuple(sfx))))}.wav"
    A.guardar_wav(str(out), (m + s * 0.4) * 0.8)
    return out


def con_audio(video, wav, nombre):
    out = TMP / f"{nombre}_av.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(wav), "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest", str(out)], check=True)
    return out


def short_horizontal(ruta):
    """Short vertical → 16:9 con fondo desenfocado, recortado antes del cierre."""
    datos = json.load(open(RAIZ / (ruta.replace("/", "/datos/", 1) + ".json"), encoding="utf-8"))
    corte = datos["segmentos"][-1][0] + 0.25
    src = RAIZ / (ruta.split("/")[0] + "/videos/" + ruta.split("/")[1] + ".mp4")
    out = TMP / (ruta.replace("/", "_") + "_h.mp4")
    filtro = ("[0:v]split[a][b];[a]scale=1920:-2,crop=1920:1080,boxblur=30:5,eq=brightness=-0.15[f];"
              "[b]scale=-2:1080[v];[f][v]overlay=(W-w)/2:0,fps=30,format=yuv420p")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-t", f"{corte:.2f}", "-filter_complex", filtro,
                    "-af", f"afade=t=out:st={corte - 0.4:.2f}:d=0.4", "-c:v", "libx264", "-crf", "21",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(out)], check=True)
    return out


def main(salida):
    piezas = []
    intro = render_tarjeta("intro", 4.0, tarjeta_intro)
    piezas.append(con_audio(intro, audio_tarjeta(4.0, [(0, "impacto"), (0.5, "whoosh"), (0.6, "riser_suave")]), "intro"))
    for num, titulo, ruta in LISTA:
        v = render_tarjeta(f"t{num}", 2.6, tarjeta_numero(num, titulo))
        piezas.append(con_audio(v, audio_tarjeta(2.6, [(0, "impacto"), (0.35, "whoosh")]), f"t{num}"))
        piezas.append(short_horizontal(ruta))
        print("✔", num, titulo.replace("\n", " "))
    fin = render_tarjeta("final", 6.0, tarjeta_final)
    piezas.append(con_audio(fin, audio_tarjeta(6.0, [(0, "whoosh"), (0.6, "ding")]), "final"))
    lista = TMP / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in piezas))
    crudo = TMP / "crudo.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-r", "30",
                    "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", str(crudo)], check=True)
    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    crudo.replace(salida)
    print("listo:", salida)


def miniatura(salida):
    c = degradado(1280, 720, [(0, "#03060F"), (1, "#3A1440")])
    rng = np.random.default_rng(3)
    for _ in range(9):
        pegar(c, brillo(float(rng.uniform(50, 120)), ["#FFE45C", "#9CFFC8", "#FF6A5A"][int(rng.integers(0, 3))], 0.5),
              float(rng.uniform(600, 1250)), float(rng.uniform(50, 650)))
    pegar(c, nico(0.3, "sorpresa", 30, 30), 250, 760, 0.85, ancla="abajo")
    pegar(c, rotulo("TOP 6", 150, "#FFD400", "#1A1022", 12), 860, 170)
    pegar(c, rotulo("MISTERIOS\nINCREÍBLES", 115, "#FFFFFF", "#FF4D6D", 10), 860, 450)
    c.convert("RGB").save(salida, quality=92)


if __name__ == "__main__":
    main(sys.argv[1])
    miniatura(str(Path(sys.argv[1]).with_suffix(".jpg")))
