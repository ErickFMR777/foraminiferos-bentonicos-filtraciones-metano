"""
candidatos.py — Estudios candidatos para ampliar la base bibliográfica.

Lista de trabajo, no datos del dashboard. Cada entrada está verificada como
referencia real (DOI resuelto), pero NINGUNA aporta registros todavía: hace
falta leer el texto completo para extraer las listas de especies.

Flujo previsto:
  1. Descargar el PDF con acceso institucional.
  2. Dejarlo en Data_nosubiralrepo/  (ya está en .gitignore).
  3. Extraer la lista de especies, pasarla por WoRMS e integrarla con el
     mismo registro de correcciones que el resto.

Prioridad — se ordena por el hueco que llena, no por relevancia general:
  1  celda 0-15° / <150 m, que sigue vacía incluso con la base ampliada
  2  trópico (0-15°) a cualquier profundidad
  3  somero (<150 m) a cualquier latitud
  4  hemisferio sur, casi ausente de la base
  5  refuerzo metodológico o fauna de referencia regional
"""

from __future__ import annotations

CANDIDATOS = [
    dict(
        prioridad=1,
        titulo="Benthic foraminifera as bioindicators of gas seep intensity in the "
               "offshore zone of the Sinú fold belt",
        autores="Barragán-Jacksson, C. M. & Bernal, G. R.",
        anio=2024,
        revista="Journal of South American Earth Sciences 148, 105103",
        doi="10.1016/j.jsames.2024.105103",
        preprint="10.2139/ssrn.4866421",
        localidad="Cinturón del Sinú, Caribe colombiano",
        lat=9.5, lon=-76.2, banda_lat="0-15", banda_prof="< 150 m",
        por_que="LA MISMA ÁREA Y EL MISMO GRUPO que la tesis: Bernal es la "
                "directora. 18 estaciones en la plataforma externa del Caribe "
                "colombiano, con tipos de pared, distribución de abundancias, "
                "modificaciones del caparazón y δ13C de tres especies "
                "(Cribroelphidium poeyanum, Quinqueloculina candeiana, Lobatula "
                "ungeriana). Es el único candidato que caería en la celda vacía "
                "y aporta justo lo que a la tesis le faltaba: réplicas "
                "espaciales e isótopos.",
        advertencia="Publicado después de la tesis, sobre el mismo muestreo, y "
                    "probablemente la "
                    "cita. Conviene leerlo ANTES de publicar el dashboard: si "
                    "ya ocupa la celda vacía, la narrativa pasa de «nadie ha "
                    "estudiado esto» a «esto se acaba de empezar a estudiar».",
    ),
    dict(
        prioridad=2,
        titulo="Review of foraminifera methodologies related to hydrocarbon seeps "
               "on the ocean floor: implications for the Colombian Caribbean",
        autores="(por confirmar; grupo del Caribe colombiano)",
        anio=2022,
        revista="Boletín de Ciencias de la Tierra",
        doi=None,
        url="http://www.scielo.org.co/scielo.php?pid=S0120-36302022000100038",
        localidad="Caribe colombiano (revisión metodológica)",
        lat=None, lon=None, banda_lat="0-15", banda_prof=None,
        por_que="Acceso abierto (SciELO y Redalyc). Revisión metodológica "
                "específica para el Caribe colombiano y del mismo año que la "
                "tesis. Útil para contrastar criterios de muestreo y "
                "clasificación más que para sumar registros.",
        advertencia="Comprobar si procede del mismo grupo o incluso de esta "
                    "tesis; podría ser una fuente circular.",
    ),
    dict(
        prioridad=3,
        titulo="Decoupling short- and long-term methane seepage dynamics: "
               "high-resolution insights from Pyrgo spp. δ13C records at Woolsey "
               "Mound, Gulf of Mexico",
        autores="(equipo UiT / Louisiana)",
        anio=2025,
        revista="Earth and Planetary Science Letters",
        doi="10.1016/j.epsl.2025.119xxx",
        url="https://munin.uit.no/bitstream/handle/10037/37942/article.pdf",
        localidad="Woolsey Mound (MC118), norte del Golfo de México",
        lat=28.85, lon=-88.49, banda_lat="15-30", banda_prof="> 500 m",
        por_que="PDF en acceso abierto en el repositorio de UiT. Montículo de "
                "hidratos con δ13C en Pyrgo spp., un miliólido porcelanáceo: "
                "aporta al eje de tipo de pared y añade una morfología "
                "(montículo de hidratos) en el Golfo de México, donde la base "
                "sólo tiene campos de filtración sin morfología determinada.",
    ),
    dict(
        prioridad=4,
        titulo="Methane seep molluscs from the Sinú–San Jacinto fold belt in the "
               "Caribbean Sea of Colombia",
        autores="(por confirmar)",
        anio=None,
        revista="Journal of the Marine Biological Association of the UK",
        doi=None,
        localidad="Cinturón Sinú–San Jacinto, Caribe colombiano",
        lat=9.5, lon=-76.2, banda_lat="0-15", banda_prof="< 150 m",
        por_que="No es de foraminíferos, pero documenta fauna quimiosimbionte "
                "en la misma área de estudio. Sirve como evidencia "
                "independiente de que la filtración existe, que es justo lo que "
                "la tesis sólo puede presumir. Vale para la narrativa, no para "
                "la base de taxones.",
    ),
    dict(
        prioridad=5,
        titulo="Recent benthic foraminifera from the Caribbean continental slope "
               "and shelf off west of Colombia",
        autores="(por confirmar)",
        anio=None,
        revista="(por confirmar)",
        doi=None,
        localidad="Talud y plataforma del Caribe colombiano",
        lat=None, lon=None, banda_lat="0-15", banda_prof=None,
        por_que="Fauna de referencia regional, no de filtración. Ampliaría "
                "caribe_referencia.py, que hoy se apoya en cinco localidades "
                "extraídas de la prosa del capítulo 4.2 de la tesis.",
    ),
]

# Regiones donde la búsqueda no dio resultados útiles, para no repetirla:
# Golfo de Cádiz (volcanes de lodo con foraminíferos, pero trabajos centrados
# en corales de agua fría y en fauna fósil), Barbados y Trinidad (sólo
# formaciones fósiles), Brasil y Argentina (foraminíferos bentónicos abundantes
# pero ningún estudio de filtración con lista de especies), Makassar y Congo
# (sin trabajos de foraminíferos en filtración localizables).
BUSQUEDAS_SIN_RESULTADO = [
    "Golfo de Cádiz — volcanes de lodo", "Barbados / Trinidad",
    "Margen brasileño y argentino", "Estrecho de Makassar", "Abanico del Congo",
]
