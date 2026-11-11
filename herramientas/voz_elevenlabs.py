#!/usr/bin/env python3
"""Genera la locución con ElevenLabs y escribe en el JSON los tiempos reales.

Usa el endpoint `with-timestamps`: devuelve el audio y el instante de cada carácter,
así que los segmentos y los subtítulos palabra por palabra quedan sincronizados
exactamente con la voz (sin estimaciones).

La clave se toma de ELEVENLABS_API_KEY (en las sesiones en la nube la inyecta el proxy).

Uso:
    python3 herramientas/voz_elevenlabs.py guion.json salida.wav [--voz TX3LPaxmHKxFdv7VOQHJ] [--velocidad 1.1]
"""
import argparse
import base64
import json
import os
import subprocess
import urllib.request

VOZ_LIAM = "TX3LPaxmHKxFdv7VOQHJ"


def generar(guion, salida, voz=VOZ_LIAM, velocidad=1.1):
    d = json.load(open(guion, encoding="utf-8"))
    textos = [s[2] for s in d["segmentos"]]
    texto = " ".join(textos)
    cuerpo = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3,
                           "use_speaker_boost": True, "speed": velocidad},
    }
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voz}/with-timestamps?output_format=mp3_44100_128",
        data=json.dumps(cuerpo).encode(), method="POST",
        headers={"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "proxy-injected"),
                 "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=300))
    mp3 = salida.rsplit(".", 1)[0] + ".mp3"
    open(mp3, "wb").write(base64.b64decode(r["audio_base64"]))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", "48000", "-ac", "1", salida], check=True)
    al = r["alignment"]
    chars, ini, fin = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    assert "".join(chars) == texto, "el texto alineado no coincide"
    # palabras = tramos sin espacios
    palabras, i = [], 0
    while i < len(chars):
        if chars[i].isspace():
            i += 1
            continue
        j = i
        while j < len(chars) and not chars[j].isspace():
            j += 1
        palabras.append([round(ini[i], 3), round(fin[j - 1], 3), "".join(chars[i:j])])
        i = j
    # fronteras de segmento
    k = 0
    total = round(fin[-1] + 0.35, 2)
    for n, s in enumerate(d["segmentos"]):
        nw = len(s[2].split())
        s[0] = 0.0 if n == 0 else palabras[k][0]
        k += nw
    for n, s in enumerate(d["segmentos"]):
        s[1] = d["segmentos"][n + 1][0] if n + 1 < len(d["segmentos"]) else total
        s[0], s[1] = round(s[0], 2), round(s[1], 2)
    d["palabras"] = palabras
    d["voz"] = {"proveedor": "ElevenLabs", "voice_id": voz, "modelo": "eleven_multilingual_v2", "velocidad": velocidad}
    json.dump(d, open(guion, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✔ {guion}: {total:.1f} s, {len(palabras)} palabras, {len(texto)} caracteres")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("salida")
    ap.add_argument("--voz", default=VOZ_LIAM)
    ap.add_argument("--velocidad", type=float, default=1.1)
    a = ap.parse_args()
    generar(a.guion, a.salida, a.voz, a.velocidad)
