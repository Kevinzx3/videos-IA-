"""Planos de los 6 videos de los días 8-10 (plantilla por datos)."""
N = "nico"
GIRO = dict(giro=True, sfx=["scratch"])
CTA_M = "¿TÚ QUÉ CREES?\nCOMENTA"


def cta(seg, txt):
    return dict(seg=seg, fondo="oscuro", cta=txt, tr="barrido", sfx=["whoosh", ("pop", 0.1), ("ding", 0.3)])


VUELO19 = [
    dict(seg=0, fondo="mar_noche", el=[("escuadron", 260, 700, 0.55)], txt="EXPEDIENTE #1", color="#FFD400", temblor=6, sfx=["impacto", "riser_suave"]),
    dict(seg=0, fr=0.55, fondo="mar_noche", el=[("escuadron", 260, 700, 0.55)], sello="NINGUNO VOLVIÓ", sfx=[("buzz", 0.15)]),
    dict(seg=1, fondo="oscuro", el=[("cal", "5", "DICIEMBRE", "1945", 540, 1000, 1.2)], txt="FLORIDA, EE. UU.", tr="barrido", sfx=["whoosh", ("pop", 0.05)]),
    dict(seg=2, fondo="espacio", el=[("escuadron", 200, 900, 0.7)], tag=("5 aviones", "· 14 tripulantes"), tagtam=95, sfx=["whoosh_grave"]),
    dict(seg=3, fondo="tormenta", el=[(N, 540, 1850, 1.0, "espiral", 160, 160)], txt="¡BRÚJULAS FALLANDO!", color="#FF4D6D", ty=800, sfx=["alarma"]),
    dict(seg=4, fondo="mar_noche", el=[("avion", 300, 800, 0.8, 40, 0)], txt="¿LOS CAYOS?", color="#FFD400", sfx=["blip"]),
    dict(seg=5, fondo="tormenta", el=[("avion", 540, 800, 0.8, 0, 0, 0)], txt="SIN COMBUSTIBLE", color="#FF4D6D", sfx=["latido", "ola"]),
    dict(seg=6, fondo="tormenta", el=[("avion", 300, 700, 0.7, 120, 120, -15)], txt="«VAMOS A AMERIZAR»", sfx=["whoosh_bajada"]),
    dict(seg=7, fondo="mar_noche", sello="SIN RESTOS", sellocolor="#FFFFFF", sfx=["ola", ("buzz", 0.2)]),
    dict(seg=8, fondo="mar_noche", **GIRO),
    dict(seg=9, fondo="tormenta", el=[("avion", 200, 750, 1.0, 60, 0)], tag=("13", "HOMBRES MÁS"), sfx=["whoosh", "riser_corto"]),
    dict(seg=10, fondo="mar_noche", el=[("explosion", 540, 800, 0.3)], txt="UNA EXPLOSIÓN", color="#FFB040", temblor=10, sfx=[("impacto", 0.3)]),
    dict(seg=11, fondo="papel", el=[("carta", "CAUSAS\nDESCONOCIDAS", "#3A3550", 540, 1000, 1.4, 0.1)], txt="NACE LA LEYENDA", color="#FFD400", sfx=["pop", ("ding", 0.8)]),
    cta(12, "¿QUÉ CREES\nQUE PASÓ?"),
]

