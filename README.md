# Videos IA: Shorts de divulgación en español

Producción de **2 videos verticales al día (9:16, 40–60 s)** para YouTube Shorts, Facebook Reels y TikTok.
Los formatos rotan entre: *¿Sabías que…?*, *Qué hacer si…*, *Ciencia explicada fácil* y *Mitos vs. realidad*.

## Estructura

```
guia/biblia-de-estilo.md         Estilo visual, personajes, tipografía, voz, música, SFX, rotación y horarios
herramientas/generar_subtitulos.py  Genera subtítulos palabra por palabra (.srt y .ass) desde el guion JSON
dia-01/
  01-mas-alto-por-la-manana.md   Video A: guion, escenas, SFX, música, fuentes, descripciones y horario
  02-corriente-de-resaca.md      Video B
  datos/*.json                   Guion con tiempos (fuente de los subtítulos)
  subtitulos/*.ass | *.srt       Subtítulos generados
```

## Flujo de trabajo por video

1. Escribe el guion con tiempos en `dia-XX/datos/NN-tema.json` (segmentos `[inicio, fin, texto]` y palabras de `enfasis`).
2. Graba o genera la voz (voz masculina de catálogo; **nunca clonar una voz real**) y ajusta los tiempos del JSON a la locución.
3. Genera los subtítulos:
   ```bash
   python3 herramientas/generar_subtitulos.py dia-01/datos/*.json --salida dia-01/subtitulos
   ```
4. Anima siguiendo la tabla de escenas del `.md` del video y la biblia de estilo (cortes cada 1–2 s).
5. Quema los subtítulos: `ffmpeg -i video.mp4 -vf "ass=dia-01/subtitulos/NN-tema.ass" -c:a copy final.mp4`
6. Pasa el checklist de calidad (sección 8 de la biblia) y publica en el horario sugerido.

## Calendario

| Día | Video A | Video B |
|---|---|---|
| 01 | ¿Por qué eres más alto por la mañana? (Ciencia fácil) | Qué hacer si el mar te arrastra (Qué hacer si…) |

## Render automático de videos (sin software de edición)

`herramientas/animar/` anima cada video por código en estilo 2.5D de fieltro (Nico y Chispa), sintetiza música y SFX originales y mezcla con la voz:

```bash
cd herramientas/animar
python3 ../alinear_voz.py ../../dia-01/datos/01-mas-alto-por-la-manana.json voz.wav   # tiempos reales
python3 ../generar_subtitulos.py ../../dia-01/datos/01-*.json --salida ../../dia-01/subtitulos
python3 render.py video_d01a imagen.mp4                                             # ~2 min con 4 núcleos
python3 audio.py voz.wav imagen.sfx.json audio.wav --bpm 104 --corte 44.45 44.9     # música + SFX + voz, −14 LUFS
ffmpeg -i imagen.mp4 -i audio.wav -vf "ass=../../dia-01/subtitulos/01-mas-alto-por-la-manana.ass" \
  -c:v libx264 -crf 23 -maxrate 6M -bufsize 12M -c:a aac -b:a 192k -shortest final.mp4
```

Video terminado: `dia-01/videos/01-mas-alto-por-la-manana.mp4` (1080×1920, 30 fps, 59 s).
| 02 | El pulpo tiene 3 corazones… y uno se apaga al nadar (¿Sabías que…?) | ¿Solo usas el 10 % de tu cerebro? MITO (Mitos vs. realidad) |

Videos terminados en `dia-0X/videos/`. Escenas de cada video: `herramientas/animar/video_d01a.py`, `video_d01b.py`, `video_d02a.py`, `video_d02b.py`.
