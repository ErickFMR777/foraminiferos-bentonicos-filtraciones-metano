"""
estudios_nuevos.py — Estudios incorporados después de la tesis.

Datos extraídos de artículos que no formaban parte de la base original. Van
marcados con origen='nuevo' para que el dashboard pueda mostrar la base tal
como la construyó la tesis o la base actualizada.

El primero es el más consecuente: Barragán-Jacksson y Bernal (2024) trabajan en la
MISMA área que la tesis —la plataforma externa frente al Golfo de
Morrosquillo, dentro del Cinturón del Sinú—, con la misma directora y dentro
del mismo proyecto MSH. Publicado un año después, ocupa la celda de la
matriz que la tesis encontraba vacía.
"""

from __future__ import annotations

# Asociaciones por zona de actividad. El artículo no publica abundancias por
# especie, así que se registra presencia con la zona a la que se asocia cada
# taxón: es lo que el propio artículo reporta como resultado.
BARRAGAN_BERNAL_2024 = dict(
    doi="10.1016/j.jsames.2024.105103",
    titulo="Benthic foraminifera as bioindicators of gas seep intensity in the "
           "offshore zone of the Sinú fold belt",
    autores=["Barragán-Jacksson, C.M.", "Bernal, G.R."],
    anio=2024,
    revista="Journal of South American Earth Sciences",
    localidad="Cinturón del Sinú, plataforma externa frente al Golfo de Morrosquillo",
    region="Caribe colombiano",
    lat=9.54, lon=-76.23, prof_m=170,          # rango declarado: 40-300 m
    lat_banda="0-15",
    tipo="frio",
    morfologia="pockmark",
    mismo_proyecto=True,
    relacion_con_tesis="MISMO proyecto (MSH) y MISMA localidad que la tesis: "
                       "la plataforma externa frente al Golfo de Morrosquillo. "
                       "Confirmado por el autor de la tesis. Es la continuación "
                       "directa de este trabajo, con 18 estaciones donde la tesis "
                       "analizó una, y con los isótopos que a la tesis le faltaban.",
    nota="Área de 297 km², 18 estaciones, profundidades de 40 a 300 m. El campo "
         "se reconoce como de filtración por pockmarks, montículos, tapetes "
         "microbianos y flares acústicos, más manchas de petróleo detectadas por "
         "satélite. Campañas de mayo y junio de 2022.",
    # Lista completa leída del artículo y validada contra WoRMS. El artículo
    # no publica abundancias por especie, así que esto es presencia.
    taxones_completos=[
        "Amphistegina gibbosa",
        "Bigenerina irregularis",
        "Bolivina cochei",
        "Cibicides refulgens",
        "Cibicidoides mundulus",
        "Cibicidoides pseudoungerianus",
        "Cribroelphidium poeyanum",
        "Elphidium crispum",
        "Eponides inceratus",
        "Gaudryina aequa",
        "Lagenammina difflugiformis",
        "Lenticulina orbicularis",
        "Liebusella soldanii",
        "Lobatula ungeriana",
        "Lobatula wuellerstorfi",
        "Melonis affinis",
        "Planulina ariminensis",
        "Quinqueloculina candeiana",
        "Quinqueloculina padana",
        "Quinqueloculina polygona",
        "Reophax agglutinatus",
        "Reophax compressus",
        "Reussella spinulosa",
        "Rosalina floridensis",
        "Triloculina trigonula",
        "Uvigerina auberiana",
        "Uvigerina peregrina",
    ],
    # (taxón, zona de actividad, banda de profundidad). Las asociaciones que
    # el propio artículo declara para cada nivel de actividad.
    taxones=[
        ("Quinqueloculina candeiana", "baja", "< 150 m"),
        ("Triloculina trigonula", "baja", "< 150 m"),
        ("Lagenammina difflugiformis", "baja", "< 150 m"),
        ("Cribroelphidium poeyanum", "baja", "< 150 m"),
        ("Lobatula ungeriana", "moderada", "< 150 m"),
        ("Cibicidoides mundulus", "moderada", "150-500 m"),
        ("Cibicidoides pseudoungerianus", "moderada", "150-500 m"),
        ("Liebusella soldanii", "moderada-alta", "150-500 m"),
        ("Bigenerina irregularis", "moderada-alta", "150-500 m"),
        ("Reophax agglutinatus", "moderada-alta", "150-500 m"),
    ],
)

# --- Diversidad medida en el mismo campo de filtración --------------------
# Dato clave para interpretar MSH-BC-21. La tesis obtuvo H' = 3,43 y lo trató
# como una anomalía frente a la literatura, que predice DIVERSIDAD BAJA en
# filtraciones. Barragán-Jacksson y Bernal miden H' entre 3,0 y 3,8 en las 18
# estaciones del mismo campo, incluidas las de actividad alta: en esta
# plataforma tropical la diversidad alta es lo normal Y es compatible con
# filtración activa. El valor de la tesis deja de ser una anomalía.
DIVERSIDAD_SINU = dict(
    fuente="Barragán-Jacksson y Bernal (2024)",
    doi="10.1016/j.jsames.2024.105103",
    n_estaciones=18,
    shannon_min=3.0,
    shannon_max=3.8,
    shannon_min_estacion="estación 10",
    shannon_max_estacion="estación 19",
    nota="Shannon > 3 en todas las estaciones del campo de filtración del Sinú, "
         "incluidas las de actividad alta.",
)

# --- Isótopos estables en el mismo campo ---------------------------------
# La tesis no midió δ13C. Estos son los primeros valores publicados para el
# área, y proceden del mismo campo de filtración.
ISOTOPOS_SINU = [
    dict(taxon="Cribroelphidium poeyanum", d13c_min=-3.85, d13c_max=1.91,
         media=-1.71,
         nota="Valores por debajo de -3 ‰ en las estaciones 4, 5 y 10."),
    dict(taxon="Quinqueloculina candeiana", d13c_min=-1.18, d13c_max=0.02,
         media=None, nota=None),
    dict(taxon="Lobatula ungeriana", d13c_min=-3.03, d13c_max=1.99,
         media=None, nota=None),
]
