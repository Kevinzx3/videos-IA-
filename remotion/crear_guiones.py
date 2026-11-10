#!/usr/bin/env python3
"""Escribe los guiones (guiones/*.json) y el documento GUIONES_Y_PROMPTS.md."""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))

ESTILO = ("2D digital illustration, textured storybook style, soft painterly fur and grass texture, "
          "simple rounded shapes with fine grain, cinematic lighting, vertical 9:16 composition, "
          "empty top third for captions, no text, no watermark")
BOSQUE = ("forest clearing at dusk, purple to orange gradient sky with faint stars, dark teal pine tree "
          "silhouettes, distant purple mountains, thin glowing horizon line, textured green meadow")
PLAYA = ("calm ocean at dusk seen half underwater, purple to orange gradient sky, soft turquoise water "
         "with light rays, sandy bottom")
PANTANO = ("muddy riverbank at dusk, purple to orange gradient sky, dark teal reeds and pine silhouettes, "
           "wet glossy sand and mud")
EXCURSIONISTA = ("a hiker with teal jacket, orange backpack, yellow beanie and blue jeans")


def p(escena, entorno=BOSQUE):
    return f"{escena}, {entorno}, {ESTILO}"


GUIONES = [
    {
        "id": "puma", "titulo": "Qué hacer si te encuentras un puma",
        "escenas": [
            {"texto": "Si alguna vez te encuentras cara a cara con un puma, lo que hagas en los próximos segundos puede salvarte la vida.",
             "movimiento": "zoom-out", "sonidos": ["golpe", "gruñido"],
             "prompt": p("close-up front view of a snarling cougar showing its fangs, amber eyes, ears back"),
             "movimiento_ia": "the cougar snarls and slowly opens its mouth, breath visible, subtle camera push-in"},
            {"texto": "Es un felino de hasta *cien* kilos, y puede saltar más de cinco metros de un solo impulso.",
             "rotulo": "100 kg", "movimiento": "pan-der", "sonidos": ["pasos"],
             "prompt": p("side view of a large cougar walking across the meadow, long tail"),
             "movimiento_ia": "the cougar walks slowly from left to right, tail swaying"},
            {"texto": "Lo primero: *nunca* salgas corriendo. Si corres, activas su instinto de caza.",
             "rotulo": "NO CORRAS", "movimiento": "zoom-in", "sonidos": ["pasos"],
             "prompt": p(f"{EXCURSIONISTA} seen from behind, standing still, a cougar staring at him from the tree line"),
             "movimiento_ia": "the hiker freezes, the cougar takes one step forward"},
            {"texto": "Hazte lo más *grande* posible: levanta los brazos, abre tu chaqueta, y habla con voz fuerte.",
             "movimiento": "zoom-in",
             "prompt": p(f"{EXCURSIONISTA} seen from behind with both arms raised high, cougar in the distance"),
             "movimiento_ia": "the hiker raises both arms slowly above his head"},
            {"texto": "Mírale a los ojos, y retrocede *despacio*, sin darle nunca la espalda.",
             "rotulo": "DESPACIO", "movimiento": "pan-izq",
             "prompt": p("side view of a cougar standing still and staring, tail flicking"),
             "movimiento_ia": "the cougar stares, tail flicking, camera slowly pans"},
            {"texto": "Y si ataca, *defiéndete* con todo: piedras, palos, lo que tengas. Nunca te hagas el muerto.",
             "rotulo": "DEFIÉNDETE", "movimiento": "temblor", "efecto": "peligro", "sonidos": ["subida", "gruñido", "latido"],
             "prompt": p("a cougar crouching low ready to pounce, tense muscles, dramatic low angle"),
             "movimiento_ia": "the cougar crouches lower and lunges, camera shake"},
            {"texto": "Síguenos para más consejos que pueden salvarte la vida.",
             "rotulo": "SÍGUENOS", "movimiento": "zoom-in",
             "prompt": p("front view of a calm cougar sitting in the meadow, looking at the camera"),
             "movimiento_ia": "the cougar blinks slowly and tilts its head"},
        ],
    },
    {
        "id": "lobos", "titulo": "Qué hacer si te encuentras una manada de lobos",
        "escenas": [
            {"texto": "Si estás en el bosque y escuchas esto, presta mucha atención.",
             "movimiento": "zoom-in", "sonidos": ["aullido"],
             "prompt": p("a grey wolf howling on a small rock, silhouetted against the dusk sky"),
             "movimiento_ia": "the wolf lifts its head and howls"},
            {"texto": "Los lobos casi nunca atacan a las personas, pero una manada puede tener más de *diez* lobos.",
             "rotulo": "+10 LOBOS", "movimiento": "pan-der", "sonidos": ["pasos"],
             "prompt": p("a pack of grey wolves walking in a line along the edge of the forest"),
             "movimiento_ia": "the wolves walk in a line from left to right"},
            {"texto": "Si te ven, *no* corras. Para un lobo, algo que huye es una presa.",
             "rotulo": "NO CORRAS", "movimiento": "zoom-in",
             "prompt": p(f"{EXCURSIONISTA} seen from behind, frozen, three wolves watching him from the meadow"),
             "movimiento_ia": "the wolves lower their heads and watch"},
            {"texto": "Ponte de pie, hazte *grande* y haz mucho ruido: grita, aplaude, golpea un palo.",
             "movimiento": "temblor",
             "prompt": p(f"{EXCURSIONISTA} seen from behind shouting with arms raised, holding a stick"),
             "movimiento_ia": "the hiker waves the stick and shouts"},
            {"texto": "Retrocede *despacio* sin darles la espalda, y si puedes, sube a un árbol.",
             "rotulo": "DESPACIO", "movimiento": "pan-izq",
             "prompt": p(f"{EXCURSIONISTA} climbing a thick pine tree, wolves at the bottom"),
             "movimiento_ia": "the hiker climbs while the wolves circle the tree"},
            {"texto": "Si atacan, *defiéndete* y protege tu cuello y tu cara con los brazos.",
             "rotulo": "PROTEGE TU CUELLO", "movimiento": "temblor", "efecto": "peligro", "sonidos": ["subida", "gruñido", "latido"],
             "prompt": p("close-up front view of a snarling grey wolf with yellow eyes"),
             "movimiento_ia": "the wolf snarls and steps forward, camera shake"},
            {"texto": "Síguenos para más consejos de supervivencia.",
             "rotulo": "SÍGUENOS", "movimiento": "zoom-out",
             "prompt": p("a calm grey wolf sitting in the meadow under the stars"),
             "movimiento_ia": "the wolf looks around calmly"},
        ],
    },
    {
        "id": "serpiente", "titulo": "Qué hacer si te muerde una serpiente de cascabel",
        "escenas": [
            {"texto": "Si oyes este sonido en el campo, quédate completamente quieto.",
             "movimiento": "zoom-in", "sonidos": ["cascabel"],
             "prompt": p("close-up of a coiled rattlesnake shaking its rattle, tongue out"),
             "movimiento_ia": "the rattle vibrates quickly, the tongue flicks"},
            {"texto": "Una serpiente de cascabel puede atacar a una distancia de hasta la *mitad* de su cuerpo.",
             "rotulo": "½ DE SU LARGO", "movimiento": "pan-der",
             "prompt": p("side view of a rattlesnake stretched out on dry ground near rocks"),
             "movimiento_ia": "the snake slithers slowly"},
            {"texto": "Aléjate *despacio*, y nunca intentes atraparla ni matarla.",
             "rotulo": "ALÉJATE", "movimiento": "zoom-out",
             "prompt": p(f"{EXCURSIONISTA} slowly stepping backwards away from a coiled snake"),
             "movimiento_ia": "the hiker steps back slowly"},
            {"texto": "Si te muerde, llama a *emergencias* de inmediato y mantén la calma.",
             "rotulo": "LLAMA AL 911", "movimiento": "temblor", "efecto": "peligro", "sonidos": ["subida", "latido"],
             "prompt": p(f"{EXCURSIONISTA} sitting on a rock holding a phone to his ear, bandage on his leg"),
             "movimiento_ia": "the hiker talks on the phone, breathing heavily"},
            {"texto": "Quítate anillos y relojes, y deja la zona de la mordida a la altura del corazón.",
             "movimiento": "zoom-in",
             "prompt": p("close-up of hands removing a ring and a watch, warm light"),
             "movimiento_ia": "hands slide off a ring and a watch"},
            {"texto": "Y *nunca* cortes la herida, ni chupes el veneno, ni pongas hielo.",
             "rotulo": "NUNCA", "movimiento": "zoom-in",
             "prompt": p("a knife, an ice cube and a tourniquet crossed out with a big red X, on a wooden table"),
             "movimiento_ia": "the red X draws itself over the objects"},
            {"texto": "Síguenos para más consejos que pueden salvarte la vida.",
             "rotulo": "SÍGUENOS", "movimiento": "zoom-out",
             "prompt": p("a rattlesnake resting coiled on a warm rock at sunset"),
             "movimiento_ia": "the snake slowly lifts its head"},
        ],
    },
    {
        "id": "tiburon", "titulo": "Qué hacer si ves un tiburón cerca",
        "escenas": [
            {"texto": "Estás nadando tranquilo, y de repente ves esto acercándose.",
             "movimiento": "zoom-in", "sonidos": ["golpe"],
             "prompt": p("a shark fin cutting the water surface heading toward the viewer", PLAYA),
             "movimiento_ia": "the fin glides toward the camera"},
            {"texto": "Primero: *no* chapotees ni nades rápido. Los movimientos bruscos lo atraen.",
             "rotulo": "NO CHAPOTEES", "movimiento": "pan-der",
             "prompt": p("underwater view of a swimmer floating calmly, a shark circling below", PLAYA),
             "movimiento_ia": "the shark circles slowly below the swimmer"},
            {"texto": "Mantén el contacto visual. A los tiburones no les gusta que los *vean* venir.",
             "movimiento": "zoom-in",
             "prompt": p("underwater close-up of a shark face looking at the camera", PLAYA),
             "movimiento_ia": "the shark turns its head toward the camera"},
            {"texto": "Retrocede poco a poco hacia la orilla o un bote, sin darle la espalda.",
             "rotulo": "A LA ORILLA", "movimiento": "pan-izq",
             "prompt": p("swimmer slowly moving backwards toward a small boat, shark fin behind", PLAYA),
             "movimiento_ia": "the swimmer backs away slowly toward the boat"},
            {"texto": "Si ataca, golpea sus *ojos* y sus branquias. Son sus puntos más sensibles.",
             "rotulo": "OJOS Y BRANQUIAS", "movimiento": "temblor", "efecto": "peligro", "sonidos": ["subida", "latido"],
             "prompt": p("underwater dramatic view of a shark with open mouth, highlighted eyes and gills", PLAYA),
             "movimiento_ia": "the shark lunges, camera shake"},
            {"texto": "Síguenos para más datos que te pueden salvar.",
             "rotulo": "SÍGUENOS", "movimiento": "zoom-out",
             "prompt": p("a shark swimming away into the blue, light rays from the surface", PLAYA),
             "movimiento_ia": "the shark swims away into the distance"},
        ],
    },
    {
        "id": "abejas", "titulo": "Qué hacer si te ataca un enjambre de abejas",
        "escenas": [
            {"texto": "Si un enjambre de abejas empieza a perseguirte, tienes muy pocos segundos.",
             "movimiento": "temblor", "sonidos": ["golpe"],
             "prompt": p("a dense dark swarm of bees flying out of a tree hollow"),
             "movimiento_ia": "the swarm pours out of the tree"},
            {"texto": "*Corre* en línea recta, lo más rápido que puedas. Aquí sí hay que correr.",
             "rotulo": "CORRE", "movimiento": "pan-der", "sonidos": ["pasos"],
             "prompt": p(f"{EXCURSIONISTA} running across the meadow, a swarm of bees behind him"),
             "movimiento_ia": "the hiker runs, the swarm follows"},
            {"texto": "Cúbrete la cara con la camiseta. Ellas atacan sobre todo la cabeza.",
             "movimiento": "zoom-in",
             "prompt": p(f"{EXCURSIONISTA} running while pulling his shirt over his face"),
             "movimiento_ia": "he pulls his shirt up over his face while running"},
            {"texto": "Métete en un coche o un edificio. *No* saltes al agua: te esperan en la superficie.",
             "rotulo": "NO AL AGUA", "movimiento": "zoom-in",
             "prompt": p("a small car parked at the edge of the forest, bees bumping against the closed windows"),
             "movimiento_ia": "bees bounce off the windows"},
            {"texto": "Después, saca los aguijones raspando con una tarjeta, no con los dedos.",
             "rotulo": "RASPA", "movimiento": "zoom-in",
             "prompt": p("close-up of a credit card scraping a bee stinger off an arm"),
             "movimiento_ia": "the card slides over the skin removing the stinger"},
            {"texto": "Síguenos para más consejos de supervivencia.",
             "rotulo": "SÍGUENOS", "movimiento": "zoom-out",
             "prompt": p("a single cute bee resting on a wildflower in the meadow"),
             "movimiento_ia": "the bee flutters its wings"},
        ],
    },
    {
        "id": "arenas", "titulo": "Qué hacer si caes en arenas movedizas",
        "escenas": [
            {"texto": "Las películas mienten: las arenas movedizas no te tragan por completo.",
             "movimiento": "zoom-in", "sonidos": ["golpe"],
             "prompt": p(f"{EXCURSIONISTA} sunk up to his waist in quicksand, worried face", PANTANO),
             "movimiento_ia": "he sinks slightly, mud bubbling"},
            {"texto": "Tu cuerpo es menos denso que la arena mojada, así que como mucho te hundes hasta la *cintura*.",
             "rotulo": "HASTA LA CINTURA", "movimiento": "pan-der",
             "prompt": p("cross-section diagram style illustration of a person floating in quicksand, sand layers", PANTANO),
             "movimiento_ia": "the sand layers shift slowly"},
            {"texto": "El peligro real es quedarte atrapado. Así que *no* forcejees.",
             "rotulo": "NO FORCEJEES", "movimiento": "temblor", "efecto": "peligro", "sonidos": ["latido"],
             "prompt": p(f"{EXCURSIONISTA} struggling in quicksand, mud splashing", PANTANO),
             "movimiento_ia": "he thrashes and sinks a bit more, camera shake"},
            {"texto": "Échate hacia atrás para repartir tu peso, y mueve las piernas muy *despacio*.",
             "rotulo": "DESPACIO", "movimiento": "zoom-in",
             "prompt": p(f"{EXCURSIONISTA} leaning back on the quicksand surface, arms spread out", PANTANO),
             "movimiento_ia": "he slowly leans back, legs rising"},
            {"texto": "Así el agua entra, la arena te suelta, y puedes flotar hasta la orilla.",
             "movimiento": "pan-izq",
             "prompt": p(f"{EXCURSIONISTA} floating on his back and paddling toward solid ground", PANTANO),
             "movimiento_ia": "he paddles slowly toward the bank"},
            {"texto": "Síguenos para más mitos y verdades de supervivencia.",
             "rotulo": "SÍGUENOS", "movimiento": "zoom-out",
             "prompt": p(f"{EXCURSIONISTA} sitting safe on the riverbank, covered in mud, smiling", PANTANO),
             "movimiento_ia": "he wipes mud from his face and smiles"},
        ],
    },
]