TARDIGRADO = [
    dict(seg=0, fondo="espacio", el=[("tardigrado", 540, 1000, 1.3, False)], txt="SOBREVIVE AL ESPACIO", color="#FFD400", temblor=6, sfx=["impacto"]),
    dict(seg=1, fondo="musgo", el=[("tardigrado", 540, 1000, 1.5, False)], tag=("< 1", "mm"), sfx=["whoosh", ("pop", 0.3)]),
    dict(seg=2, fondo="musgo", el=[("tardigrado", 540, 1050, 1.2, False), ("chispa", 820, 700)], txt="«OSOS DE AGUA»", color="#7FD3FF", sfx=["blip"]),
    dict(seg=3, fondo="musgo", el=[("carta", "MUSGO", "#4E8F4A", 230, 1000, 0.9, 0.1), ("carta", "MAR", "#3D7BE0", 540, 1000, 0.9, 0.4), ("carta", "HIELO", "#7FB8D8", 850, 1000, 0.9, 0.7)], txt="VIVEN EN TODAS PARTES", sfx=["pop3"]),
    dict(seg=4, fondo="musgo", el=[("tardigrado", 540, 1000, 1.3, True)], txt="SE SECA Y SE ENCOGE", color="#FFD400", sfx=["squish"]),
    dict(seg=5, fondo="oscuro", el=[("carta", "HIELO", "#7FB8D8", 230, 1000, 0.9, 0.1), ("carta", "CALOR", "#FF4D6D", 540, 1000, 0.9, 0.4), ("carta", "RADIACIÓN", "#C8B400", 850, 1000, 0.9, 0.7)], txt="AGUANTA TODO", sfx=["pop3"]),
    dict(seg=6, fondo="espacio", el=[("planeta", "#2F7FD1", "#5BAA4E", 540, 1700, 1.4), ("tardigrado", 540, 800, 0.7, True)], tag=("2007", "· 10 DÍAS"), tagy=1150, tr="barrido", sfx=["whoosh_grave", ("pop", 0.3)]),
    dict(seg=7, fondo="laboratorio", el=[("tardigrado", 540, 1050, 1.3, False)], txt="¡SIGUEN VIVOS!", color="#7BFF9A", sfx=["burbujas", ("ding", 0.3)]),
    dict(seg=8, fondo="laboratorio", el=[("tardigrado", 440, 1050, 1.1, False), ("tardigrado", 800, 1200, 0.5, False)], txt="Y TUVIERON CRÍAS", sfx=["pop"]),
    dict(seg=9, fondo="espacio", **GIRO),
    dict(seg=10, fondo="espacio", el=[("luna", 540, 1150, 1.4), ("explosion", 640, 1000, 0.4)], tag=("2019", "LA LUNA"), tagy=1700, temblor=10, sfx=["whoosh", ("impacto", 0.4)]),
    dict(seg=11, fondo="espacio", el=[("luna", 540, 1250, 1.2), ("tardigrado", 540, 820, 0.5, True)], txt="¿SIGUEN AHÍ?", color="#FFD400", sfx=["riser_suave"]),
    cta(12, "¿QUÉ ANIMAL\nEXPLICO AHORA?"),
]

DIATLOV = [
    dict(seg=0, fondo="nieve_noche", el=[("tienda", 540, 1250, 1.2, True)], txt="EXPEDIENTE #2", color="#FFD400", temblor=6, sfx=["impacto", "riser_suave"]),
    dict(seg=1, fondo="oscuro", el=[("cal", "FEB", "1959", "URALES", 540, 1000, 1.2)], tr="barrido", sfx=["whoosh", ("pop", 0.05)]),
    dict(seg=2, fondo="nieve_dia", el=[("tienda", 700, 1250, 0.9, False), (N, 300, 1800, 0.8, "feliz", 20, 20)], txt="9 EXCURSIONISTAS", sfx=["whoosh"]),
    dict(seg=3, fondo="nieve_dia", el=[("tienda", 540, 1150, 1.3, True)], txt="CORTADA DESDE DENTRO", color="#FF4D6D", ty=1600, sfx=["squish", ("buzz", 0.3)]),
    dict(seg=4, fondo="nieve_dia", el=[("huellas",)], tag=("−30 °C", "DESCALZOS"), tagy=900, sfx=["paso"]),
    dict(seg=5, fondo="nieve_noche", sello="SIN SUPERVIVIENTES", sellocolor="#FFFFFF", sfx=["latido"]),
    dict(seg=6, fondo="oscuro", el=[("carta", "MILITARES", "#5A6A4A", 230, 1000, 0.9, 0.1), ("carta", "¿OVNIS?", "#8A4FD0", 540, 1000, 0.9, 0.5), ("carta", "¿YETI?", "#7FB8D8", 850, 1000, 0.9, 0.9)], txt="TEORÍAS", color="#FFD400", ty=760, sfx=["pop3"]),
    dict(seg=7, fondo="nieve_noche", **GIRO),
    dict(seg=8, fondo="nieve_dia", el=[("tienda", 540, 1300, 0.9, False)], tag=("2021", "AVALANCHA DE PLACA"), tagy=800, sfx=["whoosh_grave", ("pop", 0.3)]),
    dict(seg=9, fondo="nieve_dia", el=[("tienda", 540, 1300, 0.9, False)], txt="LA NIEVE SE DESLIZA", color="#7FD3FF", temblor=8, sfx=["squish3"]),
    dict(seg=10, fondo="nieve_noche", el=[(N, 540, 1850, 1.0, "espiral", 160, 160)], txt="HUYERON SIN VESTIRSE", sfx=["latido"]),
    dict(seg=11, fondo="papel", el=[("carta", "¿CASO\nCERRADO?", "#3A3550", 540, 1000, 1.4, 0.1)], sfx=["pop"]),
    cta(12, "¿TÚ QUÉ CREES\nQUE PASÓ?"),
]

