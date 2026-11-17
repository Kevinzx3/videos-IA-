# Biblia de estilo: Shorts de divulgación en español

Es la referencia fija para todos los videos. Si algo no está aquí, decide pensando en lo siguiente: **¿se entiende en un móvil, sin sonido, en 1 segundo?**

---

## 1. Estilo visual (basado en el video de referencia)

| Elemento | Especificación |
|---|---|
| Técnica | Ilustración **2.5D tipo recortable de papel/fieltro**: figuras planas con **textura de pelo o tela**, **bordes cosidos** (línea discontinua clara en el contorno) y sombra suave proyectada en el suelo. Se animan como marionetas (rig por partes: cabeza, mandíbula, patas o brazos). |
| Fondos | **3 a 4 capas con parallax**: cielo degradado, siluetas lejanas (montañas, pinos, edificios), plano medio y suelo con textura (hierba, arena, baldosa). Siempre con **partículas flotando** (polvo, luciérnagas, burbujas) para que nunca haya un fotograma totalmente quieto. |
| Paleta base | Cielo atardecer `#2B1E3F → #C2577A → #F29E5C` · Verde bosque `#1F3B3A` · Hierba `#6E8A2E` · Acento amarillo `#FFD400` · Acento coral `#FF4D6D` · Blanco texto `#FFFFFF` |
| Paleta "mar" | Cielo `#1B2A4A → #3E7CB1 → #F6C28B` · Agua `#1F6F8B` / zona peligrosa `#0E3A4F` · Espuma `#E8F4F2` · Arena `#E2C58F` |
| Paleta "cuerpo/espacio" | Fondo `#14112B → #3B2F6B` · Órganos y huesos `#F3E6D0` · Acento cian `#3DE0E6` |
| Iluminación | Luz cálida de contraluz y un *rim light* fino sobre los personajes. Viñeta suave. |
| Movimiento | **Ningún plano quieto más de 2 s.** Como mínimo debe haber uno de estos: paneo lento, *push-in* o zoom de 3 a 8 %, parallax, respiración del personaje (escala 100 → 101,5 %) o partículas. |
| Transiciones | *Whip pan* con desenfoque de movimiento, *match cut* por forma (p. ej., esponja → disco), *zoom-through* atravesando un objeto, barrido con un elemento de la escena (ola, árbol en primer plano). |
| Ritmo | Corte o cambio de encuadre **cada 1–2 s**. En el gancho, cortes cada 0,7–1 s. |

### Etiquetas de datos (las del "300 kg" del video de referencia)
Una píldora redondeada de fondo `#1A1A1A` al 70 %, número en **Montserrat ExtraBold** amarillo `#FFD400` y unidad en pequeño. Entra con *pop* (escala 0 → 115 → 100 % en 0,25 s) junto con el SFX `pop`.

---

## 2. Personajes fijos (originales, usar en todos los videos)

### Nico, el explorador (protagonista)
- Adulto joven y curioso. Cabeza algo grande en proporción (1:3), ojos redondos y muy expresivos con cejas gruesas que hacen casi toda la actuación.
- **Vestuario fijo:** impermeable **mostaza** `#E8A93B`, gorro **rojo** con pompón `#D64545`, gafas redondas, mochila **verde** con un parche de rayo, pantalón azul marino y botas marrones.
- Textura de tela con costuras visibles en los bordes.
- **Expresiones de catálogo:** sorpresa (boca en "O", cejas arriba), "¡ajá!" (dedo índice levantado), pánico cómico (ojos en espiral), escéptico (una ceja arriba) y orgullo (brazos en jarra).
- Se le ve de frente, de perfil y de espaldas (cenital, como el excursionista del video de referencia).

### Chispa, la ayudante
- Pequeña luciérnaga redonda, del tamaño de un puño de Nico, con un cuerpo de fieltro **cian** `#3DE0E6` y una cola que brilla en amarillo.
- Es la que **trae las etiquetas de datos** y señala lo importante. No habla: hace ruiditos (*blip*).
- Funciona como transición: vuela por delante de la cámara y tapa el corte.

### Reparto secundario
Animales, órganos u objetos de cada tema, siempre con el mismo tratamiento: textura, bordes cosidos y ojos expresivos **solo si el tema lo permite** (en un oso de verdad, no; en una vértebra con cara, sí).

---

## 3. Tipografía y subtítulos

