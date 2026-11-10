# Videos cortos – Shorts / Reels / TikTok

## Poner la voz de Dan (ElevenLabs)
1. Abre `guiones_para_elevenlabs.txt` y copia el texto de un video.
2. En elevenlabs.io → Text to Speech → voz **Dan** → modelo *Multilingual v2* → genera y descarga el MP3.
3. Guárdalo en `audio/` con el nombre exacto (ej. `audio/01_cuerpo_humano.mp3`).
4. Ejecuta `python3 generar.py 01_cuerpo_humano` → el video se re-sincroniza con la voz.

## Crear un video nuevo
Añade un bloque a `guiones.json` (id, etiqueta, título, colores, emoji + texto por escena) y ejecuta `python3 generar.py <id>`.

## Publicar
- Agrega música de fondo baja desde la propia app (TikTok/IG/YT tienen biblioteca libre de derechos).
- Título con gancho + 3-5 hashtags: #sabiasque #curiosidades #datoscuriosos #aprendeentiktok
- Publica 1-2 diarios, a la misma hora.
