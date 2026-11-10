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