RAYO = [
    dict(seg=0, fondo="tormenta", el=[("nube_tormenta",), ("rayo", 540, 460, 1.4)], txt="5× MÁS CALIENTE QUE EL SOL", color="#FFD400", tam=80, temblor=8, sfx=["impacto"]),
    dict(seg=1, fondo="tormenta", el=[("termometro", 540, 1250, 1.0)], tag=("≈30 000", "°C"), tagy=700, sfx=["riser_corto", ("pop", 0.6)]),
    dict(seg=2, fondo="espacio", el=[("sol", 540, 1000, 1.6)], tag=("≈5500", "°C"), tagy=1550, sfx=["whoosh_grave", ("pop", 0.3)]),
    dict(seg=3, fondo="tormenta", el=[("nube_tormenta",), ("chispa", 540, 700)], txt="HIELO Y AGUA CHOCANDO", sfx=["blip", "burbujas"]),
    dict(seg=4, fondo="tormenta", el=[("nube_tormenta",), ("rayo", 400, 460, 1.3)], txt="¡SALTA LA CHISPA!", color="#FFD400", temblor=8, sfx=["impacto"]),
    dict(seg=5, fondo="tormenta", el=[("ondas", 540, 1100, (255, 255, 255))], txt="EL AIRE EXPLOTA:\nTRUENO", sfx=["impacto", "ola"]),
    dict(seg=6, fondo="tormenta", el=[("rayo", 700, 460, 1.2), (N, 330, 1880, 0.9, "sorpresa", 10, 10)], txt="LUZ PRIMERO,\nSONIDO DESPUÉS", ty=800, sfx=["blip", ("impacto", 0.8)]),
    dict(seg=7, fondo="espacio", el=[("planeta", "#2F7FD1", "#5BAA4E", 540, 1150, 1.3), ("rayo", 400, 900, 0.4), ("rayo", 700, 1000, 0.4)], tag=("44", "RAYOS / SEGUNDO"), tagy=1700, sfx=["pop3"]),
    dict(seg=8, fondo="tormenta", **GIRO),
    dict(seg=9, fondo="tormenta", el=[("nube_tormenta",)], txt="NO BAJA DESDE LA NUBE", color="#FF4D6D", sfx=["buzz"]),
    dict(seg=10, fondo="tormenta", el=[("nube_tormenta",), ("rayo", 540, 460, 1.4)], txt="¡SUBE DESDE EL SUELO!", color="#FFD400", ty=1700, temblor=8, sfx=["riser_corto", ("impacto", 0.5)]),
    dict(seg=11, fondo="tormenta", el=[(N, 540, 1850, 1.0, "espiral", 160, 160)], txt="VA HACIA ARRIBA", sfx=["boing"]),
    cta(12, "¿TE CAYÓ UN\nRAYO CERCA?"),
]

