# videos-IA-

Fábrica de videos cortos (TikTok, Reels, YouTube Shorts) en español, con el estilo
"ilustración con textura en bosque al atardecer": personajes animados, subtítulos
palabra por palabra, rótulos, música de fondo y efectos generados por código
(sin derechos de autor) y narración.

## Carpetas
| Carpeta | Qué hay |
|---|---|
| `remotion/` | **Fábrica principal.** Guiones + prompts de imagen → video con Remotion. Ver `remotion/LEEME.md` y `remotion/GUIONES_Y_PROMPTS.md`. |
| `estilo_bosque/` | Videos dibujados 100 % por código (puma, personajes, música y efectos en `sonido.py`). |
| `personajes/` | Primera prueba con personaje caricatura (Leo en el bosque). |
| `salida/`, `generar.py` | Primeros videos tipo "¿Sabías que…?" con emojis. |
| `voces/` | Voz local en español (se descarga con `instalar.sh`). |

## Empezar
```bash
./instalar.sh
cd remotion
python3 preparar.py puma
npx remotion render src/index.ts Escenas out/puma.mp4 --props=public/puma/datos.json
```

Para la voz de Dan (ElevenLabs): guarda los MP3 de cada escena en `remotion/public/<id>/voz/escena1.mp3`, …