from guiones_extra import GUIONES_EXTRA
for _g in GUIONES:
    _g.setdefault("categoria", "Qué hacer si...")
GUIONES += GUIONES_EXTRA


def main():
    os.makedirs(os.path.join(BASE, "guiones"), exist_ok=True)
    md = ["# Guiones y prompts\n",
          "Cómo usarlos: genera una imagen por escena con el **prompt de imagen** (Leonardo, Ideogram, "
          "Midjourney, ChatGPT/DALL·E, Gemini…), en vertical 9:16, y guárdala como "
          "`public/<id>/escena1.png`, `escena2.png`… Si usas IA de imagen a video (Kling, Runway, Pika), "
          "usa el **prompt de movimiento**. Las palabras entre *asteriscos* salen resaltadas en el subtítulo.\n",
          "**Consejo de estilo:** genera primero la escena 1, y usa esa imagen como referencia de estilo/personaje "
          "en las demás para que todo el video se vea igual.\n"]
    for g in GUIONES:
        json.dump(g, open(os.path.join(BASE, "guiones", g["id"] + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        dur = sum(len(e["texto"].split()) for e in g["escenas"]) / 2.6
        md.append(f"\n---\n\n## [{g['categoria']}] {g['titulo']}  (`{g['id']}`, ~{dur:.0f} s)\n")
        md.append("**Narración completa (para ElevenLabs):**\n\n> " + " ".join(e["texto"].replace("*", "") for e in g["escenas"]) + "\n")
        for i, e in enumerate(g["escenas"], 1):
            md.append(f"\n### Escena {i}" + (f" — rótulo «{e['rotulo']}»" if e.get("rotulo") else ""))
            md.append(f"\n- **Voz:** {e['texto']}")
            md.append(f"- **Prompt de imagen:** `{e['prompt']}`")
            md.append(f"- **Prompt de movimiento:** `{e['movimiento_ia']}`")
            if e.get("sonidos"): md.append(f"- **Sonidos:** {', '.join(e['sonidos'])}")
    open(os.path.join(BASE, "GUIONES_Y_PROMPTS.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("✔", len(GUIONES), "guiones")


if __name__ == "__main__":
    main()