VOYNICH = [
    dict(seg=0, fondo="papel", el=[("libro", 540, 1000, 1.2, -3)], txt="EXPEDIENTE #3", color="#FFD400", temblor=6, sfx=["impacto", "riser_suave"]),
    dict(seg=1, fondo="oscuro", el=[("cal", "1912", "ITALIA", None, 540, 1000, 1.2)], tr="barrido", sfx=["whoosh", ("pop", 0.05)]),
    dict(seg=2, fondo="papel", el=[("libro", 540, 1000, 1.1, 0)], txt="MANUSCRITO VOYNICH", color="#FFD400", sfx=["pop"]),
    dict(seg=3, fondo="papel", el=[("libro", 540, 1050, 1.6, 0)], tag=("+200", "PÁGINAS"), tagy=1600, sfx=["click", ("pop", 0.3)]),
    dict(seg=4, fondo="papel", el=[("libro", 540, 1000, 2.2, 0)], txt="PLANTAS QUE NO EXISTEN", fy=0.6, sfx=["whoosh"]),
    dict(seg=5, fondo="oscuro", el=[(N, 540, 1850, 1.0, "esfuerzo", 60, 60)], txt="NADIE LO HA DESCIFRADO", color="#FF4D6D", ty=800, sfx=["tictac"]),
    dict(seg=6, fondo="oscuro", el=[("carta", "¿IDIOMA?", "#3D7BE0", 230, 1000, 0.9, 0.1), ("carta", "¿CÓDIGO?", "#4E8F4A", 540, 1000, 0.9, 0.5), ("carta", "¿BROMA?", "#FF4D6D", 850, 1000, 0.9, 0.9)], sfx=["pop3"]),
    dict(seg=7, fondo="papel", **GIRO),
    dict(seg=8, fondo="laboratorio", el=[("libro", 540, 1000, 0.9, 0), ("chispa", 800, 700)], tag=("2009", "CARBONO 14"), tagy=1600, sfx=["blip", ("pop", 0.3)]),
    dict(seg=9, fondo="laboratorio", el=[("libro", 540, 900, 0.8, 0)], tag=("1404–1438", ""), tagy=1500, tagtam=150, sfx=["impacto"]),
    dict(seg=10, fondo="papel", el=[("libro", 540, 1000, 1.0, 0)], txt="UNIVERSIDAD DE YALE", color="#7FB8FF", sfx=["ding"]),
    dict(seg=11, fondo="papel", el=[("libro", 540, 1000, 1.0, 3)], sello="SIN DESCIFRAR", sfx=[("buzz", 0.2)]),
    cta(12, "¿TE ATREVES\nA LEERLO?"),
]

MIEL = [
    dict(seg=0, fondo="cocina", el=[("tarro", 540, 1150, 1.4)], txt="NUNCA CADUCA", color="#FFD400", temblor=6, sfx=["impacto"]),
    dict(seg=1, fondo="egipto", el=[("tarro", 540, 1100, 1.1)], tag=("+3000", "AÑOS"), tagy=1650, tr="barrido", sfx=["whoosh_grave", ("pop", 0.3)]),
    dict(seg=2, fondo="cocina", el=[("tarro", 540, 1150, 1.2), ("chispa", 820, 700)], txt="3 TRUCOS QUÍMICOS", color="#3A2A10", sfx=["blip"]),
    dict(seg=3, fondo="amarillo", el=[("carta", "POCA\nAGUA", "#3D7BE0", 540, 1000, 1.4, 0.05)], txt="TRUCO 1", color="#3A2A10", ty=700, sfx=["pop"]),
    dict(seg=4, fondo="cocina", el=[("tarro", 540, 1150, 1.2), ("bacteria_seca", 540, 1100)], txt="LA BACTERIA SE SECA", sfx=["squish"]),
    dict(seg=5, fondo="amarillo", el=[("carta", "MUY\nÁCIDA", "#FF4D6D", 540, 1000, 1.4, 0.05)], txt="TRUCO 2", color="#3A2A10", ty=700, sfx=["pop"]),
    dict(seg=6, fondo="amarillo", el=[("carta", "AGUA\nOXIGENADA", "#4E8F4A", 540, 1000, 1.4, 0.05)], txt="TRUCO 3", color="#3A2A10", ty=700, sfx=["pop", "burbujas"]),
    dict(seg=7, fondo="cocina", el=[("tarro", 540, 1150, 1.3)], txt="SIEMPRE BIEN CERRADA", sfx=["click"]),
    dict(seg=8, fondo="cocina", **GIRO),
    dict(seg=9, fondo="cocina", el=[("tarro", 540, 1150, 1.3, True)], txt="¿DURA Y BLANCA?", color="#FF4D6D", sfx=["blip"]),
    dict(seg=10, fondo="cocina", el=[("tarro", 540, 1150, 1.3, False), ("termometro", 870, 1250, 0.5, "#FFB040")], txt="BAÑO MARÍA", color="#FFD400", sfx=["burbujas", ("ding", 0.6)]),
    dict(seg=11, fondo="cocina", el=[("tarro", 540, 1150, 1.3)], txt="¡NO LA TIRES!", color="#FF4D6D", sfx=["pop"]),
    cta(12, "¿QUÉ ALIMENTO\nEXPLICO AHORA?"),
]