- Fuente: **Montserrat ExtraBold** (libre, Google Fonts).
- Subtítulos en el **tercio superior** (el centro queda a unos 520 px desde arriba en 1080×1920), igual que en el video de referencia, para no chocar con los botones de TikTok y Reels, que están a la derecha y abajo.
- Frases de **1 a 4 palabras**. La palabra activa va en blanco al 100 % y escalada al 112 %; el resto, en blanco al 60 %.
- Las **palabras clave** van en **amarillo `#FFD400`** al 120 % cuando suenan.
- Contorno oscuro de 6 px y sombra de 3 px. Tamaño de 96 px sobre 1080 de ancho.
- Zonas seguras: no poner texto en los 250 px de arriba, en los 420 px de abajo ni en los 140 px de la derecha.
- Los archivos `.ass` de cada video se generan con `herramientas/generar_subtitulos.py`.

---

## 4. Voz y narración

- **Voz masculina, español neutro**, enérgica y cercana. Ritmo de unas 3 a 3,5 palabras por segundo, con micro-pausas antes de cada dato clave.
- Humor ligero: comparaciones caseras ("como a un sándwich") y algún comentario breve. Sin sarcasmo hacia el espectador.
- Inspirada en el **tono** de los divulgadores de YouTube, **sin imitar ni clonar ninguna voz real**. Si usas TTS, elige una voz de catálogo genérica (de stock, nunca una clonada de una persona) o graba a un locutor con licencia.
- Ajustes de TTS sugeridos: estabilidad media-baja (más expresiva), velocidad 1,05–1,1× y énfasis con signos (¡!, ¿?) y comas.
- Postproducción: EQ con pasa-altos a 80 Hz, compresión 3:1, de-esser y loudness final de **−14 LUFS** integrados (pico −1 dBTP).

---

## 5. Música y efectos de sonido

- Música **libre de derechos** de la Biblioteca de Audio de YouTube, Pixabay Music o una librería con licencia (Epidemic, Artlist).
- Volumen: la música queda **18–22 dB por debajo de la voz**, con *ducking* automático (sidechain), y sube a −12 dB en el gancho y el cierre si no hay voz.
- Librería básica de SFX (Pixabay, Freesound CC0 o la de CapCut):
  - `whoosh` para transiciones y *whip pans*
  - `pop` cuando aparecen etiquetas y textos
  - `impacto` (*boom* grave) para datos chocantes
  - `blip` cuando Chispa aparece o se mueve
  - `ding` cuando algo sale bien o es correcto
  - `buzz` (error) para un mito o algo incorrecto
  - `squish` cuando se aprieta o comprime algo
  - `riser` para crear tensión antes del giro
  - `record scratch` para el giro inesperado

---

## 6. Rotación de formatos (2 videos al día)

| Día | Video A (mediodía) | Video B (noche) |
|---|---|---|
| Lun | Ciencia explicada fácil | Qué hacer si… |
| Mar | ¿Sabías que…? | Mitos vs. realidad |
| Mié | Qué hacer si… | Ciencia explicada fácil |
| Jue | Mitos vs. realidad | ¿Sabías que…? |
| Vie | Ciencia explicada fácil | Qué hacer si… |
| Sáb | ¿Sabías que…? | Mitos vs. realidad |
| Dom | Recopilatorio o repost del mejor de la semana | Qué hacer si… |

## 7. Horarios de publicación (punto de partida)

Son horas de referencia para una audiencia hispanohablante (México, Colombia, España). **Tómalas como hipótesis inicial** y ajústalas con las estadísticas de cada cuenta tras 2 o 3 semanas.

| Plataforma | Video A | Video B | Notas |
|---|---|---|---|
| TikTok | 12:00–13:00 | 19:00–21:00 | Los fines de semana funcionan bien a media mañana (10–11 h). |
| YouTube Shorts | 12:00–14:00 | 18:00–20:00 | Publica unas 2 h antes del pico de audiencia para que se indexe. |
| Facebook Reels | 13:00–14:00 | 20:00–21:00 | El público es algo mayor y responde mejor a "Qué hacer si…". |

Si tu audiencia principal está en España, usa esas horas en hora peninsular. Si está en LATAM, usa la hora de Ciudad de México (CDMX).

## 8. Control de calidad (antes de publicar)
- [ ] El gancho dice el dato o la pregunta en los primeros 3 s, también en texto en pantalla.
- [ ] No hay ningún plano estático de más de 2 s.
- [ ] Todos los datos tienen su fuente en la descripción o en un comentario fijado.
- [ ] Ortografía revisada: tildes, ¿ ¡ de apertura y números.
- [ ] Los subtítulos están dentro de las zonas seguras.
- [ ] La voz suena clara en el altavoz del móvil y la música no tapa las consonantes.
- [ ] Exportación 1080×1920, 30 fps, H.264, 10–16 Mbps, AAC 320 kbps.
