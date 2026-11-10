#!/usr/bin/env python3
"""Prepara un video para Remotion a partir de guiones/<id>.json.

  python3 preparar.py puma

Genera en public/<id>/:
  - mezcla.wav  (voz + música de fondo + efectos + ambiente)
  - datos.json  (escenas con tiempos y palabras para los subtítulos)

Voz: si existen public/<id>/voz/escena1.mp3, escena2.mp3... (por ejemplo, exportados
de ElevenLabs con la voz Dan) se usan esos. Si no, se genera con Piper (voz local).
Imágenes: public/<id>/escena1.png, escena2.png... (créalas con los prompts del guion).
"""
import json, os, subprocess, sys, wave
import numpy as np
import sonido as S

BASE = os.path.dirname(os.path.abspath(__file__))
VOZ_PIPER = os.environ.get("VOZ_MODELO", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "voces", "es-carlfm-x-low.onnx"))
GAP = 0.35
INICIO = 0.6
SR = S.SR


def leer_audio(ruta):
    """Devuelve audio mono float a 44.1 kHz (cualquier formato que lea ffmpeg)."""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", ruta, "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(float) / 32768


def voz_escena(dir_v, i, texto):
    for ext in ("mp3", "wav", "m4a"):
        p = os.path.join(dir_v, f"escena{i + 1}.{ext}")
        if os.path.exists(p):
            return leer_audio(p), "propia"
    tmp = os.path.join(dir_v, f"_piper{i}.wav")
    subprocess.run(["python3", "-m", "piper", "-m", VOZ_PIPER, "-f", tmp],
                   input=texto.encode(), check=True, capture_output=True)
    limpio = tmp.replace(".wav", "_ok.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af",
                    "aresample=44100,highpass=f=70,equalizer=f=160:t=q:w=1:g=3,equalizer=f=3500:t=q:w=1.5:g=2,"
                    "acompressor=threshold=-20dB:ratio=3:attack=5:release=80", "-ac", "1", limpio], check=True)
    x = leer_audio(limpio); os.remove(tmp); os.remove(limpio)
    return x, "piper"


def main(vid):
    g = json.load(open(os.path.join(BASE, "guiones", vid + ".json"), encoding="utf-8"))
    out = os.path.join(BASE, "public", vid); dir_v = os.path.join(out, "voz")
    os.makedirs(dir_v, exist_ok=True)
    escenas = g["escenas"]
    voces, tiempos, t = [], [], INICIO
    for i, e in enumerate(escenas):
        texto = e["texto"].replace("*", "")
        x, origen = voz_escena(dir_v, i, texto)
        # recortar silencios de los extremos
        nz = np.where(np.abs(x) > 0.01)[0]
        if len(nz): x = x[max(0, nz[0] - 800): nz[-1] + 2000]
        voces.append(x); d = len(x) / SR
        tiempos.append((t, t + d)); t += d + GAP + float(e.get("pausa_extra", 0))
        print(f"  escena {i + 1}: {d:.1f}s de voz ({origen})")
    total = t + 0.8; n = int(total * SR)
    voz = np.zeros(n)
    for x, (a, _) in zip(voces, tiempos):
        S.pegar(voz, x, a)
    voz = voz / (np.max(np.abs(voz)) + 1e-9) * 0.9

    # efectos según el guion
    sfx = np.zeros(n)
    for i, (e, (a, b)) in enumerate(zip(escenas, tiempos)):
        ini = 0 if i == 0 else a - 0.25
        fin = tiempos[i + 1][0] - 0.25 if i + 1 < len(tiempos) else total
        if i > 0: S.pegar(sfx, S.whoosh(), ini - 0.15, 0.55)
        if e.get("rotulo"): S.pegar(sfx, S.pop(), ini + 0.9, 0.6)
        for s in e.get("sonidos", []):
            if s == "golpe": S.pegar(sfx, S.golpe_grave(), ini + 0.05, 0.9)
            elif s == "gruñido": S.pegar(sfx, S.gruñido(1.6), ini + 0.15, 0.7)
            elif s == "aullido": S.pegar(sfx, S.aullido(), ini + 0.1, 0.8)
            elif s == "cascabel": S.pegar(sfx, S.cascabel(), ini + 0.05, 0.7)
            elif s == "subida": S.pegar(sfx, S.subida(0.8), ini - 0.8, 0.5)
            elif s == "pasos":
                tp = ini + 0.1
                while tp < fin: S.pegar(sfx, S.paso(), tp, 0.7); tp += 0.32
            elif s == "latido":
                tl = ini + 0.3
                while tl < fin: S.pegar(sfx, S.latido(), tl, 0.8); tl += 0.75
    mus = S.musica(total)[:n]; amb = S.ambiente(total)[:n]
    e_ = np.convolve(np.abs(voz), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    e_ = np.clip(e_ / (np.percentile(e_, 90) + 1e-9), 0, 1)
    m = voz + mus * 0.20 * (1 - 0.55 * e_) + amb * 0.20 + sfx * 0.55
    fade = np.minimum(1, np.minimum(np.arange(n) / (0.8 * SR), (n - np.arange(n)) / (1.5 * SR)))
    m = m * fade; m = m / (np.max(np.abs(m)) + 1e-9) * 0.93
    with wave.open(os.path.join(out, "mezcla.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((m * 32767).astype(np.int16).tobytes())

    # palabras con tiempos (proporcional a la longitud de cada palabra)
    palabras, grupo = [], 0
    for (a, b), e in zip(tiempos, escenas):
        pal = e["texto"].split(); tot = sum(len(p.strip("*")) + 2 for p in pal); tt = a; cnt = 0
        for p in pal:
            dur = (b - a) * (len(p.strip("*")) + 2) / tot
            palabras.append({"t0": round(tt, 3), "t1": round(tt + dur, 3), "texto": p.replace("*", ""),
                             "clave": p.startswith("*"), "grupo": grupo})
            tt += dur; cnt += 1
            if cnt >= 5 or p.rstrip("*")[-1] in ".,:?!":
                grupo += 1; cnt = 0
        if cnt: grupo += 1
    datos = {
        "id": vid, "total": round(total, 3), "audio": f"{vid}/mezcla.wav",
        "escenas": [{
            "imagen": f"{vid}/{e.get('imagen', f'escena{i + 1}.png')}",
            "ini": round(0 if i == 0 else tiempos[i][0] - 0.25, 3),
            "fin": round(tiempos[i + 1][0] - 0.25 if i + 1 < len(tiempos) else total, 3),
            "movimiento": e.get("movimiento", "zoom-in"),
            "rotulo": e.get("rotulo"), "efecto": e.get("efecto"),
        } for i, e in enumerate(escenas)],
        "palabras": palabras,
    }
    json.dump(datos, open(os.path.join(out, "datos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    faltan = [d["imagen"] for d in datos["escenas"] if not os.path.exists(os.path.join(BASE, "public", d["imagen"]))]
    print(f"✔ public/{vid}/datos.json y mezcla.wav ({total:.1f}s)")
    if faltan: print("⚠ Faltan imágenes:", ", ".join(faltan))
    print(f"Renderiza con:  npx remotion render src/index.ts Escenas out/{vid}.mp4 --props=public/{vid}/datos.json")


if __name__ == "__main__":
    main(sys.argv[1])
