#!/usr/bin/env python3
"""Genera subtítulos dinámicos palabra por palabra a partir de un guion JSON.

Uso:
    python3 herramientas/generar_subtitulos.py dia-01/datos/*.json --salida dia-01/subtitulos

Por cada guion crea:
  * <nombre>.palabras.srt  -> un cue por palabra (importable en CapCut, Premiere, DaVinci).
  * <nombre>.ass           -> estilo "karaoke": frase de 1-4 palabras en el tercio superior,
                              palabra activa en blanco grande y resto atenuado;
                              las palabras clave se resaltan en amarillo.
                              Se quema con: ffmpeg -i video.mp4 -vf "ass=archivo.ass" salida.mp4

Los tiempos por palabra se reparten dentro de cada segmento según su longitud.
Después de grabar la voz, ajusta los tiempos de los segmentos en el JSON
(o alinea con una herramienta de forced alignment) y vuelve a ejecutar el script.
"""
import argparse
import json
import re
from pathlib import Path

MAX_PALABRAS_FRASE = 4
PAUSA_PUNTUACION = 1.6  # peso extra tras , . : ? …


def limpiar(palabra: str) -> str:
    return re.sub(r"[^\wáéíóúüñÁÉÍÓÚÜÑ]", "", palabra).lower()


def tiempos_palabras(inicio, fin, texto):
    palabras = texto.split()
    pesos = []
    for p in palabras:
        w = len(limpiar(p)) + 2
        if re.search(r"[,.:;?!…]$", p):
            w += PAUSA_PUNTUACION
        pesos.append(w)
    total = sum(pesos)
    t = inicio
    salida = []
    for p, w in zip(palabras, pesos):
        d = (fin - inicio) * w / total
        salida.append((t, t + d, p))
        t += d
    return salida


def agrupar(palabras):
    """Agrupa en frases cortas: máx. 4 palabras, corta tras puntuación."""
    frases, actual = [], []
    for item in palabras:
        actual.append(item)
        if len(actual) >= MAX_PALABRAS_FRASE or re.search(r"[,.:;?!…]$", item[2]):
            frases.append(actual)
            actual = []
    if actual:
        frases.append(actual)
    return frases


def ts_srt(s):
    ms = int(round(s * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"


def ts_ass(s):
    cs = int(round(s * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    sec, cs = divmod(cs, 100)
    return f"{h}:{m:02}:{sec:02}.{cs:02}"


CABECERA_ASS = """[Script Info]
Title: {titulo}
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Frase,Inter Black,92,&H00FFFFFF,&H00FFFFFF,&H00201A14,&H96000000,1,0,0,0,100,100,0,0,1,6,3,8,90,140,520,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

ATENUADA = r"{\alpha&H60&\fscx100\fscy100\c&HFFFFFF&}"
ACTIVA = r"{\alpha&H00&\fscx112\fscy112\c&HFFFFFF&}"
ACTIVA_CLAVE = r"{\alpha&H00&\fscx120\fscy120\c&H00D4FF&}"  # amarillo #FFD400 (BGR)


def generar(ruta_json: Path, salida: Path):
    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    enfasis = {limpiar(e) for e in datos.get("enfasis", [])}
    palabras = []
    if datos.get("palabras"):  # tiempos exactos de la voz (ElevenLabs with-timestamps)
        ps = datos["palabras"]
        # cada palabra se mantiene hasta que empieza la siguiente (sin huecos)
        palabras = [(a, max(b, ps[k + 1][0]) if k + 1 < len(ps) else b + 0.3, w) for k, (a, b, w) in enumerate(ps)]
    else:
        for ini, fin, texto in datos["segmentos"]:
            palabras.extend(tiempos_palabras(ini, fin, texto))

    base = salida / ruta_json.stem
    # SRT palabra por palabra
    with open(f"{base}.palabras.srt", "w", encoding="utf-8") as f:
        for i, (a, b, p) in enumerate(palabras, 1):
            f.write(f"{i}\n{ts_srt(a)} --> {ts_srt(b)}\n{p}\n\n")

    # ASS dinámico
    with open(f"{base}.ass", "w", encoding="utf-8") as f:
        f.write(CABECERA_ASS.format(titulo=datos["titulo"]))
        for frase in agrupar(palabras):
            for idx, (a, b, _) in enumerate(frase):
                trozos = []
                for j, (_, _, p) in enumerate(frase):
                    if j == idx:
                        tag = ACTIVA_CLAVE if limpiar(p) in enfasis else ACTIVA
                    else:
                        tag = ATENUADA
                    trozos.append(tag + p)
                # pequeño "pop" de entrada en la primera palabra de cada frase
                pop = r"{\t(0,80,\fscx108\fscy108)\t(80,160,\fscx100\fscy100)}" if idx == 0 else ""
                f.write(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},Frase,,0,0,0,,{pop}{' '.join(trozos)}\n")
    print(f"✔ {ruta_json.name}: {len(palabras)} palabras, {datos['segmentos'][-1][1]:.1f} s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("guiones", nargs="+", type=Path)
    ap.add_argument("--salida", type=Path, required=True)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    for g in args.guiones:
        generar(g, args.salida)
