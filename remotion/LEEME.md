# Remotion – fábrica de videos

## Flujo para cada video
1. Elige un guion en `guiones/` (los textos y prompts están en `GUIONES_Y_PROMPTS.md`).
2. Genera una imagen vertical (9:16) por escena con su prompt y guárdalas en
   `public/<id>/escena1.png`, `escena2.png`, …
3. (Opcional) Voz de Dan: genera en ElevenLabs el texto de cada escena y guárdalo como
   `public/<id>/voz/escena1.mp3`, `escena2.mp3`, … Si no existen, se usa la voz local.
4. `python3 preparar.py <id>`  → voz + música + efectos + tiempos de subtítulos
5. `npx remotion render src/index.ts Escenas out/<id>.mp4 --props=public/<id>/datos.json`

Vista previa interactiva en tu computadora: `npx remotion studio`.

## Opciones por escena (en guiones/<id>.json)
- `movimiento`: zoom-in, zoom-out, pan-izq, pan-der, temblor
- `rotulo`: texto del recuadro (ej. "100 kg")
- `efecto`: "peligro" (bordes rojos)
- `sonidos`: golpe, gruñido, aullido, cascabel, pasos, latido, subida
- Palabras entre *asteriscos* se resaltan en el subtítulo.

Para crear guiones nuevos edita `crear_guiones.py` y ejecútalo.

Licencia de Remotion: gratis para personas y empresas de hasta 3 empleados.
